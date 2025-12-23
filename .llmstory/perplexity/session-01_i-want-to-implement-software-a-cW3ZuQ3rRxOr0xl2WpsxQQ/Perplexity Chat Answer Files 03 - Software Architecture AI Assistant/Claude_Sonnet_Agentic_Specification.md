# 🚀 CLAUDE SONNET AGENTIC CODING SPECIFICATION
## Software Architecture AI Assistant - Final Project Cloud-Native Deployment

**Project**: Software Architecture AI Assistant (Diagram Generator)  
**Timeline**: 2 days (16 hours) - Ultra-fast deployment focus  
**Goal**: Simple, working, cloud-native infrastructure + AI integration  
**Platform**: AWS Free Tier  
**Focus**: 80% Infrastructure/Cloud, 20% AI Features  

---

# 📋 EXECUTIVE OVERVIEW

## What We're Building

A **simple, single-page chat application** where users chat with Claude AI to generate software architecture diagrams. The AI generates diagram code (Mermaid format), which is:
1. Displayed as code in the chat
2. Rendered as interactive diagrams (React Flow)
3. Saved as markdown files to S3
4. Saved as PNG images to S3
5. Chat history saved to DynamoDB

## Architecture Summary

```
┌────────────────────────────────────────────────────────┐
│             FRONTEND (React SPA)                       │
│         Hosted on S3 + CloudFront                      │
│                                                        │
│   ┌──────────────────────────────────────────────┐    │
│   │  Chat Interface (Single Page)                │    │
│   ├──────────────────────────────────────────────┤    │
│   │  - Diagram type selector (dropdown)          │    │
│   │  - Chat input with LLM responses             │    │
│   │  - Markdown code preview (Mermaid)           │    │
│   │  - Rendered diagram (React Flow)             │    │
│   │  - Download/Save buttons (S3)                │    │
│   │  - Chat history (from DynamoDB)              │    │
│   └──────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────┘
                        ↓ API Calls
┌────────────────────────────────────────────────────────┐
│           API GATEWAY + LAMBDA (Backend)               │
│              Python 3.11 Serverless                    │
│                                                        │
│  Lambda Functions:                                     │
│  ├─ generate_diagram (LLM + Mermaid generation)        │
│  ├─ save_chat (DynamoDB CRUD)                          │
│  ├─ save_diagram (S3 storage)                          │
│  └─ get_chat_history (DynamoDB read)                   │
└────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
    ┌─────────┐          ┌─────────┐         ┌──────────┐
    │DynamoDB │          │   S3    │         │  Claude  │
    │(Chats)  │          │(Images) │         │API (LLM) │
    └─────────┘          └─────────┘         └──────────┘
```

---

# 🎯 CORE REQUIREMENTS

## Must-Have Features (MVP)

✅ **Chat Interface**
- Single page React application
- Input field for user prompts
- Display AI responses as messages
- Diagram type selector (dropdown)

✅ **Diagram Generation**
- LLM generates Mermaid diagram code
- AI understands these diagram types:
  - Flowchart (default)
  - Entity-Relationship (ERD)
  - Sequence Diagram
  - Class Diagram
  - State Diagram
  - High-Level Architecture (simple diagram)
  - DFD (Data Flow Diagram)

✅ **Display Diagrams**
- Show Mermaid code in chat
- Render diagram using React Flow
- Display both code and visual side-by-side

✅ **Storage**
- Save chat messages to DynamoDB
- Save diagram markdown to S3
- Save diagram PNG to S3
- Generate unique IDs for each diagram

✅ **Cloud Infrastructure**
- API Gateway → Lambda endpoints
- Lambda Python functions (minimal, modular)
- DynamoDB for chat storage
- S3 for diagram storage (markdown + PNG)
- CloudFront for frontend CDN
- VPC, IAM roles, Security groups

✅ **Infrastructure-as-Code**
- Complete Terraform code
- Modular structure
- Environment variables
- Easy one-command deployment

## Nice-to-Have (Try But Don't Block)

⭐ **Interactive Canvas**
- Zoom, pan, drag capabilities with React Flow
- Edit diagram nodes (stretch goal)

⭐ **Diagram Download**
- Download as PNG
- Download as Mermaid markdown

