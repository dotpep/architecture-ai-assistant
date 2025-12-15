"""
Unit tests for get_history Lambda function.
"""

import json
import sys
import os
import base64
from unittest.mock import Mock, patch, MagicMock

# Mock boto3 before importing modules that use it
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()
sys.modules['botocore.exceptions'] = MagicMock()

# Add src paths - get_history path FIRST so it takes precedence
get_history_path = os.path.join(os.path.dirname(__file__), '../../src/backend/lambda_functions/get_history')
shared_path = os.path.join(os.path.dirname(__file__), '../../src/backend/shared')

# Clear sys.path of any conflicting lambda_function modules
sys.path = [p for p in sys.path if 'lambda_functions' not in p]

sys.path.insert(0, get_history_path)
sys.path.insert(1, shared_path)

# Import with explicit module name to avoid conflicts
import importlib.util
spec = importlib.util.spec_from_file_location("get_history_lambda", os.path.join(get_history_path, "lambda_function.py"))
lambda_function = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lambda_function)

handler = lambda_function.handler
get_history = lambda_function.get_history
get_messages_by_session = lambda_function.get_messages_by_session
encode_next_token = lambda_function.encode_next_token
decode_next_token = lambda_function.decode_next_token


class TestGetHistory:
    """Test suite for get_history Lambda function."""
    
    def test_get_history_success_no_pagination(self):
        """Test successful retrieval of chat history without pagination."""
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
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'chats' in body
        assert 'count' in body
        assert body['count'] == 2
        assert body['nextToken'] is None
        assert len(body['chats']) == 2
        # Verify sorted by timestamp descending
        assert body['chats'][0]['timestamp'] >= body['chats'][1]['timestamp']
    
    def test_get_history_with_limit(self):
        """Test retrieval with custom limit parameter."""
        mock_items = [
            {'chatId': f'test-id-{i}', 'timestamp': 1702564800 - i, 'status': 'completed'}
            for i in range(10)
        ]
        
        mock_dynamodb = Mock()
        mock_dynamodb.scan_all.return_value = {
            'items': mock_items[:5],
            'count': 5,
            'last_evaluated_key': {'chatId': 'test-id-5', 'timestamp': 1702564795}
        }
        
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {'limit': '5'}
        }
        
        response = get_history(event, mock_dynamodb)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 5
        assert body['nextToken'] is not None
        mock_dynamodb.scan_all.assert_called_once_with(limit=5, last_evaluated_key=None)
    
    def test_get_history_with_pagination_token(self):
        """Test retrieval with pagination token."""
        last_key = {'chatId': 'test-id-5', 'timestamp': 1702564795}
        next_token = encode_next_token(last_key)
        
        mock_items = [
            {'chatId': f'test-id-{i}', 'timestamp': 1702564790 - i, 'status': 'completed'}
            for i in range(5)
        ]
        
        mock_dynamodb = Mock()
        mock_dynamodb.scan_all.return_value = {
            'items': mock_items,
            'count': 5,
            'last_evaluated_key': None
        }
        
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {
                'limit': '5',
                'nextToken': next_token
            }
        }
        
        response = get_history(event, mock_dynamodb)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 5
        assert body['nextToken'] is None
        mock_dynamodb.scan_all.assert_called_once_with(limit=5, last_evaluated_key=last_key)
    
    def test_get_history_invalid_limit_too_low(self):
        """Test error handling for limit below minimum."""
        mock_dynamodb = Mock()
        
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {'limit': '0'}
        }
        
        response = get_history(event, mock_dynamodb)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'between 1 and 100' in body['error']
    
    def test_get_history_invalid_limit_too_high(self):
        """Test error handling for limit above maximum."""
        mock_dynamodb = Mock()
        
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {'limit': '101'}
        }
        
        response = get_history(event, mock_dynamodb)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'between 1 and 100' in body['error']
    
    def test_get_history_invalid_next_token(self):
        """Test error handling for invalid pagination token."""
        mock_dynamodb = Mock()
        
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': {'nextToken': 'invalid-token'}
        }
        
        response = get_history(event, mock_dynamodb)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Invalid nextToken' in body['error']
    
    def test_get_history_dynamodb_error(self):
        """Test error handling for DynamoDB failures."""
        mock_dynamodb = Mock()
        mock_dynamodb.scan_all.side_effect = Exception("DynamoDB error")
        
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': None
        }
        
        response = get_history(event, mock_dynamodb)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Failed to retrieve chat history' in body['error']
    
    def test_get_history_default_limit(self):
        """Test that default limit is 50 when not specified."""
        mock_dynamodb = Mock()
        mock_dynamodb.scan_all.return_value = {
            'items': [],
            'count': 0,
            'last_evaluated_key': None
        }
        
        event = {
            'httpMethod': 'GET',
            'queryStringParameters': None
        }
        
        response = get_history(event, mock_dynamodb)
        
        assert response['statusCode'] == 200
        mock_dynamodb.scan_all.assert_called_once_with(limit=50, last_evaluated_key=None)
    
    def test_encode_decode_next_token(self):
        """Test encoding and decoding of pagination tokens."""
        original_key = {
            'chatId': 'test-id-123',
            'timestamp': 1702564800
        }
        
        # Encode
        token = encode_next_token(original_key)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode
        decoded_key = decode_next_token(token)
        assert decoded_key == original_key
    
    def test_decode_invalid_token(self):
        """Test decoding of invalid token returns None."""
        result = decode_next_token('not-a-valid-base64-token!!!')
        assert result is None
    
    def test_handler_get_method(self):
        """Test handler routes GET requests correctly."""
        with patch.object(lambda_function, 'DynamoDBHelper') as mock_helper_class:
            mock_helper = Mock()
            mock_helper_class.return_value = mock_helper
            mock_helper.scan_all.return_value = {
                'items': [],
                'count': 0,
                'last_evaluated_key': None
            }
            
            event = {
                'httpMethod': 'GET',
                'queryStringParameters': None
            }
            
            response = handler(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'chats' in body
            assert 'count' in body
    
    def test_handler_options_method(self):
        """Test handler handles OPTIONS for CORS."""
        event = {
            'httpMethod': 'OPTIONS'
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
    
    def test_handler_unsupported_method(self):
        """Test handler rejects unsupported HTTP methods."""
        with patch('lambda_function.DynamoDBHelper'):
            event = {
                'httpMethod': 'POST'
            }
            
            response = handler(event, None)
            
            assert response['statusCode'] == 405
            body = json.loads(response['body'])
            assert 'error' in body
            assert 'not allowed' in body['error']
    
    def test_response_format_compliance(self):
        """Test that response format matches API specification."""
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


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
