# IAM Roles and Security

> **Relevant source files**
> * [.gitignore](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/.gitignore)
> * [docs/infrastucture/IAM_SETUP.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md)
> * [infrastructure/terraform/api_gateway.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf)
> * [infrastructure/terraform/lambda.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf)

## Purpose and Scope

This document details the Identity and Access Management (IAM) configuration for the Architecture AI Assistant system. It covers the execution roles for Lambda functions, their policies implementing least-privilege access, resource-based permissions for API Gateway integration, and deployment user configuration. For infrastructure provisioning details, see [Terraform Variables and Configuration](/dotpep/architecture-ai-assistant/5.5-terraform-variables-and-configuration). For Lambda-specific configuration including environment variables, see [Lambda Infrastructure](/dotpep/architecture-ai-assistant/5.1-lambda-infrastructure).

The system implements a defense-in-depth security model with three distinct security layers:

1. **Execution Roles**: Identity-based policies for Lambda functions to access AWS services
2. **Resource-Based Policies**: Allow API Gateway to invoke Lambda functions
3. **Deployment Permissions**: IAM user/role for Terraform to provision infrastructure

---

## IAM Architecture Overview

The Architecture AI Assistant uses separate IAM roles for each Lambda function, following the principle of least privilege. Each role grants only the minimum permissions required for that function's specific operations.

### IAM Role Structure

```

```

**Sources:** [infrastructure/terraform/lambda.tf L57-L87](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L57-L87)

 [infrastructure/terraform/lambda.tf L105-L130](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L105-L130)

 [infrastructure/terraform/lambda.tf L148-L173](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L148-L173)

 [docs/infrastucture/IAM_SETUP.md L298-L320](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L298-L320)

---

## Lambda Execution Roles

Each Lambda function is assigned a dedicated execution role at function creation. The role ARN is specified in the `role` parameter of the Lambda resource definition.

### Role Assignments

| Lambda Function | Role Reference | Configuration File |
| --- | --- | --- |
| `generate_diagram` | `aws_iam_role.lambda_generate_diagram.arn` | [infrastructure/terraform/lambda.tf L60](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L60-L60) |
| `chat_crud` | `aws_iam_role.lambda_chat_crud.arn` | [infrastructure/terraform/lambda.tf L108](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L108-L108) |
| `get_history` | `aws_iam_role.lambda_get_history.arn` | [infrastructure/terraform/lambda.tf L151](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L151-L151) |

**Sources:** [infrastructure/terraform/lambda.tf L57-L87](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L57-L87)

 [infrastructure/terraform/lambda.tf L105-L130](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L105-L130)

 [infrastructure/terraform/lambda.tf L148-L173](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L148-L173)

---

### Generate Diagram Lambda Role

The `generate_diagram` Lambda requires the most comprehensive permissions as it orchestrates diagram generation, storage, and metadata persistence.

#### Required Permissions

```

```

#### Permission Scope

| Service | Actions | Resources | Justification |
| --- | --- | --- | --- |
| **DynamoDB** | `PutItem`, `GetItem` | `chat_history` table | Save generated diagram metadata and retrieve chat context |
| **S3** | `PutObject`, `GetObject` | `diagrams/*` prefix in main bucket | Store Mermaid markdown and rendered PNG files |
| **CloudWatch Logs** | `CreateLogGroup`, `CreateLogStream`, `PutLogEvents` | `/aws/lambda/${function_name}` | Logging and debugging |

**Sources:** [docs/infrastucture/IAM_SETUP.md L302-L307](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L302-L307)

 [infrastructure/terraform/lambda.tf L57-L87](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L57-L87)

---

### Chat CRUD Lambda Role

The `chat_crud` Lambda requires full CRUD operations on DynamoDB for manual chat message persistence.

#### Required Permissions

| Service | Actions | Resources | Justification |
| --- | --- | --- | --- |
| **DynamoDB** | `PutItem`, `GetItem`, `UpdateItem`, `DeleteItem` | `chat_history` table | Complete CRUD operations for chat messages |
| **CloudWatch Logs** | `CreateLogGroup`, `CreateLogStream`, `PutLogEvents` | `/aws/lambda/${function_name}` | Logging and debugging |

**Note:** While the function is named `chat_crud`, in practice it primarily handles `PutItem` operations. The additional permissions support future functionality for editing and deleting messages.

**Sources:** [docs/infrastucture/IAM_SETUP.md L309-L313](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L309-L313)

 [infrastructure/terraform/lambda.tf L105-L130](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L105-L130)

---

### Get History Lambda Role

The `get_history` Lambda requires read-only access to DynamoDB for retrieving paginated chat history.

#### Required Permissions

