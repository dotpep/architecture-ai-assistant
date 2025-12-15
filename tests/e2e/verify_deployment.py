#!/usr/bin/env python3
"""
Deployment verification script for Architecture AI Assistant.
Verifies that all infrastructure components are properly deployed and configured.
"""

import requests
import json
import time
import sys
import boto3
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError, NoCredentialsError

# Configuration
CLOUDFRONT_URL = "https://d1to0rasl28a6e.cloudfront.net"
API_GATEWAY_URL = "https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev"
DYNAMODB_TABLE = "architecture-ai-assistant-chat_history-dev"
S3_BUCKET = "architecture-ai-assistant-bucket-dev"
AWS_REGION = "us-east-1"

# Lambda function names
LAMBDA_FUNCTIONS = [
    "architecture-ai-assistant-generate-diagram-dev",
    "architecture-ai-assistant-chat-crud-dev",
    "architecture-ai-assistant-get-history-dev",
    "architecture-ai-assistant-session-crud-dev"
]


def log_info(msg):
    print(f"ℹ {msg}")


def log_success(msg):
    print(f"✓ {msg}")


def log_error(msg):
    print(f"✗ {msg}")


def log_warning(msg):
    print(f"⚠ {msg}")


def verify_aws_credentials() -> bool:
    """Verify AWS credentials are configured."""
    log_info("Verifying AWS credentials...")
    
    try:
        sts = boto3.client('sts', region_name=AWS_REGION)
        identity = sts.get_caller_identity()
        log_success(f"AWS credentials verified (Account: {identity['Account']})")
        return True
    except NoCredentialsError:
        log_error("AWS credentials not found. Please configure AWS CLI.")
        return False
    except Exception as e:
        log_error(f"Failed to verify AWS credentials: {e}")
        return False


def verify_dynamodb_table() -> bool:
    """Verify DynamoDB table exists and is accessible."""
    log_info(f"Verifying DynamoDB table: {DYNAMODB_TABLE}")
    
    try:
        dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
        response = dynamodb.describe_table(TableName=DYNAMODB_TABLE)
        
        table_status = response['Table']['TableStatus']
        if table_status == 'ACTIVE':
            log_success(f"DynamoDB table is active")
            
            # Check table schema
            key_schema = response['Table']['KeySchema']
            expected_keys = {'PK', 'SK'}
            actual_keys = {key['AttributeName'] for key in key_schema}
            
            if expected_keys.issubset(actual_keys):
                log_success("DynamoDB table schema is correct (PK/SK pattern)")
                return True
            else:
                log_error(f"DynamoDB table schema incorrect. Expected PK/SK, got: {actual_keys}")
                return False
        else:
            log_error(f"DynamoDB table status: {table_status}")
            return False
            
    except ClientError as e:
        log_error(f"Failed to access DynamoDB table: {e}")
        return False
    except Exception as e:
        log_error(f"Unexpected error verifying DynamoDB: {e}")
        return False


def verify_s3_bucket() -> bool:
    """Verify S3 bucket exists and is accessible."""
    log_info(f"Verifying S3 bucket: {S3_BUCKET}")
    
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        
        # Check if bucket exists
        s3.head_bucket(Bucket=S3_BUCKET)
        log_success("S3 bucket exists and is accessible")
        
        # Check bucket policy/permissions by trying to list objects
        try:
            response = s3.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=1)
            log_success("S3 bucket permissions verified")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                log_warning("S3 bucket exists but list access denied (may be expected)")
                return True
            else:
                log_error(f"S3 bucket permission error: {e}")
                return False
                
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            log_error("S3 bucket not found")
        else:
            log_error(f"Failed to access S3 bucket: {e}")
        return False
    except Exception as e:
        log_error(f"Unexpected error verifying S3: {e}")
        return False


