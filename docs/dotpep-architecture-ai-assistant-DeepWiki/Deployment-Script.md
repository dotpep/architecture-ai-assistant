# Deployment Script

> **Relevant source files**
> * [README.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md)
> * [infrastructure/scripts/deploy.sh](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh)
> * [infrastructure/scripts/lambda/deploy_lambda.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/deploy_lambda.py)
> * [src/backend/lambda_functions/chat_crud/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py)
> * [src/backend/lambda_functions/generate_diagram/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py)
> * [src/backend/lambda_functions/get_history/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py)
> * [tests/e2e/e2e_verification.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py)
> * [tests/e2e/verify_deployment.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py)

## Purpose and Scope

This page documents the `deploy.sh` script, which orchestrates the complete end-to-end deployment of the Architecture AI Assistant. The script automates four distinct phases: Lambda function packaging, infrastructure provisioning via Terraform, frontend application build, and CloudFront cache management. For details on the Terraform configuration itself, see [Terraform Variables and Configuration](/dotpep/architecture-ai-assistant/5.5-terraform-variables-and-configuration). For IAM setup required before running deployment, see [IAM Setup for Deployment](/dotpep/architecture-ai-assistant/6.2-iam-setup-for-deployment). For environment configuration, see [Environment Configuration](/dotpep/architecture-ai-assistant/6.3-environment-configuration).

**Sources:** [infrastructure/scripts/deploy.sh L1-L10](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L1-L10)

---

## Overview

The deployment script is located at `infrastructure/scripts/deploy.sh` and implements a linear, fail-fast deployment pipeline. The script uses `set -e` to exit immediately on any error, ensuring failed deployments don't leave the system in an inconsistent state. The deployment process is divided into four sequential phases, with validation checks performed before any deployment actions begin.

### Deployment Phases Sequence

```

```

**Sources:** [infrastructure/scripts/deploy.sh L11-L246](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L11-L246)

 [README.md L102-L119](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L102-L119)

---

## Phase 1: Lambda Function Packaging

The Lambda packaging phase creates deployment artifacts for all backend functions. The process separates shared dependencies into a Lambda layer and packages each function independently.

### Lambda Packaging Architecture

```

```

### Lambda Layer Creation

The Lambda layer contains all shared Python modules and their dependencies. This approach reduces deployment package size and enables code reuse across functions.

**Process:**

1. Create `build/lambda/layer/python/` directory
2. Copy all files from `src/backend/shared/` to `layer/python/`
3. Install dependencies from root `requirements.txt` into `layer/python/`
4. Create `lambda_layer.zip` from the layer directory

**Implementation:**

[infrastructure/scripts/deploy.sh L83-L101](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L83-L101)

**Key Variables:**

* `LAYER_DIR`: `$BUILD_DIR/lambda/layer`
* `SHARED_DIR`: `$PROJECT_ROOT/src/backend/shared`
* Output artifact: `$LAMBDA_BUILD_DIR/lambda_layer.zip`

### Individual Function Packaging

Each Lambda function is packaged separately with only its function-specific code. Shared dependencies are excluded because they're provided by the Lambda layer.

**Implementation:**

[infrastructure/scripts/deploy.sh L103-L134](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L103-L134)

**Process for each function:**

1. Create build directory: `build/lambda/{function_name}/`
2. Copy function code from `src/backend/lambda_functions/{function_name}/`
3. If `requirements.txt` exists in function directory, install to build directory
4. Create zip: `build/lambda/{function_name}.zip`

**Packaged Functions:**

* `generate_diagram` - Diagram generation with LLM integration
* `chat_crud` - Chat message persistence
* `get_history` - Paginated history retrieval

| Function | Source Path | Build Artifact | Size Optimization |
| --- | --- | --- | --- |
| `generate_diagram` | `src/backend/lambda_functions/generate_diagram/` | `generate_diagram.zip` | Shared modules in layer |
| `chat_crud` | `src/backend/lambda_functions/chat_crud/` | `chat_crud.zip` | Shared modules in layer |
| `get_history` | `src/backend/lambda_functions/get_history/` | `get_history.zip` | Shared modules in layer |
| **Layer** | `src/backend/shared/` | `lambda_layer.zip` | Reused across all functions |

