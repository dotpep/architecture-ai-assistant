#!/bin/bash

# Build Lambda Layer with Python Dependencies
# This script creates a Lambda layer with required Python packages for AWS Lambda

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
LAYER_DIR="$PROJECT_ROOT/infrastructure/lambda_layer"
PYTHON_DIR="$LAYER_DIR/python"

echo "Building Lambda layer for Python 3.11 on x86_64..."

# Create directory structure
mkdir -p "$PYTHON_DIR"

# Install dependencies with Lambda-compatible flags
echo "Installing requests..."
pip install requests \
  --target "$PYTHON_DIR/" \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --python-version 3.11 \
  --quiet

# Create zip file
echo "Creating layer zip..."
cd "$LAYER_DIR"
zip -r "$PROJECT_ROOT/infrastructure/terraform/lambda_layer.zip" python/ > /dev/null 2>&1

echo "✓ Lambda layer built: $PROJECT_ROOT/infrastructure/terraform/lambda_layer.zip"
echo "✓ Size: $(du -h $PROJECT_ROOT/infrastructure/terraform/lambda_layer.zip | cut -f1)"

# Clean up
rm -rf "$LAYER_DIR"

echo "✓ Done!"
