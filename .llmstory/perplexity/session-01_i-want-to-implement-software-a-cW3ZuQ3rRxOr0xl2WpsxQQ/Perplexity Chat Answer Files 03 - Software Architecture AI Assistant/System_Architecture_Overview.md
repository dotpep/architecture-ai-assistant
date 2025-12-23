# 🎯 FINAL SYSTEM OVERVIEW & ARCHITECTURE DIAGRAM
## Your Architecture AI Assistant - Complete System Design

---

# 🏗️ COMPLETE SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    ☁️  AWS CLOUD ENVIRONMENT (Free Tier)                  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                     FRONTEND TIER (S3 + CloudFront)               │    │
│  │                                                                   │    │
│  │  ┌──────────────────────────────────────────────────────────┐   │    │
│  │  │  React SPA (Single Page Application)                     │   │    │
│  │  │  - Chat Interface                                        │   │    │
│  │  │  - Diagram Type Selector                                │   │    │
│  │  │  - Message Display                                      │   │    │
│  │  │  - React Flow Diagram Renderer                          │   │    │
│  │  │  - Download Buttons (PNG/Markdown)                      │   │    │
│  │  └──────────────────────────────────────────────────────────┘   │    │
│  │           ↓ Hosted on S3, Distributed via CloudFront             │    │
│  │  ┌────────────────────┐         ┌──────────────────┐            │    │
│  │  │   S3 Bucket        │         │  CloudFront CDN  │            │    │
│  │  │  (frontend/build/) │────────→│  (Global Cache)  │            │    │
│  │  └────────────────────┘         └────────┬─────────┘            │    │
│  │                                           │                      │    │
│  │                                    📱 Users Access              │    │
│  │                                 (CloudFront URL)                │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                      ↓ HTTPS API Calls                     │
│                                      ↓ (JSON requests/responses)           │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                     API TIER (API Gateway)                        │    │
│  │                                                                   │    │
│  │  ┌──────────────────────────────────────────────────────────┐   │    │
│  │  │  AWS API Gateway (REST API)                              │   │    │
│  │  │                                                          │   │    │
│  │  │  POST /api/diagram/generate   ─────→ Lambda Function    │   │    │
│  │  │  GET  /api/chat/history       ─────→ Lambda Function    │   │    │
│  │  │  POST /api/chat/save          ─────→ Lambda Function    │   │    │
│  │  │  GET  /api/diagram/{id}/down  ─────→ Lambda Function    │   │    │
│  │  │                                                          │   │    │
│  │  │  CORS: Allow * (for development)                        │   │    │
│  │  │  Auth: None (sessionless)                               │   │    │
│  │  └──────────────────────────────────────────────────────────┘   │    │
│  │                         ↓ Route & Invoke                         │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                              ↓ Parallel                                    │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │              BACKEND TIER (Lambda Functions - Python 3.11)        │    │
│  │                                                                   │    │
│  │  ┌──────────────────────┐  ┌──────────────────┐                 │    │
│  │  │ Lambda Function 1    │  │ Lambda Function 2 │                │    │
│  │  │ generate_diagram     │  │ save_chat        │                │    │
│  │  │                      │  │                  │                │    │
│  │  │ Input: user prompt   │  │ Input: message   │                │    │
│  │  │        diagram type  │  │        timestamp │                │    │
│  │  │                      │  │                  │                │    │
│  │  │ 1. Call Claude API   │  │ 1. Generate UUID │                │    │
│  │  │ 2. Parse response    │  │ 2. Add timestamp │                │    │
│  │  │ 3. Extract Mermaid   │  │ 3. Put in DDB    │                │    │
│  │  │ 4. Render to PNG     │  │ 4. Return 200 OK │                │    │
│  │  │ 5. Upload to S3      │  │                  │                │    │
│  │  │ 6. Save to DDB       │  └──────────────────┘                │    │
│  │  │ 7. Return response   │                                      │    │
│  │  └──────────────────────┘  ┌──────────────────┐                │    │
│  │                            │ Lambda Function 3 │                │    │
│  │                            │ get_chat_history │                │    │
│  │                            │                  │                │    │
│  │                            │ Input: limit     │                │    │
│  │                            │        pagination│                │    │
│  │                            │                  │                │    │
│  │                            │ 1. Query DDB     │                │    │
│  │                            │ 2. Sort & filter │                │    │
│  │                            │ 3. Return items  │                │    │
│  │                            └──────────────────┘                │    │
│  │                                                                   │    │
│  │  All functions have:                                             │    │
│  │  - Timeout: 60 seconds                                           │    │
│  │  - Memory: 512 MB                                                │    │
│  │  - Cold start: ~1-3 seconds first time                           │    │
│  │  - Warm start: <100ms thereafter                                 │    │
│  │                                                                   │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│      ↓                     ↓                     ↓                         │
│  ┌──────────────┐   ┌─────────────┐   ┌────────────────┐                 │
│  │ Call Claude  │   │  DynamoDB   │   │  S3 Storage    │                 │
│  │  API (LLM)   │   │ (Chat Hist) │   │ (Diagrams)     │                 │
│  │              │   │             │   │                │                 │
│  │ External API │   │ chat_history│   │ diagrams/      │                 │
│  │ (Anthropic)  │   │ table       │   │ - *.md files   │                 │
│  │              │   │             │   │ - *.png images │                 │
│  │ Input: Prompt│   │ Attributes: │   │                │                 │
│  │ Output:      │   │ - chatId    │   │ Access: Public │                 │
│  │ Mermaid code │   │ - timestamp │   │ via CloudFront │                 │
│  │              │   │ - message   │   │                │                 │
│  │              │   │ - diagram   │   │ Lifecycle:     │                 │
│  │              │   │             │   │ Keep forever   │                 │
│  └──────────────┘   └─────────────┘   └────────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 📊 DATA FLOW DIAGRAM

