# Requirements Document

## Introduction

This document specifies the requirements for the **Software Architecture AI Assistant**, a cloud-native web application that enables users to generate software architecture diagrams through natural language conversations with an LLM. The system focuses on strong cloud infrastructure (80%) with a simple, working AI application (20%) for a Final Project in Cloud-Native AI Application Deployment.

The application provides a single-page chat interface where users can request various types of architecture diagrams (Flowchart, ERD, Sequence, Class, State, High-Level Architecture, DFD). The LLM generates diagrams in Mermaid format, which are rendered visually and stored persistently in AWS cloud services.

## Glossary

- **Architecture_AI_Assistant**: The complete cloud-native web application system that generates software architecture diagrams through AI-powered chat
- **LLM_API**: A configurable Large Language Model API endpoint (not hardcoded to a specific provider) used for generating diagram code from natural language prompts
- **Mermaid_Code**: Text-based diagram definition syntax that can be rendered into visual diagrams
- **React_Flow**: A React library for rendering interactive node-based diagrams with zoom and pan capabilities
- **Chat_Session**: A browser session containing the conversation history between user and AI
- **Diagram_Type**: One of the supported diagram categories: Flowchart, ERD, Sequence, Class, State, Architecture, DFD
- **S3_Bucket**: AWS Simple Storage Service container for storing diagram files (markdown and PNG images)
- **DynamoDB_Table**: AWS NoSQL database table for storing chat history and diagram metadata
- **Lambda_Function**: AWS serverless compute function handling backend API logic
- **API_Gateway**: AWS service routing HTTP requests to Lambda functions
- **CloudFront_Distribution**: AWS CDN service for serving the frontend application globally
- **Terraform_Configuration**: Infrastructure-as-Code files defining all AWS resources

## Requirements

### Requirement 1: Chat Interface

**User Story:** As a user, I want to interact with an AI through a chat interface, so that I can request architecture diagrams using natural language.

#### Acceptance Criteria

1. WHEN a user opens the application URL THEN the Architecture_AI_Assistant SHALL display a single-page chat interface with a message input field and diagram type selector
2. WHEN a user types a message and submits it THEN the Architecture_AI_Assistant SHALL send the message to the backend LLM_API and display a loading indicator
3. WHEN the LLM_API returns a response THEN the Architecture_AI_Assistant SHALL display the AI response in the chat area within 30 seconds
4. WHEN a user selects a Diagram_Type from the dropdown THEN the Architecture_AI_Assistant SHALL use that type as context for the LLM prompt
5. IF the LLM_API request fails THEN the Architecture_AI_Assistant SHALL display a user-friendly error message and allow retry

### Requirement 2: Diagram Generation

**User Story:** As a user, I want the AI to generate architecture diagrams from my descriptions, so that I can visualize software systems without manual drawing.

#### Acceptance Criteria

1. WHEN a user submits a diagram request THEN the Architecture_AI_Assistant SHALL generate valid Mermaid_Code for the requested Diagram_Type
2. WHEN Mermaid_Code is generated THEN the Architecture_AI_Assistant SHALL display the code in a syntax-highlighted code block in the chat
3. WHEN Mermaid_Code is generated THEN the Architecture_AI_Assistant SHALL render the diagram visually using React_Flow with zoom and pan capabilities
4. WHEN a diagram is generated THEN the Architecture_AI_Assistant SHALL support these Diagram_Types: Flowchart, ERD, Sequence, Class, State, Architecture, DFD
5. WHEN the LLM generates Mermaid_Code THEN the Architecture_AI_Assistant SHALL validate the code syntax before rendering

### Requirement 3: Diagram Storage and Download

**User Story:** As a user, I want to save and download my generated diagrams, so that I can use them in documentation and presentations.

#### Acceptance Criteria

1. WHEN a diagram is generated THEN the Architecture_AI_Assistant SHALL save the Mermaid_Code as a markdown file to the S3_Bucket
2. WHEN a diagram is generated THEN the Architecture_AI_Assistant SHALL render and save a PNG image to the S3_Bucket
3. WHEN a diagram is displayed THEN the Architecture_AI_Assistant SHALL provide a download button for the PNG image
4. WHEN a diagram is displayed THEN the Architecture_AI_Assistant SHALL provide a download button for the markdown file
5. WHEN a user clicks a download button THEN the Architecture_AI_Assistant SHALL initiate a file download from the S3_Bucket via CloudFront_Distribution

### Requirement 4: Chat History Persistence

**User Story:** As a user, I want my chat history to be saved, so that I can view previous conversations and diagrams after refreshing the page.

#### Acceptance Criteria

1. WHEN a chat message is sent or received THEN the Architecture_AI_Assistant SHALL save the message to the DynamoDB_Table with a unique chat ID and timestamp
2. WHEN a user opens the application THEN the Architecture_AI_Assistant SHALL load and display the previous Chat_Session history from DynamoDB_Table
3. WHEN chat history is loaded THEN the Architecture_AI_Assistant SHALL re-render all previously generated diagrams from stored Mermaid_Code
4. WHEN querying chat history THEN the Architecture_AI_Assistant SHALL support pagination with a configurable limit parameter

