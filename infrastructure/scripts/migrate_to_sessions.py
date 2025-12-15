#!/usr/bin/env python3
"""
Data Migration Script: Flat Messages to Session-Based Structure

This script migrates existing DynamoDB data from the old flat structure
(chatId + timestamp) to the new session-based structure (PK + SK pattern).

Each existing message becomes its own session with one message.

Requirements: 2.1 (Session Management)

Usage:
    python migrate_to_sessions.py [--dry-run] [--table-name TABLE_NAME] [--region REGION]
"""

import argparse
import boto3
import uuid
from datetime import datetime
from decimal import Decimal

def generate_session_id():
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def extract_session_title(message, max_length=50):
    """Extract session title from user message"""
    if not message:
        return "Untitled Session"
    
    # Clean the message
    title = message.strip()
    
    # Truncate if needed
    if len(title) > max_length:
        return title[:max_length] + "..."
    
    return title

def migrate_item_to_session(item, dry_run=False):
    """
    Convert a flat message item to session-based structure.
    
    Returns a tuple of (session_item, message_item)
    """
    # Generate new session ID
    session_id = generate_session_id()
    
    # Extract data from old item
    chat_id = item.get('chatId', '')
    timestamp = item.get('timestamp', 0)
    user_message = item.get('userMessage', '')
    diagram_type = item.get('diagramType', 'architecture')
    ai_response = item.get('aiResponse', '')
    mermaid_code = item.get('mermaidCode', '')
    image_url = item.get('imageUrl', '')
    markdown_url = item.get('markdownUrl', '')
    status = item.get('status', 'completed')
    
    # Create session metadata item
    session_item = {
        'PK': f'SESSION#{session_id}',
        'SK': 'METADATA',
        'sessionId': session_id,
        'title': extract_session_title(user_message),
        'diagramType': diagram_type,
        'createdAt': timestamp,
        'updatedAt': timestamp,
        'messageCount': 1
    }
    
    # Create message item
    message_id = str(uuid.uuid4())
    message_item = {
        'PK': f'SESSION#{session_id}',
        'SK': f'MSG#{timestamp}',
        'messageId': message_id,
        'sessionId': session_id,
        'timestamp': timestamp,
        'userMessage': user_message,
        'diagramType': diagram_type,
        'aiResponse': ai_response,
        'mermaidCode': mermaid_code,
        'imageUrl': image_url,
        'markdownUrl': markdown_url,
        'status': status
    }
    
    # Add optional fields if they exist
    if 'diagramImageS3Key' in item:
        message_item['diagramImageS3Key'] = item['diagramImageS3Key']
    if 'diagramMarkdownS3Key' in item:
        message_item['diagramMarkdownS3Key'] = item['diagramMarkdownS3Key']
    
    return session_item, message_item

def migrate_data(table_name, region, dry_run=False):
    """
    Main migration function.
    
    Scans the old table structure and creates new session-based items.
    """
    print(f"Starting migration for table: {table_name}")
    print(f"Region: {region}")
    print(f"Dry run: {dry_run}")
    print("-" * 60)
    
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    # Scan all existing items
    print("\nScanning existing items...")
    response = table.scan()
    items = response.get('Items', [])
    
    # Handle pagination if needed
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    print(f"Found {len(items)} items to migrate")
    
    if len(items) == 0:
        print("\nNo items to migrate. Exiting.")
        return
    
    # Migrate each item
    migrated_count = 0
    error_count = 0
    
    for idx, item in enumerate(items, 1):
        try:
            # Convert to session structure
            session_item, message_item = migrate_item_to_session(item, dry_run)
            
            if dry_run:
                print(f"\n[DRY RUN] Item {idx}/{len(items)}:")
                print(f"  Old: chatId={item.get('chatId')}, timestamp={item.get('timestamp')}")
                print(f"  New Session: {session_item['PK']}, {session_item['SK']}")
                print(f"  New Message: {message_item['PK']}, {message_item['SK']}")
                print(f"  Title: {session_item['title']}")
            else:
                # Write new items to table
                table.put_item(Item=session_item)
                table.put_item(Item=message_item)
                
                # Delete old item
                table.delete_item(
                    Key={
                        'chatId': item['chatId'],
                        'timestamp': item['timestamp']
                    }
                )
                
                migrated_count += 1
                
                if migrated_count % 10 == 0:
                    print(f"Migrated {migrated_count}/{len(items)} items...")
        
        except Exception as e:
            error_count += 1
            print(f"\nError migrating item {idx}: {str(e)}")
            print(f"  Item: {item}")
            continue
    
    # Summary
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    if dry_run:
        print(f"DRY RUN - No changes made")
        print(f"Items that would be migrated: {len(items)}")
    else:
        print(f"Successfully migrated: {migrated_count}")
        print(f"Errors: {error_count}")
        print(f"Total processed: {len(items)}")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(
        description='Migrate DynamoDB data from flat structure to session-based structure'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run migration without making changes (preview mode)'
    )
    parser.add_argument(
        '--table-name',
        type=str,
        default='architecture-ai-assistant-chat_history-dev',
        help='DynamoDB table name (default: architecture-ai-assistant-chat_history-dev)'
    )
    parser.add_argument(
        '--region',
        type=str,
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )
    
    args = parser.parse_args()
    
    # Confirm before running
    if not args.dry_run:
        print("\n" + "!" * 60)
        print("WARNING: This will modify your DynamoDB table!")
        print("!" * 60)
        response = input("\nAre you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled.")
            return
    
    # Run migration
    migrate_data(args.table_name, args.region, args.dry_run)

if __name__ == '__main__':
    main()