⭐ **Multiple Diagram Types in One Prompt**
- "Project" mode generates multiple diagram types
- Feature: Dropdown to select specific types

---

# 🏗️ DETAILED ARCHITECTURE

## Frontend Stack

```
React 18 + TypeScript
├─ React Flow (diagram rendering)
├─ Axios (API calls)
├─ TailwindCSS (styling)
├─ react-markdown (display markdown)
├─ html2canvas + jspdf (download diagrams)
└─ zustand (state management - optional, simple is better)
```

## Backend Stack

```
Python 3.11 (Lambda)
├─ aws-lambda-powertools (structured logging)
├─ boto3 (AWS SDK)
├─ anthropic (Claude API)
├─ mermaid-js (diagram rendering to PNG)
├─ json (for data handling)
└─ uuid (for unique IDs)
```

## Cloud Services (5 Total)

1. **API Gateway** - REST API routing
2. **Lambda** - Backend compute
3. **DynamoDB** - Chat history storage
4. **S3** - Diagram storage (markdown + images)
5. **CloudFront** - Frontend CDN

## Infrastructure-as-Code

```
Terraform 1.5+
├─ variables.tf (input variables)
├─ main.tf (VPC, networking)
├─ api_gateway.tf (API Gateway)
├─ lambda.tf (Lambda functions)
├─ dynamodb.tf (DynamoDB table)
├─ s3.tf (S3 buckets)
├─ cloudfront.tf (CDN)
├─ iam.tf (IAM roles/policies)
├─ outputs.tf (output values)
└─ terraform.tfvars (configuration)
```

---

# 📊 DATABASE SCHEMA

## DynamoDB Table: `chat_history`

```
PrimaryKey: chatId (GUID)
SortKey: timestamp (unix timestamp)

Attributes:
{
  "chatId": "uuid-1234",
  "timestamp": 1702564800,
  "userMessage": "Create a microservices architecture",
  "diagramType": "flowchart",  // "flowchart", "erdiagram", "sequence", etc.
  "aiResponse": "```mermaid\ngraph TD...",
  "diagramMermaidCode": "graph TD...",
  "diagramImageS3Key": "diagrams/uuid-1234.png",
  "diagramMarkdownS3Key": "diagrams/uuid-1234.md",
  "status": "completed"  // "pending", "completed", "failed"
}
```

## S3 Bucket Structure

```
s3://architecture-ai-bucket/
├─ diagrams/
│  ├─ {diagram-id}.md (Mermaid code as markdown)
│  ├─ {diagram-id}.png (Rendered diagram image)
│  ├─ {diagram-id}.mermaid (Raw Mermaid syntax)
│  └─ ...
├─ frontend/
│  ├─ index.html
│  ├─ js/
│  │  └─ main.js
│  ├─ css/
│  │  └─ styles.css
│  └─ assets/
└─ uploads/
   └─ (if user uploads files)
```

---

# 🔌 API SPECIFICATION

## Endpoint 1: Generate Diagram

```
POST /api/diagram/generate
Content-Type: application/json

Request Body:
{
  "userPrompt": "Create a microservices architecture for e-commerce",
  "diagramType": "flowchart",  // "flowchart", "erdiagram", "sequence", "class", "state", "architecture", "dfd"
  "includeExplanation": true
}

Response (200 OK):
{
  "chatId": "uuid-1234",
  "timestamp": 1702564800,
  "userPrompt": "Create a microservices...",
  "diagramType": "flowchart",
  "mermaidCode": "graph TD\n  A[User] --> B[API]...",
  "imageUrl": "https://cloudfront-url/diagrams/uuid-1234.png",
  "markdownUrl": "https://cloudfront-url/diagrams/uuid-1234.md",
  "explanation": "This diagram shows...",
  "status": "completed"
}

Response (400 Bad Request):
{
  "error": "Invalid diagram type"
}

Response (500 Server Error):
{
  "error": "Failed to generate diagram"
}
```

## Endpoint 2: Get Chat History

```
GET /api/chat/history?limit=50

Response (200 OK):
{
  "chats": [
    {
      "chatId": "uuid-1234",
      "timestamp": 1702564800,
      "userPrompt": "Create a...",
      "diagramType": "flowchart",
      "mermaidCode": "graph TD...",
      "imageUrl": "https://...",
      "status": "completed"
    },
    ...
  ],
  "count": 15,
  "nextToken": "xyz"  // for pagination
}
```

## Endpoint 3: Save Chat Message

```
POST /api/chat/save
Content-Type: application/json

