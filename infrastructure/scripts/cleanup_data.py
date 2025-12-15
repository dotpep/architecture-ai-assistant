#!/usr/bin/env python3
"""
Script to clean up DynamoDB chat history and S3 diagrams
Updated for session-based data model with PK/SK pattern
"""

import boto3

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')

# DynamoDB cleanup
print("Cleaning up DynamoDB chat history...")
table = dynamodb.Table('architecture-ai-assistant-chat_history-dev')

# Scan all items (both sessions and messages)
response = table.scan()
items = response.get('Items', [])

# Delete each item using PK/SK pattern
deleted_count = 0
for item in items:
    table.delete_item(
        Key={
            'PK': item['PK'],
            'SK': item['SK']
        }
    )
    deleted_count += 1

print(f"✓ Deleted {deleted_count} items (sessions and messages) from DynamoDB")

# S3 cleanup - delete all diagrams
print("\nCleaning up S3 diagrams...")
bucket = 'architecture-ai-assistant-bucket-dev'

# List all objects in diagrams folder
response = s3.list_objects_v2(Bucket=bucket, Prefix='diagrams/')
objects = response.get('Contents', [])

# Delete each object
deleted_diagrams = 0
for obj in objects:
    if obj['Key'] != 'diagrams/':  # Skip the folder itself
        s3.delete_object(Bucket=bucket, Key=obj['Key'])
        deleted_diagrams += 1

print(f"✓ Deleted {deleted_diagrams} diagram files from S3")

print("\n✓ Cleanup complete!")
print(f"  - DynamoDB: {deleted_count} items deleted")
print(f"  - S3: {deleted_diagrams} files deleted")
