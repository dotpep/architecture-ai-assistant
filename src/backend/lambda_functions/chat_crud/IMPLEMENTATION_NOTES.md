# Chat CRUD Lambda - Session Support Implementation

## Changes Made

### 1. Updated Request Validation
- Added `sessionId` as a required field in request body
- Added validation for `sessionId` format using `validate_session_id()` utility
- Maintains existing validation for `userMessage` and `diagramType`

### 2. Updated Message Storage Structure
The Lambda now uses the PK/SK pattern for DynamoDB:

**Previous Structure:**
```json
{
  "chatId": "uuid",
  "timestamp": 1234567890,
  "userMessage": "...",
  "diagramType": "...",
  ...
}
```

**New Structure:**
```json
{
  "PK": "SESSION#{sessionId}",
  "SK": "MSG#{timestamp}",
  "messageId": "uuid",
  "sessionId": "uuid",
  "timestamp": 1234567890,
  "userMessage": "...",
  "diagramType": "...",
  ...
}
```

### 3. Key Changes in save_message()
- Now requires `sessionId` in request body
- Generates `messageId` using `generate_message_id()` utility
- Constructs PK as `SESSION#{sessionId}`
- Constructs SK as `MSG#{timestamp}`
- Stores both `messageId` and `sessionId` in the item
- Returns `messageId` and `sessionId` in response (instead of `chatId`)

### 4. Backward Compatibility
- The function still accepts optional fields like `aiResponse`, `mermaidCode`, `imageUrl`, etc.
- Status defaults to 'pending' if not provided

## API Contract

### Request
```json
POST /api/chat
{
  "sessionId": "uuid-string",
  "userMessage": "Create a flowchart...",
  "diagramType": "flowchart",
  "aiResponse": "optional",
  "mermaidCode": "optional",
  "imageUrl": "optional",
  "markdownUrl": "optional",
  "status": "optional"
}
```

### Response
```json
{
  "success": true,
  "messageId": "uuid-string",
  "sessionId": "uuid-string",
  "timestamp": 1234567890
}
```

## Requirements Validated
- **Requirement 2.1**: Messages are stored with reference to sessionId
- **Requirement 2.2**: Messages include messageId, sessionId, timestamp, userMessage, diagramType, and status
- **Requirement 5.4**: API associates messages with provided sessionId
