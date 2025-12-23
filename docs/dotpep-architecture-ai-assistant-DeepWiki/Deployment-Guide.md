# Deployment Guide

> **Relevant source files**
> * [.gitignore](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/.gitignore)
> * [README.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md)
> * [docs/infrastucture/IAM_SETUP.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md)
> * [infrastructure/scripts/deploy.sh](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh)
> * [infrastructure/scripts/lambda/deploy_lambda.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/deploy_lambda.py)
> * [src/backend/lambda_functions/chat_crud/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py)
> * [src/backend/lambda_functions/generate_diagram/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py)
> * [src/backend/lambda_functions/get_history/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py)
> * [tests/e2e/e2e_verification.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py)
> * [tests/e2e/verify_deployment.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py)

## Purpose and Scope

This guide provides a comprehensive walkthrough for deploying the Architecture AI Assistant to AWS infrastructure. It covers the prerequisites, the automated deployment process via `deploy.sh`, deployment phases, and post-deployment verification procedures.

For detailed information on specific deployment aspects, see:

* **[Deployment Script](/dotpep/architecture-ai-assistant/6.1-deployment-script)** - In-depth explanation of the `deploy.sh` script phases and internal mechanics
* **[IAM Setup for Deployment](/dotpep/architecture-ai-assistant/6.2-iam-setup-for-deployment)** - Detailed IAM permissions configuration and security best practices
* **[Environment Configuration](/dotpep/architecture-ai-assistant/6.3-environment-configuration)** - Required environment variables, `.env` files, and secrets management

This page focuses on the overall deployment workflow and getting the system running in AWS.

---

## Prerequisites

Before initiating deployment, verify that all required tools and configurations are in place.

### Required Software Tools

| Tool | Minimum Version | Verification Command | Purpose |
| --- | --- | --- | --- |
| **AWS CLI** | v2.x | `aws --version` | AWS resource management and S3/CloudFront operations |
| **Terraform** | v1.0+ | `terraform --version` | Infrastructure provisioning |
| **Node.js** | v18.x+ | `node --version` | Frontend build process |
| **npm** | Latest | `npm --version` | Frontend dependency management |
| **Python 3** | v3.11+ | `python3 --version` | Lambda function packaging |
| **pip3** | Latest | `pip3 --version` | Python dependency installation |
| **zip** | Any | `zip --version` | Lambda package creation |

### AWS Account Requirements

The deployment requires AWS credentials configured with appropriate permissions. Run `aws configure` to set up credentials if not already configured. The deployment user requires permissions to create and manage:

* Lambda functions and layers
* API Gateway REST APIs
* DynamoDB tables
* S3 buckets
* CloudFront distributions
* IAM roles and policies
* CloudWatch log groups

See **[IAM Setup for Deployment](/dotpep/architecture-ai-assistant/6.2-iam-setup-for-deployment)** for detailed permission requirements and setup instructions for the `terraform-deploy-user`.

### Configuration Files Required

Before deployment, ensure the following configuration file exists:

**`infrastructure/terraform/terraform.tfvars`** - Must contain:

```

```

See **[Environment Configuration](/dotpep/architecture-ai-assistant/6.3-environment-configuration)** for complete configuration details and supported LLM providers.

**Sources:** [README.md L21-L68](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L21-L68)

 [docs/infrastucture/IAM_SETUP.md L1-L70](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L1-L70)

---

## Deployment Architecture Overview

The deployment orchestrates four distinct phases to provision infrastructure, package application code, and configure content delivery.

### Deployment Orchestration Flow

```

```

The `deploy.sh` script at [infrastructure/scripts/deploy.sh](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh)

 coordinates the entire deployment lifecycle, ensuring dependencies between phases are properly managed. Each phase is idempotent and can be run independently if needed.

**Sources:** [infrastructure/scripts/deploy.sh L1-L246](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L1-L246)

 [README.md L102-L184](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L102-L184)

---

## Quick Start: One-Command Deployment

The fastest way to deploy the complete application to AWS:

```

```

This single command executes all four deployment phases sequentially. Expected duration: **5-10 minutes**.

### Deployment Output Structure

The script provides color-coded progress output:

* **Blue (ℹ)**: Informational messages about current operation
* **Green (✓)**: Successful completion of phase or operation
* **Yellow (⚠)**: Warning messages (non-fatal)
* **Red (✗)**: Error messages (deployment failure)

### Prerequisites Validation

