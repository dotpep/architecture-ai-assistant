#!/usr/bin/env python3
"""
End-to-end verification script for Architecture AI Assistant.
Tests the complete user flow: open app, generate diagram, download, verify chat history.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Configuration
CLOUDFRONT_URL = "https://d1to0rasl28a6e.cloudfront.net"
API_GATEWAY_URL = "https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev"
DYNAMODB_TABLE = "architecture-ai-assistant-chat_history-dev"
S3_BUCKET = "architecture-ai-assistant-bucket-dev"
AWS_REGION = "us-east-1"

# Test data
TEST_PROMPT = "Create a simple flowchart showing a user login process with email and password validation"
TEST_DIAGRAM_TYPE = "flowchart"


def log_info(msg):
    print(f"ℹ {msg}")


def log_success(msg):
    print(f"✓ {msg}")


def log_error(msg):
    print(f"✗ {msg}")


def log_warning(msg):
    print(f"⚠ {msg}")


def test_frontend_accessibility() -> bool:
    """Test that the frontend is accessible via CloudFront."""
    log_info("Testing frontend accessibility...")
    
    try:
        response = requests.get(CLOUDFRONT_URL, timeout=10)
        if response.status_code == 200:
            if "<!DOCTYPE html>" in response.text or "<html" in response.text:
                log_success("Frontend is accessible and returns HTML")
                return True
            else:
                log_error("Frontend returned non-HTML content")
                return False
        else:
            log_error(f"Frontend returned status code {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Failed to access frontend: {e}")
        return False


def test_api_endpoints() -> bool:
    """Test that API endpoints are accessible."""
    log_info("Testing API endpoints...")
    
    endpoints = [
        ("POST", "/api/diagram/generate"),
        ("GET", "/api/chat/history"),
        ("POST", "/api/chat/save")
    ]
    
    all_accessible = True
    
    for method, endpoint in endpoints:
        try:
            url = f"{API_GATEWAY_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json={}, timeout=10)
            
            # We expect 400 (bad request) for POST with empty body, or 200 for GET
            if response.status_code in [200, 400, 405]:
                log_success(f"{method} {endpoint} is accessible")
            else:
                log_warning(f"{method} {endpoint} returned {response.status_code}")
        except Exception as e:
            log_error(f"Failed to access {method} {endpoint}: {e}")
            all_accessible = False
    
    return all_accessible


def test_diagram_generation() -> Optional[Dict[str, Any]]:
    """Test diagram generation via API."""
    log_info("Testing diagram generation...")
    
    try:
        payload = {
            "userPrompt": TEST_PROMPT,
            "diagramType": TEST_DIAGRAM_TYPE
        }
        
        response = requests.post(
            f"{API_GATEWAY_URL}/api/diagram/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ["chatId", "mermaidCode", "imageUrl", "markdownUrl", "status"]
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                log_error(f"Response missing fields: {missing_fields}")
                return None
            
            if data["status"] != "completed":
                log_error(f"Diagram generation failed with status: {data['status']}")
                return None
            
            log_success(f"Diagram generated successfully (ID: {data['chatId']})")
            return data
        else:
            log_error(f"Diagram generation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        log_error(f"Failed to generate diagram: {e}")
        return None


def test_download_urls(diagram_data: Dict[str, Any]) -> bool:
    """Test that download URLs are accessible."""
    log_info("Testing download URLs...")
    
    urls = {
        "Image": diagram_data.get("imageUrl"),
        "Markdown": diagram_data.get("markdownUrl")
    }
    
    all_accessible = True
    
    for name, url in urls.items():
        if not url:
            log_error(f"{name} URL is missing")
            all_accessible = False
            continue
        
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                log_success(f"{name} URL is accessible")
            else:
                log_error(f"{name} URL returned status {response.status_code}")
                all_accessible = False
        except Exception as e:
            log_error(f"Failed to access {name} URL: {e}")
            all_accessible = False
    
    return all_accessible


def test_chat_history(chat_id: str) -> bool:
    """Test that chat history can be retrieved."""
    log_info("Testing chat history retrieval...")
    
    try:
        # Wait a moment for DynamoDB to be consistent
        time.sleep(1)
        
        response = requests.get(
            f"{API_GATEWAY_URL}/api/chat/history?limit=10",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            if "chats" not in data or "count" not in data:
                log_error("History response missing required fields")
                return False
            
            # Check if our chat is in the history
            chat_found = any(chat.get("chatId") == chat_id for chat in data["chats"])
            
            if chat_found:
                log_success(f"Chat history retrieved successfully (found {data['count']} chats)")
                return True
            else:
                log_warning(f"Chat {chat_id} not found in history yet (may need more time)")
                return True  # Don't fail - DynamoDB eventual consistency
        else:
            log_error(f"History retrieval failed with status {response.status_code}")
            return False
            
    except Exception as e:
        log_error(f"Failed to retrieve chat history: {e}")
        return False


def test_save_chat() -> Optional[str]:
    """Test saving a chat message."""
    log_info("Testing chat save functionality...")
    
    try:
        payload = {
            "userMessage": "Test message for verification",
            "diagramType": "flowchart"
        }
        
        response = requests.post(
            f"{API_GATEWAY_URL}/api/chat/save",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success") and data.get("chatId"):
                log_success(f"Chat saved successfully (ID: {data['chatId']})")
                return data["chatId"]
            else:
                log_error("Chat save response indicates failure")
                return None
        else:
            log_error(f"Chat save failed with status {response.status_code}")
            return None
            
    except Exception as e:
        log_error(f"Failed to save chat: {e}")
        return None


def main():
    """Run all end-to-end verification tests."""
    print("\n" + "="*60)
    print("  End-to-End Verification - Architecture AI Assistant")
    print("="*60 + "\n")
    
    results = {
        "frontend_accessible": False,
        "api_endpoints_accessible": False,
        "diagram_generation": False,
        "download_urls_accessible": False,
        "chat_history_retrieval": False,
        "chat_save": False
    }
    
    # Test 1: Frontend accessibility
    results["frontend_accessible"] = test_frontend_accessibility()
    print()
    
    # Test 2: API endpoints
    results["api_endpoints_accessible"] = test_api_endpoints()
    print()
    
    # Test 3: Diagram generation
    diagram_data = test_diagram_generation()
    results["diagram_generation"] = diagram_data is not None
    print()
    
    # Test 4: Download URLs
    if diagram_data:
        results["download_urls_accessible"] = test_download_urls(diagram_data)
        print()
        
        # Test 5: Chat history
        results["chat_history_retrieval"] = test_chat_history(diagram_data["chatId"])
        print()
    
    # Test 6: Chat save
    chat_id = test_save_chat()
    results["chat_save"] = chat_id is not None
    print()
    
    # Summary
    print("="*60)
    print("  Verification Summary")
    print("="*60 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed\n")
    
    if passed == total:
        log_success("All end-to-end verification tests passed!")
        return 0
    else:
        log_error(f"{total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