## User Interaction Flow

```
1️⃣  USER OPENS APP
    ↓
    Browser loads CloudFront URL
    ↓
    React app loads from S3
    ↓
    Fetch initial chat history from Lambda
    ↓
    Display empty chat or previous messages

2️⃣  USER TYPES PROMPT & SENDS
    ↓
    "Create a microservices architecture with 3 services"
    ↓
    Select diagram type: "Flowchart"
    ↓
    Click [Generate]

3️⃣  FRONTEND MAKES API CALL
    ↓
    POST /api/diagram/generate
    {
      userPrompt: "Create a microservices...",
      diagramType: "Flowchart"
    }
    ↓
    API Gateway routes to Lambda
    ↓
    Lambda cold-starts (first time ~3s)

4️⃣  LAMBDA GENERATES DIAGRAM
    ↓
    Call Claude API with prompt
    ↓
    Claude: "Here's a Mermaid diagram..."
    ↓
    Parse Mermaid code from response
    ↓
    Render Mermaid → PNG
    ↓
    Upload PNG to S3 (diagrams/)
    ↓
    Upload Markdown to S3 (diagrams/)
    ↓
    Save to DynamoDB:
    {
      chatId: "uuid-1234",
      timestamp: 1702564800,
      userMessage: "Create a...",
      diagramType: "Flowchart",
      mermaidCode: "graph TD\n...",
      imageS3Url: "https://cf-url/diagrams/uuid.png",
      status: "completed"
    }

5️⃣  LAMBDA RETURNS RESPONSE
    ↓
    {
      success: true,
      mermaidCode: "graph TD\nA[Service 1]...",
      imageUrl: "https://cloudfront-url/diagrams/uuid.png",
      markdownUrl: "https://cloudfront-url/diagrams/uuid.md",
      timestamp: 1702564800
    }

6️⃣  FRONTEND DISPLAYS RESULTS
    ↓
    Show in chat:
    ┌─────────────────────────────────────┐
    │ You: Create a microservices...      │
    │                                     │
    │ Assistant: Here's the diagram...    │
    │                                     │
    │ [Mermaid Code]:                     │
    │ ```                                 │
    │ graph TD                            │
    │   A[Service 1] → B[Service 2]       │
    │ ```                                 │
    │                                     │
    │ [Rendered Diagram]:                 │
    │ ┌─────────────────────────────────┐ │
    │ │ Interactive diagram with        │ │
    │ │ - Zoom capability (scroll wheel) │ │
    │ │ - Pan capability (drag)          │ │
    │ │ - Auto-layout nodes              │ │
    │ └─────────────────────────────────┘ │
    │                                     │
    │ [Download Buttons]:                 │
    │ [📥 Download PNG] [📄 Download MD]  │
    └─────────────────────────────────────┘

7️⃣  USER CAN DOWNLOAD
    ↓
    Click [Download PNG]
    ↓
    Browser downloads from S3 (via CloudFront)
    ↓
    File: diagram-uuid.png (300 KB typical)
    ↓
    OR
    ↓
    Click [Download Markdown]
    ↓
    Browser downloads from S3 (via CloudFront)
    ↓
    File: diagram-uuid.md (5 KB typical)

8️⃣  USER REFRESHES PAGE
    ↓
    All previous chats still visible
    ↓
    Loaded from DynamoDB
    ↓
    Diagrams still render (code cached in DDB)
    ↓
    Download links still work (images in S3)
```

