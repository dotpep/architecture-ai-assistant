"""
Test Lambda function for DynamoDB CRUD operations
Requirements: 4.1, 6.3
"""
import json
import os
import time
import boto3
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'architecture-ai-assistant-chat_history-dev')
table = dynamodb.Table(table_name)


def handler(event, context):
    """
    Test handler for DynamoDB CRUD operations
    
    Supports:
    - PUT: Create/update an item
    - GET: Retrieve an item
    """
    try:
        # Parse the request
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        operation = body.get('operation', 'PUT')
        
        if operation == 'PUT':
            # Test PUT operation
            chat_id = body.get('chatId', f'test-{int(time.time())}')
            timestamp = body.get('timestamp', int(time.time()))
            test_data = body.get('data', 'Test message')
            
            # Put item to DynamoDB
            response = table.put_item(
                Item={
                    'chatId': chat_id,
                    'timestamp': timestamp,
                    'userMessage': test_data,
                    'status': 'test'
                }
            )
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': True,
                    'operation': 'PUT',
                    'chatId': chat_id,
                    'timestamp': timestamp,
                    'message': 'Item successfully written to DynamoDB'
                })
            }
            
        elif operation == 'GET':
            # Test GET operation
            chat_id = body.get('chatId')
            timestamp = body.get('timestamp')
            
            if not chat_id or not timestamp:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': False,
                        'error': 'chatId and timestamp are required for GET operation'
                    })
                }
            
            # Get item from DynamoDB
            response = table.get_item(
                Key={
                    'chatId': chat_id,
                    'timestamp': timestamp
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
