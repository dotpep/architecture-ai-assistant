#!/bin/bash
# Architecture AI Assistant - Deployment Script
# Requirements: 6.1, 6.2, 8.4
# 
# This script performs a complete deployment of the Architecture AI Assistant:
# 1. Packages Lambda functions with dependencies
# 2. Deploys infrastructure with Terraform
# 3. Builds and uploads frontend to S3
# 4. Invalidates CloudFront cache

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo ""
echo "=========================================="
echo "  Architecture AI Assistant Deployment"
echo "=========================================="
echo ""

# ============================================
# Step 1: Validate Prerequisites
# ============================================

log_info "Validating prerequisites..."

# Check for required commands
REQUIRED_COMMANDS=("terraform" "aws" "python3" "node" "npm" "zip")
for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
        log_error "Required command '$cmd' not found. Please install it first."
        exit 1
    fi
done

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    log_error "AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

log_success "Prerequisites validated"

# ============================================
# Step 2: Package Lambda Functions
# ============================================

log_info "Packaging Lambda functions..."

LAMBDA_DIR="$PROJECT_ROOT/src/backend/lambda_functions"
SHARED_DIR="$PROJECT_ROOT/src/backend/shared"
BUILD_DIR="$PROJECT_ROOT/build"
LAMBDA_BUILD_DIR="$BUILD_DIR/lambda"

# Create build directory
mkdir -p "$LAMBDA_BUILD_DIR"

# Package shared dependencies as Lambda layer
log_info "Creating Lambda layer with shared dependencies..."
LAYER_DIR="$LAMBDA_BUILD_DIR/layer"
mkdir -p "$LAYER_DIR/python"

# Copy shared modules
cp -r "$SHARED_DIR"/* "$LAYER_DIR/python/"

# Install Python dependencies for layer (if requirements.txt exists)
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip3 install -r "$PROJECT_ROOT/requirements.txt" -t "$LAYER_DIR/python" --quiet
fi

# Create layer zip
cd "$LAYER_DIR"
zip -r "$LAMBDA_BUILD_DIR/lambda_layer.zip" . > /dev/null
cd "$PROJECT_ROOT"
log_success "Lambda layer packaged"

# Package individual Lambda functions
LAMBDA_FUNCTIONS=("generate_diagram" "chat_crud" "get_history")

for func in "${LAMBDA_FUNCTIONS[@]}"; do
    log_info "Packaging $func Lambda function..."
    
    FUNC_DIR="$LAMBDA_DIR/$func"
    FUNC_BUILD_DIR="$LAMBDA_BUILD_DIR/$func"
    
    if [ ! -d "$FUNC_DIR" ]; then
        log_warning "Function directory $FUNC_DIR not found, skipping..."
        continue
    fi
    
    # Create function build directory
    mkdir -p "$FUNC_BUILD_DIR"
    
    # Copy function code
    cp -r "$FUNC_DIR"/* "$FUNC_BUILD_DIR/"
    
    # Install function-specific dependencies if requirements.txt exists
    if [ -f "$FUNC_DIR/requirements.txt" ]; then
        pip3 install -r "$FUNC_DIR/requirements.txt" -t "$FUNC_BUILD_DIR" --quiet
    fi
    
    # Create function zip
    cd "$FUNC_BUILD_DIR"
    zip -r "$LAMBDA_BUILD_DIR/${func}.zip" . > /dev/null
    cd "$PROJECT_ROOT"
    
    log_success "$func packaged"
done

# ============================================
# Step 3: Deploy Infrastructure with Terraform
# ============================================

log_info "Deploying infrastructure with Terraform..."

TERRAFORM_DIR="$PROJECT_ROOT/infrastructure/terraform"
cd "$TERRAFORM_DIR"

# Copy packaged Lambda functions to Terraform directory
if [ -f "$LAMBDA_BUILD_DIR/lambda_layer.zip" ]; then
    cp "$LAMBDA_BUILD_DIR/lambda_layer.zip" "$TERRAFORM_DIR/"
fi

for func in "${LAMBDA_FUNCTIONS[@]}"; do
    if [ -f "$LAMBDA_BUILD_DIR/${func}.zip" ]; then
        cp "$LAMBDA_BUILD_DIR/${func}.zip" "$TERRAFORM_DIR/"
    fi
done

# Initialize Terraform if needed
if [ ! -d ".terraform" ]; then
    log_info "Initializing Terraform..."
    terraform init
fi

# Plan and apply
log_info "Running Terraform plan..."
terraform plan -out=tfplan

log_info "Applying Terraform configuration..."
terraform apply tfplan

# Capture outputs
log_info "Capturing Terraform outputs..."
OUTPUTS=$(terraform output -json)

S3_BUCKET=$(echo "$OUTPUTS" | python3 -c "import sys, json; print(json.load(sys.stdin)['s3_bucket_name']['value'])")
CLOUDFRONT_DISTRO=$(echo "$OUTPUTS" | python3 -c "import sys, json; print(json.load(sys.stdin)['cloudfront_distribution_id']['value'])")
CLOUDFRONT_URL=$(echo "$OUTPUTS" | python3 -c "import sys, json; print(json.load(sys.stdin)['cloudfront_url']['value'])")
API_GATEWAY_URL=$(echo "$OUTPUTS" | python3 -c "import sys, json; print(json.load(sys.stdin)['api_gateway_url']['value'])")

log_success "Infrastructure deployed"

cd "$PROJECT_ROOT"

# ============================================
# Step 4: Build and Deploy Frontend
# ============================================

log_info "Building frontend application..."

FRONTEND_DIR="$PROJECT_ROOT/src/frontend"
cd "$FRONTEND_DIR"

# Install dependencies
log_info "Installing frontend dependencies..."
npm install --silent

# Create/update .env file with API Gateway URL
log_info "Configuring frontend environment..."
cat > .env << EOF
VITE_API_BASE_URL=$API_GATEWAY_URL
EOF

# Build frontend
log_info "Building production bundle..."
npm run build

log_success "Frontend built"

# Upload to S3
log_info "Uploading frontend to S3..."
aws s3 sync dist/ "s3://$S3_BUCKET/frontend/" --delete --quiet

log_success "Frontend uploaded to S3"

cd "$PROJECT_ROOT"

# ============================================
# Step 5: Invalidate CloudFront Cache
# ============================================

log_info "Invalidating CloudFront cache..."

INVALIDATION_OUTPUT=$(aws cloudfront create-invalidation \
    --distribution-id "$CLOUDFRONT_DISTRO" \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)

log_success "CloudFront cache invalidation created (ID: $INVALIDATION_OUTPUT)"

# ============================================
# Deployment Complete
# ============================================

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
log_success "Frontend URL: $CLOUDFRONT_URL"
log_success "API Gateway URL: $API_GATEWAY_URL"
log_success "S3 Bucket: $S3_BUCKET"
echo ""
log_info "Note: CloudFront cache invalidation may take a few minutes to complete."
log_info "You can check the status with:"
echo "  aws cloudfront get-invalidation --distribution-id $CLOUDFRONT_DISTRO --id $INVALIDATION_OUTPUT"
echo ""
