"""
Lambda function for session CRUD operations.
Handles creating, reading, updating, and deleting chat sessions.
"""

import json
import os
import sys
from typing import Dict, Any, Optional

# Add shared modules to path
sys.path.append('/opt/python')  # Lambda layer path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from utils import (
    generate_session_id, 
    get_current_timestamp, 
    validate_session_id,
    extract_session_title,
    validate_diagram_type
)
from aws_helpers import DynamoDBHelper


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a standardized API Gateway response.
    
    Args:
        status_code: HTTP status code
        body: Response body dictionary
        
    Returns:
        Dict formatted for API Gateway
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
        },
        'body': json.dumps(body)
    }


def create_session(event: Dict[str, Any], dynamodb_helper: DynamoDBHelper) -> Dict[str, Any]:
    """
    Create a new chat session.
    
    Args:
        event: Lambda event containing the request
        dynamodb_helper: DynamoDB helper instance
        
    Returns:
        API Gateway response dictionary
    """
    try:
        # Parse request body (optional parameters)
        body = json.loads(event.get('body', '{}'))
        
        # Generate session ID and timestamp
        session_id = generate_session_id()
        timestamp = get_current_timestamp()
        
        # Get optional parameters
        title = body.get('title', 'New Chat')
        diagram_type = body.get('diagramType', 'flowchart')
        
        # Validate diagram type if provided
        if not validate_diagram_type(diagram_type):
            return create_response(400, {'error': f'Invalid diagram type: {diagram_type}'})
        
        # Prepare session metadata item for DynamoDB
        item = {
            'PK': f'SESSION#{session_id}',
            'SK': 'METADATA',
            'sessionId': session_id,
            'title': title,
            'diagramType': diagram_type,
            'createdAt': timestamp,
            'updatedAt': timestamp,
            'messageCount': 0
        }
        
        # Save to DynamoDB
        dynamodb_helper.put_item(item)
        
        # Return success response
        return create_response(200, {
            'success': True,
            'sessionId': session_id,
            'title': title,
            'diagramType': diagram_type,
            'createdAt': timestamp,
            'updatedAt': timestamp,
            'messageCount': 0
        })
        
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        print(f"Error creating session: {str(e)}")
        return create_response(500, {'error': 'Failed to create session'})


def get_session(session_id: str, dynamodb_helper: DynamoDBHelper) -> Dict[str, Any]:
    """
    Get a single session by ID.
    
    Args:
        session_id: The session ID to retrieve
        dynamodb_helper: DynamoDB helper instance
        
    Returns:
        API Gateway response dictionary
    """
    try:
        # Validate session ID format
        if not validate_session_id(session_id):
            return create_response(400, {'error': 'Invalid session ID format'})
        
        # Query DynamoDB for session metadata
        pk = f'SESSION#{session_id}'
        sk = 'METADATA'
        
        # Use get_item_by_keys method (we'll need to add this to DynamoDBHelper)
        table = dynamodb_helper.table
        response = table.get_item(
            Key={
                'PK': pk,
                'SK': sk
            }
        )
        
        item = response.get('Item')
        
        if not item:
            return create_response(404, {'error': 'Session not found'})
        
        # Return session data
        return create_response(200, {
            'sessionId': item['sessionId'],
            'title': item['title'],
            'diagramType': item['diagramType'],
            'createdAt': item['createdAt'],
            'updatedAt': item['updatedAt'],
            'messageCount': item.get('messageCount', 0)
        })
        
    except Exception as e:
        print(f"Error getting session: {str(e)}")
        return create_response(500, {'error': 'Failed to retrieve session'})


def list_sessions(event: Dict[str, Any], dynamodb_helper: DynamoDBHelper) -> Dict[str, Any]:
    """
    List all sessions with pagination support.
    
    Args:
        event: Lambda event containing query parameters
        dynamodb_helper: DynamoDB helper instance
        
    Returns:
        API Gateway response dictionary
    """
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        limit = int(query_params.get('limit', 50))
        
        # Scan for all session metadata items
        table = dynamodb_helper.table
        scan_params = {
            'FilterExpression': 'SK = :metadata',
            'ExpressionAttributeValues': {
                ':metadata': 'METADATA'
            },
            'Limit': limit
        }
        
        response = table.scan(**scan_params)
        items = response.get('Items', [])
        
        # Transform items to session format
        sessions = []
        for item in items:
            sessions.append({
                'sessionId': item['sessionId'],
                'title': item['title'],
                'diagramType': item['diagramType'],
                'createdAt': item['createdAt'],
                'updatedAt': item['updatedAt'],
                'messageCount': item.get('messageCount', 0)
            })
        
        # Sort by createdAt descending (most recent first)
        sessions.sort(key=lambda x: x['createdAt'], reverse=True)
        
        # Return sessions list
        return create_response(200, {
            'sessions': sessions,
            'count': len(sessions)
        })
        
    except Exception as e:
        print(f"Error listing sessions: {str(e)}")
        return create_response(500, {'error': 'Failed to list sessions'})