### Requirement 5: LLM Integration

**User Story:** As a developer, I want the LLM integration to be configurable, so that different LLM providers can be used without code changes.

#### Acceptance Criteria

1. WHEN the Lambda_Function calls the LLM_API THEN the Architecture_AI_Assistant SHALL use environment variables for API endpoint and authentication
2. WHEN sending a prompt to the LLM_API THEN the Architecture_AI_Assistant SHALL include a system prompt that instructs the LLM to generate valid Mermaid_Code for the specified Diagram_Type
3. WHEN the LLM_API returns a response THEN the Architecture_AI_Assistant SHALL parse and extract the Mermaid_Code from the response
4. IF the LLM_API returns invalid Mermaid_Code THEN the Architecture_AI_Assistant SHALL return an error response with details

### Requirement 6: AWS Infrastructure

**User Story:** As a cloud engineer, I want the entire infrastructure defined as code, so that the system can be deployed with a single command.

#### Acceptance Criteria

1. WHEN deploying the system THEN the Terraform_Configuration SHALL create all required AWS resources: API_Gateway, Lambda_Function, DynamoDB_Table, S3_Bucket, CloudFront_Distribution
2. WHEN the Terraform_Configuration is applied THEN the Architecture_AI_Assistant SHALL output the CloudFront URL, API Gateway URL, and resource identifiers
3. WHEN Lambda_Functions are deployed THEN the Architecture_AI_Assistant SHALL configure IAM roles with least-privilege permissions for DynamoDB, S3, and CloudWatch
4. WHEN the S3_Bucket is created THEN the Architecture_AI_Assistant SHALL configure it for static website hosting with CloudFront as the origin
5. WHEN API_Gateway is configured THEN the Architecture_AI_Assistant SHALL enable CORS for all origins during development

### Requirement 7: API Endpoints

**User Story:** As a frontend developer, I want well-defined REST API endpoints, so that I can integrate the frontend with backend services.

#### Acceptance Criteria

1. WHEN a POST request is sent to /api/diagram/generate THEN the Architecture_AI_Assistant SHALL accept userPrompt and diagramType parameters and return generated Mermaid_Code with S3 URLs
2. WHEN a GET request is sent to /api/chat/history THEN the Architecture_AI_Assistant SHALL return paginated chat messages from DynamoDB_Table
3. WHEN a POST request is sent to /api/chat/save THEN the Architecture_AI_Assistant SHALL save the chat message to DynamoDB_Table and return confirmation
4. WHEN any API request fails THEN the Architecture_AI_Assistant SHALL return appropriate HTTP status codes (400 for bad request, 500 for server error) with error details

### Requirement 8: Frontend Hosting

**User Story:** As a user, I want the application to load quickly from anywhere, so that I can use it without delays.

#### Acceptance Criteria

1. WHEN the React application is built THEN the Architecture_AI_Assistant SHALL produce static files suitable for S3 hosting
2. WHEN static files are deployed to S3_Bucket THEN the CloudFront_Distribution SHALL serve them with HTTPS and caching
3. WHEN a user accesses the CloudFront URL THEN the Architecture_AI_Assistant SHALL load the complete chat interface within 3 seconds on standard broadband
4. WHEN frontend assets are updated THEN the Architecture_AI_Assistant SHALL support CloudFront cache invalidation

### Requirement 9: Diagram Rendering

**User Story:** As a user, I want to interact with rendered diagrams, so that I can explore complex architectures easily.

#### Acceptance Criteria

1. WHEN Mermaid_Code is received THEN the Architecture_AI_Assistant SHALL parse it and render using React_Flow components
2. WHEN a diagram is rendered THEN the Architecture_AI_Assistant SHALL enable mouse scroll zoom functionality
3. WHEN a diagram is rendered THEN the Architecture_AI_Assistant SHALL enable click-and-drag pan functionality
4. WHEN a diagram contains multiple nodes THEN the Architecture_AI_Assistant SHALL apply automatic layout positioning

### Requirement 10: LLM Prompt Engineering

**User Story:** As a system architect, I want the LLM to generate accurate and valid diagrams, so that the output is immediately usable.

#### Acceptance Criteria

1. WHEN the system sends a prompt to LLM_API THEN the Architecture_AI_Assistant SHALL include a system context that specifies Mermaid syntax rules for the requested Diagram_Type
2. WHEN generating Flowchart diagrams THEN the Architecture_AI_Assistant SHALL instruct the LLM to use graph TD or graph LR syntax
3. WHEN generating ERD diagrams THEN the Architecture_AI_Assistant SHALL instruct the LLM to use erDiagram syntax with proper relationship notation
4. WHEN generating Sequence diagrams THEN the Architecture_AI_Assistant SHALL instruct the LLM to use sequenceDiagram syntax with participant declarations
5. WHEN the LLM generates a response THEN the Architecture_AI_Assistant SHALL extract code blocks marked with ```mermaid delimiters