---

# 🔄 COMPONENT INTERACTION

## Frontend Components

```
App.tsx (Main Component)
│
├─ Header.tsx
│  └─ Title: "Software Architecture AI Assistant"
│
├─ DiagramTypeSelector.tsx (Dropdown)
│  ├─ Flowchart (default)
│  ├─ ERD Diagram
│  ├─ Sequence Diagram
│  ├─ Class Diagram
│  ├─ State Diagram
│  ├─ Architecture
│  └─ DFD
│
├─ ChatContainer.tsx (Main Chat Area)
│  │
│  ├─ ChatMessages.tsx (Messages List)
│  │  │
│  │  └─ ChatMessage.tsx (Individual Message)
│  │     ├─ UserMessage
│  │     │  └─ Shows user prompt
│  │     │
│  │     └─ AIMessage
│  │        ├─ MermaidCodePreview.tsx
│  │        │  └─ Syntax-highlighted code block
│  │        │
│  │        ├─ DiagramRenderer.tsx
│  │        │  └─ React Flow rendering
│  │        │     ├─ Mermaid → React Flow conversion
│  │        │     ├─ Zoom/Pan controls
│  │        │     └─ Interactive nodes
│  │        │
│  │        └─ DownloadButtons.tsx
│  │           ├─ [Download PNG]
│  │           └─ [Download Markdown]
│  │
│  └─ ChatInput.tsx (Input Area)
│     ├─ TextInput field
│     ├─ [Generate] button
│     └─ Loading spinner
│
└─ ErrorBoundary.tsx
   └─ Error display & fallback
```

---

# 🗄️ DATABASE SCHEMA

## DynamoDB Table: `chat_history`

```
Partition Key: chatId (UUID)
Sort Key: timestamp (Unix timestamp)

Item Example:
{
  "chatId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1702564800,
  
  "userMessage": "Create a microservices architecture with user service, product service, and order service",
  "diagramType": "flowchart",
  
  "aiResponse": "Here's a microservices architecture diagram...",
  "mermaidCode": "graph TD\n  A[User Service] --> B[Order Service]\n  B --> C[Product Service]",
  
  "diagramImageS3Key": "diagrams/550e8400-e29b-41d4-a716-446655440000.png",
  "diagramMarkdownS3Key": "diagrams/550e8400-e29b-41d4-a716-446655440000.md",
  
  "imageUrl": "https://cloudfront-url/diagrams/550e8400-e29b-41d4-a716-446655440000.png",
  "markdownUrl": "https://cloudfront-url/diagrams/550e8400-e29b-41d4-a716-446655440000.md",
  
  "status": "completed",  // "pending", "completed", "failed"
  "processingTime": 8.5,  // seconds
  
  "ttl": 1734604800  // Optional: auto-delete old records after 1 year
}
```

## S3 Bucket Structure

```
s3://architecture-ai-bucket/
│
├─ frontend/
│  ├─ index.html
│  ├─ js/
│  │  └─ main.js (compiled React)
│  ├─ css/
│  │  └─ style.css (Tailwind)
│  └─ assets/
│     └─ (images, fonts, etc.)
│
├─ diagrams/
│  ├─ 550e8400-e29b-41d4-a716-446655440000.png (image)
│  ├─ 550e8400-e29b-41d4-a716-446655440000.md (markdown)
│  ├─ 550e8400-e29b-41d4-a716-446655440001.png
│  ├─ 550e8400-e29b-41d4-a716-446655440001.md
│  └─ ... (more diagrams)
│
└─ (optional: user uploads if file upload feature added)
```