Request Body:
{
  "chatId": "uuid-1234",
  "userMessage": "Create a...",
  "diagramType": "flowchart"
}

Response (200 OK):
{
  "success": true,
  "chatId": "uuid-1234",
  "timestamp": 1702564800
}
```

## Endpoint 4: Download Diagram

```
GET /api/diagram/{diagramId}/download?format=png
  // format: "png", "markdown", "mermaid"

Response (200 OK):
Content-Type: image/png  // or text/markdown
[Binary image data or markdown text]
```

---

# 💻 FRONTEND SPECIFICATIONS

## Page Layout

```
┌─────────────────────────────────────────────────┐
│  Software Architecture AI Assistant              │
├─────────────────────────────────────────────────┤
│                                                 │
│  Diagram Type: [Dropdown Menu ▼]                │
│  ├─ Flowchart (default)                         │
│  ├─ ERD Diagram                                 │
│  ├─ Sequence Diagram                            │
│  ├─ Class Diagram                               │
│  ├─ State Diagram                               │
│  ├─ Architecture (High-Level)                   │
│  ├─ DFD (Data Flow)                             │
│  └─ Project (All diagrams)                      │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  CHAT MESSAGES AREA:                            │
│  ┌─────────────────────────────────────────┐   │
│  │ You: Create a microservices architecture│   │
│  │                                          │   │
│  │ AI: Here's a microservices diagram...   │   │
│  │                                          │   │
│  │ [Mermaid Code Preview]:                  │   │
│  │ ```mermaid                               │   │
│  │ graph TD                                 │   │
│  │   A[API Gateway]                         │   │
│  │   B[User Service]                        │   │
│  │   ...                                    │   │
│  │ ```                                      │   │
│  │                                          │   │
│  │ [Rendered Diagram]:                      │   │
│  │ ┌─────────────────────────────────────┐ │   │
│  │ │  [Interactive Diagram with boxes]   │ │   │
│  │ │  - Can zoom, pan                    │ │   │
│  │ │  - Draggable nodes (optional)       │ │   │
│  │ │  - Auto-layout                      │ │   │
│  │ └─────────────────────────────────────┘ │   │
│  │                                          │   │
│  │ [Download Options]:                      │   │
│  │ [Download PNG] [Download Markdown]      │   │
│  │                                          │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
├─────────────────────────────────────────────────┤
│ INPUT AREA:                                     │
│ ┌────────────────────────────────────────────┐ │
│ │ Type your prompt here...                  │ │
│ │ (e.g., "Create a C4 diagram for...")      │ │
│ └────────────────────────────────────────────┘ │
│ [Generate] [Clear Chat]                        │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Component Hierarchy

```
<App>
  ├─ <Header>
  │  └─ Title + Info
  ├─ <DiagramTypeSelector>
  │  └─ Dropdown with diagram types
  ├─ <ChatContainer>
  │  ├─ <ChatMessages>
  │  │  ├─ <UserMessage>
  │  │  └─ <AIMessage>
  │  │     ├─ <MermaidCodePreview>
  │  │     ├─ <DiagramRenderer> (React Flow)
  │  │     └─ <DownloadButtons>
  │  └─ <ChatInput>
  │     ├─ <TextInput>
  │     └─ <SendButton>
  └─ <LoadingIndicator>
```

## Key Features

- **Messages display as they come in** (pseudo real-time with polling)
- **Code syntax highlighting** for Mermaid code
- **Responsive design** (mobile-friendly)
- **Local state** for chat (no page reload persistence yet - just current session)
- **Error handling** with user-friendly messages
- **Loading states** with spinner

---

# 🐍 BACKEND SPECIFICATIONS

## Lambda Function 1: `generate_diagram`