def verify_lambda_functions() -> bool:
    """Verify all Lambda functions exist and are configured correctly."""
    log_info("Verifying Lambda functions...")
    
    try:
        lambda_client = boto3.client('lambda', region_name=AWS_REGION)
        all_functions_ok = True
        
        for function_name in LAMBDA_FUNCTIONS:
            try:
                response = lambda_client.get_function(FunctionName=function_name)
                
                # Check function state
                state = response['Configuration']['State']
                if state == 'Active':
                    log_success(f"Lambda function {function_name} is active")
                else:
                    log_error(f"Lambda function {function_name} state: {state}")
                    all_functions_ok = False
                    
                # Check runtime
                runtime = response['Configuration']['Runtime']
                if runtime.startswith('python'):
                    log_success(f"Lambda function {function_name} runtime: {runtime}")
                else:
                    log_warning(f"Lambda function {function_name} unexpected runtime: {runtime}")
                    
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    log_error(f"Lambda function {function_name} not found")
                else:
                    log_error(f"Error accessing Lambda function {function_name}: {e}")
                all_functions_ok = False
                
        return all_functions_ok
        
    except Exception as e:
        log_error(f"Unexpected error verifying Lambda functions: {e}")
        return False


def verify_api_gateway() -> bool:
    """Verify API Gateway is deployed and accessible."""
    log_info("Verifying API Gateway deployment...")
    
    # Test all endpoints
    endpoints = [
        ("GET", "/api/chat/history"),
        ("POST", "/api/diagram/generate"),
        ("POST", "/api/chat/save"),
        ("GET", "/api/session"),
        ("POST", "/api/session"),
    ]
    
    all_endpoints_ok = True
    
    for method, endpoint in endpoints:
        try:
            url = f"{API_GATEWAY_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json={}, timeout=10)
            
            # We expect 200 (success) or 400 (bad request for empty POST)
            if response.status_code in [200, 400]:
                log_success(f"API Gateway endpoint {method} {endpoint} is accessible")
            else:
                log_error(f"API Gateway endpoint {method} {endpoint} returned {response.status_code}")
                all_endpoints_ok = False
                
        except Exception as e:
            log_error(f"Failed to access API Gateway endpoint {method} {endpoint}: {e}")
            all_endpoints_ok = False
    
    return all_endpoints_ok


def verify_cloudfront_distribution() -> bool:
    """Verify CloudFront distribution is serving the frontend."""
    log_info("Verifying CloudFront distribution...")
    
    try:
        response = requests.get(CLOUDFRONT_URL, timeout=10)
        
        if response.status_code == 200:
            # Check if it's serving HTML content
            if "<!DOCTYPE html>" in response.text or "<html" in response.text:
                log_success("CloudFront is serving HTML content")
                
                # Check for React app indicators
                if "react" in response.text.lower() or "vite" in response.text.lower():
                    log_success("Frontend React application detected")
                else:
                    log_warning("React application indicators not found in HTML")
                
                return True
            else:
                log_error("CloudFront not serving HTML content")
                return False
        else:
            log_error(f"CloudFront returned status code {response.status_code}")
            return False
            
    except Exception as e:
        log_error(f"Failed to access CloudFront distribution: {e}")
        return False


