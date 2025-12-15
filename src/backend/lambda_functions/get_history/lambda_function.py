"""
Lambda function for retrieving chat history.
Handles querying chat messages from DynamoDB with pagination support.
"""

import json
import os
import sys
import base64
from typing import Dict, Any, Optional
from decimal import Decimal

# Add shared modules to path
sys.path.append('/opt/python')  # Lambda layer path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from aws_helpers import DynamoDBHelper


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal objects from DynamoDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert Decimal to int if it's a whole number, otherwise float
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        return super().default(obj)


def convert_decimals(obj):
    """Recursively convert Decimal objects to int/float."""
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


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
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }


def encode_next_token(last_evaluated_key: Dict[str, Any]) -> str:
    """
    Encode the last evaluated key as a base64 token for pagination.
    
    Args:
        last_evaluated_key: DynamoDB LastEvaluatedKey
        
    Returns:
        str: Base64 encoded token
    """
    # Convert Decimals before JSON encoding
    converted_key = convert_decimals(last_evaluated_key)
    json_str = json.dumps(converted_key)
    return base64.b64encode(json_str.encode()).decode()


def decode_next_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a base64 pagination token back to LastEvaluatedKey.
    
    Args:
        token: Base64 encoded token
        
    Returns:
        Dict: LastEvaluatedKey or None if invalid
    """
    try:
        json_str = base64.b64decode(token.encode()).decode()
        return json.loads(json_str)
    except Exception:
        return None


def get_history(event: Dict[str, Any], dynamodb_helper: DynamoDBHelper) -> Dict[str, Any]:
    """
    Retrieve chat history from DynamoDB with pagination support.
    
    Args:
        event: Lambda event containing the request
        dynamodb_helper: DynamoDB helper instance
        
    Returns:
        API Gateway response dictionary
    """
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        
        # Get limit parameter (default: 50)
        limit = int(query_params.get('limit', 50))
        
        # Validate limit
        if limit < 1 or limit > 100:
            return create_response(400, {'error': 'Limit must be between 1 and 100'})
        
        # Get nextToken parameter for pagination
        next_token = query_params.get('nextToken')
        last_evaluated_key = None
        
        if next_token:
            last_evaluated_key = decode_next_token(next_token)
            if last_evaluated_key is None:
                return create_response(400, {'error': 'Invalid nextToken'})
        
        # Query DynamoDB - scan all items sorted by timestamp descending
        result = dynamodb_helper.scan_all(
            limit=limit,
            last_evaluated_key=last_evaluated_key
        )
        
        # Sort items by timestamp descending (in case scan doesn't maintain order)
        items = sorted(result['items'], key=lambda x: x.get('timestamp', 0), reverse=True)
        
        # Convert Decimals to int/float for JSON serialization
        items = convert_decimals(items)
        
        # Prepare response
        response_body = {
            'chats': items,
            'count': len(items)
        }
        
        # Add nextToken if there are more results
        if result['last_evaluated_key']:
            response_body['nextToken'] = encode_next_token(result['last_evaluated_key'])
        else:
            response_body['nextToken'] = None
        
        return create_response(200, response_body)
        
    except ValueError as e:
        return create_response(400, {'error': f'Invalid parameter: {str(e)}'})
    except Exception as e:
        import traceback
        print(f"Error retrieving history: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return create_response(500, {'error': 'Failed to retrieve chat history'})


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for retrieving chat history.
    
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
    http_method = event.get('httpMethod', 'GET')
    
    if http_method == 'GET':
        return get_history(event, dynamodb_helper)
    else:
        return create_response(405, {'error': f'Method {http_method} not allowed'})
