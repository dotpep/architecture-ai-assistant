"""
AWS service helper functions for DynamoDB and S3 operations.
"""

import boto3
import json
import os
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError


# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')


class DynamoDBHelper:
    """Helper class for DynamoDB operations."""
    
    def __init__(self, table_name: Optional[str] = None):
        """
        Initialize DynamoDB helper.
        
        Args:
            table_name: Name of the DynamoDB table. If None, reads from environment.
        """
        self.table_name = table_name or os.environ.get('DYNAMODB_TABLE_NAME', 'chat_history')
        self.table = dynamodb.Table(self.table_name)
    
    def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Put an item into DynamoDB table.
        
        Args:
            item: Dictionary containing the item data
            
        Returns:
            Dict containing the response from DynamoDB
            
        Raises:
            ClientError: If the put operation fails
        """
        try:
            response = self.table.put_item(Item=item)
            return response
        except ClientError as e:
            raise Exception(f"Failed to put item to DynamoDB: {e.response['Error']['Message']}")
    
    def get_item(self, chat_id: str, timestamp: int) -> Optional[Dict[str, Any]]:
        """
        Get an item from DynamoDB table by chat_id and timestamp.
        
        Args:
            chat_id: The partition key (chatId)
            timestamp: The sort key (timestamp)
            
        Returns:
            Dict containing the item, or None if not found
            
        Raises:
            ClientError: If the get operation fails
        """
        try:
            response = self.table.get_item(
                Key={
                    'chatId': chat_id,
                    'timestamp': timestamp
                }
            )
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Failed to get item from DynamoDB: {e.response['Error']['Message']}")
    
    def query_by_chat_id(self, chat_id: str, limit: int = 50, 
                         last_evaluated_key: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Query items by chat_id with pagination support.
        
        Args:
            chat_id: The partition key to query
            limit: Maximum number of items to return
            last_evaluated_key: Token for pagination
            
        Returns:
            Dict containing items and pagination token
            
        Raises:
            ClientError: If the query operation fails
        """
        try:
            query_params = {
                'KeyConditionExpression': 'chatId = :chat_id',
                'ExpressionAttributeValues': {
                    ':chat_id': chat_id
                },
                'Limit': limit,
                'ScanIndexForward': False  # Sort by timestamp descending
            }
            
            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key
            
            response = self.table.query(**query_params)
            
            return {
                'items': response.get('Items', []),
                'count': response.get('Count', 0),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
        except ClientError as e:
            raise Exception(f"Failed to query DynamoDB: {e.response['Error']['Message']}")
    
    def query_messages_by_session(self, session_id: str, limit: int = 100,
                                   last_evaluated_key: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Query messages for a specific session using PK/SK pattern.
        
        Args:
            session_id: The session ID to query messages for
            limit: Maximum number of items to return
            last_evaluated_key: Token for pagination
            
        Returns:
            Dict containing items and pagination token
            
        Raises:
            ClientError: If the query operation fails
        """
        try:
            pk = f'SESSION#{session_id}'
            
            query_params = {
                'KeyConditionExpression': 'PK = :pk AND begins_with(SK, :sk_prefix)',
                'ExpressionAttributeValues': {
                    ':pk': pk,
                    ':sk_prefix': 'MSG#'
                },
                'Limit': limit,
                'ScanIndexForward': True  # Sort by timestamp ascending (chronological order)
            }
            
            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key
            
            response = self.table.query(**query_params)
            
            return {
                'items': response.get('Items', []),
                'count': response.get('Count', 0),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
        except ClientError as e:
            raise Exception(f"Failed to query messages by session: {e.response['Error']['Message']}")
    
    def scan_all(self, limit: int = 50, 
                 last_evaluated_key: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Scan all items in the table with pagination support.
        
        Args:
            limit: Maximum number of items to return
            last_evaluated_key: Token for pagination
            
        Returns:
            Dict containing items and pagination token
            
        Raises:
            ClientError: If the scan operation fails
        """
        try:
            scan_params = {
                'Limit': limit
            }
            
            if last_evaluated_key:
                scan_params['ExclusiveStartKey'] = last_evaluated_key
            
            response = self.table.scan(**scan_params)
            
            return {
                'items': response.get('Items', []),
                'count': response.get('Count', 0),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
        except ClientError as e:
            raise Exception(f"Failed to scan DynamoDB: {e.response['Error']['Message']}")


class S3Helper:
    """Helper class for S3 operations."""
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize S3 helper.
        
        Args:
            bucket_name: Name of the S3 bucket. If None, reads from environment.
        """
        self.bucket_name = bucket_name or os.environ.get('S3_BUCKET_NAME')
        self.cloudfront_url = os.environ.get('CLOUDFRONT_URL', '')
    
    def put_object(self, key: str, body: str, content_type: str = 'text/plain') -> str:
        """
        Put an object into S3 bucket.
        
        Args:
            key: S3 object key (path)
            body: Content to upload
            content_type: MIME type of the content
            
        Returns:
            str: CloudFront URL of the uploaded object
            
        Raises:
            ClientError: If the put operation fails
        """
        try:
            s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=body,
                ContentType=content_type
            )
            
            # Return CloudFront URL if available, otherwise S3 URL
            if self.cloudfront_url:
                return f"{self.cloudfront_url}/{key}"
            else:
                return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
                
        except ClientError as e:
            raise Exception(f"Failed to put object to S3: {e.response['Error']['Message']}")
    
    def get_object(self, key: str) -> str:
        """
        Get an object from S3 bucket.
        
        Args:
            key: S3 object key (path)
            
        Returns:
            str: Content of the object
            
        Raises:
            ClientError: If the get operation fails
        """
        try:
            response = s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            raise Exception(f"Failed to get object from S3: {e.response['Error']['Message']}")
    
    def put_diagram_markdown(self, chat_id: str, mermaid_code: str) -> str:
        """
        Save Mermaid diagram code as markdown file to S3.
        
        Args:
            chat_id: Unique identifier for the chat/diagram
            mermaid_code: Mermaid diagram code
            
        Returns:
            str: CloudFront URL of the markdown file
        """
        key = f"diagrams/{chat_id}.md"
        markdown_content = f"```mermaid\n{mermaid_code}\n```"
        # Use text/plain for better compatibility with browsers and CloudFront
        return self.put_object(key, markdown_content, 'text/plain; charset=utf-8')
    
    def put_diagram_image(self, chat_id: str, image_data: bytes) -> str:
        """
        Save diagram image (PNG) to S3.
        
        Args:
            chat_id: Unique identifier for the chat/diagram
            image_data: Binary image data
            
        Returns:
            str: CloudFront URL of the image file
        """
        key = f"diagrams/{chat_id}.png"
        try:
            s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_data,
                ContentType='image/png'
            )
            
            if self.cloudfront_url:
                return f"{self.cloudfront_url}/{key}"
            else:
                return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
                
        except ClientError as e:
            raise Exception(f"Failed to put image to S3: {e.response['Error']['Message']}")
    
    def get_diagram_markdown(self, chat_id: str) -> str:
        """
        Retrieve Mermaid diagram markdown from S3.
        
        Args:
            chat_id: Unique identifier for the chat/diagram
            
        Returns:
            str: Markdown content
        """
        key = f"diagrams/{chat_id}.md"
        return self.get_object(key)