**Sources:** [infrastructure/scripts/deploy.sh L70-L134](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L70-L134)

 [infrastructure/scripts/lambda/deploy_lambda.py L53-L141](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/deploy_lambda.py#L53-L141)

---

## Phase 2: Terraform Infrastructure Provisioning

The Terraform phase provisions all AWS infrastructure resources and captures output values needed for subsequent deployment phases.

### Terraform Execution Flow

```

```

### Terraform Initialization

Before applying configuration, the script checks if Terraform has been initialized. If `.terraform` directory doesn't exist, `terraform init` is executed to download provider plugins and initialize the backend.

[infrastructure/scripts/deploy.sh L156-L160](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L156-L160)

### Artifact Deployment

All Lambda deployment packages are copied from the build directory to the Terraform workspace before Terraform execution:

[infrastructure/scripts/deploy.sh L145-L154](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L145-L154)

This ensures Terraform has access to the latest Lambda code when provisioning or updating functions.

### Plan and Apply

The script generates an execution plan (`tfplan`) and applies it immediately:

[infrastructure/scripts/deploy.sh L162-L167](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L162-L167)

Using `-out=tfplan` ensures the exact plan that was reviewed is applied, preventing race conditions from concurrent Terraform changes.

### Output Capture

After successful provisioning, the script captures Terraform outputs using `terraform output -json` and extracts specific values:

[infrastructure/scripts/deploy.sh L169-L177](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L169-L177)

**Captured Outputs:**

* `S3_BUCKET` - Used for frontend upload in Phase 3
* `CLOUDFRONT_DISTRO` - Used for cache invalidation in Phase 4
* `CLOUDFRONT_URL` - Displayed to user as frontend URL
* `API_GATEWAY_URL` - Injected into frontend `.env` file

**Sources:** [infrastructure/scripts/deploy.sh L136-L180](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L136-L180)

 [README.md L147-L157](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L147-L157)

---

## Phase 3: Frontend Build and Upload

The frontend build phase compiles the React application with the correct API endpoint configuration and uploads it to S3.

### Frontend Configuration and Build Process

```

```

### Dependency Installation

The script installs all frontend dependencies before building:

[infrastructure/scripts/deploy.sh L191-L193](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L191-L193)

The `--silent` flag suppresses verbose npm output for cleaner deployment logs.

### Environment Configuration

The script dynamically generates a `.env` file in the frontend directory with the API Gateway URL from Terraform outputs:

[infrastructure/scripts/deploy.sh L195-L199](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L195-L199)

**Environment Variable:**

* `VITE_API_BASE_URL` - Read by Vite at build time and embedded into the compiled JavaScript

This environment variable is consumed by the frontend API service layer at [src/frontend/src/services/api.ts](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/src/services/api.ts)

 to construct API request URLs.

### Production Build

The build command executes Vite's production build pipeline:

[infrastructure/scripts/deploy.sh L201-L203](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L201-L203)

**Build Output:**

* Optimized JavaScript bundles with code splitting
* Minified CSS
* Static assets with content hashing
* `index.html` entry point

All build artifacts are written to `src/frontend/dist/`.

### S3 Upload

The compiled frontend is synchronized to the S3 bucket under the `/frontend/` prefix:

[infrastructure/scripts/deploy.sh L207-L210](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L207-L210)

**Command Options:**

* `--delete` - Removes files from S3 that don't exist locally (ensures clean deployment)
* `--quiet` - Suppresses detailed file transfer output

The S3 bucket is configured with static website hosting and serves as the CloudFront origin for the frontend. See [CloudFront and S3 Configuration](/dotpep/architecture-ai-assistant/5.3-cloudfront-and-s3-configuration) for details on bucket policies and CloudFront integration.

**Sources:** [infrastructure/scripts/deploy.sh L182-L213](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L182-L213)

 [README.md L158-L175](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L158-L175)

---

## Phase 4: CloudFront Cache Invalidation

After uploading the new frontend to S3, the script invalidates the CloudFront cache to ensure users immediately receive the latest version.

### Invalidation Process

[infrastructure/scripts/deploy.sh L219-L227](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L219-L227)

**Invalidation Parameters:**

* `--distribution-id` - The CloudFront distribution ID from Terraform outputs
* `--paths "/*"` - Invalidates all cached paths
* `--query 'Invalidation.Id'` - Extracts the invalidation ID from the response

**Invalidation Behavior:**

* CloudFront invalidation is asynchronous and typically takes 1-5 minutes
* Users may see cached content until invalidation completes
* The invalidation ID can be used to check status with `aws cloudfront get-invalidation`

**Cost Consideration:** AWS provides 1,000 free invalidation paths per month per distribution. The wildcard `/*` invalidation counts as one path.

**Sources:** [infrastructure/scripts/deploy.sh L215-L227](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L215-L227)

 [README.md L176-L183](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L176-L183)

---

## Prerequisites Validation

Before executing any deployment steps, the script validates that all required tools and credentials are available.

### Required Tools Check

[infrastructure/scripts/deploy.sh L52-L60](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L52-L60)

**Validated Commands:**

* `terraform` - Infrastructure provisioning
* `aws` - AWS CLI for S3 and CloudFront operations
* `python3` - Lambda layer dependency installation
* `node` - Frontend dependency installation
* `npm` - Frontend build execution
* `zip` - Lambda package creation

### AWS Credentials Validation

[infrastructure/scripts/deploy.sh L62-L66](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L62-L66)

The script calls `aws sts get-caller-identity` to verify AWS credentials are configured and valid. This check prevents deployment failures after lengthy packaging steps.

**Sources:** [infrastructure/scripts/deploy.sh L47-L68](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L47-L68)

 [README.md L21-L69](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L21-L69)

---

## Directory Structure and Build Artifacts

### Key Directory Paths

The script uses several directory path variables defined at the beginning:

[infrastructure/scripts/deploy.sh L37-L39](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L37-L39)

| Variable | Path | Purpose |
| --- | --- | --- |
| `SCRIPT_DIR` | `infrastructure/scripts/` | Script location |
| `PROJECT_ROOT` | Root of repository | Base for all relative paths |
| `LAMBDA_DIR` | `src/backend/lambda_functions/` | Lambda function source code |
| `SHARED_DIR` | `src/backend/shared/` | Shared Python modules |
| `BUILD_DIR` | `build/` | Build artifacts (created during deployment) |
| `LAMBDA_BUILD_DIR` | `build/lambda/` | Lambda packaging workspace |
| `TERRAFORM_DIR` | `infrastructure/terraform/` | Terraform configuration |
| `FRONTEND_DIR` | `src/frontend/` | React application source |

### Build Artifacts Structure

After successful packaging, the build directory contains:

```markdown
build/
└── lambda/
    ├── lambda_layer.zip           # Shared dependencies layer
    ├── generate_diagram.zip       # Generate diagram function
    ├── chat_crud.zip              # Chat CRUD function
    ├── get_history.zip            # Get history function
    ├── layer/                     # Layer build workspace (temporary)
    │   └── python/
    ├── generate_diagram/          # Function build workspace (temporary)
    ├── chat_crud/                 # Function build workspace (temporary)
    └── get_history/               # Function build workspace (temporary)
```

**Sources:** [infrastructure/scripts/deploy.sh L37-L39](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L37-L39)

 [infrastructure/scripts/deploy.sh L76-L82](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L76-L82)

---

## Logging and User Feedback

The script implements colored console output for clear status communication:

### Log Functions

[infrastructure/scripts/deploy.sh L13-L35](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L13-L35)

**Log Types:**

* `log_info()` - Blue ℹ symbol for informational messages
* `log_success()` - Green ✓ symbol for successful operations
* `log_warning()` - Yellow ⚠ symbol for warnings
* `log_error()` - Red ✗ symbol for errors

### Deployment Completion Summary

After successful deployment, the script displays key outputs:

[infrastructure/scripts/deploy.sh L233-L246](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L233-L246)

**Displayed Information:**

* `CLOUDFRONT_URL` - Frontend application URL
* `API_GATEWAY_URL` - Backend API endpoint
* `S3_BUCKET` - S3 bucket name
* Invalidation status check command

**Sources:** [infrastructure/scripts/deploy.sh L13-L35](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L13-L35)

 [infrastructure/scripts/deploy.sh L229-L246](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L229-L246)

---

## Error Handling

The script uses `set -e` at the beginning to enable fail-fast behavior:

[infrastructure/scripts/deploy.sh L11](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L11-L11)

**Behavior:**

* Any command returning a non-zero exit code causes immediate script termination
* Prevents partial deployments that could leave the system in an inconsistent state
* Each phase must complete successfully before the next phase begins

**Implications:**

* If Lambda packaging fails, Terraform is never executed
* If Terraform fails, frontend build is skipped
* If frontend build fails, CloudFront cache is not invalidated

This linear dependency chain ensures deployment atomicity at the phase level.

**Sources:** [infrastructure/scripts/deploy.sh L11](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L11-L11)

---

## Usage

### Standard Deployment

Execute from the scripts directory:

```

```

### Prerequisites

Before running the deployment script:

1. Configure AWS credentials: `aws configure`
2. Create `infrastructure/terraform/terraform.tfvars` with required variables
3. Ensure all required tools are installed

For detailed setup instructions, see [Environment Configuration](/dotpep/architecture-ai-assistant/6.3-environment-configuration) and [IAM Setup for Deployment](/dotpep/architecture-ai-assistant/6.2-iam-setup-for-deployment).

### Expected Duration

A complete deployment typically takes 5-10 minutes:

* Lambda packaging: 1-2 minutes
* Terraform apply: 2-5 minutes (longer for initial deployment)
* Frontend build: 1-2 minutes
* S3 upload and CloudFront invalidation: 1 minute

**Sources:** [README.md L102-L119](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/README.md#L102-L119)

 [infrastructure/scripts/deploy.sh L1-L246](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L1-L246)

---

## Alternative: Python Lambda Deployment Script

The repository also includes a Python-based Lambda deployment script at `infrastructure/scripts/lambda/deploy_lambda.py`. This script focuses specifically on Lambda function updates without full infrastructure provisioning.

**Key Differences:**

* Updates existing Lambda functions via AWS CLI
* Does not execute Terraform
* Useful for rapid Lambda code updates during development
* Requires Terraform outputs to determine Lambda function names

**Usage:**

```

```

This script is not part of the standard deployment flow but provides a faster iteration cycle when only Lambda code changes.

**Sources:** [infrastructure/scripts/lambda/deploy_lambda.py L1-L226](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/deploy_lambda.py#L1-L226)