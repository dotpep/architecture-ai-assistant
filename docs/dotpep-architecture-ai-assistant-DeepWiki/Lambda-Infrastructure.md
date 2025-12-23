# Lambda Infrastructure

> **Relevant source files**
> * [infrastructure/scripts/lambda/requirements.txt](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/requirements.txt)
> * [infrastructure/terraform/api_gateway.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf)
> * [infrastructure/terraform/lambda.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf)
> * [infrastructure/terraform/tfplan](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/tfplan)

## Purpose and Scope

This document details the Terraform configuration for provisioning AWS Lambda functions in the Architecture AI Assistant system. It covers the Lambda layer for shared dependencies, the three Lambda function resources (`generate_diagram`, `chat_crud`, `get_history`), their execution parameters, environment variable configuration, and CloudWatch logging setup.

For information about the IAM roles and policies that govern Lambda execution permissions, see [IAM Roles and Security](/dotpep/architecture-ai-assistant/5.4-iam-roles-and-security). For details on how API Gateway invokes these Lambda functions, see [API Gateway Configuration](/dotpep/architecture-ai-assistant/5.2-api-gateway-configuration). For the actual implementation code within these functions, see [Backend Lambda Functions](/dotpep/architecture-ai-assistant/4-backend-lambda-functions).

---

## Lambda Layer Architecture

The system uses a single Lambda layer (`aws_lambda_layer_version.shared_dependencies`) to provide shared Python dependencies across all three Lambda functions. This approach reduces deployment package size and ensures consistent dependency versions.

### Layer Configuration

The layer is defined in [infrastructure/terraform/lambda.tf L9-L19](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L9-L19)

 with the following properties:

| Property | Value | Purpose |
| --- | --- | --- |
| `layer_name` | `${var.project_name}-shared-deps-${var.environment}` | Environment-specific naming |
| `filename` | `lambda_layer.zip` | Pre-packaged dependencies |
| `compatible_runtimes` | `["python3.11"]` | Python 3.11 runtime compatibility |
| `source_code_hash` | `filebase64sha256("lambda_layer.zip")` | Triggers updates on content changes |

