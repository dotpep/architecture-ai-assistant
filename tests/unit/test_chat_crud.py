"""
Unit tests for chat_crud Lambda function.
"""

import json
import sys
import os
import uuid
from unittest.mock import Mock, patch, MagicMock

# Mock boto3 before importing modules that use it
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()
sys.modules['botocore.exceptions'] = MagicMock()

# Add backend modules to path - chat_crud path FIRST so it takes precedence
chat_crud_path = os.path.join(os.path.dirname(__file__), '../../src/backend/lambda_functions/chat_crud')
shared_path = os.path.join(os.path.dirname(__file__), '../../src/backend/shared')

# Clear sys.path of any conflicting lambda_function modules
sys.path = [p for p in sys.path if 'lambda_functions' not in p]

sys.path.insert(0, chat_crud_path)
sys.path.insert(1, shared_path)

# Import with explicit module name to avoid conflicts
import importlib.util
spec = importlib.util.spec_from_file_location("chat_crud_lambda", os.path.join(chat_crud_path, "lambda_function.py"))
lambda_function = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lambda_function)


class TestChatCrudLambda:
    """Test cases for chat_crud Lambda function."""
    
    def test_validate_request_success(self):
        """Test request validation with valid data."""
        body = {
            'sessionId': str(uuid.uuid4()),
            'userMessage': 'Create a flowchart',
            'diagramType': 'flowchart'
        }
        
        is_valid, error = lambda_function.validate_request(body)
        assert is_valid is True
        assert error == ""
    
    def test_validate_request_missing_user_message(self):
        """Test request validation with missing userMessage."""
        body = {
            'sessionId': str(uuid.uuid4()),
            'diagramType': 'flowchart'
        }
        
        is_valid, error = lambda_function.validate_request(body)
        assert is_valid is False
        assert 'userMessage' in error
    
    def test_validate_request_missing_diagram_type(self):
        """Test request validation with missing diagramType."""
        body = {
            'sessionId': str(uuid.uuid4()),
            'userMessage': 'Create a flowchart'
        }
        
        is_valid, error = lambda_function.validate_request(body)
        assert is_valid is False
        assert 'diagramType' in error
    
    def test_validate_request_invalid_diagram_type(self):
        """Test request validation with invalid diagram type."""
        body = {
            'sessionId': str(uuid.uuid4()),
            'userMessage': 'Create a diagram',
            'diagramType': 'invalid_type'
        }
        
        is_valid, error = lambda_function.validate_request(body)
        assert is_valid is False
        assert 'Invalid diagram type' in error
    
    def test_save_message_generates_message_id(self):
        """Test that save_message generates messageId when not provided."""
        # Setup mock DynamoDB helper
        mock_db_instance = MagicMock()
        
        # Use a valid UUID for sessionId
        test_session_id = str(uuid.uuid4())
        
        # Create event
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'sessionId': test_session_id,
                'userMessage': 'Create a flowchart',
                'diagramType': 'flowchart'
            })
        }
        
        # Call function
        response = lambda_function.save_message(event, mock_db_instance)
        
        # Verify response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'messageId' in body
        assert 'sessionId' in body
        assert body['sessionId'] == test_session_id
        assert 'timestamp' in body
        
        # Verify DynamoDB was called
        mock_db_instance.put_item.assert_called_once()
        call_args = mock_db_instance.put_item.call_args[0][0]
        assert call_args['PK'] == f'SESSION#{test_session_id}'
        assert call_args['SK'].startswith('MSG#')
        assert call_args['userMessage'] == 'Create a flowchart'
        assert call_args['diagramType'] == 'flowchart'
        assert call_args['status'] == 'pending'
    
    def test_save_message_uses_provided_message_id(self):
        """Test that save_message uses provided messageId."""
        # Setup mock DynamoDB helper
        mock_db_instance = MagicMock()
        
        # Use valid UUIDs
        test_session_id = str(uuid.uuid4())
        test_message_id = str(uuid.uuid4())
        
        # Create event with messageId
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'sessionId': test_session_id,
                'messageId': test_message_id,
                'userMessage': 'Create a sequence diagram',
                'diagramType': 'sequence'
            })
        }
        
        # Call function
        response = lambda_function.save_message(event, mock_db_instance)
        
        # Verify response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['messageId'] == test_message_id
        assert body['sessionId'] == test_session_id
        
        # Verify DynamoDB was called with correct messageId and sessionId
        call_args = mock_db_instance.put_item.call_args[0][0]
        assert call_args['messageId'] == test_message_id
        assert call_args['sessionId'] == test_session_id
        assert call_args['PK'] == f'SESSION#{test_session_id}'
    
    def test_save_message_includes_optional_fields(self):
        """Test that save_message includes optional fields when provided."""
        # Setup mock DynamoDB helper
        mock_db_instance = MagicMock()
        
        # Use a valid UUID for sessionId
        test_session_id = str(uuid.uuid4())
        
        # Create event with optional fields
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'sessionId': test_session_id,
                'userMessage': 'Create an ERD',
                'diagramType': 'erdiagram',
                'aiResponse': 'Here is your diagram',
                'mermaidCode': 'erDiagram\n  USER ||--o{ ORDER : places',
                'imageUrl': 'https://example.com/image.png',
                'markdownUrl': 'https://example.com/diagram.md',
                'status': 'completed'
            })
        }
        
        # Call function
        response = lambda_function.save_message(event, mock_db_instance)
        
        # Verify response
        assert response['statusCode'] == 200
        
        # Verify all fields were saved
        call_args = mock_db_instance.put_item.call_args[0][0]
        assert call_args['sessionId'] == test_session_id
        assert call_args['PK'] == f'SESSION#{test_session_id}'
        assert call_args['aiResponse'] == 'Here is your diagram'
        assert call_args['mermaidCode'] == 'erDiagram\n  USER ||--o{ ORDER : places'
        assert call_args['imageUrl'] == 'https://example.com/image.png'
        assert call_args['markdownUrl'] == 'https://example.com/diagram.md'
        assert call_args['status'] == 'completed'
    
    @patch('lambda_function.DynamoDBHelper')
    def test_save_message_invalid_json(self, mock_db):
        """Test save_message with invalid JSON."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        event = {
            'httpMethod': 'POST',
            'body': 'invalid json{'
        }
        
        response = lambda_function.save_message(event, mock_db_instance)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Invalid JSON' in body['error']
    
    @patch('lambda_function.DynamoDBHelper')
    def test_handler_options_request(self, mock_db):
        """Test handler handles OPTIONS request for CORS."""
        event = {
            'httpMethod': 'OPTIONS'
        }
        
        response = lambda_function.handler(event, None)
        
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
    
    def test_handler_post_request(self):
        """Test handler handles POST request."""
        # Setup mocks
        mock_db_instance = MagicMock()
        
        # Use a valid UUID for sessionId
        test_session_id = str(uuid.uuid4())
        
        # Patch DynamoDBHelper in the lambda_function module
        with patch.object(lambda_function, 'DynamoDBHelper', return_value=mock_db_instance):
            event = {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'sessionId': test_session_id,
                    'userMessage': 'Create a class diagram',
                    'diagramType': 'class'
                })
            }
            
            response = lambda_function.handler(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['success'] is True
            assert 'messageId' in body
            assert 'sessionId' in body


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