def update_session(session_id: str, event: Dict[str, Any], 
                   dynamodb_helper: DynamoDBHelper) -> Dict[str, Any]:
    """
    Update a session (currently only title updates supported).
    
    Args:
        session_id: The session ID to update
        event: Lambda event containing the request
        dynamodb_helper: DynamoDB helper instance
        
    Returns:
        API Gateway response dictionary
    """
    try:
        # Validate session ID format
        if not validate_session_id(session_id):
            return create_response(400, {'error': 'Invalid session ID format'})
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Get title from request
        title = body.get('title')
        if not title:
            return create_response(400, {'error': 'Missing required field: title'})
        
        # Update session in DynamoDB
        pk = f'SESSION#{session_id}'
        sk = 'METADATA'
        timestamp = get_current_timestamp()
        
        table = dynamodb_helper.table
        response = table.update_item(
            Key={
                'PK': pk,
                'SK': sk
            },
            UpdateExpression='SET title = :title, updatedAt = :updated',
            ExpressionAttributeValues={
                ':title': title,
                ':updated': timestamp
            },
            ReturnValues='ALL_NEW'
        )
        
        updated_item = response.get('Attributes', {})
        
        # Return success response
        return create_response(200, {
            'success': True,
            'sessionId': session_id,
            'title': updated_item.get('title'),
            'updatedAt': updated_item.get('updatedAt')
        })
        
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        print(f"Error updating session: {str(e)}")
        return create_response(500, {'error': 'Failed to update session'})


def delete_session(session_id: str, dynamodb_helper: DynamoDBHelper) -> Dict[str, Any]:
    """
    Delete a session and all its messages.
    
    Args:
        session_id: The session ID to delete
        dynamodb_helper: DynamoDB helper instance
        
    Returns:
        API Gateway response dictionary
    """
    try:
        # Validate session ID format
        if not validate_session_id(session_id):
            return create_response(400, {'error': 'Invalid session ID format'})
        
        # Query all items for this session (metadata + messages)
        pk = f'SESSION#{session_id}'
        table = dynamodb_helper.table
        
        response = table.query(
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': pk
            }
        )
        
        items = response.get('Items', [])
        
        if not items:
            return create_response(404, {'error': 'Session not found'})
        
        # Delete all items (metadata and messages)
        for item in items:
            table.delete_item(
                Key={
                    'PK': item['PK'],
                    'SK': item['SK']
                }
            )
        
        # Return success response
        return create_response(200, {
            'success': True,
            'sessionId': session_id,
            'deletedItems': len(items)
        })
        
    except Exception as e:
        print(f"Error deleting session: {str(e)}")
        return create_response(500, {'error': 'Failed to delete session'})


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for session CRUD operations.
    
    Args:
        event: Lambda event from API Gateway
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    # Handle OPTIONS request for CORS
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {})
    
    # Initialize DynamoDB helper
    dynamodb_helper = DynamoDBHelper()
    
    # Get HTTP method and path parameters
    http_method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters') or {}
    session_id = path_params.get('sessionId')
    
    # Route to appropriate handler
    if http_method == 'POST':
        return create_session(event, dynamodb_helper)
    
    elif http_method == 'GET':
        if session_id:
            # GET /api/session/{sessionId}
            return get_session(session_id, dynamodb_helper)
        else:
            # GET /api/session
            return list_sessions(event, dynamodb_helper)
    
    elif http_method == 'PUT':
        if not session_id:
            return create_response(400, {'error': 'Session ID required for update'})
        return update_session(session_id, event, dynamodb_helper)
    
    elif http_method == 'DELETE':
        if not session_id:
            return create_response(400, {'error': 'Session ID required for delete'})
        return delete_session(session_id, dynamodb_helper)
    
    else:
        return create_response(405, {'error': f'Method {http_method} not allowed'})