```python
Handler: lambda_function.handler
Timeout: 60 seconds
Memory: 512 MB
Environment Variables:
  - CLAUDE_API_KEY (from Secrets Manager or passed)
  - MERMAID_SERVER_URL (or use npm package)
  - S3_BUCKET_NAME
  - DYNAMODB_TABLE_NAME

Input:
{
  "userPrompt": "string",
  "diagramType": "string"
}

Process:
1. Validate input
2. Call Claude API with prompt + diagram type context
3. Extract Mermaid code from response
4. Render Mermaid to PNG (using mermaid-cli or mermaid.js)
5. Upload PNG to S3
6. Upload Markdown to S3
7. Save to DynamoDB
8. Return response with URLs

Output:
{
  "chatId": "uuid",
  "mermaidCode": "...",
  "imageUrl": "...",
  "markdownUrl": "...",
  "status": "completed"
}
```

## Lambda Function 2: `save_chat`

```python
Handler: chat_handler.save_message
Timeout: 10 seconds
Memory: 256 MB

Input:
{
  "chatId": "uuid",
  "userMessage": "string",
  "diagramType": "string"
}

Process:
1. Generate UUID if needed
2. Get current timestamp
3. Put item in DynamoDB
4. Return confirmation

Output:
{
  "success": true,
  "chatId": "uuid",
  "timestamp": 1234567890
}
```

## Lambda Function 3: `get_chat_history`

```python
Handler: chat_handler.get_history
Timeout: 10 seconds
Memory: 256 MB

Input:
{
  "limit": 50,
  "nextToken": "optional"
}

Process:
1. Query DynamoDB table
2. Sort by timestamp DESC
3. Paginate results
4. Return messages

Output:
{
  "chats": [...],
  "count": 15,
  "nextToken": "..."
}
```

## Python Dependencies (Lambda Layer)

```
boto3==1.26.137
anthropic==0.7.0
requests==2.31.0
mermaid==0.0.2 (or use mermaid-cli via subprocess)
Pillow==10.0.0 (for image processing)
```

---

# 🔒 SECURITY & IAM

## Lambda Execution Role Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/chat_history"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::architecture-ai-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": "logs:*",
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:*:*:secret:claude-api-key"
    }
  ]
}
```

## API Gateway CORS

```
Allow Origins: *  (for development, restrict in production)
Allow Methods: GET, POST, OPTIONS
Allow Headers: Content-Type, Authorization
```

---

# 📦 DEPLOYMENT STRUCTURE

## Repository Structure

```
project-root/
├── README.md (deployment instructions)
├── infrastructure/
│  ├── terraform/
│  │  ├── main.tf
│  │  ├── variables.tf
│  │  ├── outputs.tf
│  │  ├── api_gateway.tf
│  │  ├── lambda.tf
│  │  ├── dynamodb.tf
│  │  ├─── s3.tf
│  │  ├── cloudfront.tf
│  │  ├── iam.tf
│  │  ├── vpc.tf
│  │  ├── terraform.tfvars
│  │  └── .tfignore
│  └── scripts/
│     ├── deploy.sh (one-command deploy)
│     ├── destroy.sh (cleanup)
│     └── setup.sh (initial setup)
│
├── backend/
│  ├── lambda_functions/
│  │  ├── generate_diagram/
│  │  │  ├── lambda_function.py
│  │  │  ├── requirements.txt
│  │  │  └── mermaid_renderer.py
│  │  ├── chat_crud/
│  │  │  ├── lambda_function.py
│  │  │  └── requirements.txt
│  │  └── get_history/
│  │     ├── lambda_function.py
│  │     └── requirements.txt
│  ├── shared/
│  │  ├── constants.py
│  │  ├── utils.py
│  │  └── aws_helpers.py
│  └── lambda_layer/
│     └── python/
│        └── requirements.txt
│
├── frontend/
│  ├── public/
│  │  ├── index.html
│  │  └── favicon.ico
│  ├── src/
│  │  ├── App.tsx
│  │  ├── App.css
│  │  ├── components/
│  │  │  ├── ChatContainer.tsx
│  │  │  ├── ChatMessage.tsx
│  │  │  ├── DiagramRenderer.tsx
│  │  │  ├── DiagramTypeSelector.tsx
│  │  │  ├── ChatInput.tsx
│  │  │  └── Header.tsx
│  │  ├── pages/
│  │  │  └── ChatPage.tsx
│  │  ├── services/
│  │  │  └── api.ts (Axios service)
│  │  ├── types/
│  │  │  └── index.ts
│  │  ├── utils/
│  │  │  ├── mermaidParser.ts
│  │  │  └── downloadHelper.ts
│  │  └── index.tsx
│  ├── package.json
│  ├── tsconfig.json
│  ├── tailwind.config.js
│  └── .gitignore
│
└── docs/
   ├── ARCHITECTURE.md
   ├── DEPLOYMENT.md
   ├── API.md
   └── TROUBLESHOOTING.md
