#!/usr/bin/env python3
"""
Script to package and deploy Lambda functions to AWS.
Handles packaging Lambda functions with dependencies and uploading to AWS Lambda.
"""

import os
import sys
import json
import subprocess
import shutil
import zipfile
from pathlib import Path

# Configuration
# Navigate from infrastructure/scripts/lambda to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
LAMBDA_DIR = PROJECT_ROOT / "src" / "backend" / "lambda_functions"
SHARED_DIR = PROJECT_ROOT / "src" / "backend" / "shared"
BUILD_DIR = PROJECT_ROOT / "build" / "lambda"
TERRAFORM_DIR = PROJECT_ROOT / "infrastructure" / "terraform"

LAMBDA_FUNCTIONS = ["generate_diagram", "chat_crud", "get_history", "session_crud"]
AWS_REGION = "us-east-1"


def log_info(msg):
    print(f"[INFO] {msg}")


def log_success(msg):
    print(f"[OK] {msg}")


def log_error(msg):
    print(f"[ERROR] {msg}")


def run_command(cmd, cwd=None):
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            log_error(f"Command failed: {cmd}")
            print(result.stderr)
            return False
        return True
    except Exception as e:
        log_error(f"Error running command: {e}")
        return False


def create_layer():
    """Create Lambda layer with shared dependencies."""
    log_info("Creating Lambda layer with shared dependencies...")
    
    layer_dir = BUILD_DIR / "layer"
    python_dir = layer_dir / "python"
    
    # Clean and create directories
    if layer_dir.exists():
        shutil.rmtree(layer_dir)
    python_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy shared modules
    for item in SHARED_DIR.iterdir():
        if item.is_file() and item.suffix == ".py":
            shutil.copy(item, python_dir)
    
    # Install dependencies
    log_info("Installing Python dependencies...")
    requirements_file = PROJECT_ROOT / "requirements.txt"
    if requirements_file.exists():
        cmd = f"pip3 install -r {requirements_file} -t {python_dir} --quiet"
        if not run_command(cmd):
            log_error("Failed to install dependencies")
            return False
    
    # Create layer zip
    layer_zip = BUILD_DIR / "lambda_layer.zip"
    log_info(f"Creating layer zip: {layer_zip}")
    
    with zipfile.ZipFile(layer_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(layer_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(layer_dir)
                zf.write(file_path, arcname)
    
    log_success("Lambda layer created")
    return True


def package_function(func_name):
    """Package a single Lambda function."""
    log_info(f"Packaging {func_name} Lambda function...")
    
    func_dir = LAMBDA_DIR / func_name
    func_build_dir = BUILD_DIR / func_name
    
    if not func_dir.exists():
        log_error(f"Function directory not found: {func_dir}")
        return False
    
    # Clean and create build directory
    if func_build_dir.exists():
        shutil.rmtree(func_build_dir)
    func_build_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy function code
    for item in func_dir.iterdir():
        if item.is_file() and item.suffix == ".py":
            shutil.copy(item, func_build_dir)
    
    # Copy shared modules to root level (so they can be imported directly)
    for item in SHARED_DIR.iterdir():
        if item.is_file() and item.suffix == ".py":
            shutil.copy(item, func_build_dir)
    
    # Install function-specific dependencies if they exist
    func_requirements = func_dir / "requirements.txt"
    if func_requirements.exists():
        cmd = f"pip3 install -r {func_requirements} -t {func_build_dir} --quiet"
        if not run_command(cmd):
            log_error(f"Failed to install dependencies for {func_name}")
            return False
    
    # Create function zip
    func_zip = BUILD_DIR / f"{func_name}.zip"
    log_info(f"Creating function zip: {func_zip}")
    
    with zipfile.ZipFile(func_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(func_build_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(func_build_dir)
                zf.write(file_path, arcname)
    
    log_success(f"{func_name} packaged")
    return True


def upload_lambda_function(func_name):
    """Upload a Lambda function to AWS."""
    log_info(f"Uploading {func_name} to AWS Lambda...")
    
    func_zip = BUILD_DIR / f"{func_name}.zip"
    if not func_zip.exists():
        log_error(f"Function zip not found: {func_zip}")
        return False
    
    # Get function name from Terraform outputs
    terraform_output = subprocess.run(
        "terraform output -json",
        shell=True,
        cwd=TERRAFORM_DIR,
        capture_output=True,
        text=True
    )
    
    if terraform_output.returncode != 0:
        log_error("Failed to get Terraform outputs")
        return False
    
    outputs = json.loads(terraform_output.stdout)
    
    # Map function names to Terraform output keys
    func_mapping = {
        "generate_diagram": "lambda_generate_diagram_arn",
        "chat_crud": "lambda_chat_crud_arn",
        "get_history": "lambda_get_history_arn",
        "session_crud": "lambda_session_crud_arn"
    }
    
    if func_name not in func_mapping:
        log_error(f"Unknown function: {func_name}")
        return False
    
    # Extract function name from ARN
    arn = outputs[func_mapping[func_name]]["value"]
    lambda_func_name = arn.split(":")[-1]
    
    # Upload function code
    cmd = f"aws lambda update-function-code --function-name {lambda_func_name} --zip-file fileb://{func_zip} --region {AWS_REGION}"
    if not run_command(cmd):
        log_error(f"Failed to upload {func_name}")
        return False
    
    log_success(f"{func_name} uploaded")
    return True


def main():
    """Main deployment function."""
    print("\n" + "="*50)
    print("  Lambda Function Deployment")
    print("="*50 + "\n")
    
    # Create build directory
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Create Lambda layer
    if not create_layer():
        log_error("Failed to create Lambda layer")
        sys.exit(1)
    
    # Step 2: Package Lambda functions
    for func in LAMBDA_FUNCTIONS:
        if not package_function(func):
            log_error(f"Failed to package {func}")
            sys.exit(1)
    
    # Step 3: Upload Lambda functions
    for func in LAMBDA_FUNCTIONS:
        if not upload_lambda_function(func):
            log_error(f"Failed to upload {func}")
            sys.exit(1)
    
    print("\n" + "="*50)
    print("  Deployment Complete!")
    print("="*50 + "\n")
    log_success("All Lambda functions deployed successfully")


if __name__ == "__main__":
    main()