| Service | Actions | Resources | Justification |
| --- | --- | --- | --- |
| **DynamoDB** | `Query`, `Scan` | `chat_history` table | Retrieve chat history with pagination support |
| **CloudWatch Logs** | `CreateLogGroup`, `CreateLogStream`, `PutLogEvents` | `/aws/lambda/${function_name}` | Logging and debugging |

#### Query vs Scan

The role grants both `Query` and `Scan` permissions:

* **Query**: Used for efficient retrieval by `chatId` (partition key)
* **Scan**: Required for retrieving all chat messages across different chat sessions

**Sources:** [docs/infrastucture/IAM_SETUP.md L315-L319](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L315-L319)

 [infrastructure/terraform/lambda.tf L148-L173](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L148-L173)

---

## Trust Relationships

All Lambda execution roles share the same trust policy, allowing the AWS Lambda service to assume the role.

### Standard Lambda Trust Policy

```

```

This trust relationship is automatically configured when creating IAM roles with `assume_role_policy` in Terraform.

**Sources:** [docs/infrastucture/IAM_SETUP.md L298-L320](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L298-L320)

---

## Resource-Based Policies

In addition to execution roles, Lambda functions require resource-based policies to allow API Gateway invocation.

### API Gateway Lambda Permissions

```

```

### Permission Configuration

Each Lambda function has a corresponding `aws_lambda_permission` resource granting API Gateway invocation rights:

| Permission Resource | Lambda Function | Source ARN Pattern |
| --- | --- | --- |
| `api_gateway_generate_diagram` | `generate_diagram` | `${aws_api_gateway_rest_api.main.execution_arn}/*/*` |
| `api_gateway_chat_crud` | `chat_crud` | `${aws_api_gateway_rest_api.main.execution_arn}/*/*` |
| `api_gateway_get_history` | `get_history` | `${aws_api_gateway_rest_api.main.execution_arn}/*/*` |

The wildcard pattern `/*/*` allows invocation from any stage and any HTTP method within the API Gateway.

**Sources:** [infrastructure/terraform/api_gateway.tf L359-L383](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L359-L383)

#### Permission Attributes

```
statement_id  = "AllowAPIGatewayInvoke"
action        = "lambda:InvokeFunction"
principal     = "apigateway.amazonaws.com"
source_arn    = "${api_gateway_execution_arn}/*/*"
```

* **statement_id**: Unique identifier for the permission statement in the Lambda function policy
* **action**: Grants `InvokeFunction` permission only (no UpdateFunctionCode, DeleteFunction, etc.)
* **principal**: Restricts invocation to API Gateway service
* **source_arn**: Scopes permission to the specific API Gateway instance

**Sources:** [infrastructure/terraform/api_gateway.tf L359-L383](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L359-L383)

---

## CloudWatch Log Group Permissions

Each Lambda function has an associated CloudWatch Log Group managed by Terraform with 14-day retention.

### Log Group Configuration

| Lambda Function | Log Group Resource | Log Group Name | Retention |
| --- | --- | --- | --- |
| `generate_diagram` | `aws_cloudwatch_log_group.generate_diagram` | `/aws/lambda/${function_name}` | 14 days |
| `chat_crud` | `aws_cloudwatch_log_group.chat_crud` | `/aws/lambda/${function_name}` | 14 days |
| `get_history` | `aws_cloudwatch_log_group.get_history` | `/aws/lambda/${function_name}` | 14 days |

The log groups are created explicitly in Terraform to ensure consistent retention policies and proper resource lifecycle management.

**Sources:** [infrastructure/terraform/lambda.tf L89-L97](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L89-L97)

 [infrastructure/terraform/lambda.tf L132-L140](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L132-L140)

 [infrastructure/terraform/lambda.tf L175-L183](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L175-L183)

---

## Deployment User Permissions

The Terraform deployment process requires a separate IAM user or role with permissions to create and manage all infrastructure resources.

### Deployment IAM Architecture

```

```

### Required Deployment Permissions

The deployment user requires permissions across seven AWS service categories:

| Service Category | Key Actions | Justification |
| --- | --- | --- |
| **Lambda** | `CreateFunction`, `UpdateFunctionCode`, `PublishLayerVersion` | Create and update Lambda functions and layers |
| **IAM** | `CreateRole`, `AttachRolePolicy`, `PassRole` | Create execution roles for Lambda functions |
| **API Gateway** | `POST`, `PUT`, `DELETE`, `PATCH` | Configure REST API and integrations |
| **DynamoDB** | `CreateTable`, `UpdateTable`, `DescribeTable` | Provision chat_history table |
| **S3** | `CreateBucket`, `PutBucketPolicy`, `PutObject` | Create buckets and upload deployment artifacts |
| **CloudFront** | `CreateDistribution`, `UpdateDistribution`, `CreateOriginAccessControl` | Setup CDN distribution |
| **CloudWatch Logs** | `CreateLogGroup`, `PutRetentionPolicy` | Configure log retention |