```

---

# 🚀 DEPLOYMENT INSTRUCTIONS

## Phase 1: Setup (15 min)

```bash
# 1. Clone/prepare repo
git clone <repo-url>
cd architecture-ai-project

# 2. Install dependencies
cd infrastructure/terraform
terraform init

cd ../../backend
pip install -r lambda_functions/generate_diagram/requirements.txt

cd ../frontend
npm install

# 3. Set environment variables
export AWS_REGION=us-east-1
export AWS_PROFILE=default
export CLAUDE_API_KEY=your-api-key
export S3_BUCKET_NAME=architecture-ai-bucket
export DYNAMODB_TABLE=chat_history
```

## Phase 2: Deploy Infrastructure (20 min)

```bash
cd infrastructure/terraform

# Review plan
terraform plan

# Deploy
terraform apply -auto-approve

# Get outputs
terraform output api_gateway_url
terraform output cloudfront_url
terraform output dynamodb_table_name
```

## Phase 3: Deploy Backend (10 min)

```bash
cd backend

# Package Lambda functions
./scripts/package_lambda.sh

# Deploy via Terraform (included)
terraform apply -auto-approve
```

## Phase 4: Deploy Frontend (10 min)

```bash
cd frontend

# Build React app
npm run build

# Deploy to S3
aws s3 sync build/ s3://architecture-ai-bucket/frontend/ \
  --delete --cache-control max-age=31536000

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --paths "/*"
```

## One-Command Deploy Script

```bash
#!/bin/bash
# ./scripts/deploy.sh

set -e

echo "🚀 Deploying Architecture AI Assistant..."

# 1. Infrastructure
echo "1️⃣ Deploying infrastructure..."
cd infrastructure/terraform
terraform init
terraform apply -auto-approve
OUTPUTS=$(terraform output -json)
cd ../..

# 2. Backend
echo "2️⃣ Deploying backend..."
cd backend
./scripts/package_lambda.sh
cd ..

# 3. Frontend
echo "3️⃣ Building frontend..."
cd frontend
npm install
npm run build
cd ..

# 4. Upload frontend
echo "4️⃣ Uploading frontend to S3..."
BUCKET=$(echo $OUTPUTS | jq -r '.s3_bucket_name.value')
DISTRO=$(echo $OUTPUTS | jq -r '.cloudfront_distribution_id.value')
aws s3 sync frontend/build/ s3://$BUCKET/frontend/ --delete
aws cloudfront create-invalidation --distribution-id $DISTRO --paths "/*"

# 5. Display outputs
echo ""
echo "✅ Deployment complete!"
echo "Frontend URL: $(echo $OUTPUTS | jq -r '.cloudfront_url.value')"
echo "API Gateway: $(echo $OUTPUTS | jq -r '.api_gateway_url.value')"
echo ""
```

---

# 📝 CLAUDE SONNET AGENTIC CODING PROMPT

**Copy this prompt exactly for Claude Sonnet to generate the project:**

---

## CLAUDE AGENTIC PROMPT (START HERE)

```
You are an expert cloud architect and full-stack developer. 
Generate COMPLETE, PRODUCTION-READY code for a Software Architecture 
AI Assistant deployed on AWS.

PROJECT REQUIREMENTS:
- Timeline: MAXIMUM 2 days from code generation to live deployment
- Focus: 80% Cloud Infrastructure, 20% AI Features
- Must be SIMPLE, WORKING, DEPLOYABLE with ONE COMMAND
- NO complex debugging or optional features

ARCHITECTURE:
- Frontend: React SPA on S3 + CloudFront
- Backend: Python Lambda functions (modular)
- Database: DynamoDB for chat history
- Storage: S3 for diagrams (markdown + PNG)
- API: API Gateway + Lambda
- IaC: Terraform for everything

