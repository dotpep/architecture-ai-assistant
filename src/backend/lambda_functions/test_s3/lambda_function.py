"""
Test Lambda function for S3 upload operations
Requirements: 3.1, 6.3
"""
import json
import os
import time
import boto3
from botocore.exceptions import ClientError

# Initialize S3 client
s3_client = boto3.client('s3')
bucket_name = os.environ.get('S3_BUCKET_NAME', 'architecture-ai-assistant-bucket-dev')


def handler(event, context):
    """
    Test handler for S3 upload operations
    
    Supports:
    - PUT: Upload a test file to S3
    - GET: Retrieve a test file from S3
    """
    try:
        # Parse the request
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        operation = body.get('operation', 'PUT')
        
        if operation == 'PUT':
            # Test PUT operation
            file_key = body.get('fileKey', f'test/test-{int(time.time())}.txt')
            content = body.get('content', 'Test content from Lambda')
            
            # Upload to S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            # Generate the S3 URL
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': True,
                    'operation': 'PUT',
                    'bucket': bucket_name,
                    'key': file_key,
                    's3Url': s3_url,
                    'message': 'File successfully uploaded to S3'
                })
            }
            
        elif operation == 'GET':
            # Test GET operation
            file_key = body.get('fileKey')
            
            if not file_key:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': False,
                        'error': 'fileKey is required for GET operation'
                    })
                }
            
            try:
                # Get object from S3
                response = s3_client.get_object(
                    Bucket=bucket_name,
                    Key=file_key
                )
                
                # Read the content
                content = response['Body'].read().decode('utf-8')
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': True,
                        'operation': 'GET',
                        'bucket': bucket_name,
                        'key': file_key,
                        'content': content,
                        'contentLength': response['ContentLength'],
                        'contentType': response['ContentType'],
                        'message': 'File successfully retrieved from S3'
                    })
                }
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchKey':
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({
                            'success': False,
                            'error': 'File not found in S3'
                        })
                    }
                else:
                    raise
        
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
