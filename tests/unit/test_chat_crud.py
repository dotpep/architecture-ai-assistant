"""
Unit tests for chat_crud Lambda function.
"""

import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add backend modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/backend/lambda_functions/chat_crud'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/backend/shared'))

import lambda_function


class TestChatCrudLambda:
    """Test cases for chat_crud Lambda function."""
    
    def test_validate_request_success(self):
        """Test request validation with valid data."""
        body = {
            'userMessage': 'Create a flowchart',
            'diagramType': 'flowchart'
        }
        
        is_valid, error = lambda_function.validate_request(body)
        assert is_valid is True
        assert error == ""
    
    def test_validate_request_missing_user_message(self):
        """Test request validation with missing userMessage."""
        body = {
            'diagramType': 'flowchart'
        }
        
        is_valid, error = lambda_function.validate_request(body)
        assert is_valid is False
        assert 'userMessage' in error
    
    def test_validate_request_missing_diagram_type(self):
        """Test request validation with missing diagramType."""
        body = {
            'userMessage': 'Create a flowchart'
        }
        
        is_valid, error = lambda_function.validate_request(body)
        assert is_valid is False
        assert 'diagramType' in error
    
    def test_validate_request_invalid_diagram_type(self):
        """Test request validation with invalid diagram type."""
        body = {
            'userMessage': 'Create a diagram',
            'diagramType': 'invalid_type'
        }
        
        is_valid, error = lambda_function.validate_request(body)
        assert is_valid is False
        assert 'Invalid diagram type' in error
    
    @patch('lambda_function.DynamoDBHelper')
    @patch('lambda_function.get_current_timestamp')
    @patch('lambda_function.generate_chat_id')
    def test_save_message_generates_chat_id(self, mock_gen_id, mock_timestamp, mock_db):
        """Test that save_message generates chatId when not provided."""
        # Setup mocks
        mock_gen_id.return_value = 'test-uuid-123'
        mock_timestamp.return_value = 1702564800
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Create event
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
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
        assert body['chatId'] == 'test-uuid-123'
        assert body['timestamp'] == 1702564800
        
        # Verify DynamoDB was called
        mock_db_instance.put_item.assert_called_once()
        call_args = mock_db_instance.put_item.call_args[0][0]
        assert call_args['chatId'] == 'test-uuid-123'
        assert call_args['timestamp'] == 1702564800
        assert call_args['userMessage'] == 'Create a flowchart'
        assert call_args['diagramType'] == 'flowchart'
        assert call_args['status'] == 'pending'
    
    @patch('lambda_function.DynamoDBHelper')
    @patch('lambda_function.get_current_timestamp')
    def test_save_message_uses_provided_chat_id(self, mock_timestamp, mock_db):
        """Test that save_message uses provided chatId."""
        # Setup mocks
        mock_timestamp.return_value = 1702564800
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Create event with chatId
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'chatId': 'existing-chat-id',
                'userMessage': 'Create a sequence diagram',
                'diagramType': 'sequence'
            })
        }
        
        # Call function
        response = lambda_function.save_message(event, mock_db_instance)
        
        # Verify response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['chatId'] == 'existing-chat-id'
        
        # Verify DynamoDB was called with correct chatId
        call_args = mock_db_instance.put_item.call_args[0][0]
        assert call_args['chatId'] == 'existing-chat-id'
    
    @patch('lambda_function.DynamoDBHelper')
    @patch('lambda_function.get_current_timestamp')
    @patch('lambda_function.generate_chat_id')
    def test_save_message_includes_optional_fields(self, mock_gen_id, mock_timestamp, mock_db):
        """Test that save_message includes optional fields when provided."""
        # Setup mocks
        mock_gen_id.return_value = 'test-uuid-456'
        mock_timestamp.return_value = 1702564900
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Create event with optional fields
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
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
    def test_lambda_handler_options_request(self, mock_db):
        """Test lambda_handler handles OPTIONS request for CORS."""
        event = {
            'httpMethod': 'OPTIONS'
        }
        
        response = lambda_function.lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
    
    @patch('lambda_function.DynamoDBHelper')
    @patch('lambda_function.get_current_timestamp')
    @patch('lambda_function.generate_chat_id')
    def test_lambda_handler_post_request(self, mock_gen_id, mock_timestamp, mock_db):
        """Test lambda_handler handles POST request."""
        # Setup mocks
        mock_gen_id.return_value = 'test-uuid-789'
        mock_timestamp.return_value = 1702565000
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'userMessage': 'Create a class diagram',
                'diagramType': 'class'
            })
        }
        
        response = lambda_function.lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['chatId'] == 'test-uuid-789'


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