USER FLOW:
1. User opens single-page chat application
2. Selects diagram type from dropdown (flowchart, ERD, sequence, etc.)
3. Types prompt: "Create microservices architecture"
4. Sends to Lambda via API Gateway
5. Lambda calls Claude AI with diagram generation prompt
6. Claude returns Mermaid diagram code
7. Lambda renders Mermaid to PNG
8. Both PNG and Mermaid markdown saved to S3
9. Chat history saved to DynamoDB
10. Frontend displays:
    - Chat message
    - Mermaid code (syntax highlighted)
    - Rendered diagram (React Flow with zoom/pan)
    - Download buttons for PNG and markdown

MUST GENERATE:

1. TERRAFORM CODE (Infrastructure-as-Code)
   - All AWS resources defined in Terraform
   - Modular structure (.tf files for each service)
   - Easy one-command deployment
   - Outputs for API Gateway, CloudFront, S3, DynamoDB
   - IAM roles with minimal required permissions
   - Security groups and VPC setup
   - Environment variable management
   - deploy.sh script for one-command deployment

2. BACKEND CODE (Python Lambda)
   - lambda_functions/generate_diagram/lambda_function.py
     * Call Claude API with prompt
     * Generate Mermaid diagram code
     * Render to PNG
     * Save to S3 (both .md and .png)
     * Save to DynamoDB
     * Return response
   - lambda_functions/chat_crud/lambda_function.py
     * Save chat messages to DynamoDB
     * Get chat history from DynamoDB
     * Pagination support
   - shared utilities for AWS SDK operations
   - requirements.txt for all dependencies
   - Minimal, simple, no over-engineering

3. FRONTEND CODE (React)
   - src/App.tsx (main component)
   - src/components/ChatContainer.tsx
   - src/components/ChatMessage.tsx
   - src/components/DiagramRenderer.tsx (React Flow integration)
   - src/components/DiagramTypeSelector.tsx (dropdown)
   - src/components/ChatInput.tsx
   - src/services/api.ts (Axios API calls)
   - src/types/index.ts (TypeScript types)
   - public/index.html (single HTML file)
   - Tailwind CSS for styling
   - React Flow for diagram rendering
   - package.json with all dependencies
   - npm build script ready for S3 deployment

4. DOCUMENTATION
   - README.md with deployment steps
   - ARCHITECTURE.md explaining the system
   - API.md documenting endpoints
   - TROUBLESHOOTING.md for common issues

CRITICAL CONSTRAINTS:
✅ Simple and working > fancy but broken
✅ One-command deploy (deploy.sh)
✅ No authentication (session-based only)
✅ No complex features that add >1 day to development
✅ Cloud infrastructure is the star (80% focus)
✅ Use Mermaid for diagrams (client-side rendering)
✅ React Flow for interactive rendering
✅ DynamoDB for scalability and simplicity
✅ S3 for indefinite storage
✅ Lambda for serverless simplicity
✅ Terraform for IaC mastery

DIAGRAM TYPES SUPPORTED:
- Flowchart (default, required)
- ERD Diagram (required)
- Sequence Diagram (required)
- Class Diagram (nice-to-have)
- State Diagram (nice-to-have)
- Architecture (High-Level) (required)
- DFD (Data Flow Diagram) (nice-to-have)

IF FEATURE ADDS >1 DAY → SKIP IT
This is a final project, not production app.

GENERATE EVERYTHING NEEDED TO:
1. Run terraform apply → Full infrastructure deployed
2. Deploy frontend → npm run build → S3 upload
3. Open CloudFront URL → Working chat application
4. Type prompt → Get diagram back
5. Download diagram → Works perfectly

NO ASSUMPTIONS - Complete, working, tested code only.

TIME BUDGET:
- Terraform code: 2 hours
- Backend code: 3 hours
- Frontend code: 3 hours
- Documentation: 1 hour
- Buffer: 7 hours
TOTAL: 16 hours (exactly 2 days)

START CODING NOW. Generate everything as complete files.
File by file. Function by function. Complete.

BEGIN WITH:
1. Architecture diagram (ASCII or Mermaid)
2. File structure
3. Terraform code (first priority - infrastructure is the star)
4. Backend code
5. Frontend code
6. Deployment scripts
7. Documentation