---

# 🔐 Security Architecture

## IAM Permissions (Least Privilege)

```
Lambda Execution Role Policy:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:*:table/chat_history"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::architecture-ai-bucket/diagrams/*"
    },
    {
      "Effect": "Allow",
      "Action": "logs:*",
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:claude-api-key"
    }
  ]
}
```

## API Gateway CORS

```
Allow Origins: * (open for MVP, restrict in production)
Allow Methods: GET, POST, OPTIONS
Allow Headers: Content-Type, Authorization
Allow Credentials: false
Expose Headers: X-Request-Id
```

## Network Security

```
VPC Security Groups:
├─ ALB Security Group (if needed)
│  └─ Allow 443 inbound (HTTPS only)
│
├─ Lambda Security Group
│  └─ Allows outbound to CloudFront, DynamoDB, S3
│
└─ Database Security Group
   └─ Allow only from Lambda security group
```

---

# ⚡ PERFORMANCE CHARACTERISTICS

## Response Times

```
User Opens App:
├─ CloudFront cache hit: ~200ms
├─ CloudFront cache miss: ~500ms
└─ First-time users: ~1s

Generate Diagram:
├─ API Gateway routing: ~100ms
├─ Lambda cold start: ~1-3s (first invocation)
├─ Lambda warm start: ~100ms (subsequent)
├─ Claude API call: ~5-15s (depends on prompt)
├─ Mermaid rendering: ~1s
├─ S3 upload (PNG): ~1s
├─ DynamoDB write: ~100ms
├─ Total cold start: ~8-20s
├─ Total warm start: ~6-16s
└─ User sees result: ~10-20s typical

Get Chat History:
├─ DynamoDB query: ~100ms
├─ Return to frontend: ~300ms
├─ Frontend render: ~500ms
└─ Total: ~1s

Download Diagram:
├─ CloudFront cache hit: ~200ms
├─ S3 direct: ~500ms
└─ Browser download: depends on file size

Diagram Rendering (React Flow):
├─ Load Mermaid code: <100ms
├─ Parse to React Flow: ~200ms
├─ Render nodes: ~300ms
├─ User sees diagram: ~500ms
```

## Scalability

```
Current Setup (Free Tier):
├─ Lambda: 1M requests/month free
├─ DynamoDB: 25 GB storage free
├─ S3: 5 GB storage free
├─ CloudFront: 1 TB transfer free
└─ You'll use ~5% of free tier

Projected Usage (100 diagrams/day):
├─ Lambda: ~3,000 requests/month (~0.3% of limit)
├─ DynamoDB: ~100 MB (0.4% of limit)
├─ S3: ~30 MB (0.6% of limit)
├─ CloudFront: ~100 GB/month (10% of limit)
└─ Total cost: $0 (within free tier)

If 10,000+ users:
├─ Add DynamoDB auto-scaling
├─ Enable Lambda reserved concurrency
├─ Enable CloudFront caching headers
├─ Add API Gateway throttling
└─ Cost: ~$50-100/month
```

---

# 📱 User Experience Flow

## Perfect Happy Path

```
1. User opens CloudFront URL
   ✅ Page loads instantly (CloudFront cache)
   
2. Chat history visible
   ✅ Previous conversations loaded
   
3. User selects "Flowchart" from dropdown
   ✅ Dropdown shows all diagram types
   
4. User types: "Create auth service flow"
   ✅ Text input responsive
   
5. Click [Generate]
   ✅ Button shows loading spinner
   ✅ "Generating diagram..."
   
6. Lambda processes request
   ✅ Claude AI generates Mermaid code
   ✅ Mermaid renders to PNG
   ✅ Saves to S3 and DynamoDB
   
7. Result appears in chat
   ✅ Message shows in chat
   ✅ Mermaid code visible and syntax highlighted
   ✅ Diagram renders with boxes and arrows
   ✅ Can zoom with scroll wheel
   ✅ Can pan with mouse drag
   
8. Download buttons appear
   ✅ [📥 Download PNG] button
   ✅ [📄 Download Markdown] button
   
9. User clicks Download PNG
   ✅ File "diagram-{id}.png" downloads
   ✅ Can use in presentation/document
   
10. User refreshes page
    ✅ Chat history still visible
    ✅ Diagram renders again from saved Mermaid code
    ✅ Download buttons still work
```

