"""
Unit tests for session_crud Lambda function.
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

# Add backend modules to path - session_crud path FIRST so it takes precedence
session_crud_path = os.path.join(os.path.dirname(__file__), '../../src/backend/lambda_functions/session_crud')
shared_path = os.path.join(os.path.dirname(__file__), '../../src/backend/shared')

# Clear sys.path of any conflicting lambda_function modules
sys.path = [p for p in sys.path if 'lambda_functions' not in p]

sys.path.insert(0, session_crud_path)
sys.path.insert(1, shared_path)

# Import with explicit module name to avoid conflicts
import importlib.util
spec = importlib.util.spec_from_file_location("session_crud_lambda", os.path.join(session_crud_path, "lambda_function.py"))
lambda_function = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lambda_function)


class TestCreateSession:
    """Test cases for create_session function."""
    
    def test_create_session_with_defaults(self):
        """Test creating a session with default values."""
        mock_db_instance = MagicMock()
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({})
        }
        
        response = lambda_function.create_session(event, mock_db_instance)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'sessionId' in body
        assert body['title'] == 'New Chat'
        assert body['diagramType'] == 'flowchart'
        assert body['messageCount'] == 0
        assert 'createdAt' in body
        assert 'updatedAt' in body
        
        # Verify DynamoDB was called
        mock_db_instance.put_item.assert_called_once()
        call_args = mock_db_instance.put_item.call_args[0][0]
        assert call_args['SK'] == 'METADATA'
        assert call_args['PK'].startswith('SESSION#')
        assert call_args['messageCount'] == 0
    
    def test_create_session_with_custom_title(self):
        """Test creating a session with custom title."""
        mock_db_instance = MagicMock()
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'title': 'My Custom Session',
                'diagramType': 'sequence'
            })
        }
        
        response = lambda_function.create_session(event, mock_db_instance)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['title'] == 'My Custom Session'
        assert body['diagramType'] == 'sequence'
        
        call_args = mock_db_instance.put_item.call_args[0][0]
        assert call_args['title'] == 'My Custom Session'
        assert call_args['diagramType'] == 'sequence'
    
    def test_create_session_invalid_diagram_type(self):
        """Test creating a session with invalid diagram type."""
        mock_db_instance = MagicMock()
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'diagramType': 'invalid_type'
            })
        }
        
        response = lambda_function.create_session(event, mock_db_instance)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Invalid diagram type' in body['error']
    
    def test_create_session_invalid_json(self):
        """Test creating a session with invalid JSON."""
        mock_db_instance = MagicMock()
        
        event = {
            'httpMethod': 'POST',
            'body': 'invalid json{'
        }
        
        response = lambda_function.create_session(event, mock_db_instance)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Invalid JSON' in body['error']


class TestGetSession:
    """Test cases for get_session function."""
    
    def test_get_session_success(self):
        """Test successfully retrieving a session."""
        mock_db_instance = MagicMock()
        test_session_id = str(uuid.uuid4())
        
        # Mock DynamoDB response
        mock_db_instance.table.get_item.return_value = {
            'Item': {
                'PK': f'SESSION#{test_session_id}',
                'SK': 'METADATA',
                'sessionId': test_session_id,
                'title': 'Test Session',
                'diagramType': 'flowchart',
                'createdAt': 1702564800,
                'updatedAt': 1702564800,
                'messageCount': 5
            }
        }
        
        response = lambda_function.get_session(test_session_id, mock_db_instance)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['sessionId'] == test_session_id
        assert body['title'] == 'Test Session'
        assert body['diagramType'] == 'flowchart'
        assert body['messageCount'] == 5
    
    def test_get_session_not_found(self):
        """Test retrieving a non-existent session."""
        mock_db_instance = MagicMock()
        test_session_id = str(uuid.uuid4())
        
        # Mock DynamoDB response with no item
        mock_db_instance.table.get_item.return_value = {}
        
        response = lambda_function.get_session(test_session_id, mock_db_instance)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'Session not found' in body['error']
    
    def test_get_session_invalid_id_format(self):
        """Test retrieving a session with invalid ID format."""
        mock_db_instance = MagicMock()
        
        response = lambda_function.get_session('invalid-id', mock_db_instance)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Invalid session ID format' in body['error']


class TestListSessions:
    """Test cases for list_sessions function."""
    
    def test_list_sessions_success(self):
        """Test successfully listing sessions."""
        mock_db_instance = MagicMock()
        
        # Mock DynamoDB scan response
        mock_db_instance.table.scan.return_value = {
            'Items': [
                {
                    'PK': 'SESSION#id1',
                    'SK': 'METADATA',
                    'sessionId': 'id1',
                    'title': 'Session 1',
                    'diagramType': 'flowchart',
                    'createdAt': 1702564800,
                    'updatedAt': 1702564800,
                    'messageCount': 3
                },
                {
                    'PK': 'SESSION#id2',
                    'SK': 'METADATA',
                    'sessionId': 'id2',
                    'title': 'Session 2',
                    'diagramType': 'sequence',
                    'createdAt': 1702564900,
                    'updatedAt': 1702564900,
                    'messageCount': 1
                }
            ]
        }
        
        event = {
            'queryStringParameters': None
        }
        
        response = lambda_function.list_sessions(event, mock_db_instance)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'sessions' in body
        assert body['count'] == 2
        assert len(body['sessions']) == 2
        # Verify sorted by createdAt descending
        assert body['sessions'][0]['createdAt'] >= body['sessions'][1]['createdAt']
    
    def test_list_sessions_empty(self):
        """Test listing sessions when none exist."""
        mock_db_instance = MagicMock()
        
        mock_db_instance.table.scan.return_value = {
            'Items': []
        }
        
        event = {
            'queryStringParameters': None
        }
        
        response = lambda_function.list_sessions(event, mock_db_instance)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['count'] == 0
        assert body['sessions'] == []
    
    def test_list_sessions_with_limit(self):
        """Test listing sessions with custom limit."""
        mock_db_instance = MagicMock()
        
        mock_db_instance.table.scan.return_value = {
            'Items': []
        }
        
        event = {
            'queryStringParameters': {'limit': '10'}
        }
        
        response = lambda_function.list_sessions(event, mock_db_instance)
        
        assert response['statusCode'] == 200
        # Verify scan was called with correct limit
        call_kwargs = mock_db_instance.table.scan.call_args[1]
        assert call_kwargs['Limit'] == 10


class TestUpdateSession:
    """Test cases for update_session function."""
    
    def test_update_session_title_success(self):
        """Test successfully updating a session title."""
        mock_db_instance = MagicMock()
        test_session_id = str(uuid.uuid4())
        
        # Mock DynamoDB update response
        mock_db_instance.table.update_item.return_value = {
            'Attributes': {
                'PK': f'SESSION#{test_session_id}',
                'SK': 'METADATA',
                'sessionId': test_session_id,
                'title': 'Updated Title',
                'updatedAt': 1702565000
            }
        }
        
        event = {
            'body': json.dumps({
                'title': 'Updated Title'
            })
        }
        
        response = lambda_function.update_session(test_session_id, event, mock_db_instance)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['sessionId'] == test_session_id
        assert body['title'] == 'Updated Title'
        assert 'updatedAt' in body
    
    def test_update_session_missing_title(self):
        """Test updating a session without providing title."""
        mock_db_instance = MagicMock()
        test_session_id = str(uuid.uuid4())
        
        event = {
            'body': json.dumps({})
        }
        
        response = lambda_function.update_session(test_session_id, event, mock_db_instance)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Missing required field: title' in body['error']
    
    def test_update_session_invalid_id_format(self):
        """Test updating a session with invalid ID format."""
        mock_db_instance = MagicMock()
        
        event = {
            'body': json.dumps({'title': 'New Title'})
        }
        
        response = lambda_function.update_session('invalid-id', event, mock_db_instance)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Invalid session ID format' in body['error']
    
    def test_update_session_invalid_json(self):
        """Test updating a session with invalid JSON."""
        mock_db_instance = MagicMock()
        test_session_id = str(uuid.uuid4())
        
        event = {
            'body': 'invalid json{'
        }
        
        response = lambda_function.update_session(test_session_id, event, mock_db_instance)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Invalid JSON' in body['error']


class TestDeleteSession:
    """Test cases for delete_session function."""
    
    def test_delete_session_success(self):
        """Test successfully deleting a session."""
        mock_db_instance = MagicMock()
        test_session_id = str(uuid.uuid4())
        
        # Mock DynamoDB query response with session and messages
        mock_db_instance.table.query.return_value = {
            'Items': [
                {
                    'PK': f'SESSION#{test_session_id}',
                    'SK': 'METADATA'
                },
                {
                    'PK': f'SESSION#{test_session_id}',
                    'SK': 'MSG#1702564800'
                },
                {
                    'PK': f'SESSION#{test_session_id}',
                    'SK': 'MSG#1702564900'
                }
            ]
        }
        
        response = lambda_function.delete_session(test_session_id, mock_db_instance)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['sessionId'] == test_session_id
        assert body['deletedItems'] == 3
        
        # Verify delete_item was called 3 times
        assert mock_db_instance.table.delete_item.call_count == 3
    
    def test_delete_session_not_found(self):
        """Test deleting a non-existent session."""
        mock_db_instance = MagicMock()
        test_session_id = str(uuid.uuid4())
        
        # Mock DynamoDB query response with no items
        mock_db_instance.table.query.return_value = {
            'Items': []
        }
        
        response = lambda_function.delete_session(test_session_id, mock_db_instance)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'Session not found' in body['error']
    
    def test_delete_session_invalid_id_format(self):
        """Test deleting a session with invalid ID format."""
        mock_db_instance = MagicMock()
        
        response = lambda_function.delete_session('invalid-id', mock_db_instance)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Invalid session ID format' in body['error']


class TestHandler:
    """Test cases for main handler function."""
    
    def test_handler_options_request(self):
        """Test handler handles OPTIONS request for CORS."""
        event = {
            'httpMethod': 'OPTIONS'
        }
        
        response = lambda_function.handler(event, None)
        
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
    
    def test_handler_post_create_session(self):
        """Test handler routes POST to create_session."""
        with patch.object(lambda_function, 'DynamoDBHelper') as mock_helper_class:
            mock_helper = MagicMock()
            mock_helper_class.return_value = mock_helper
            
            event = {
                'httpMethod': 'POST',
                'body': json.dumps({'title': 'Test Session'}),
                'pathParameters': None
            }
            
            response = lambda_function.handler(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['success'] is True
            assert 'sessionId' in body
    
    def test_handler_get_single_session(self):
        """Test handler routes GET with sessionId to get_session."""
        with patch.object(lambda_function, 'DynamoDBHelper') as mock_helper_class:
            mock_helper = MagicMock()
            mock_helper_class.return_value = mock_helper
            test_session_id = str(uuid.uuid4())
            
            mock_helper.table.get_item.return_value = {
                'Item': {
                    'sessionId': test_session_id,
                    'title': 'Test',
                    'diagramType': 'flowchart',
                    'createdAt': 1702564800,
                    'updatedAt': 1702564800,
                    'messageCount': 0
                }
            }
            
            event = {
                'httpMethod': 'GET',
                'pathParameters': {'sessionId': test_session_id}
            }
            
            response = lambda_function.handler(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['sessionId'] == test_session_id
    
    def test_handler_get_list_sessions(self):
        """Test handler routes GET without sessionId to list_sessions."""
        with patch.object(lambda_function, 'DynamoDBHelper') as mock_helper_class:
            mock_helper = MagicMock()
            mock_helper_class.return_value = mock_helper
            
            mock_helper.table.scan.return_value = {
                'Items': []
            }
            
            event = {
                'httpMethod': 'GET',
                'pathParameters': None,
                'queryStringParameters': None
            }
            
            response = lambda_function.handler(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'sessions' in body
            assert 'count' in body
    
    def test_handler_put_update_session(self):
        """Test handler routes PUT to update_session."""
        with patch.object(lambda_function, 'DynamoDBHelper') as mock_helper_class:
            mock_helper = MagicMock()
            mock_helper_class.return_value = mock_helper
            test_session_id = str(uuid.uuid4())
            
            mock_helper.table.update_item.return_value = {
                'Attributes': {
                    'sessionId': test_session_id,
                    'title': 'Updated',
                    'updatedAt': 1702565000
                }
            }
            
            event = {
                'httpMethod': 'PUT',
                'pathParameters': {'sessionId': test_session_id},
                'body': json.dumps({'title': 'Updated'})
            }
            
            response = lambda_function.handler(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['success'] is True
    
    def test_handler_put_without_session_id(self):
        """Test handler rejects PUT without sessionId."""
        with patch.object(lambda_function, 'DynamoDBHelper'):
            event = {
                'httpMethod': 'PUT',
                'pathParameters': None,
                'body': json.dumps({'title': 'Updated'})
            }
            
            response = lambda_function.handler(event, None)
            
            assert response['statusCode'] == 400
            body = json.loads(response['body'])
            assert 'Session ID required' in body['error']
    
    def test_handler_delete_session(self):
        """Test handler routes DELETE to delete_session."""
        with patch.object(lambda_function, 'DynamoDBHelper') as mock_helper_class:
            mock_helper = MagicMock()
            mock_helper_class.return_value = mock_helper
            test_session_id = str(uuid.uuid4())
            
            mock_helper.table.query.return_value = {
                'Items': [
                    {'PK': f'SESSION#{test_session_id}', 'SK': 'METADATA'}
                ]
            }
            
            event = {
                'httpMethod': 'DELETE',
                'pathParameters': {'sessionId': test_session_id}
            }
            
            response = lambda_function.handler(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['success'] is True
    
    def test_handler_delete_without_session_id(self):
        """Test handler rejects DELETE without sessionId."""
        with patch.object(lambda_function, 'DynamoDBHelper'):
            event = {
                'httpMethod': 'DELETE',
                'pathParameters': None
            }
            
            response = lambda_function.handler(event, None)
            
            assert response['statusCode'] == 400
            body = json.loads(response['body'])
            assert 'Session ID required' in body['error']
    
    def test_handler_unsupported_method(self):
        """Test handler rejects unsupported HTTP methods."""
        with patch.object(lambda_function, 'DynamoDBHelper'):
            event = {
                'httpMethod': 'PATCH',
                'pathParameters': None
            }
            
            response = lambda_function.handler(event, None)
            
            assert response['statusCode'] == 405
            body = json.loads(response['body'])
            assert 'not allowed' in body['error']


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