Before executing deployment phases, `deploy.sh` validates that all required commands are available [infrastructure/scripts/deploy.sh L51-L68](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L51-L68)

:

```

```

If any prerequisite fails, the script exits immediately with an error message indicating the missing component.

**Sources:** [infrastructure/scripts/deploy.sh L37-L68](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L37-L68)

 [README.md L104-L119](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L104-L119)

---

## Deployment Phases Overview

### Phase 1: Lambda Function Packaging

**Location:** [infrastructure/scripts/deploy.sh L70-L134](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L70-L134)

This phase creates deployment packages for Lambda functions:

1. **Lambda Layer Creation** - Packages shared dependencies * Copies contents of `src/backend/shared/` to `build/lambda/layer/python/` * Installs Python dependencies from `requirements.txt` * Creates `lambda_layer.zip` containing all shared code
2. **Individual Function Packaging** - Creates function-specific packages * Packages `generate_diagram`, `chat_crud`, `get_history` functions * Each function gets its own ZIP file * Function-specific dependencies are included if `requirements.txt` exists

**Build Artifacts:**

```
build/lambda/
├── lambda_layer.zip
├── generate_diagram.zip
├── chat_crud.zip
└── get_history.zip
```

### Phase 2: Infrastructure Provisioning with Terraform

**Location:** [infrastructure/scripts/deploy.sh L136-L180](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L136-L180)

Terraform provisions all AWS resources:

1. **Initialization** - `terraform init` downloads required providers
2. **Planning** - `terraform plan` creates execution plan (`tfplan`)
3. **Application** - `terraform apply` creates/updates resources
4. **Output Capture** - Extracts `cloudfront_url`, `api_gateway_url`, `s3_bucket_name`, `cloudfront_distribution_id`

**Resources Created:**

* 3 Lambda functions with execution roles
* 1 Lambda layer for shared code
* API Gateway with 3 endpoints
* DynamoDB table with partition key `chatId` and sort key `timestamp`
* 2 S3 buckets (frontend, diagrams)
* CloudFront distribution with Origin Access Control

See **[Infrastructure as Code](/dotpep/architecture-ai-assistant/5-infrastructure-as-code)** for detailed resource configuration.

### Phase 3: Frontend Build and Configuration

**Location:** [infrastructure/scripts/deploy.sh L182-L213](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L182-L213)

Builds the React SPA with production optimizations:

1. **Dependency Installation** - `npm install` in `src/frontend/`
2. **Environment Configuration** - Creates `.env` file with `VITE_API_BASE_URL` from Terraform output
3. **Production Build** - `npm run build` generates optimized bundle in `dist/` * Minification and tree-shaking * Asset hashing for cache busting * Source maps for debugging

**Build Output:** `src/frontend/dist/` containing:

* `index.html` - Single-page application entry point
* `assets/` - JavaScript bundles, CSS files, fonts, images

### Phase 4: S3 Upload and CloudFront Invalidation

**Location:** [infrastructure/scripts/deploy.sh L215-L227](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L215-L227)

Deploys the frontend and ensures immediate availability:

1. **S3 Sync** - `aws s3 sync dist/ s3://<bucket>/frontend/ --delete` * Uploads all files from `dist/` to S3 * `--delete` flag removes old files not in current build
2. **Cache Invalidation** - `aws cloudfront create-invalidation --paths "/*"` * Forces CloudFront to fetch fresh content from S3 * Invalidation typically completes in 1-3 minutes

**Sources:** [infrastructure/scripts/deploy.sh L70-L227](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L70-L227)

 [README.md L121-L184](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L121-L184)

---

## Deployment Success Verification

### Terraform Outputs

After successful deployment, retrieve key URLs:

```

```

**Expected Output:**

```
cloudfront_url = "https://d1234567890abc.cloudfront.net"
api_gateway_url = "https://abcd1234.execute-api.us-east-1.amazonaws.com/dev"
```

### Automated Verification Tests

The codebase includes end-to-end verification scripts that test the complete deployment:

#### verify_deployment.py

**Location:** [tests/e2e/verify_deployment.py L1-L310](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L1-L310)

Runs six verification tests:

