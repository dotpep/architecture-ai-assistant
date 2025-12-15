"""
Manual test script for get_history Lambda function.
Run this to verify the implementation without pytest.
"""

import json
import sys
import os
from unittest.mock import Mock, MagicMock

# Mock boto3 before importing
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()
sys.modules['botocore.exceptions'] = MagicMock()

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/backend/lambda_functions/get_history'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/backend/shared'))

from lambda_function import get_history, encode_next_token, decode_next_token, lambda_handler


def test_get_history_basic():
    """Test basic get_history functionality."""
    print("Testing basic get_history...")
    
    # Mock DynamoDB response
    mock_items = [
        {
            'chatId': 'test-id-1',
            'timestamp': 1702564800,
            'userMessage': 'Create a flowchart',
            'diagramType': 'flowchart',
            'status': 'completed'
        },
        {
            'chatId': 'test-id-2',
            'timestamp': 1702564700,
            'userMessage': 'Create an ERD',
            'diagramType': 'erdiagram',
            'status': 'completed'
        }
    ]
    
    mock_dynamodb = Mock()
    mock_dynamodb.scan_all.return_value = {
        'items': mock_items,
        'count': 2,
        'last_evaluated_key': None
    }
    
    event = {
        'httpMethod': 'GET',
        'queryStringParameters': None
    }
    
    response = get_history(event, mock_dynamodb)
    
    assert response['statusCode'] == 200, f"Expected 200, got {response['statusCode']}"
    body = json.loads(response['body'])
    assert 'chats' in body, "Response missing 'chats' field"
    assert 'count' in body, "Response missing 'count' field"
    assert body['count'] == 2, f"Expected count 2, got {body['count']}"
    assert body['nextToken'] is None, "Expected no nextToken"
    
    print("✓ Basic get_history test passed")


def test_pagination():
    """Test pagination functionality."""
    print("Testing pagination...")
    
    mock_items = [
        {'chatId': f'test-id-{i}', 'timestamp': 1702564800 - i, 'status': 'completed'}
        for i in range(5)
    ]
    
    last_key = {'chatId': 'test-id-5', 'timestamp': 1702564795}
    
    mock_dynamodb = Mock()
    mock_dynamodb.scan_all.return_value = {
        'items': mock_items,
        'count': 5,
        'last_evaluated_key': last_key
    }
    
    event = {
        'httpMethod': 'GET',
        'queryStringParameters': {'limit': '5'}
    }
    
    response = get_history(event, mock_dynamodb)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['count'] == 5
    assert body['nextToken'] is not None, "Expected nextToken for pagination"
    
    # Test using the nextToken
    next_token = body['nextToken']
    decoded = decode_next_token(next_token)
    assert decoded == last_key, "Token decode mismatch"
    
    print("✓ Pagination test passed")


def test_invalid_limit():
    """Test invalid limit handling."""
    print("Testing invalid limit...")
    
    mock_dynamodb = Mock()
    
    # Test limit too low
    event = {
        'httpMethod': 'GET',
        'queryStringParameters': {'limit': '0'}
    }
    
    response = get_history(event, mock_dynamodb)
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    
    # Test limit too high
    event['queryStringParameters']['limit'] = '101'
    response = get_history(event, mock_dynamodb)
    assert response['statusCode'] == 400
    
    print("✓ Invalid limit test passed")


def test_encode_decode_token():
    """Test token encoding/decoding."""
    print("Testing token encoding/decoding...")
    
    original = {
        'chatId': 'test-123',
        'timestamp': 1702564800
    }
    
    # Encode
    token = encode_next_token(original)
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode
    decoded = decode_next_token(token)
    assert decoded == original
    
    # Test invalid token
    invalid_result = decode_next_token('invalid!!!')
    assert invalid_result is None
    
    print("✓ Token encoding/decoding test passed")


def test_lambda_handler():
    """Test lambda_handler routing."""
    print("Testing lambda_handler...")
    
    # Mock DynamoDB
    with MagicMock() as mock_helper_class:
        mock_helper = Mock()
        mock_helper.scan_all.return_value = {
            'items': [],
            'count': 0,
            'last_evaluated_key': None
        }
        
        # Patch DynamoDBHelper
        import lambda_function
        original_helper = lambda_function.DynamoDBHelper
        lambda_function.DynamoDBHelper = lambda: mock_helper
        
        try:
            # Test GET
            event = {
                'httpMethod': 'GET',
                'queryStringParameters': None
            }
            response = lambda_handler(event, None)
            assert response['statusCode'] == 200
            
            # Test OPTIONS
            event = {'httpMethod': 'OPTIONS'}
            response = lambda_handler(event, None)
            assert response['statusCode'] == 200
            
            # Test unsupported method
            event = {'httpMethod': 'POST'}
            response = lambda_handler(event, None)
            assert response['statusCode'] == 405
            
            print("✓ Lambda handler test passed")
        finally:
            lambda_function.DynamoDBHelper = original_helper


def test_response_format():
    """Test response format compliance."""
    print("Testing response format...")
    
    mock_dynamodb = Mock()
    mock_dynamodb.scan_all.return_value = {
        'items': [
            {
                'chatId': 'test-id',
                'timestamp': 1702564800,
                'userMessage': 'test',
                'diagramType': 'flowchart',
                'status': 'completed'
            }
        ],
        'count': 1,
        'last_evaluated_key': None
    }
    
    event = {
        'httpMethod': 'GET',
        'queryStringParameters': None
    }
    
    response = get_history(event, mock_dynamodb)
    body = json.loads(response['body'])
    
    # Verify required fields
    assert 'chats' in body
    assert 'count' in body
    assert isinstance(body['chats'], list)
    assert isinstance(body['count'], int)
    
    # Verify CORS headers
    assert 'Access-Control-Allow-Origin' in response['headers']
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
    
    print("✓ Response format test passed")


def main():
    """Run all manual tests."""
    print("\n" + "="*60)
    print("Running manual tests for get_history Lambda function")
    print("="*60 + "\n")
    
    try:
        test_get_history_basic()
        test_pagination()
        test_invalid_limit()
        test_encode_decode_token()
        test_lambda_handler()
        test_response_format()
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60 + "\n")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}\n")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
