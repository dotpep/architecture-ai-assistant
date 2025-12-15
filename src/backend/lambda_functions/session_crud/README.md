# Session CRUD Lambda Function

This Lambda function handles all CRUD operations for chat sessions in the Architecture AI Assistant.

## Endpoints

### POST /api/session
Create a new chat session.

**Request Body (optional):**
```json
{
  "title": "New Chat",
  "diagramType": "flowchart"
}
```

**Response:**
```json
{
  "success": true,
  "sessionId": "uuid-here",
  "title": "New Chat",
  "diagramType": "flowchart",
  "createdAt": 1702000000,
  "updatedAt": 1702000000,
  "messageCount": 0
}
```

### GET /api/session
List all sessions.

**Query Parameters:**
- `limit` (optional): Maximum number of sessions to return (default: 50)

**Response:**
```json
{
  "sessions": [
    {
      "sessionId": "uuid-here",
      "title": "Microservices architecture",
      "diagramType": "architecture",
      "createdAt": 1702000000,
      "updatedAt": 1702000100,
      "messageCount": 3
    }
  ],
  "count": 1
}
```

### GET /api/session/{sessionId}
Get a single session by ID.

**Response:**
```json
{
  "sessionId": "uuid-here",
  "title": "Microservices architecture",
  "diagramType": "architecture",
  "createdAt": 1702000000,
  "updatedAt": 1702000100,
  "messageCount": 3
}
```

### PUT /api/session/{sessionId}
Update a session's title.

**Request Body:**
```json
{
  "title": "Updated title"
}
```

**Response:**
```json
{
  "success": true,
  "sessionId": "uuid-here",
  "title": "Updated title",
  "updatedAt": 1702000200
}
```

### DELETE /api/session/{sessionId}
Delete a session and all its messages.

**Response:**
```json
{
  "success": true,
  "sessionId": "uuid-here",
  "deletedItems": 5
}
```

## Error Responses

All error responses follow this format:
```json
{
  "error": "Error message description"
}
```

Common error codes:
- `400`: Bad request (invalid input, missing fields)
- `404`: Session not found
- `405`: Method not allowed
- `500`: Internal server error

## Environment Variables

- `DYNAMODB_TABLE_NAME`: Name of the DynamoDB table (default: 'chat_history')

## DynamoDB Schema

Sessions use a single-table design with PK/SK pattern:

**Session Metadata:**
- PK: `SESSION#{sessionId}`
- SK: `METADATA`
- Attributes: sessionId, title, diagramType, createdAt, updatedAt, messageCount

**Session Messages:**
- PK: `SESSION#{sessionId}`
- SK: `MSG#{timestamp}`
- Attributes: messageId, sessionId, timestamp, userMessage, aiResponse, etc.