GO!
```

---

# ⚡ QUICK START (After Claude Generates Code)

## Step 1: Prepare AWS Account (5 min)

```bash
# Create AWS account (if not exists)
# Enable programmatic access
# Generate AWS credentials

aws configure
# Enter: AWS Access Key ID
# Enter: AWS Secret Access Key
# Enter: Default region (us-east-1)
# Enter: Default output format (json)

# Verify credentials
aws sts get-caller-identity
```

## Step 2: Set Environment Variables (5 min)

```bash
export AWS_REGION=us-east-1
export CLAUDE_API_KEY=sk-ant-... (get from Anthropic)
export S3_BUCKET_NAME=architecture-ai-bucket-$(date +%s)
export DYNAMODB_TABLE_NAME=chat_history
```

## Step 3: Deploy Infrastructure (15 min)

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply -auto-approve

# Get outputs
terraform output
```

## Step 4: Deploy Backend (10 min)

```bash
cd backend
./scripts/package_lambda.sh
# (Terraform handles deployment)
```

## Step 5: Deploy Frontend (10 min)

```bash
cd frontend
npm install
npm run build
aws s3 sync build/ s3://$(echo $S3_BUCKET_NAME)/frontend/ --delete
```

## Step 6: Test (5 min)

```bash
# Get CloudFront URL from Terraform output
# Open URL in browser
# Test chat with: "Create a flowchart for user authentication"
# Verify:
#   - Diagram renders
#   - PNG downloaded
#   - Markdown downloaded
#   - Chat saved to DynamoDB
```

---

# 🎓 LEARNING OUTCOMES

By the time you deploy this:

✅ **Terraform & IaC Mastery**
- Define complete AWS infrastructure as code
- Understand modular Terraform
- Deploy with one command

✅ **AWS Services Knowledge**
- API Gateway routing
- Lambda functions
- DynamoDB design
- S3 bucket management
- CloudFront distribution

✅ **Serverless Architecture**
- Stateless Lambda functions
- Event-driven design
- Scalable systems

✅ **Full-Stack Development**
- React modern patterns
- Axios API integration
- Async/await
- Component architecture

✅ **AI Integration**
- Claude API usage
- Prompt engineering
- LLM response parsing

✅ **DevOps & Deployment**
- Infrastructure as Code
- Automated deployments
- CI/CD thinking

---

# 📊 SUCCESS METRICS

✅ You can demo:
- Chat interface working
- Diagram generation working
- Diagrams rendering in frontend
- Download PNG/Markdown working
- Chat history persistent
- Live CloudFront URL

✅ Infrastructure:
- 5 AWS services integrated
- Terraform code clean and modular
- One-command deployment
- Zero manual setup

✅ Learning:
- You understand Terraform
- You understand Lambda
- You understand AWS architecture
- You can explain the system to your professor

---

# 🔧 TROUBLESHOOTING QUICK REF

| Issue | Solution |
|-------|----------|
| Lambda timeout | Increase timeout to 60s, check Mermaid rendering time |
| CORS error | Add `*` to API Gateway CORS |
| Mermaid not rendering | Check npm package version, use mermaid-js client-side |
| S3 access denied | Check IAM role permissions |
| CloudFront not updating | Invalidate cache with CloudFront invalidation |
| DynamoDB item too large | Compress image, store reference only |
| API call fails | Check API Gateway URL, check CORS headers |

---

## 🎯 YOUR NEXT STEP

**Paste the CLAUDE AGENTIC PROMPT above into Claude Sonnet Opus 4.5 and request:**

```
"Generate the COMPLETE Software Architecture AI Assistant project with:
1. Full Terraform infrastructure code
2. Complete Python Lambda backend
3. Complete React frontend
4. Deployment script
5. Documentation

Make it simple, working, deployable in 2 days. 
Focus on INFRASTRUCTURE as the star feature.
Provide EVERY FILE needed - no placeholders."
```

Then Claude will generate everything. Copy files, run deploy.sh, and go live! 🚀

---

**Specification Version**: 2.0  
**Date**: December 15, 2025  
**Status**: Ready for Claude Sonnet Agentic Coding  
**Timeline**: 2 days to live deployment  
**Goal**: ✅ SIMPLE + WORKING + CLOUD-NATIVE  
