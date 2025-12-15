# Get History Lambda - Session Support Implementation

## Changes Made

### 1. Added New Function: get_messages_by_session()
A new function to retrieve messages for a specific session:
- Extracts `sessionId` from path parameters
- Validates sessionId format (UUID)
- Queries DynamoDB using the new `query_messages_by_session()` helper
- Returns messages in chronological order (oldest first)
- Supports pagination with limit and nextToken

### 2. Updated Handler Routing
The handler now routes based on path parameters:
- If `sessionId` is in path parameters → calls `get_messages_by_session()`
- Otherwise → calls legacy `get_history()` function

### 3. Added DynamoDB Helper Method
Added `query_messages_by_session()` to `aws_helpers.py`:
- Queries by PK = `SESSION#{sessionId}`
- Filters SK starting with `MSG#`
- Returns results in chronological order (ScanIndexForward=True)
- Supports pagination

## API Endpoints

### New Endpoint: Get Messages by Session
```
GET /api/session/{sessionId}/messages?limit=100&nextToken=...
```

**Response:**
```json
{
  "messages": [
    {
      "PK": "SESSION#uuid",
      "SK": "MSG#1234567890",
      "messageId": "uuid",
      "sessionId": "uuid",
      "timestamp": 1234567890,
      "userMessage": "...",
      "diagramType": "...",
      "status": "completed",
      ...
    }
  ],
  "count": 10,
  "sessionId": "uuid",
  "nextToken": "base64-encoded-token-or-null"
}
```

### Legacy Endpoint (Maintained)
```
GET /api/history?limit=50&nextToken=...
```

Still works as before, scanning all items.

## Message Ordering

**Important:** Messages are returned in **chronological order** (oldest first) to match the requirements:
- Requirement 2.3: "Messages SHALL maintain chronological order based on timestamp"
- Requirement 5.3: "Messages SHALL be returned ordered by timestamp"

This is achieved by setting `ScanIndexForward=True` in the DynamoDB query.

## Error Handling

### 400 Bad Request
- Missing sessionId in path
- Invalid sessionId format (not a valid UUID)
- Invalid limit (not between 1-100)
- Invalid nextToken

### 500 Internal Server Error
- DynamoDB query failures
- Unexpected exceptions

## Requirements Validated
- **Requirement 2.3**: Messages maintain chronological order
- **Requirement 5.3**: API returns messages for specified sessionId ordered by timestamp
