# Terraform Variables and Configuration

> **Relevant source files**
> * [infrastructure/scripts/lambda/requirements.txt](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/requirements.txt)
> * [infrastructure/terraform/tfplan](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/tfplan)
> * [infrastructure/terraform/variables.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf)

## Purpose and Scope

This document details the Terraform input variables and configuration system used to parameterize infrastructure provisioning for the Architecture AI Assistant. It covers variable definitions, types, default values, sensitivity settings, and how these variables flow through the deployment pipeline to configure AWS resources and Lambda function environments.

For the complete Terraform infrastructure modules that consume these variables, see [Lambda Infrastructure](/dotpep/architecture-ai-assistant/5.1-lambda-infrastructure), [API Gateway Configuration](/dotpep/architecture-ai-assistant/5.2-api-gateway-configuration), [CloudFront and S3 Configuration](/dotpep/architecture-ai-assistant/5.3-cloudfront-and-s3-configuration), and [IAM Roles and Security](/dotpep/architecture-ai-assistant/5.4-iam-roles-and-security). For the deployment process that provides variable values, see [Deployment Guide](/dotpep/architecture-ai-assistant/6-deployment-guide) and [Environment Configuration](/dotpep/architecture-ai-assistant/6.3-environment-configuration).

---

## Variable Definition Overview

The Terraform configuration defines 10 input variables in [infrastructure/terraform/variables.tf L1-L53](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L1-L53)

 that control all aspects of infrastructure provisioning. These variables fall into three categories: AWS infrastructure configuration, resource naming conventions, and LLM API integration settings.

### Variable Declaration Structure

```

```

**Sources:** [infrastructure/terraform/variables.tf L1-L53](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L1-L53)

---

## AWS Infrastructure Variables

These variables control the AWS region, environment designation, and core infrastructure settings.

| Variable Name | Type | Default | Description | Used By |
| --- | --- | --- | --- | --- |
| `aws_region` | string | `"us-east-1"` | AWS region for resource deployment | All Terraform modules |
| `environment` | string | `"dev"` | Environment name for resource tagging | All Terraform modules |
| `project_name` | string | `"architecture-ai-assistant"` | Base name for resource naming | All Terraform modules |

### aws_region Variable

Defined in [infrastructure/terraform/variables.tf L4-L8](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L4-L8)

 this variable specifies the AWS region where all resources are provisioned. The default value `"us-east-1"` is used unless overridden via `terraform.tfvars` or command-line arguments.

```

```

The region value is consumed by the AWS provider configuration and affects:

* Lambda function deployment locations
* DynamoDB table region
* S3 bucket region
* CloudFront origin configuration
* API Gateway regional endpoints

### environment Variable

The environment designation [infrastructure/terraform/variables.tf L10-L14](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L10-L14)

 enables multi-environment deployments by prefixing resource names and applying environment-specific tags. Common values include `"dev"`, `"staging"`, and `"prod"`.

### project_name Variable

The project name [infrastructure/terraform/variables.tf L16-L20](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L16-L20)

 serves as the base identifier for constructing resource names throughout the infrastructure, ensuring consistent naming conventions across all AWS resources.

**Sources:** [infrastructure/terraform/variables.tf L4-L20](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L4-L20)

---

## Resource Naming Variables

These variables define specific names for storage resources used by the application.

| Variable Name | Type | Default | Sensitive | Purpose |
| --- | --- | --- | --- | --- |
| `s3_bucket_name` | string | `"architecture-ai-assistant-bucket"` | No | S3 bucket for frontend and diagrams |
| `dynamodb_table_name` | string | `"chat_history"` | No | DynamoDB table for chat persistence |

### s3_bucket_name Variable

Defined in [infrastructure/terraform/variables.tf L22-L26](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L22-L26)

 this variable names the S3 bucket that stores:

* Frontend SPA assets (`/frontend/`)
* Generated diagram images (`/diagrams/*.png`)
* Diagram markdown source (`/diagrams/*.md`)

The bucket name must be globally unique across AWS and is used by:

* S3 bucket resource creation in `s3.tf`
* CloudFront origin configuration in `cloudfront.tf`
* Lambda function environment variables for diagram storage

### dynamodb_table_name Variable

The DynamoDB table name [infrastructure/terraform/variables.tf L28-L32](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L28-L32)

 identifies the table storing chat history records. This name is referenced by:

* DynamoDB table resource in `dynamodb.tf`
* Lambda functions via the `DYNAMODB_TABLE` environment variable
* IAM policies granting Lambda access to the table

**Sources:** [infrastructure/terraform/variables.tf L22-L32](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L22-L32)

---

## LLM Integration Variables

Three sensitive variables configure the external LLM API integration used by the `generate_diagram` Lambda function.

```

```

### llm_api_endpoint Variable

Defined in [infrastructure/terraform/variables.tf L34-L39](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L34-L39)

 with `sensitive = true`, this variable contains the base URL of the OpenAI-compatible LLM API. The sensitivity marking ensures:

* Values are redacted in Terraform plan/apply output
* The value is not displayed in logs
* State file encryption protects the value at rest

Example values:

* `"https://api.openai.com/v1"`
* `"https://api.groq.com/openai/v1"`
* Custom self-hosted LLM endpoints

### llm_api_key Variable

The API authentication key [infrastructure/terraform/variables.tf L41-L46](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L41-L46)

 is also marked `sensitive = true`. This credential is:

* Stored encrypted in `terraform.tfstate`
* Injected as the `LLM_API_KEY` environment variable in the `generate_diagram` Lambda
* Never logged or exposed in deployment outputs

### llm_model Variable

The model identifier [infrastructure/terraform/variables.tf L48-L52](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L48-L52)

 specifies which LLM model to use for diagram generation. Default value `"llama-3.3-70b-versatile"` targets Groq's API, but can be overridden for other providers:

* `"gpt-4"` or `"gpt-3.5-turbo"` for OpenAI
* `"claude-3-opus"` for Anthropic
* Custom model names for self-hosted deployments

**Sources:** [infrastructure/terraform/variables.tf L34-L52](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L34-L52)

---

## Variable Flow Through Infrastructure

This diagram maps how variables flow from definition through Terraform modules to deployed AWS resources and Lambda execution environments.

```

```

### Variable Precedence

Terraform resolves variable values in the following precedence order (highest to lowest):

1. **Command-line `-var` flags**: `terraform apply -var="environment=prod"`
2. **Environment variables**: `export TF_VAR_environment=prod`
3. **`terraform.tfvars` file**: Key-value pairs in the workspace directory
4. **`*.auto.tfvars` files**: Automatically loaded variable files
5. **Default values**: Specified in [infrastructure/terraform/variables.tf L1-L53](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L1-L53)

### Variable Usage in Lambda Configuration

The Lambda module consumes these variables to configure function environment variables. For example, the `generate_diagram` function receives:

```

```

These environment variables are then accessed by the Lambda Python code using `os.environ` calls.

**Sources:** [infrastructure/terraform/variables.tf L1-L53](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L1-L53)

---

## Variable Override Mechanisms

### Using terraform.tfvars

Create a `terraform.tfvars` file in the `infrastructure/terraform/` directory (this file is gitignored):

```

```

### Using Environment Variables

Export variables with the `TF_VAR_` prefix:

```

```

### Using Command-Line Arguments

Pass variables directly during `terraform apply`:

```

```

### Integration with deploy.sh

The deployment script [infrastructure/scripts/deploy.sh](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh)

 reads sensitive variables from environment variables and passes them to Terraform automatically. Users must set:

```

```

The script then converts these to `TF_VAR_*` format before invoking Terraform.

**Sources:** [infrastructure/terraform/variables.tf L1-L53](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L1-L53)

---

## Security Considerations

### Sensitive Variable Handling

The two LLM API variables are marked `sensitive = true` [infrastructure/terraform/variables.tf L37-L44](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L37-L44)

 which triggers special handling:

| Security Measure | Implementation | Purpose |
| --- | --- | --- |
| **Redacted Output** | Terraform CLI masks values in logs | Prevents credential leakage in CI/CD logs |
| **State Encryption** | Values encrypted in `terraform.tfstate` | Protects credentials at rest |
| **No Plan Display** | Sensitive values show as `(sensitive value)` | Prevents exposure during review |
| **Environment Isolation** | Lambda environment variables not logged | Prevents CloudWatch log exposure |

### State File Protection

The `terraform.tfstate` file contains all variable values, including sensitive ones. Protection measures:

1. **File excluded from git**: Listed in `.gitignore`
2. **Remote state recommended**: Use S3 backend with encryption for production
3. **Access control**: Restrict state file access via IAM policies
4. **Encryption at rest**: Enable S3 bucket encryption if using remote state

### Best Practices

```

```

**Recommendations:**

1. Never commit `terraform.tfvars` or `.env` files containing secrets
2. Use environment variables for CI/CD pipelines
3. Rotate `llm_api_key` regularly
4. Enable S3 backend with encryption for production deployments
5. Use AWS Secrets Manager for sensitive values in production

**Sources:** [infrastructure/terraform/variables.tf L34-L46](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L34-L46)

---

## Environment-Specific Configuration

The `environment` variable [infrastructure/terraform/variables.tf L10-L14](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L10-L14)

 enables deploying multiple isolated environments from the same Terraform configuration.

### Resource Naming Pattern

Most resources incorporate the environment value in their names:

```
{project_name}-{environment}-{resource_type}
```

Examples:

* `architecture-ai-assistant-dev-lambda-generate`
* `architecture-ai-assistant-prod-api-gateway`
* `architecture-ai-assistant-staging-s3-bucket`

### Multi-Environment Setup

To deploy multiple environments, create separate variable files:

**terraform.dev.tfvars:**

```

```

**terraform.prod.tfvars:**

```

```

Deploy using:

```

```

### Workspace-Based Isolation

Alternatively, use Terraform workspaces with environment-specific variables:

```

```

**Sources:** [infrastructure/terraform/variables.tf L10-L14](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L10-L14)

---

## Variable Dependencies in Infrastructure Modules

### Lambda Module Dependencies

The Lambda configuration requires all variables to properly configure the three functions:

* **Environment Variables**: LLM API settings, storage locations
* **IAM Policies**: Derived from `s3_bucket_name` and `dynamodb_table_name` for least-privilege access
* **Function Names**: Constructed from `project_name` and `environment`

### S3 Module Dependencies

S3 bucket configuration uses:

* `s3_bucket_name`: Primary bucket identifier
* `project_name` + `environment`: Bucket tags and naming conventions

### DynamoDB Module Dependencies

Table configuration requires:

* `dynamodb_table_name`: Table name
* `environment`: Resource tagging

### API Gateway Module Dependencies

API Gateway resources use:

* `project_name`: API name construction
* `environment`: Stage naming and deployment tags

**Sources:** [infrastructure/terraform/variables.tf L1-L53](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L1-L53)

---

## Summary Table

| Variable | Type | Default | Sensitive | Primary Consumer | Purpose |
| --- | --- | --- | --- | --- | --- |
| `aws_region` | string | `us-east-1` | No | AWS Provider | Region selection |
| `environment` | string | `dev` | No | All modules | Environment designation |
| `project_name` | string | `architecture-ai-assistant` | No | All modules | Resource naming base |
| `s3_bucket_name` | string | `architecture-ai-assistant-bucket` | No | S3, CloudFront, Lambda | Bucket identifier |
| `dynamodb_table_name` | string | `chat_history` | No | DynamoDB, Lambda | Table name |
| `llm_api_endpoint` | string | `""` | Yes | Lambda (generate_diagram) | LLM API URL |
| `llm_api_key` | string | `""` | Yes | Lambda (generate_diagram) | LLM API authentication |
| `llm_model` | string | `llama-3.3-70b-versatile` | No | Lambda (generate_diagram) | LLM model selection |

**Sources:** [infrastructure/terraform/variables.tf L1-L53](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L1-L53)