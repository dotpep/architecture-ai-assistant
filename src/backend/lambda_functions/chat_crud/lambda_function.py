"""
Lambda function for chat CRUD operations.
Handles saving chat messages to DynamoDB.
"""

import json
import os
import sys
from typing import Dict, Any

# Add shared modules to path
sys.path.append('/opt/python')  # Lambda layer path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from utils import generate_chat_id, get_current_timestamp, validate_diagram_type
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
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(body)
    }


def validate_request(body: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate the incoming request body.
    
    Args:
        body: Request body dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # userMessage is required
    if 'userMessage' not in body or not body['userMessage']:
        return False, "Missing required field: userMessage"
    
    # diagramType is required
    if 'diagramType' not in body or not body['diagramType']:
        return False, "Missing required field: diagramType"
    
    # Validate diagram type
    if not validate_diagram_type(body['diagramType']):
        return False, f"Invalid diagram type: {body['diagramType']}"
    
    return True, ""


def save_message(event: Dict[str, Any], dynamodb_helper: DynamoDBHelper) -> Dict[str, Any]:
    """
    Save a chat message to DynamoDB.
    
    Args:
        event: Lambda event containing the request
        dynamodb_helper: DynamoDB helper instance
        
    Returns:
        API Gateway response dictionary
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Validate request
        is_valid, error_message = validate_request(body)
        if not is_valid:
            return create_response(400, {'error': error_message})
        
        # Generate chatId if not provided
        chat_id = body.get('chatId', generate_chat_id())
        
        # Generate timestamp
        timestamp = get_current_timestamp()
        
        # Prepare item for DynamoDB
        item = {
            'chatId': chat_id,
            'timestamp': timestamp,
            'userMessage': body['userMessage'],
            'diagramType': body['diagramType'],
            'status': 'pending'
        }
        
        # Add optional fields if present
        if 'aiResponse' in body:
            item['aiResponse'] = body['aiResponse']
        if 'mermaidCode' in body:
            item['mermaidCode'] = body['mermaidCode']
        if 'imageUrl' in body:
            item['imageUrl'] = body['imageUrl']
        if 'markdownUrl' in body:
            item['markdownUrl'] = body['markdownUrl']
        if 'diagramImageS3Key' in body:
            item['diagramImageS3Key'] = body['diagramImageS3Key']
        if 'diagramMarkdownS3Key' in body:
            item['diagramMarkdownS3Key'] = body['diagramMarkdownS3Key']
        if 'status' in body:
            item['status'] = body['status']
        
        # Save to DynamoDB
        dynamodb_helper.put_item(item)
        
        # Return success response
        return create_response(200, {
            'success': True,
            'chatId': chat_id,
            'timestamp': timestamp
        })
        
    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        print(f"Error saving message: {str(e)}")
        return create_response(500, {'error': 'Failed to save chat message'})


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for chat CRUD operations.
    
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
    
    # Route to appropriate handler
    http_method = event.get('httpMethod', 'POST')
    
    if http_method == 'POST':
        return save_message(event, dynamodb_helper)
    else:
        return create_response(405, {'error': f'Method {http_method} not allowed'})
