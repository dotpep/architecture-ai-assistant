#!/usr/bin/env python3
"""
End-to-end verification script for the Architecture AI Assistant deployment.
Tests the complete user flow: open app, generate diagram, download, and verify chat history persistence.

Requirements: 1.1, 2.1, 3.5, 4.2
"""

import json
import time
import requests
import sys
from pathlib import Path

# Configuration
API_GATEWAY_URL = "https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev"
CLOUDFRONT_URL = "https://d1to0rasl28a6e.cloudfront.net"
AWS_REGION = "us-east-1"

# Test data
TEST_PROMPT = "Create a simple flowchart for a user login process"
TEST_DIAGRAM_TYPE = "flowchart"


def log_info(msg):
    print(f"ℹ {msg}")


def log_success(msg):
    print(f"✓ {msg}")


def log_error(msg):
    print(f"✗ {msg}")


def log_warning(msg):
    print(f"⚠ {msg}")


def verify_cloudfront_accessible():
    """Verify that CloudFront URL is accessible."""
    log_info("Verifying CloudFront frontend accessibility...")
    try:
        response = requests.get(CLOUDFRONT_URL, timeout=10)
        if response.status_code == 200:
            log_success("CloudFront frontend is accessible")
            return True
        else:
            log_error(f"CloudFront returned status code {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Failed to access CloudFront: {str(e)}")
        return False


