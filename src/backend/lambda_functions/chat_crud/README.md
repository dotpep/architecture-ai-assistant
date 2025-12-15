# Chat CRUD Lambda Function

## Overview

This Lambda function handles CRUD (Create, Read, Update, Delete) operations for chat messages. Currently implements the save operation for storing chat messages to DynamoDB using a session-based data model.

## Functionality

### Save Chat Message (POST)

Saves a chat message to DynamoDB with the following features:
- Requires a valid `sessionId` to associate the message with a session
- Generates a unique `messageId` if not provided
- Automatically adds a timestamp
- Validates required fields (`sessionId`, `userMessage`, `diagramType`)
- Supports optional fields for diagram data
- Uses PK/SK pattern for efficient querying (PK: `SESSION#{sessionId}`, SK: `MSG#{timestamp}`)
- Returns confirmation with `messageId`, `sessionId`, and `timestamp`

## API Specification

### Endpoint
`POST /api/chat/save`

### Request Body

**Required Fields:**
- `sessionId` (string): UUID of the session this message belongs to
- `userMessage` (string): The user's message/prompt
- `diagramType` (string): Type of diagram (flowchart, erdiagram, sequence, class, state, architecture, dfd)

**Optional Fields:**
- `messageId` (string): Existing message ID (generated if not provided)
- `aiResponse` (string): AI's response text
- `mermaidCode` (string): Generated Mermaid diagram code
- `imageUrl` (string): CloudFront URL for diagram PNG
- `markdownUrl` (string): CloudFront URL for diagram markdown
- `diagramImageS3Key` (string): S3 key for PNG image
- `diagramMarkdownS3Key` (string): S3 key for markdown file
- `status` (string): Status of the message (pending, completed, failed)

### Request Example

```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
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
  "messageId": "660e8400-e29b-41d4-a716-446655440001",
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1702564800
}
```

**Error (400 - Bad Request):**
```json
{
  "error": "Missing required field: sessionId"
}
```

**Error (500 - Server Error):**
```json
{
  "error": "Failed to save chat message"
}
```

## DynamoDB Schema

### Table: chat_history (Session-based Model)

The table uses a single-table design with PK/SK pattern to store both sessions and messages:

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| PK | String | Partition Key | Format: `SESSION#{sessionId}` |
| SK | String | Sort Key | Format: `MSG#{timestamp}` for messages, `METADATA` for sessions |
| messageId | String | - | UUID for the message |
| sessionId | String | - | UUID for the session |
| timestamp | Number | - | Unix timestamp |
| userMessage | String | - | User's prompt text |
| diagramType | String | - | Type of diagram requested |
| aiResponse | String | - | Full AI response text |
| mermaidCode | String | - | Extracted Mermaid code |
| diagramImageS3Key | String | - | S3 key for PNG image |
| diagramMarkdownS3Key | String | - | S3 key for markdown file |
| imageUrl | String | - | CloudFront URL for image |
| markdownUrl | String | - | CloudFront URL for markdown |
| status | String | - | pending, completed, failed |

**Example Message Item:**
```json
{
  "PK": "SESSION#550e8400-e29b-41d4-a716-446655440000",
  "SK": "MSG#1702564800",
  "messageId": "660e8400-e29b-41d4-a716-446655440001",
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1702564800,
  "userMessage": "Create a flowchart",
  "diagramType": "flowchart",
  "status": "completed"
}
```

## Environment Variables

- `DYNAMODB_TABLE_NAME`: Name of the DynamoDB table (default: `chat_history`)

## Dependencies

- `boto3`: AWS SDK for Python
- `utils`: Shared utility functions (UUID generation, timestamp, validation)
- `aws_helpers`: DynamoDB helper class

## Requirements Validation

This implementation satisfies:
- **Requirement 2.1**: Stores messages with reference to session ID
- **Requirement 2.2**: Includes all required message fields (messageId, sessionId, timestamp, userMessage, diagramType, status)
- **Requirement 5.4**: Associates messages with provided sessionId

## Error Handling

The function handles the following error cases:
1. Missing required fields (sessionId, userMessage, diagramType) (400)
2. Invalid session ID format (400)
3. Invalid diagram type (400)
4. Invalid JSON in request body (400)
5. DynamoDB operation failures (500)

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
        'sessionId': '550e8400-e29b-41d4-a716-446655440000',
        'userMessage': 'Create a sequence diagram',
        'diagramType': 'sequence'
    })
}

# Call the handler
response = handler(event, None)

# Response will contain:
# {
#   'statusCode': 200,
#   'body': '{"success": true, "messageId": "...", "sessionId": "...", "timestamp": 1702564800}'
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
