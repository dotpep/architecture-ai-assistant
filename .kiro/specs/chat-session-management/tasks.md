# Implementation Plan

- [x] 1. Update DynamoDB schema and backend infrastructure






  - [x] 1.1 Update DynamoDB table configuration in Terraform to support single-table design with PK/SK pattern

    - Modify `infrastructure/terraform/dynamodb.tf` to use `PK` as hash key and `SK` as range key
    - Add GSI for listing sessions by createdAt timestamp
    - _Requirements: 2.1, 5.2_
  - [x] 1.2 Create data migration script to convert existing flat messages to session-based structure


    - Create script in `infrastructure/scripts/` to migrate existing data
    - Each existing message becomes its own session with one message
    - _Requirements: 2.1_

- [x] 2. Implement backend session service





  - [x] 2.1 Create session utility functions in shared module


    - Add `generate_session_id()` function to `src/backend/shared/utils.py`
    - Add `extract_session_title(message: str, max_length: int = 50)` function
    - Add session validation helpers
    - _Requirements: 1.1, 4.1, 4.2_
  - [ ]* 2.2 Write property test for session ID uniqueness
    - **Property 1: Session ID Uniqueness**
    - **Validates: Requirements 1.1**
  - [ ]* 2.3 Write property test for title extraction
    - **Property 3: Title Extraction Correctness**
    - **Validates: Requirements 4.1, 4.2**
  - [x] 2.4 Create session CRUD Lambda function


    - Create `src/backend/lambda_functions/session_crud/lambda_function.py`
    - Implement POST handler for creating sessions
    - Implement GET handler for listing sessions
    - Implement GET handler for single session by ID
    - Implement PUT handler for updating session title
    - Implement DELETE handler for deleting session
    - _Requirements: 1.1, 5.1, 5.2_
  - [ ]* 2.5 Write property test for session list metadata completeness
    - **Property 9: Session List Metadata Completeness**
    - **Validates: Requirements 5.2**
  - [ ]* 2.6 Write property test for invalid session ID error handling
    - **Property 10: Invalid Session ID Error Handling**
    - **Validates: Requirements 5.5**

- [x] 3. Update message service for session support




  - [x] 3.1 Update chat_crud Lambda to support session-based message storage


    - Modify `src/backend/lambda_functions/chat_crud/lambda_function.py`
    - Add sessionId parameter to message save operation
    - Update DynamoDB item structure to use PK/SK pattern
    - _Requirements: 2.1, 2.2, 5.4_
  - [ ]* 3.2 Write property test for message-session association
    - **Property 4: Message-Session Association**
    - **Validates: Requirements 2.1, 5.4**
  - [ ]* 3.3 Write property test for message field completeness
    - **Property 5: Message Field Completeness**
    - **Validates: Requirements 2.2**
  - [x] 3.4 Update get_history Lambda to retrieve messages by session


    - Modify `src/backend/lambda_functions/get_history/lambda_function.py`
    - Add endpoint to get messages for a specific session
    - Ensure messages are returned in chronological order
    - _Requirements: 2.3, 5.3_
  - [ ]* 3.5 Write property test for message chronological ordering
    - **Property 6: Message Chronological Ordering**
    - **Validates: Requirements 2.3, 5.3**
  - [ ]* 3.6 Write property test for serialization round-trip
    - **Property 7: Serialization Round-Trip**
    - **Validates: Requirements 2.4, 2.5**

- [x] 4. Checkpoint - Ensure all backend tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Update Terraform for new Lambda and API Gateway routes








  - [x] 5.1 Add session_crud Lambda resource to Terraform


    - Update `infrastructure/terraform/lambda.tf` with new Lambda function
    - Configure IAM permissions for DynamoDB access
    - _Requirements: 5.1_
  - [x] 5.2 Add API Gateway routes for session endpoints



    - Update `infrastructure/terraform/api_gateway.tf`
    - Add routes: POST/GET /api/session, GET/PUT/DELETE /api/session/{sessionId}
    - Add route: GET /api/session/{sessionId}/messages
    - _Requirements: 5.1, 5.2, 5.3_


- [x] 6. Update frontend types and API service




  - [x] 6.1 Add session types to frontend type definitions


    - Update `src/frontend/src/types/index.ts`
    - Add Session interface, SessionListResponse, CreateSessionResponse types
    - _Requirements: 1.1, 3.1_
  - [x] 6.2 Add session API functions to API service


    - Update `src/frontend/src/services/api.ts`
    - Add createSession(), getSessions(), getSessionMessages(), updateSessionTitle() functions
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 7. Implement frontend session state management




  - [x] 7.1 Create session state hook or context

    - Create `src/frontend/src/hooks/useSessionState.ts` or context
    - Implement session list loading, current session tracking, session creation
    - _Requirements: 1.2, 1.3, 3.3_
  - [ ]* 7.2 Write property test for session creation state reset
    - **Property 2: Session Creation State Reset**
    - **Validates: Requirements 1.2, 1.3**

- [x] 8. Update Sidebar component for session display





  - [x] 8.1 Refactor Sidebar to display sessions instead of messages


    - Update `src/frontend/src/components/Sidebar.tsx`
    - Display session title and diagram type icon
    - Implement session selection handler
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - [x] 8.2 Implement date grouping utility for sessions


    - Create utility function to group sessions by Today/Yesterday/Last 7 Days/Older
    - _Requirements: 3.1_
  - [ ]* 8.3 Write property test for session date grouping
    - **Property 8: Session Date Grouping**
    - **Validates: Requirements 3.1**

- [ ] 9. Update ChatContainer for session-based messaging
  - [ ] 9.1 Refactor ChatContainer to work with sessions
    - Update `src/frontend/src/components/ChatContainer.tsx`
    - Load messages for current session on session change
    - Create session on first message if no current session
    - Update session title after first message
    - _Requirements: 1.4, 2.1, 3.3, 4.3_

- [ ] 10. Update App component to integrate session management
  - [ ] 10.1 Integrate session state into App component
    - Update `src/frontend/src/App.tsx`
    - Wire up session state to Sidebar and ChatContainer
    - Implement handleNewChat to create new session
    - _Requirements: 1.1, 1.2, 1.3_

- [ ] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Final integration and cleanup
  - [ ] 12.1 Update README with new session management features
    - Document new API endpoints
    - Update architecture diagrams if needed
    - _Requirements: All_
  - [ ] 12.2 Clean up deprecated code and unused imports
    - Remove old flat message handling code
    - Update any remaining references to old data model
    - _Requirements: All_

- [ ] 13. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