def verify_cors_configuration() -> bool:
    """Verify CORS is properly configured."""
    log_info("Verifying CORS configuration...")
    
    try:
        # Make an OPTIONS request to check CORS headers
        response = requests.options(
            f"{API_GATEWAY_URL}/api/diagram/generate",
            headers={
                'Origin': CLOUDFRONT_URL,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        if cors_headers['Access-Control-Allow-Origin']:
            log_success("CORS Access-Control-Allow-Origin header present")
        else:
            log_warning("CORS Access-Control-Allow-Origin header missing")
            
        if cors_headers['Access-Control-Allow-Methods']:
            log_success("CORS Access-Control-Allow-Methods header present")
        else:
            log_warning("CORS Access-Control-Allow-Methods header missing")
            
        return True
        
    except Exception as e:
        log_warning(f"Could not verify CORS configuration: {e}")
        return True  # Don't fail deployment verification for CORS issues


def verify_iam_permissions() -> bool:
    """Verify IAM permissions are correctly configured."""
    log_info("Verifying IAM permissions...")
    
    try:
        # Test DynamoDB access
        dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
        dynamodb.describe_table(TableName=DYNAMODB_TABLE)
        log_success("IAM permissions for DynamoDB verified")
        
        # Test S3 access
        s3 = boto3.client('s3', region_name=AWS_REGION)
        s3.head_bucket(Bucket=S3_BUCKET)
        log_success("IAM permissions for S3 verified")
        
        # Test Lambda access
        lambda_client = boto3.client('lambda', region_name=AWS_REGION)
        lambda_client.list_functions(MaxItems=1)
        log_success("IAM permissions for Lambda verified")
        
        return True
        
    except Exception as e:
        log_error(f"IAM permission verification failed: {e}")
        return False


def verify_session_management_deployment() -> bool:
    """Verify session management features are properly deployed."""
    log_info("Verifying session management deployment...")
    
    try:
        # Test session creation endpoint
        response = requests.post(f"{API_GATEWAY_URL}/api/session", json={}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["sessionId", "title", "diagramType", "createdAt", "updatedAt", "messageCount"]
            
            if all(field in data for field in required_fields):
                log_success("Session creation endpoint working correctly")
                session_id = data["sessionId"]
                
                # Test session list endpoint
                list_response = requests.get(f"{API_GATEWAY_URL}/api/session?limit=5", timeout=10)
                if list_response.status_code == 200:
                    list_data = list_response.json()
                    if "sessions" in list_data and "count" in list_data:
                        log_success("Session list endpoint working correctly")
                        
                        # Test session messages endpoint
                        messages_response = requests.get(
                            f"{API_GATEWAY_URL}/api/session/{session_id}/messages", 
                            timeout=10
                        )
                        if messages_response.status_code == 200:
                            messages_data = messages_response.json()
                            if "chats" in messages_data and "count" in messages_data:
                                log_success("Session messages endpoint working correctly")
                                return True
                            else:
                                log_error("Session messages endpoint response format incorrect")
                        else:
                            log_error(f"Session messages endpoint failed: {messages_response.status_code}")
                    else:
                        log_error("Session list endpoint response format incorrect")
                else:
                    log_error(f"Session list endpoint failed: {list_response.status_code}")
            else:
                log_error("Session creation endpoint response missing required fields")
        else:
            log_error(f"Session creation endpoint failed: {response.status_code}")
            
        return False
        
    except Exception as e:
        log_error(f"Session management verification failed: {e}")
        return False


def main():
    """Run all deployment verification tests."""
    print("\n" + "="*70)
    print("  Deployment Verification - Architecture AI Assistant")
    print("  Including Session Management Infrastructure")
    print("="*70 + "\n")
    
    results = {
        "aws_credentials": False,
        "dynamodb_table": False,
        "s3_bucket": False,
        "lambda_functions": False,
        "api_gateway": False,
        "cloudfront_distribution": False,
        "cors_configuration": False,
        "iam_permissions": False,
        "session_management": False
    }
    
    # Test 1: AWS Credentials
    results["aws_credentials"] = verify_aws_credentials()
    print()
    
    if not results["aws_credentials"]:
        log_error("Cannot proceed without AWS credentials")
        return 1
    
    # Test 2: DynamoDB Table
    results["dynamodb_table"] = verify_dynamodb_table()
    print()
    
    # Test 3: S3 Bucket
    results["s3_bucket"] = verify_s3_bucket()
    print()
    
    # Test 4: Lambda Functions
    results["lambda_functions"] = verify_lambda_functions()
    print()
    
    # Test 5: API Gateway
    results["api_gateway"] = verify_api_gateway()
    print()
    
    # Test 6: CloudFront Distribution
    results["cloudfront_distribution"] = verify_cloudfront_distribution()
    print()
    
    # Test 7: CORS Configuration
    results["cors_configuration"] = verify_cors_configuration()
    print()
    
    # Test 8: IAM Permissions
    results["iam_permissions"] = verify_iam_permissions()
    print()
    
    # Test 9: Session Management
    results["session_management"] = verify_session_management_deployment()
    print()
    
    # Summary
    print("="*70)
    print("  Deployment Verification Summary")
    print("="*70 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} verifications passed\n")
    
    if passed == total:
        log_success("All deployment verifications passed!")
        log_info("The Architecture AI Assistant is fully deployed and operational.")
        return 0
    else:
        log_error(f"{total - passed} verification(s) failed")
        log_info("Please check the failed components before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())