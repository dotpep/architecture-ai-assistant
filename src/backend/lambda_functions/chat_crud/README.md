# Chat CRUD Lambda Function

## Overview

This Lambda function handles CRUD (Create, Read, Update, Delete) operations for chat messages. Currently implements the save operation for storing chat messages to DynamoDB.

## Functionality

### Save Chat Message (POST)

Saves a chat message to DynamoDB with the following features:
- Generates a unique `chatId` if not provided
- Automatically adds a timestamp
- Validates required fields (`userMessage`, `diagramType`)
- Supports optional fields for diagram data
- Returns confirmation with `chatId` and `timestamp`

## API Specification

### Endpoint
`POST /api/chat/save`

### Request Body

**Required Fields:**
- `userMessage` (string): The user's message/prompt
- `diagramType` (string): Type of diagram (flowchart, erdiagram, sequence, class, state, architecture, dfd)

**Optional Fields:**
- `chatId` (string): Existing chat ID (generated if not provided)
- `aiResponse` (string): AI's response text
- `mermaidCode` (string): Generated Mermaid diagram code
- `imageUrl` (string): CloudFront URL for diagram PNG
- `markdownUrl` (string): CloudFront URL for diagram markdown
- `diagramImageS3Key` (string): S3 key for PNG image
- `diagramMarkdownS3Key` (string): S3 key for markdown file
- `status` (string): Status of the chat (pending, completed, failed)

### Request Example

```json
{
  "userMessage": "Create a flowchart for user authentication",
  "diagramType": "flowchart",
  "aiResponse": "Here is your authentication flowchart",
  "mermaidCode": "graph TD\n  A[Start] --> B[Login]",
  "imageUrl": "https://cloudfront.example.com/diagrams/abc-123.png",
  "markdownUrl": "https://cloudfront.example.com/diagrams/abc-123.md",
  "status": "completed"
}
```

### Response

**Success (200):**
```json
{
  "success": true,
  "chatId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1702564800
}
```

**Error (400 - Bad Request):**
```json
{
  "error": "Missing required field: userMessage"
}
```

**Error (500 - Server Error):**
```json
{
  "error": "Failed to save chat message"
}
```

## DynamoDB Schema

### Table: chat_history

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| chatId | String | Partition Key | UUID for the chat entry |
| timestamp | Number | Sort Key | Unix timestamp |
| userMessage | String | - | User's prompt text |
| diagramType | String | - | Type of diagram requested |
| aiResponse | String | - | Full AI response text |
| mermaidCode | String | - | Extracted Mermaid code |
| diagramImageS3Key | String | - | S3 key for PNG image |
| diagramMarkdownS3Key | String | - | S3 key for markdown file |
| imageUrl | String | - | CloudFront URL for image |
| markdownUrl | String | - | CloudFront URL for markdown |
| status | String | - | pending, completed, failed |

## Environment Variables

- `DYNAMODB_TABLE_NAME`: Name of the DynamoDB table (default: `chat_history`)

## Dependencies

- `boto3`: AWS SDK for Python
- `utils`: Shared utility functions (UUID generation, timestamp, validation)
- `aws_helpers`: DynamoDB helper class

## Requirements Validation

This implementation satisfies:
- **Requirement 4.1**: Saves chat messages to DynamoDB with unique chat ID and timestamp
- **Requirement 7.3**: POST /api/chat/save endpoint saves messages and returns confirmation

## Error Handling

The function handles the following error cases:
1. Missing required fields (400)
2. Invalid diagram type (400)
3. Invalid JSON in request body (400)
4. DynamoDB operation failures (500)

## CORS Support

The function includes CORS headers to allow cross-origin requests:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Headers: Content-Type`
- `Access-Control-Allow-Methods: POST, OPTIONS`

## Testing

See `tests/unit/test_chat_crud.py` for unit tests covering:
- Request validation
- Chat ID generation
- Optional field handling
- Error cases
- Response formatting

## Usage Example

```python
import json

# Example event from API Gateway
event = {
    'httpMethod': 'POST',
    'body': json.dumps({
        'userMessage': 'Create a sequence diagram',
        'diagramType': 'sequence'
    })
}

# Call the handler
response = lambda_handler(event, None)

# Response will contain:
# {
#   'statusCode': 200,
#   'body': '{"success": true, "chatId": "...", "timestamp": 1702564800}'
# }
```

## Future Enhancements

Potential additions for future iterations:
- GET operation to retrieve specific chat messages
- UPDATE operation to modify existing messages
- DELETE operation to remove messages
- Batch operations for multiple messages
- Query by date range
- Full-text search capabilities
