# Get History Lambda Function

## Overview

This Lambda function retrieves chat history from DynamoDB with pagination support. It handles GET requests to the `/api/chat/history` endpoint.

## Functionality

- Queries all chat messages from DynamoDB
- Supports pagination with configurable limit
- Returns results sorted by timestamp descending
- Encodes pagination tokens as base64 strings

## API Specification

### Endpoint
`GET /api/chat/history`

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | integer | No | 50 | Maximum number of items to return (1-100) |
| nextToken | string | No | - | Pagination token from previous response |

### Response Format

**Success (200)**
```json
{
  "chats": [
    {
      "chatId": "uuid",
      "timestamp": 1702564800,
      "userMessage": "string",
      "diagramType": "flowchart",
      "mermaidCode": "string",
      "imageUrl": "string",
      "markdownUrl": "string",
      "status": "completed"
    }
  ],
  "count": 15,
  "nextToken": "base64-encoded-token"
}
```

**Error (400)**
```json
{
  "error": "Invalid parameter: limit must be between 1 and 100"
}
```

**Error (500)**
```json
{
  "error": "Failed to retrieve chat history"
}
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| DYNAMODB_TABLE_NAME | Name of the DynamoDB table | Yes |

## Requirements Validation

This implementation satisfies:
- **Requirement 4.2**: Loads chat history from DynamoDB
- **Requirement 4.4**: Supports pagination with configurable limit
- **Requirement 7.2**: Returns paginated chat messages with proper format

## Implementation Notes

1. **Pagination**: Uses DynamoDB's scan operation with LastEvaluatedKey for pagination
2. **Token Encoding**: Pagination tokens are base64-encoded JSON for security and URL safety
3. **Sorting**: Results are sorted by timestamp in descending order (newest first)
4. **Limit Validation**: Enforces limit between 1 and 100 to prevent excessive data transfer
5. **Error Handling**: Comprehensive error handling for invalid parameters and DynamoDB failures

## Testing

See `tests/unit/test_get_history.py` for unit tests.
