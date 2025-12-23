# Architecture AI Assistant

A cloud-native web application that generates software architecture diagrams through natural language conversations with an LLM. Built with AWS serverless architecture and React.

## Overview

The Architecture AI Assistant enables users to:
- Generate architecture diagrams using natural language prompts
- Support multiple diagram types: Flowchart, ERD, Sequence, Class, State, Architecture, DFD
- View diagrams rendered interactively with zoom and pan
- Download diagrams as PNG images or Mermaid markdown
- Manage multiple chat sessions with automatic title generation
- Navigate between different conversation sessions
- Persist chat history with session-based organization

## Architecture

- **Frontend**: React + TypeScript SPA hosted on S3 with CloudFront CDN
- **Backend**: Python Lambda functions behind API Gateway
- **Storage**: DynamoDB for session-based chat history, S3 for diagram files
- **Infrastructure**: Terraform for Infrastructure-as-Code

---
![High Level Architecture](/docs/architecutre-diagram.png)



---
DeepWiki Generated Docs Index: [deepwiki.com/dotpep/architecture-ai-assistant](https://deepwiki.com/dotpep/architecture-ai-assistant)


### Session Management

The application uses a session-based architecture where:
- Each chat session contains multiple message exchanges
- Sessions are automatically titled from the first user message
- The sidebar displays sessions grouped by date (Today, Yesterday, Last 7 Days, Older)
- DynamoDB uses a single-table design with PK/SK pattern for efficient querying
- Session metadata and messages are stored together for optimal performance

## Prerequisites

Before deploying the Architecture AI Assistant, ensure you have the following installed:

### Required Tools

1. **AWS CLI** (v2.x or later)
   - Installation: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
   - Verify: `aws --version`

2. **Terraform** (v1.0 or later)
   - Installation: https://developer.hashicorp.com/terraform/downloads
   - Verify: `terraform --version`

3. **Node.js** (v18.x or later) and npm
   - Installation: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

4. **Python 3** (v3.11 or later) and pip
   - Installation: https://www.python.org/downloads/
   - Verify: `python3 --version` and `pip3 --version`

5. **zip** utility
   - Usually pre-installed on Linux/macOS
   - Windows: Install via Git Bash or WSL

### AWS Account Setup

1. **AWS Account**: You need an active AWS account with appropriate permissions
2. **AWS Credentials**: Configure AWS CLI with your credentials
   ```bash
   aws configure
   ```
   You'll need:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., `us-east-1`)
   - Default output format (e.g., `json`)

3. **IAM Permissions**: Your AWS user/role needs permissions to create:
   - Lambda functions and layers
   - API Gateway REST APIs
   - DynamoDB tables
   - S3 buckets
   - CloudFront distributions
   - IAM roles and policies
   - CloudWatch log groups

   See [IAM_SETUP.md](./infrastructure/docs/IAM_SETUP.md) for detailed permission requirements.

## Environment Variables

### Required Environment Variables

The application requires the following environment variables:

#### LLM API Configuration

Set these in `infrastructure/terraform/terraform.tfvars`:

```hcl
# LLM API Configuration
llm_api_endpoint = "https://api.your-llm-provider.com/v1/chat/completions"
llm_api_key      = "your-api-key-here"

# Project Configuration
project_name = "architecture-ai-assistant"
environment  = "dev"
aws_region   = "us-east-1"
```

**Important**: Never commit `terraform.tfvars` with real API keys to version control. Use `terraform.tfvars.example` as a template.

#### Supported LLM Providers

The application is designed to work with any OpenAI-compatible API endpoint:
- OpenAI GPT-4
- Anthropic Claude (via OpenAI-compatible wrapper)
- Azure OpenAI
- Local LLM servers (Ollama, LM Studio, etc.)

## Deployment

### Quick Start (One-Command Deployment)

The easiest way to deploy the entire application:

```bash
cd infrastructure/scripts
./deploy.sh
```

This script will:
1. Package Lambda functions with dependencies
2. Deploy infrastructure with Terraform
3. Build and upload the frontend to S3
4. Invalidate CloudFront cache

The deployment takes approximately 5-10 minutes.

### Manual Deployment Steps

If you prefer to deploy step-by-step:

#### 1. Configure Terraform Variables

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

#### 2. Package Lambda Functions

```bash
# From project root
cd src/backend/lambda_functions

# Package each function
for func in generate_diagram chat_crud get_history; do
    cd $func
    zip -r ../../../../infrastructure/terraform/${func}.zip .
    cd ..
done
```

#### 3. Deploy Infrastructure

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

Save the outputs - you'll need them for the frontend configuration.

#### 4. Build and Deploy Frontend

```bash
cd src/frontend

# Install dependencies
npm install

# Create .env file with API Gateway URL from Terraform output
echo "VITE_API_BASE_URL=<your-api-gateway-url>" > .env

# Build
npm run build

# Upload to S3 (replace with your bucket name from Terraform output)
aws s3 sync dist/ s3://<your-bucket-name>/frontend/ --delete
```

#### 5. Invalidate CloudFront Cache

```bash
# Replace with your CloudFront distribution ID from Terraform output
aws cloudfront create-invalidation \
    --distribution-id <your-distribution-id> \
    --paths "/*"
```

## Accessing the Application

After deployment, access the application at the CloudFront URL provided in the Terraform outputs:

```bash
cd infrastructure/terraform
terraform output cloudfront_url
```

Example: `https://d1234567890abc.cloudfront.net`

## Development

### Local Frontend Development

```bash
cd src/frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Testing Lambda Functions Locally

```bash
cd src/backend/lambda_functions/generate_diagram
python3 lambda_function.py
```

### Running Tests

```bash
# Unit tests
cd tests/unit
python3 -m pytest

# Integration tests
cd tests/integration
./scripts/run_integration_tests.sh
```

## Project Structure

```
.
├── infrastructure/
│   ├── terraform/          # Terraform IaC files
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── lambda.tf
│   │   ├── api_gateway.tf
│   │   ├── dynamodb.tf
│   │   ├── s3.tf
│   │   ├── cloudfront.tf
│   │   └── iam.tf
│   ├── scripts/            # Deployment scripts
│   │   └── deploy.sh
│   └── docs/               # Infrastructure documentation
│       └── IAM_SETUP.md
├── src/
│   ├── backend/
│   │   ├── lambda_functions/
│   │   │   ├── generate_diagram/
│   │   │   ├── chat_crud/
│   │   │   ├── get_history/
│   │   │   └── session_crud/    # Session management
│   │   └── shared/              # Shared utilities
│   └── frontend/
│       └── src/
│           ├── components/
│           ├── hooks/           # Session state management
│           ├── services/
│           ├── types/
│           └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── docs/                   # Project documentation
```

## API Endpoints

### Session Management

#### POST /api/session
Create a new chat session

**Response:**
```json
{
  "sessionId": "uuid",
  "title": "",
  "diagramType": "flowchart",
  "createdAt": 1702564800,
  "updatedAt": 1702564800,
  "messageCount": 0
}
```

#### GET /api/session
List all chat sessions

**Query Parameters:**
- `limit` (optional): Number of results (default: 50)
- `nextToken` (optional): Pagination token

**Response:**
```json
{
  "sessions": [
    {
      "sessionId": "uuid",
      "title": "Microservices architecture for e-commerce",
      "diagramType": "flowchart",
      "createdAt": 1702564800,
      "updatedAt": 1702564900,
      "messageCount": 3
    }
  ],
  "count": 1,
  "nextToken": "optional-token"
}
```

#### GET /api/session/{sessionId}
Get a specific session

**Response:**
```json
{
  "sessionId": "uuid",
  "title": "Microservices architecture",
  "diagramType": "flowchart",
  "createdAt": 1702564800,
  "updatedAt": 1702564900,
  "messageCount": 3
}
```

#### PUT /api/session/{sessionId}
Update session title

**Request:**
```json
{
  "title": "Updated session title"
}
```

#### DELETE /api/session/{sessionId}
Delete a session and all its messages

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

#### GET /api/session/{sessionId}/messages
Get all messages for a session

**Response:**
```json
{
  "messages": [
    {
      "messageId": "msg-uuid",
      "sessionId": "uuid",
      "timestamp": 1702564800,
      "userMessage": "Create a microservices diagram",
      "diagramType": "flowchart",
      "aiResponse": "Here's your diagram...",
      "mermaidCode": "graph TD\n  A[Service] --> B[Database]",
      "imageUrl": "https://cloudfront-url/diagrams/uuid.png",
      "markdownUrl": "https://cloudfront-url/diagrams/uuid.md",
      "status": "completed"
    }
  ]
}
```

### Diagram Generation

#### POST /api/diagram/generate
Generate a new architecture diagram

**Request:**
```json
{
  "sessionId": "uuid",
  "userPrompt": "Create a microservices architecture diagram",
  "diagramType": "flowchart"
}
```

**Response:**
```json
{
  "messageId": "msg-uuid",
  "sessionId": "uuid",
  "timestamp": 1702564800,
  "mermaidCode": "graph TD\n  A[Service] --> B[Database]",
  "imageUrl": "https://cloudfront-url/diagrams/uuid.png",
  "markdownUrl": "https://cloudfront-url/diagrams/uuid.md",
  "status": "completed"
}
```

### Legacy Endpoints (Deprecated)

These endpoints are maintained for backward compatibility but should not be used in new implementations.

#### GET /api/chat/history
Retrieve chat history with pagination (deprecated - use GET /api/session and GET /api/session/{sessionId}/messages instead)

**Query Parameters:**
- `limit` (optional): Number of results (default: 50)
- `nextToken` (optional): Pagination token

**Note:** This endpoint scans all items and does not support session-based filtering.

#### POST /api/chat/save
Save a chat message (deprecated - use POST /api/diagram/generate with sessionId instead)

**Request:**
```json
{
  "chatId": "uuid",
  "userMessage": "Create a diagram",
  "diagramType": "flowchart"
}
```

**Note:** This endpoint does not associate messages with sessions. Use the session-based workflow instead.

## Troubleshooting

### Deployment Issues

**Terraform fails with permission errors:**
- Verify your AWS credentials: `aws sts get-caller-identity`
- Check IAM permissions (see IAM_SETUP.md)

**Lambda functions not updating:**
- Ensure you're packaging functions correctly
- Check Lambda function logs in CloudWatch

**Frontend not loading:**
- Verify S3 bucket policy allows CloudFront access
- Check CloudFront distribution status
- Ensure cache invalidation completed

### Runtime Issues

**LLM API errors:**
- Verify `llm_api_key` is set correctly in Terraform variables
- Check Lambda function environment variables
- Review CloudWatch logs for the generate_diagram function

**CORS errors:**
- Verify API Gateway CORS configuration
- Check that frontend is using correct API Gateway URL

**Diagrams not rendering:**
- Check browser console for errors
- Verify Mermaid code syntax
- Ensure React Flow dependencies are installed

## Monitoring

### CloudWatch Logs

Lambda function logs are available in CloudWatch:
- `/aws/lambda/architecture-ai-assistant-generate-diagram-dev`
- `/aws/lambda/architecture-ai-assistant-chat-crud-dev`
- `/aws/lambda/architecture-ai-assistant-get-history-dev`
- `/aws/lambda/architecture-ai-assistant-session-crud-dev`

### Metrics

Monitor key metrics in CloudWatch:
- Lambda invocations and errors
- API Gateway request count and latency
- DynamoDB read/write capacity
- S3 bucket size and requests
- CloudFront cache hit ratio

## Cost Estimation

Approximate monthly costs (assuming moderate usage):
- Lambda: $5-20 (based on invocations)
- API Gateway: $3-10 (based on requests)
- DynamoDB: $1-5 (on-demand pricing)
- S3: $1-3 (storage and requests)
- CloudFront: $1-5 (data transfer)
- **Total: ~$11-43/month**

Plus LLM API costs (varies by provider and usage).

## Cleanup

To destroy all AWS resources:

```bash
cd infrastructure/terraform
terraform destroy
```

**Warning**: This will permanently delete all data including chat history and diagrams.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Your Repo URL]
- Documentation: [Your Docs URL]

## Acknowledgments

- Built with AWS serverless architecture
- Diagram rendering powered by Mermaid.js and React Flow
- Infrastructure managed with Terraform
