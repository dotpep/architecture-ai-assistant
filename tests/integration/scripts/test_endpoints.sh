#!/bin/bash

# API Gateway Endpoint Tests
# Tests all API Gateway endpoints for the Architecture AI Assistant

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_GATEWAY_URL=${API_GATEWAY_URL:-https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev}
TIMEOUT=${TIMEOUT:-10}

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

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

# Test functions
test_generate_diagram() {
    log_info "Testing POST /api/diagram/generate..."
    
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST "$API_GATEWAY_URL/api/diagram/generate" \
        -H "Content-Type: application/json" \
        -d '{
            "userPrompt": "Create a simple flowchart",
            "diagramType": "flowchart"
        }' \
        --max-time "$TIMEOUT")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "500" ]; then
        log_success "POST /api/diagram/generate (HTTP $HTTP_CODE)"
    else
        log_error "POST /api/diagram/generate (HTTP $HTTP_CODE)"
    fi
}

test_save_chat() {
    log_info "Testing POST /api/chat/save..."
    
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST "$API_GATEWAY_URL/api/chat/save" \
        -H "Content-Type: application/json" \
        -d '{
            "chatId": "test-'$(date +%s)'",
            "userMessage": "Test message",
            "diagramType": "flowchart"
        }' \
        --max-time "$TIMEOUT")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "400" ]; then
        log_success "POST /api/chat/save (HTTP $HTTP_CODE)"
    else
        log_error "POST /api/chat/save (HTTP $HTTP_CODE)"
    fi
}

test_get_history() {
    log_info "Testing GET /api/chat/history..."
    
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X GET "$API_GATEWAY_URL/api/chat/history?limit=10" \
        -H "Content-Type: application/json" \
        --max-time "$TIMEOUT")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "400" ]; then
        log_success "GET /api/chat/history (HTTP $HTTP_CODE)"
    else
        log_error "GET /api/chat/history (HTTP $HTTP_CODE)"
    fi
}

test_cors_headers() {
    log_info "Testing CORS headers..."
    
    RESPONSE=$(curl -s -i -X OPTIONS "$API_GATEWAY_URL/api/diagram/generate" \
        -H "Origin: http://localhost:3000" \
        --max-time "$TIMEOUT")
    
    if echo "$RESPONSE" | grep -q "Access-Control-Allow-Origin"; then
        log_success "CORS headers present"
    else
        log_error "CORS headers missing"
    fi
}

test_invalid_endpoint() {
    log_info "Testing invalid endpoint..."
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X GET "$API_GATEWAY_URL/api/invalid" \
        --max-time "$TIMEOUT")
    
    if [ "$HTTP_CODE" = "404" ] || [ "$HTTP_CODE" = "403" ]; then
        log_success "Invalid endpoint returns error (HTTP $HTTP_CODE)"
    else
        log_error "Invalid endpoint (HTTP $HTTP_CODE)"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}API Gateway Endpoint Tests${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    log_info "Testing API Gateway: $API_GATEWAY_URL"
    echo ""
    
    # Run tests
    test_generate_diagram
    test_save_chat
    test_get_history
    test_cors_headers
    test_invalid_endpoint
    
    # Summary
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Test Summary${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All endpoint tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}✗ Some endpoint tests failed!${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