| Test | Validates | Expected Result |
| --- | --- | --- |
| `verify_cloudfront_accessible()` | CloudFront serves frontend | HTTP 200, HTML content |
| `verify_api_gateway_accessible()` | API Gateway endpoints exist | HTTP 200 or 400 (not 403/404) |
| `verify_diagram_generation()` | Complete diagram generation flow | Returns `chatId`, `mermaidCode`, `imageUrl`, `markdownUrl` |
| `verify_chat_save()` | DynamoDB persistence | Returns `success: true`, `chatId` |
| `verify_chat_history()` | History retrieval with pagination | Returns `chats` array, `count`, `nextToken` |
| `verify_download_urls()` | S3/CloudFront file access | HTTP 200 for both PNG and markdown URLs |

**Running Verification:**

```

```

**Sample Output:**

```yaml
========================================
  Architecture AI Assistant - End-to-End Verification
========================================

ℹ Verifying CloudFront frontend accessibility...
✓ CloudFront frontend is accessible

ℹ Testing diagram generation endpoint...
✓ Diagram generation successful
  Chat ID: 123e4567-e89b-12d3-a456-426614174000
  Status: completed
  Mermaid code length: 234 characters

========================================
  Verification Summary
========================================
✓ PASS: Cloudfront
✓ PASS: Api Gateway
✓ PASS: Diagram Generation
✓ PASS: Chat Save
✓ PASS: Chat History
✓ PASS: Download Urls

✓ All 6 tests passed!
```

### Manual Verification Checklist

After deployment, manually verify critical functionality:

1. **Frontend Access** * Navigate to CloudFront URL in browser * Verify page loads without errors * Check browser console for JavaScript errors
2. **API Gateway Integration** * Open browser DevTools Network tab * Attempt to generate a diagram * Verify API requests return HTTP 200
3. **Diagram Generation** * Enter prompt: "Create a simple flowchart" * Select diagram type: "Flowchart" * Click "Generate Diagram" * Verify diagram renders in React Flow viewer
4. **Download Functionality** * Click "Download PNG" - file should download * Click "Download Markdown" - `.md` file should download
5. **Chat History Persistence** * Refresh the browser page * Previous diagrams should persist in history

**Sources:** [tests/e2e/verify_deployment.py L1-L310](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L1-L310)

 [tests/e2e/e2e_verification.py L1-L308](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L1-L308)

---

## Troubleshooting Common Deployment Issues

### Prerequisites and Configuration Errors

#### Error: "Required command 'terraform' not found"

**Cause:** Terraform not installed or not in PATH

**Solution:**

```

```

#### Error: "AWS credentials not configured"

**Cause:** `aws sts get-caller-identity` fails at [infrastructure/scripts/deploy.sh L63-L66](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L63-L66)

**Solution:**

```

```

#### Error: "terraform.tfvars not found"

**Cause:** Missing or incorrectly named configuration file

**Solution:**

```

```

### Terraform Provisioning Errors

#### Error: "User is not authorized to perform: lambda:CreateFunction"

**Cause:** Insufficient IAM permissions

**Solution:** See **[IAM Setup for Deployment](/dotpep/architecture-ai-assistant/6.2-iam-setup-for-deployment)** to create `terraform-deploy-user` with `TerraformDeploymentPolicy` attached. Verify permissions:

```

```

#### Error: "Error creating CloudFront Distribution: PreconditionFailed"

**Cause:** S3 bucket policy not correctly configured or Origin Access Control issues

**Solution:** Check Terraform state consistency:

```

```

If inconsistent, manually delete the partial CloudFront distribution in AWS Console and re-run `terraform apply`.

#### Error: "Error creating Lambda function: InvalidParameterValueException"

**Cause:** Lambda ZIP file corrupted or missing dependencies

**Solution:** Rebuild Lambda packages:

```

```

### Frontend Build Errors

#### Error: "Module not found: Can't resolve 'react-flow-renderer'"

**Cause:** Frontend dependencies not installed

**Solution:**

```

```

#### Error: "VITE_API_BASE_URL is not defined"

**Cause:** `.env` file not created in Phase 3

**Solution:** Manually create `.env` file:

```

```

### Runtime Errors After Deployment

#### Error: "502 Bad Gateway" when generating diagrams

**Cause 1:** LLM API credentials incorrect or endpoint unreachable

**Solution:** Check Lambda environment variables:

```

```

Verify `LLM_API_ENDPOINT` and `LLM_API_KEY` are set correctly. Update via Terraform variables if needed.

**Cause 2:** Lambda timeout (>60 seconds)

**Solution:** Check CloudWatch logs:

```

```

Look for timeout errors. If LLM API is slow, consider increasing Lambda timeout in [infrastructure/terraform/lambda.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf)

#### Error: "403 Forbidden" when accessing CloudFront