The layer includes the `requests` library (version 2.28.0+) as specified in [infrastructure/scripts/lambda/requirements.txt L1](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/requirements.txt#L1-L1)

 which is used for HTTP calls to external LLM APIs and the Kroki diagram rendering service.

**Layer Lifecycle Management**

The layer resource uses `create_before_destroy = true` [infrastructure/terraform/lambda.tf L17](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L17-L17)

 to ensure zero-downtime updates. When dependencies change, Terraform creates a new layer version before destroying the old one, preventing function execution failures during deployment.

**Sources:** [infrastructure/terraform/lambda.tf L9-L19](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L9-L19)

 [infrastructure/scripts/lambda/requirements.txt L1](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/requirements.txt#L1-L1)

---

## Lambda Function Resources

The system provisions three Lambda functions, each with distinct responsibilities, resource allocations, and environment configurations.

### Lambda Function Configuration Matrix

```

```

**Sources:** [infrastructure/terraform/lambda.tf L57-L183](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L57-L183)

---

## Generate Diagram Function

The `generate_diagram` Lambda function handles the computationally intensive workflow of generating architecture diagrams through LLM API calls and rendering.

### Resource Configuration

```

```

**Configuration Rationale:**

* **Timeout (60s)**: Accommodates LLM API latency (typically 5-15s) plus Kroki rendering time (1-3s) with buffer for retries
* **Memory (512MB)**: Supports in-memory diagram validation, LLM response parsing, and base64 encoding of PNG images
* **Runtime (python3.11)**: Latest Python 3.x runtime with improved performance and security

### Environment Variables

The function receives seven environment variables [infrastructure/terraform/lambda.tf L71-L80](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L71-L80)

:

| Variable | Source | Usage |
| --- | --- | --- |
| `DYNAMODB_TABLE_NAME` | `aws_dynamodb_table.chat_history.name` | DynamoDB table for chat persistence |
| `S3_BUCKET_NAME` | `aws_s3_bucket.main.id` | S3 bucket for diagram storage |
| `CLOUDFRONT_URL` | `aws_cloudfront_distribution.frontend.domain_name` | CloudFront distribution URL for generating public diagram URLs |
| `LLM_API_ENDPOINT` | `var.llm_api_endpoint` | External LLM service endpoint (OpenAI-compatible) |
| `LLM_API_KEY` | `var.llm_api_key` | API authentication key (sensitive) |
| `LLM_MODEL` | `var.llm_model` | Model identifier (e.g., `gpt-3.5-turbo`) |
| `ENVIRONMENT` | `var.environment` | Deployment environment tag |

### CloudWatch Logging

The log group `aws_cloudwatch_log_group.generate_diagram` [infrastructure/terraform/lambda.tf L90-L97](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L90-L97)

 captures execution logs with:

* **Log group name:** `/aws/lambda/${function_name}`
* **Retention:** 14 days (compliant with short-term debugging requirements)
* **IAM permissions:** Granted via `lambda_generate_diagram` role (see [IAM Roles and Security](/dotpep/architecture-ai-assistant/5.4-iam-roles-and-security))

**Sources:** [infrastructure/terraform/lambda.tf L57-L97](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L57-L97)

---

## Chat CRUD Function

The `chat_crud` Lambda function handles chat message persistence operations with lower resource requirements than `generate_diagram`.

### Resource Configuration

```

```

**Configuration Rationale:**

* **Timeout (10s)**: Sufficient for single DynamoDB write operations (typically < 100ms) with retry buffer
* **Memory (256MB)**: Baseline for JSON parsing and DynamoDB SDK operations

### Environment Variables

The function receives two environment variables [infrastructure/terraform/lambda.tf L119-L123](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L119-L123)

:

| Variable | Source | Usage |
| --- | --- | --- |
| `DYNAMODB_TABLE_NAME` | `aws_dynamodb_table.chat_history.name` | Target table for chat operations |
| `ENVIRONMENT` | `var.environment` | Environment tagging |

**Note:** This function does not require S3, CloudFront, or LLM API access, demonstrating the principle of least privilege in environment variable configuration.

### CloudWatch Logging

The log group `aws_cloudwatch_log_group.chat_crud` [infrastructure/terraform/lambda.tf L133-L140](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L133-L140)

 follows the same 14-day retention pattern as `generate_diagram`.

**Sources:** [infrastructure/terraform/lambda.tf L105-L140](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L105-L140)

---

## Get History Function

The `get_history` Lambda function retrieves paginated chat history from DynamoDB with identical resource configuration to `chat_crud`.

### Resource Configuration

```

```

**Configuration Rationale:**

* **Timeout (10s)**: Accommodates DynamoDB scan/query operations with pagination cursors
* **Memory (256MB)**: Handles JSON array construction for multiple chat records

### Environment Variables

Identical to `chat_crud` [infrastructure/terraform/lambda.tf L162-L166](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L162-L166)

:

| Variable | Source | Usage |
| --- | --- | --- |
| `DYNAMODB_TABLE_NAME` | `aws_dynamodb_table.chat_history.name` | Source table for history queries |
| `ENVIRONMENT` | `var.environment` | Environment tagging |

### CloudWatch Logging

The log group `aws_cloudwatch_log_group.get_history` [infrastructure/terraform/lambda.tf L176-L183](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L176-L183)

 completes the uniform logging configuration across all functions.

**Sources:** [infrastructure/terraform/lambda.tf L148-L183](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L148-L183)

---

## Placeholder Deployment Package

Terraform cannot provision Lambda functions without a deployment package. The configuration uses a placeholder ZIP file generated via `data.archive_file.lambda_placeholder` [infrastructure/terraform/lambda.tf L26-L48](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L26-L48)

### Placeholder Function Code

The placeholder contains a minimal Python handler that returns CORS-compliant responses:

```

```

**Deployment Workflow:**

1. Terraform provisions Lambda functions with placeholder code [infrastructure/terraform/lambda.tf L66-L67](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L66-L67)
2. The `deploy.sh` script packages actual function code from `backend/lambda_functions/`
3. AWS CLI updates function code outside Terraform (see [Deployment Script](/dotpep/architecture-ai-assistant/6.1-deployment-script))

This approach decouples infrastructure provisioning from application code deployment, enabling independent update cycles.

**Sources:** [infrastructure/terraform/lambda.tf L26-L48](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L26-L48)

---

## Lambda Function Naming and Tagging

All Lambda resources follow a consistent naming convention: `${var.project_name}-${function_name}-${var.environment}`.

### Function Name Examples

For `var.project_name = "arch-ai-assistant"` and `var.environment = "prod"`:

| Resource | Function Name |
| --- | --- |
| Generate Diagram | `arch-ai-assistant-generate-diagram-prod` |
| Chat CRUD | `arch-ai-assistant-chat-crud-prod` |
| Get History | `arch-ai-assistant-get-history-prod` |

### Resource Tags

Each function includes metadata tags [infrastructure/terraform/lambda.tf L83-L86](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L83-L86)

:

```

```

These tags enable cost allocation tracking, resource filtering, and operational queries in AWS Console and CLI tools.

**Sources:** [infrastructure/terraform/lambda.tf L83-L86](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L83-L86)

 [infrastructure/terraform/lambda.tf L126-L129](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L126-L129)

 [infrastructure/terraform/lambda.tf L169-L172](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L169-L172)

---

## Lambda-CloudWatch Integration Diagram

The following diagram illustrates how Lambda functions, CloudWatch log groups, and IAM roles interact:

```

```

**Sources:** [infrastructure/terraform/lambda.tf L90-L97](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L90-L97)

 [infrastructure/terraform/lambda.tf L133-L140](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L133-L140)

 [infrastructure/terraform/lambda.tf L176-L183](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L176-L183)

---

## Environment Variable Flow

This diagram shows how Terraform variables and AWS resource attributes populate Lambda environment variables:

```

```

**Sources:** [infrastructure/terraform/lambda.tf L71-L80](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L71-L80)

 [infrastructure/terraform/lambda.tf L119-L123](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L119-L123)

 [infrastructure/terraform/lambda.tf L162-L166](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L162-L166)

---

## Resource Dependencies

Terraform manages implicit dependencies between Lambda functions and other infrastructure components:

| Lambda Resource | Depends On | Reason |
| --- | --- | --- |
| `aws_lambda_function.generate_diagram` | `aws_lambda_layer_version.shared_dependencies` | Layer must exist before function creation |
| `aws_lambda_function.generate_diagram` | `aws_iam_role.lambda_generate_diagram` | Role must exist for function execution |
| `aws_lambda_function.generate_diagram` | `aws_dynamodb_table.chat_history` | Environment variable requires table name |
| `aws_lambda_function.generate_diagram` | `aws_s3_bucket.main` | Environment variable requires bucket ID |
| `aws_lambda_function.generate_diagram` | `aws_cloudfront_distribution.frontend` | Environment variable requires distribution domain |
| `aws_cloudwatch_log_group.*` | `aws_lambda_function.*` | Log group name includes function name |

These dependencies ensure correct provisioning order: IAM roles → Lambda layer → Lambda functions → CloudWatch log groups.

**Sources:** [infrastructure/terraform/lambda.tf L60](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L60-L60)

 [infrastructure/terraform/lambda.tf L69](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L69-L69)

 [infrastructure/terraform/lambda.tf L73-L76](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L73-L76)

---

## Lambda Configuration Summary

### Function Comparison Table

| Property | generate_diagram | chat_crud | get_history |
| --- | --- | --- | --- |
| **Purpose** | Diagram generation via LLM | Chat message persistence | Chat history retrieval |
| **Timeout** | 60 seconds | 10 seconds | 10 seconds |
| **Memory** | 512 MB | 256 MB | 256 MB |
| **Runtime** | python3.11 | python3.11 | python3.11 |
| **Handler** | lambda_function.handler | lambda_function.handler | lambda_function.handler |
| **Layer** | shared_dependencies | shared_dependencies | shared_dependencies |
| **Environment Variables** | 7 (incl. LLM config) | 2 (DDB only) | 2 (DDB only) |
| **Log Retention** | 14 days | 14 days | 14 days |

### Common Configuration Elements

All three Lambda functions share:

* **Runtime:** Python 3.11 [infrastructure/terraform/lambda.tf L62](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L62-L62)
* **Handler:** `lambda_function.handler` [infrastructure/terraform/lambda.tf L61](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L61-L61)
* **Layer:** `aws_lambda_layer_version.shared_dependencies.arn` [infrastructure/terraform/lambda.tf L69](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L69-L69)
* **Deployment:** Placeholder ZIP with `create_before_destroy` lifecycle [infrastructure/terraform/lambda.tf L66-L67](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L66-L67)
* **Logging:** 14-day CloudWatch log retention [infrastructure/terraform/lambda.tf L92](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L92-L92)

**Sources:** [infrastructure/terraform/lambda.tf L57-L183](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L57-L183)