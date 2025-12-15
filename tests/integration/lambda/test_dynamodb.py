"""
Integration tests for DynamoDB operations
Tests Lambda → DynamoDB connectivity
Updated for session-based data model with PK/SK pattern
"""
import json
import os
import time
import boto3
import uuid
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'architecture-ai-assistant-chat_history-dev')
table = dynamodb.Table(table_name)


def handler(event, context):
    """
    Test handler for DynamoDB CRUD operations
    
    Supports:
    - PUT: Create/update an item (session or message)
    - GET: Retrieve an item
    """
    try:
        # Parse the request
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        operation = body.get('operation', 'PUT')
        
        if operation == 'PUT':
            # Test PUT operation with PK/SK pattern
            session_id = body.get('sessionId', str(uuid.uuid4()))
            timestamp = body.get('timestamp', int(time.time()))
            test_data = body.get('data', 'Test message')
            item_type = body.get('itemType', 'message')  # 'session' or 'message'
            
            # Build item based on type
            if item_type == 'session':
                item = {
                    'PK': f'SESSION#{session_id}',
                    'SK': 'METADATA',
                    'sessionId': session_id,
                    'title': test_data,
                    'diagramType': 'flowchart',
                    'createdAt': timestamp,
                    'updatedAt': timestamp,
                    'messageCount': 0
                }
            else:  # message
                message_id = body.get('messageId', str(uuid.uuid4()))
                item = {
                    'PK': f'SESSION#{session_id}',
                    'SK': f'MSG#{timestamp}',
                    'messageId': message_id,
                    'sessionId': session_id,
                    'timestamp': timestamp,
                    'userMessage': test_data,
                    'diagramType': 'flowchart',
                    'status': 'test'
                }
            
            # Put item to DynamoDB
            response = table.put_item(Item=item)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': True,
                    'operation': 'PUT',
                    'sessionId': session_id,
                    'timestamp': timestamp,
                    'itemType': item_type,
                    'message': 'Item successfully written to DynamoDB'
                })
            }
            
        elif operation == 'GET':
            # Test GET operation with PK/SK pattern
            pk = body.get('PK')
            sk = body.get('SK')
            
            if not pk or not sk:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': False,
                        'error': 'PK and SK are required for GET operation'
                    })
                }
            
            # Get item from DynamoDB
            response = table.get_item(
                Key={
                    'PK': pk,
                    'SK': sk
                }
            )
            
            item = response.get('Item')
            
            if item:
                # Convert Decimal to int/float for JSON serialization
                item = json.loads(json.dumps(item, default=str))
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': True,
                        'operation': 'GET',
                        'item': item,
                        'message': 'Item successfully retrieved from DynamoDB'
                    })
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': False,
                        'error': 'Item not found'
                    })
                }
        
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': False,
                    'error': f'Unsupported operation: {operation}'
                })
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