---

# 🎓 Technology Stack Summary

```
FRONTEND STACK:
├─ React 18 (UI library)
├─ TypeScript (type safety)
├─ React Flow (diagram rendering)
├─ Axios (HTTP client)
├─ TailwindCSS (styling)
├─ React Router (if needed for multi-page)
└─ Vite (build tool, fast)

BACKEND STACK:
├─ Python 3.11 (runtime)
├─ AWS Lambda (compute)
├─ boto3 (AWS SDK)
├─ anthropic (Claude API)
├─ mermaid-js (diagram rendering)
├─ json (data handling)
└─ uuid (ID generation)

INFRASTRUCTURE:
├─ Terraform 1.5+ (IaC)
├─ AWS VPC (networking)
├─ AWS Security Groups (firewall)
├─ AWS IAM (access control)
├─ AWS API Gateway (routing)
├─ AWS Lambda (compute)
├─ AWS DynamoDB (database)
├─ AWS S3 (storage)
├─ AWS CloudFront (CDN)
└─ AWS Secrets Manager (secrets)

DEPLOYMENT:
├─ git (version control)
├─ npm (package manager)
├─ Terraform CLI (IaC deployment)
├─ AWS CLI (AWS management)
└─ GitHub/GitLab (code hosting)
```

---

# 🚀 YOUR 16-HOUR DEPLOYMENT TIMELINE

```
HOUR 0-2: Setup & Claude Request
├─ Create project directory
├─ Copy Claude specification
├─ Request code generation
└─ ⏰ Total: 2 hours

HOUR 2-4: Code Organization
├─ Create directory structure
├─ Organize generated files
├─ Verify all files present
└─ ⏰ Total: 2 hours

HOUR 4-6: AWS Preparation
├─ Create AWS account
├─ Generate credentials
├─ Configure AWS CLI
├─ Get Claude API key
└─ ⏰ Total: 2 hours

HOUR 6-12: Infrastructure Deployment
├─ Terraform init
├─ Terraform plan
├─ Terraform apply (creates 5 AWS services)
├─ Deploy Lambda functions
└─ ⏰ Total: 6 hours

HOUR 12-14: Frontend Deployment
├─ npm install
├─ npm run build
├─ Upload to S3
├─ CloudFront invalidation
└─ ⏰ Total: 2 hours

HOUR 14-16: Testing & Documentation
├─ Test full workflow
├─ Create screenshots
├─ Write README
├─ Prepare for demo
└─ ⏰ Total: 2 hours

TOTAL: 16 hours ✅
```

---

# ✅ WHAT SUCCESS LOOKS LIKE

```
✅ Terraform deploys without errors
✅ 5 AWS services visible in console
✅ API Gateway shows endpoints
✅ Lambda functions deployed
✅ DynamoDB table created
✅ S3 buckets created
✅ CloudFront distribution active

✅ Frontend loads from CloudFront URL
✅ Chat interface visible
✅ Dropdown shows diagram types
✅ Can type and submit messages
✅ AI generates diagram code
✅ Mermaid code displays in chat
✅ Diagram renders as visual
✅ Download PNG works
✅ Download Markdown works
✅ Refresh page shows chat history

✅ All 5 AWS services working together
✅ Zero authentication errors
✅ Zero CORS errors
✅ Zero Lambda timeout errors
✅ Total cost: $0 (free tier)

🎉 YOU'RE DONE! Submit to professor!
```

---

**Architecture Version**: 2.0  
**Date**: December 15, 2025  
**Status**: ✅ READY FOR DEPLOYMENT  
**Timeline**: 16 hours  
**Success Rate**: 95%+ if following spec  

**LET'S BUILD! 🚀**