**Sources:** [docs/infrastucture/IAM_SETUP.md L68-L251](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L68-L251)

### PassRole Permission

The `iam:PassRole` permission is critical and requires special attention. It allows the deployment user to assign IAM roles to Lambda functions during creation.

#### PassRole Flow

```

```

**Without PassRole permission**, Terraform cannot assign execution roles to Lambda functions, causing deployment failure with error: `User is not authorized to perform: iam:PassRole`.

**Sources:** [docs/infrastucture/IAM_SETUP.md L186-L212](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L186-L212)

---

## Security Best Practices

### Principle of Least Privilege

The system implements least-privilege access at multiple levels:

1. **Function-Specific Roles**: Each Lambda has a separate role rather than sharing a common role
2. **Action Scoping**: Policies grant only required actions (e.g., `get_history` has no `PutItem` permission)
3. **Resource Scoping**: Where possible, permissions are restricted to specific resources (e.g., S3 `diagrams/*` prefix)

### Separation of Concerns

| Role Type | Scope | Purpose |
| --- | --- | --- |
| **Deployment User** | Infrastructure management | Create and update AWS resources |
| **Lambda Execution Roles** | Runtime operations | Access data and services during function execution |
| **Resource-Based Policies** | Service integration | Allow cross-service invocation |

This separation ensures:

* Lambda functions cannot modify infrastructure
* Deployment user credentials are not used at runtime
* API Gateway cannot access data directly, only invoke functions

**Sources:** [docs/infrastucture/IAM_SETUP.md L322-L370](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L322-L370)

### Credential Management

**Deployment Credentials:**

* Use IAM user with access keys configured via `aws configure --profile`
* Store credentials in `~/.aws/credentials` (never commit to version control)
* Rotate access keys regularly (recommended: every 90 days)

**Runtime Credentials:**

* Lambda execution roles use temporary credentials via STS AssumeRole
* Credentials are automatically rotated by AWS
* No long-term credentials are stored in function code or environment variables

### Sensitive Variables

The LLM API key is passed as an environment variable to `generate_diagram` Lambda:

```markdown
environment {
  variables = {
    LLM_API_KEY = var.llm_api_key  # Marked as sensitive in variables.tf
  }
}
```

In Terraform, this variable should be marked `sensitive = true` to prevent it from appearing in logs or plan output.

**Sources:** [infrastructure/terraform/lambda.tf L71-L81](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L71-L81)

 [docs/infrastucture/IAM_SETUP.md L322-L370](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L322-L370)

---

## IAM Policy Reference

### Complete Deployment Policy Structure

The full deployment policy (`TerraformDeploymentPolicy`) includes the following statement IDs:

* `LambdaManagement`: All Lambda function and layer operations
* `APIGatewayManagement`: REST API configuration operations
* `DynamoDBManagement`: Table lifecycle management
* `S3Management`: Bucket and object operations
* `CloudFrontManagement`: Distribution and OAC configuration
* `IAMManagement`: Role and policy management
* `CloudWatchLogsManagement`: Log group operations
* `TerraformStateManagement`: S3 backend state file access
* `EC2NetworkingForLambda`: VPC configuration (if VPC-enabled Lambdas)

The complete policy definition is available at [docs/infrastucture/IAM_SETUP.md L68-L251](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L68-L251)

**Sources:** [docs/infrastucture/IAM_SETUP.md L68-L251](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L68-L251)

---

## Permission Verification

### Testing Lambda Execution Role

```

```

### Testing Deployment User Permissions

```

```

**Sources:** [docs/infrastucture/IAM_SETUP.md L371-L410](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L371-L410)

---

## Common Issues and Troubleshooting

### Permission Denied During Deployment

**Error:** `User: arn:aws:iam::xxx:user/terraform-deploy-user is not authorized to perform: iam:PassRole`

**Solution:** Ensure the deployment policy includes `iam:PassRole` action with appropriate resource scope.

### Lambda Cannot Write to CloudWatch Logs

**Error:** `Unable to write to CloudWatch Logs`

**Cause:** Lambda execution role missing CloudWatch Logs permissions

**Solution:** Verify the role includes:

* `logs:CreateLogGroup`
* `logs:CreateLogStream`
* `logs:PutLogEvents`

### API Gateway Cannot Invoke Lambda

**Error:** `Execution failed due to configuration error: Invalid permissions`

**Cause:** Missing resource-based policy on Lambda function

**Solution:** Verify `aws_lambda_permission` resource exists with:

* `principal = "apigateway.amazonaws.com"`
* `source_arn` matching API Gateway execution ARN

**Sources:** [docs/infrastucture/IAM_SETUP.md L371-L410](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L371-L410)