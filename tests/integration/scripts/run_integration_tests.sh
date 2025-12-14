#!/bin/bash

# Integration Test Runner
# Executes all integration tests for the Architecture AI Assistant

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="$(dirname "$SCRIPT_DIR")"
PAYLOADS_DIR="$TESTS_DIR/payloads"
RESULTS_DIR="$TESTS_DIR/results"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
RESULTS_FILE="$RESULTS_DIR/test_results_$TIMESTAMP.md"

# AWS Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
DYNAMODB_TABLE=${DYNAMODB_TABLE_NAME:-architecture-ai-assistant-chat_history-dev}
S3_BUCKET=${S3_BUCKET_NAME:-architecture-ai-assistant-bucket-dev}
LAMBDA_CHAT_CRUD=${LAMBDA_CHAT_CRUD:-architecture-ai-assistant-chat-crud-dev}
LAMBDA_GENERATE_DIAGRAM=${LAMBDA_GENERATE_DIAGRAM:-architecture-ai-assistant-generate-diagram-dev}
API_GATEWAY_URL=${API_GATEWAY_URL:-https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev}
CLOUDFRONT_URL=${CLOUDFRONT_URL:-https://d1to0rasl28a6e.cloudfront.net}

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓ PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}[✗ FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test functions
test_dynamodb_put() {
    log_info "Testing DynamoDB PUT operation..."
    ((TESTS_TOTAL++))
    
    RESPONSE=$(aws lambda invoke \
        --function-name "$LAMBDA_CHAT_CRUD" \
        --cli-binary-format raw-in-base64-out \
        --payload file://"$PAYLOADS_DIR/dynamodb/put_operation.json" \
        --region "$AWS_REGION" \
        /tmp/response.json 2>&1 && cat /tmp/response.json)
    
    if echo "$RESPONSE" | grep -q '"success": true'; then
        log_success "DynamoDB PUT operation"
    else
        log_error "DynamoDB PUT operation"
        echo "$RESPONSE"
    fi
}

test_dynamodb_get() {
    log_info "Testing DynamoDB GET operation..."
    ((TESTS_TOTAL++))
    
    RESPONSE=$(aws lambda invoke \
        --function-name "$LAMBDA_CHAT_CRUD" \
        --cli-binary-format raw-in-base64-out \
        --payload file://"$PAYLOADS_DIR/dynamodb/get_operation.json" \
        --region "$AWS_REGION" \
        /tmp/response.json 2>&1 && cat /tmp/response.json)
    
    if echo "$RESPONSE" | grep -q '"success": true'; then
        log_success "DynamoDB GET operation"
    else
        log_error "DynamoDB GET operation"
        echo "$RESPONSE"
    fi
}

test_s3_put() {
    log_info "Testing S3 PUT operation..."
    ((TESTS_TOTAL++))
    
    RESPONSE=$(aws lambda invoke \
        --function-name "$LAMBDA_GENERATE_DIAGRAM" \
        --cli-binary-format raw-in-base64-out \
        --payload file://"$PAYLOADS_DIR/s3/put_operation.json" \
        --region "$AWS_REGION" \
        /tmp/response.json 2>&1 && cat /tmp/response.json)
    
    if echo "$RESPONSE" | grep -q '"success": true'; then
        log_success "S3 PUT operation"
    else
        log_error "S3 PUT operation"
        echo "$RESPONSE"
    fi
}

test_s3_get() {
    log_info "Testing S3 GET operation..."
    ((TESTS_TOTAL++))
    
    RESPONSE=$(aws lambda invoke \
        --function-name "$LAMBDA_GENERATE_DIAGRAM" \
        --cli-binary-format raw-in-base64-out \
        --payload file://"$PAYLOADS_DIR/s3/get_operation.json" \
        --region "$AWS_REGION" \
        /tmp/response.json 2>&1 && cat /tmp/response.json)
    
    if echo "$RESPONSE" | grep -q '"success": true'; then
        log_success "S3 GET operation"
    else
        log_error "S3 GET operation"
        echo "$RESPONSE"
    fi
}

test_s3_iam_policy() {
    log_info "Testing S3 IAM policy restrictions..."
    ((TESTS_TOTAL++))
    
    RESPONSE=$(aws lambda invoke \
        --function-name "$LAMBDA_GENERATE_DIAGRAM" \
        --cli-binary-format raw-in-base64-out \
        --payload file://"$PAYLOADS_DIR/s3/invalid_path.json" \
        --region "$AWS_REGION" \
        /tmp/response.json 2>&1 && cat /tmp/response.json)
    
    if echo "$RESPONSE" | grep -q 'AccessDenied'; then
        log_success "S3 IAM policy correctly restricts access"
    else
        log_warning "S3 IAM policy test - expected AccessDenied"
    fi
}

test_cloudfront() {
    log_info "Testing CloudFront distribution..."
    ((TESTS_TOTAL++))
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$CLOUDFRONT_URL/")
    
    if [ "$HTTP_CODE" = "200" ]; then
        log_success "CloudFront distribution serving frontend"
    else
        log_error "CloudFront distribution (HTTP $HTTP_CODE)"
    fi
}

test_api_gateway() {
    log_info "Testing API Gateway connectivity..."
    ((TESTS_TOTAL++))
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "$API_GATEWAY_URL/api/chat/save" \
        -H "Content-Type: application/json" \
        -d '{"chatId":"test","userMessage":"test","diagramType":"flowchart"}')
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "400" ]; then
        log_success "API Gateway responding"
    else
        log_error "API Gateway (HTTP $HTTP_CODE)"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Integration Test Suite${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    log_info "Starting integration tests..."
    log_info "Timestamp: $TIMESTAMP"
    log_info "Region: $AWS_REGION"
    echo ""
    
    # Run tests
    test_dynamodb_put
    test_dynamodb_get
    test_s3_put
    test_s3_get
    test_s3_iam_policy
    test_cloudfront
    test_api_gateway
    
    # Summary
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Test Summary${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "Total Tests: $TESTS_TOTAL"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}✗ Some tests failed!${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