**Cause:** CloudFront cache not invalidated or S3 bucket policy incorrect

**Solution:**

```

```

#### Error: "No Access-Control-Allow-Origin header" (CORS error)

**Cause:** API Gateway CORS configuration missing or incorrect

**Solution:** CORS is configured in [infrastructure/terraform/api_gateway.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf)

 Verify OPTIONS method exists:

```

```

Each resource should have an OPTIONS method. If missing, re-run `terraform apply`.

**Sources:** [README.md L310-L342](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L310-L342)

 [infrastructure/scripts/deploy.sh L51-L68](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L51-L68)

 [docs/infrastucture/IAM_SETUP.md L370-L410](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L370-L410)

---

## Manual Deployment Steps

For scenarios requiring fine-grained control or debugging, execute deployment phases individually:

### Step 1: Package Lambda Functions

```

```

### Step 2: Deploy Infrastructure with Terraform

```

```

### Step 3: Build and Deploy Frontend

```

```

### Step 4: Invalidate CloudFront Cache

```

```

**Sources:** [README.md L121-L184](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L121-L184)

 [infrastructure/scripts/deploy.sh L70-L227](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L70-L227)

---

## Deployment State Management

### Terraform State File

Terraform maintains infrastructure state in `infrastructure/terraform/terraform.tfstate` [.gitignore L7](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/.gitignore#L7-L7)

 This file:

* Tracks all provisioned AWS resources
* Maps Terraform configuration to real AWS resource IDs
* Enables incremental updates and resource deletion
* **Must not be committed to version control** (contains sensitive data)

**State Operations:**

```

```

### Build Artifacts

The `build/` directory contains temporary deployment artifacts [.gitignore L24-L27](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/.gitignore#L24-L27)

:

```
build/
└── lambda/
    ├── lambda_layer.zip
    ├── generate_diagram.zip
    ├── chat_crud.zip
    ├── get_history.zip
    ├── layer/
    │   └── python/
    ├── generate_diagram/
    ├── chat_crud/
    └── get_history/
```

These files are generated during Phase 1 and consumed by Terraform in Phase 2. They are ignored by Git and should be rebuilt for each deployment.

### Frontend Build Output

The `src/frontend/dist/` directory contains the production-optimized React SPA [.gitignore L24-L27](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/.gitignore#L24-L27)

:

```
src/frontend/dist/
├── index.html
├── assets/
│   ├── index-[hash].js
│   ├── index-[hash].css
│   └── vendor-[hash].js
└── favicon.ico
```

This directory is generated in Phase 3 and uploaded to S3 in Phase 4. The `[hash]` values change with each build for cache busting.

**Sources:** [.gitignore L1-L45](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/.gitignore#L1-L45)

 [infrastructure/scripts/deploy.sh L78-L134](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L78-L134)

---

## Post-Deployment Access

### Application URLs

After successful deployment, access the application through CloudFront:

```

```

### API Endpoints

The API Gateway provides three REST endpoints:

| Endpoint | Method | Purpose | Request Body |
| --- | --- | --- | --- |
| `/api/diagram/generate` | POST | Generate diagram from prompt | `{"userPrompt": "...", "diagramType": "flowchart"}` |
| `/api/chat/save` | POST | Save chat message to DynamoDB | `{"userMessage": "...", "diagramType": "..."}` |
| `/api/chat/history` | GET | Retrieve paginated chat history | Query params: `limit`, `nextToken` |

**Testing with curl:**

```

```

### CloudWatch Logs

Monitor Lambda function execution in real-time:

```

```

**Sources:** [README.md L185-L194](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L185-L194)

 [README.md L266-L308](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L266-L308)

 [README.md L343-L360](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L343-L360)

---

## Deployment Cleanup

To completely remove all AWS resources and clean up local artifacts:

### Destroy AWS Infrastructure

```

```

This command:

1. Prompts for confirmation (type `yes`)
2. Deletes all resources in reverse dependency order
3. Updates `terraform.tfstate` to reflect empty state

**Warning:** This operation is **irreversible** and will permanently delete:

* All chat history in DynamoDB
* All diagram files in S3
* CloudFront distribution
* API Gateway endpoints
* Lambda functions

### Clean Local Build Artifacts

```

```

### Verify Cleanup

Confirm all resources are deleted:

```

```

**Sources:** [README.md L372-L382](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L372-L382)

 [.gitignore L1-L45](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/.gitignore#L1-L45)