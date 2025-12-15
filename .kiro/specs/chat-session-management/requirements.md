# Requirements Document

## Introduction

This feature implements proper chat session management for the Architecture AI Assistant. Currently, the application treats each message as an independent entity without grouping them into conversation sessions. This feature introduces a session-based architecture where users can create new chat sessions, each containing multiple message exchanges (prompts and AI responses). The sidebar will display sessions (not individual messages), and selecting a session will load all messages within that conversation.

## Glossary

- **Chat_Session**: A conversation container that groups multiple related message exchanges between the user and the AI assistant. Each session has a unique identifier and metadata.
- **Message**: A single exchange within a session, containing a user prompt and the corresponding AI response with generated diagram.
- **Session_ID**: A unique identifier (UUID) for a chat session, used as the partition key in DynamoDB.
- **Message_ID**: A unique identifier for a message within a session.
- **Session_Title**: A human-readable title for a session, typically derived from the first user prompt.
- **Chat_History_API**: The backend API endpoint responsible for retrieving and managing chat sessions and messages.
- **DynamoDB**: The AWS NoSQL database service used to persist chat sessions and messages.

## Requirements

### Requirement 1

**User Story:** As a user, I want to create a new chat session, so that I can start a fresh conversation without mixing it with previous conversations.

#### Acceptance Criteria

1. WHEN a user clicks the "New Chat" button THEN the System SHALL create a new session record in DynamoDB with a unique Session_ID and timestamp
2. WHEN a new session is created THEN the System SHALL clear the chat interface and display an empty conversation view
3. WHEN a new session is created THEN the System SHALL set the session as the current active session for subsequent messages
4. WHEN a session is created THEN the System SHALL generate a Session_Title from the first user message once submitted

### Requirement 2

**User Story:** As a user, I want my messages to be grouped within a session, so that I can see the full conversation history when I return to a session.

#### Acceptance Criteria

1. WHEN a user submits a message THEN the System SHALL store the message with a reference to the current Session_ID
2. WHEN a message is stored THEN the System SHALL include the Message_ID, Session_ID, timestamp, user prompt, AI response, and diagram data
3. WHEN multiple messages exist in a session THEN the System SHALL maintain chronological order based on timestamp
4. WHEN serializing messages to DynamoDB THEN the System SHALL encode them using JSON format
5. WHEN deserializing messages from DynamoDB THEN the System SHALL decode them from JSON format preserving all fields

### Requirement 3

**User Story:** As a user, I want to see my chat sessions listed in the sidebar, so that I can easily navigate between different conversations.

#### Acceptance Criteria

1. WHEN the application loads THEN the System SHALL retrieve and display all sessions grouped by date (Today, Yesterday, Last 7 Days, Older)
2. WHEN displaying sessions THEN the System SHALL show the Session_Title and diagram type icon for each session
3. WHEN a user selects a session from the sidebar THEN the System SHALL load and display all messages within that session
4. WHEN the current session is displayed in the sidebar THEN the System SHALL highlight the selected session visually

### Requirement 4

**User Story:** As a user, I want the session title to be automatically generated from my first message, so that I can identify sessions without manual naming.

#### Acceptance Criteria

1. WHEN the first message is submitted in a session THEN the System SHALL extract the first 50 characters of the user prompt as the Session_Title
2. WHEN the extracted title exceeds 50 characters THEN the System SHALL truncate and append ellipsis
3. WHEN updating the session title THEN the System SHALL persist the title to DynamoDB

### Requirement 5

**User Story:** As a developer, I want the backend API to support session-based operations, so that the frontend can properly manage chat sessions.

#### Acceptance Criteria

1. WHEN the frontend requests to create a session THEN the Chat_History_API SHALL accept a POST request and return the new Session_ID
2. WHEN the frontend requests session list THEN the Chat_History_API SHALL return sessions with metadata (Session_ID, Session_Title, created timestamp, last message timestamp, diagram type)
3. WHEN the frontend requests messages for a session THEN the Chat_History_API SHALL return all messages for the specified Session_ID ordered by timestamp
4. WHEN the frontend saves a message THEN the Chat_History_API SHALL associate the message with the provided Session_ID
5. IF a request contains an invalid Session_ID THEN the Chat_History_API SHALL return a 400 error with descriptive message