def verify_api_gateway_accessible():
    """Verify that API Gateway is accessible."""
    log_info("Verifying API Gateway accessibility...")
    try:
        # Try to call the generate_diagram endpoint with a test payload
        url = f"{API_GATEWAY_URL}/api/diagram/generate"
        headers = {"Content-Type": "application/json"}
        payload = {
            "userPrompt": TEST_PROMPT,
            "diagramType": TEST_DIAGRAM_TYPE
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        # We expect either 200 (success) or 502 (LLM API error), but not 404 or 403
        if response.status_code in [200, 502]:
            log_success("API Gateway is accessible")
            return True, response
        elif response.status_code == 404:
            log_error("API Gateway endpoint not found (404)")
            return False, None
        elif response.status_code == 403:
            log_error("API Gateway access forbidden (403)")
            return False, None
        else:
            log_warning(f"API Gateway returned status code {response.status_code}")
            return True, response
    except Exception as e:
        log_error(f"Failed to access API Gateway: {str(e)}")
        return False, None


def verify_diagram_generation():
    """Verify that diagram generation works."""
    log_info("Testing diagram generation endpoint...")
    try:
        url = f"{API_GATEWAY_URL}/api/diagram/generate"
        headers = {"Content-Type": "application/json"}
        payload = {
            "userPrompt": TEST_PROMPT,
            "diagramType": TEST_DIAGRAM_TYPE
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ["chatId", "mermaidCode", "imageUrl", "markdownUrl", "status"]
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                log_error(f"Response missing fields: {missing_fields}")
                return False, None
            
            # Verify Mermaid code is present
            if not data.get("mermaidCode"):
                log_error("Mermaid code is empty")
                return False, None
            
            log_success("Diagram generation successful")
            log_info(f"  Chat ID: {data['chatId']}")
            log_info(f"  Status: {data['status']}")
            log_info(f"  Mermaid code length: {len(data['mermaidCode'])} characters")
            
            return True, data
        elif response.status_code == 502:
            log_warning("LLM API service unavailable (502) - this is expected if LLM API key is not configured")
            return False, None
        else:
            log_error(f"Diagram generation failed with status {response.status_code}")
            log_error(f"Response: {response.text}")
            return False, None
    except Exception as e:
        log_error(f"Failed to test diagram generation: {str(e)}")
        return False, None


def verify_chat_save():
    """Verify that chat messages can be saved."""
    log_info("Testing chat save endpoint...")
    try:
        url = f"{API_GATEWAY_URL}/api/chat/save"
        headers = {"Content-Type": "application/json"}
        payload = {
            "userMessage": TEST_PROMPT,
            "diagramType": TEST_DIAGRAM_TYPE
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            if not data.get("success") or not data.get("chatId"):
                log_error("Invalid save response structure")
                return False, None
            
            log_success("Chat save successful")
            log_info(f"  Chat ID: {data['chatId']}")
            
            return True, data
        else:
            log_error(f"Chat save failed with status {response.status_code}")
            log_error(f"Response: {response.text}")
            return False, None
    except Exception as e:
        log_error(f"Failed to test chat save: {str(e)}")
        return False, None


def verify_chat_history():
    """Verify that chat history can be retrieved."""
    log_info("Testing chat history endpoint...")
    try:
        url = f"{API_GATEWAY_URL}/api/chat/history?limit=10"
        headers = {"Content-Type": "application/json"}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            if "chats" not in data or "count" not in data:
                log_error("Invalid history response structure")
                return False, None
            
            log_success("Chat history retrieval successful")
            log_info(f"  Total chats: {data['count']}")
            log_info(f"  Returned chats: {len(data['chats'])}")
            
            if data['chats']:
                first_chat = data['chats'][0]
                log_info(f"  Latest chat ID: {first_chat.get('chatId')}")
            
            return True, data
        else:
            log_error(f"Chat history retrieval failed with status {response.status_code}")
            log_error(f"Response: {response.text}")
            return False, None
    except Exception as e:
        log_error(f"Failed to test chat history: {str(e)}")
        return False, None


def verify_download_urls():
    """Verify that download URLs are accessible."""
    log_info("Testing download URL accessibility...")
    
    # First, generate a diagram to get URLs
    success, diagram_data = verify_diagram_generation()
    
    if not success or not diagram_data:
        log_warning("Skipping download URL verification (diagram generation failed)")
        return False
    
    # Test markdown URL
    markdown_url = diagram_data.get("markdownUrl")
    if markdown_url:
        try:
            response = requests.head(markdown_url, timeout=10)
            if response.status_code == 200:
                log_success(f"Markdown download URL is accessible")
            else:
                log_warning(f"Markdown URL returned status {response.status_code}")
        except Exception as e:
            log_warning(f"Failed to verify markdown URL: {str(e)}")
    
    # Test image URL
    image_url = diagram_data.get("imageUrl")
    if image_url:
        try:
            response = requests.head(image_url, timeout=10)
            if response.status_code == 200:
                log_success(f"Image download URL is accessible")
            else:
                log_warning(f"Image URL returned status {response.status_code}")
        except Exception as e:
            log_warning(f"Failed to verify image URL: {str(e)}")
    
    return True


def main():
    """Run all verification tests."""
    print("\n" + "="*60)
    print("  Architecture AI Assistant - End-to-End Verification")
    print("="*60 + "\n")
    
    results = {
        "cloudfront": False,
        "api_gateway": False,
        "diagram_generation": False,
        "chat_save": False,
        "chat_history": False,
        "download_urls": False
    }
    
    # Test 1: CloudFront accessibility
    results["cloudfront"] = verify_cloudfront_accessible()
    print()
    
    # Test 2: API Gateway accessibility
    api_accessible, _ = verify_api_gateway_accessible()
    results["api_gateway"] = api_accessible
    print()
    
    # Test 3: Diagram generation
    diagram_success, _ = verify_diagram_generation()
    results["diagram_generation"] = diagram_success
    print()
    
    # Test 4: Chat save
    chat_save_success, _ = verify_chat_save()
    results["chat_save"] = chat_save_success
    print()
    
    # Test 5: Chat history
    history_success, _ = verify_chat_history()
    results["chat_history"] = history_success
    print()
    
    # Test 6: Download URLs
    results["download_urls"] = verify_download_urls()
    print()
    
    # Summary
    print("="*60)
    print("  Verification Summary")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
    
    print()
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    if passed == total:
        log_success(f"All {total} tests passed!")
        return 0
    else:
        log_warning(f"{passed}/{total} tests passed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
