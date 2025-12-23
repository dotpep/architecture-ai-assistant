# Infrastructure as Code

> **Relevant source files**
> * [infrastructure/scripts/lambda/requirements.txt](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/requirements.txt)
> * [infrastructure/terraform/api_gateway.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf)
> * [infrastructure/terraform/cloudfront.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf)
> * [infrastructure/terraform/lambda.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf)
> * [infrastructure/terraform/tfplan](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/tfplan)
> * [infrastructure/terraform/variables.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf)
> * [src/backend/shared/aws_helpers.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/shared/aws_helpers.py)
> * [src/backend/shared/utils.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/shared/utils.py)
> * [src/frontend/src/components/DownloadButtons.tsx](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/frontend/src/components/DownloadButtons.tsx)

## Purpose and Scope

This document provides an overview of the Terraform-based Infrastructure as Code (IaC) implementation for the Architecture AI Assistant. It covers the organization of Terraform modules, resource dependency relationships, and the overall infrastructure provisioning approach. For detailed information about specific resource types, see:

* Lambda function configuration: [5.1](/dotpep/architecture-ai-assistant/5.1-lambda-infrastructure)
* API Gateway setup: [5.2](/dotpep/architecture-ai-assistant/5.2-api-gateway-configuration)
* CloudFront and S3 configuration: [5.3](/dotpep/architecture-ai-assistant/5.3-cloudfront-and-s3-configuration)
* IAM roles and security policies: [5.4](/dotpep/architecture-ai-assistant/5.4-iam-roles-and-security)
* Terraform variables and configuration management: [5.5](/dotpep/architecture-ai-assistant/5.5-terraform-variables-and-configuration)

For deployment procedures and the deployment script, see [6.1](/dotpep/architecture-ai-assistant/6.1-deployment-script).

---

## Terraform Module Structure

The infrastructure code is organized into modular Terraform files, each responsible for a specific AWS service or resource category. This separation enables independent development, testing, and maintenance of each infrastructure component.

### File Organization Diagram

```mermaid
flowchart TD

main["main.tf<br>Provider & Backend"]
vars["variables.tf<br>Input Variables"]
outputs["outputs.tf<br>Output Values"]
lambda["lambda.tf<br>Lambda Functions & Layers"]
apigw["api_gateway.tf<br>REST API & Routes"]
cf["cloudfront.tf<br>CDN Distribution"]
s3["s3.tf<br>Storage Buckets"]
ddb["dynamodb.tf<br>chat_history Table"]
iam["iam.tf<br>Roles & Policies"]
lambda_res["aws_lambda_function<br>aws_lambda_layer_version"]
apigw_res["aws_api_gateway_rest_api<br>aws_api_gateway_deployment"]
cf_res["aws_cloudfront_distribution<br>aws_cloudfront_cache_policy"]
s3_res["aws_s3_bucket<br>aws_s3_bucket_policy"]
ddb_res["aws_dynamodb_table"]
iam_res["aws_iam_role<br>aws_iam_policy"]

lambda --> lambda_res
apigw --> apigw_res
cf --> cf_res
s3 --> s3_res
ddb --> ddb_res
iam --> iam_res

subgraph subGraph1 ["Resources Created"]
    lambda_res
    apigw_res
    cf_res
    s3_res
    ddb_res
    iam_res
end

subgraph infrastructure/terraform/ ["infrastructure/terraform/"]
    main
    vars
    outputs
    lambda
    apigw
    cf
    s3
    ddb
    iam
    main --> lambda
    main --> apigw
    main --> cf
    main --> s3
    main --> ddb
    main --> iam
    vars --> lambda
    vars --> apigw
    vars --> cf
    lambda --> outputs
    apigw --> outputs
    cf --> outputs
end
```

**Sources:** [infrastructure/terraform/lambda.tf L1-L184](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L1-L184)

 [infrastructure/terraform/api_gateway.tf L1-L449](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L1-L449)

 [infrastructure/terraform/cloudfront.tf L1-L179](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L1-L179)

 [infrastructure/terraform/variables.tf L1-L53](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L1-L53)

### Terraform Configuration Files

| File | Primary Resources | Lines of Code | Purpose |
| --- | --- | --- | --- |
| `main.tf` | Provider configuration | ~50 | AWS provider setup and backend configuration |
| `variables.tf` | Variable declarations | 53 | Input parameters for customization |
| `outputs.tf` | Output values | ~50 | Export values for deployment scripts |
| `lambda.tf` | Lambda functions, layers | 184 | Function definitions and configurations |
| `api_gateway.tf` | API Gateway resources | 449 | REST API structure and Lambda integrations |
| `cloudfront.tf` | CloudFront distribution | 179 | CDN configuration and cache policies |
| `s3.tf` | S3 buckets | ~100 | Storage for frontend and diagrams |
| `dynamodb.tf` | DynamoDB table | ~50 | Chat history storage schema |
| `iam.tf` | IAM roles and policies | ~300 | Least-privilege security policies |

**Sources:** [infrastructure/terraform/lambda.tf L1-L184](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L1-L184)

 [infrastructure/terraform/api_gateway.tf L1-L449](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L1-L449)

 [infrastructure/terraform/cloudfront.tf L1-L179](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L1-L179)

---

## Resource Dependency Graph

The Terraform resources have explicit and implicit dependencies that determine the order of creation and deletion. Understanding these dependencies is critical for troubleshooting deployment issues and managing infrastructure changes.

### Core Infrastructure Dependencies

```mermaid
flowchart TD

s3_bucket["aws_s3_bucket.main"]
ddb_table["aws_dynamodb_table.chat_history"]
iam_lambda_gen["aws_iam_role.lambda_generate_diagram"]
iam_lambda_chat["aws_iam_role.lambda_chat_crud"]
iam_lambda_hist["aws_iam_role.lambda_get_history"]
lambda_layer["aws_lambda_layer_version.shared_dependencies"]
lambda_gen["aws_lambda_function.generate_diagram"]
lambda_chat["aws_lambda_function.chat_crud"]
lambda_hist["aws_lambda_function.get_history"]
api_rest["aws_api_gateway_rest_api.main"]
api_resource_gen["aws_api_gateway_resource.diagram_generate"]
api_method_gen["aws_api_gateway_method.diagram_generate_post"]
api_integration["aws_api_gateway_integration.diagram_generate_post"]
api_deployment["aws_api_gateway_deployment.main"]
api_stage["aws_api_gateway_stage.main"]
cf_oac["aws_cloudfront_origin_access_control.main"]
cf_dist["aws_cloudfront_distribution.frontend"]
s3_policy["aws_s3_bucket_policy.main"]

iam_lambda_gen --> lambda_gen
iam_lambda_chat --> lambda_chat
iam_lambda_hist --> lambda_hist
ddb_table --> lambda_gen
ddb_table --> lambda_chat
ddb_table --> lambda_hist
s3_bucket --> lambda_gen
lambda_gen --> api_integration
s3_bucket --> cf_oac
cf_dist --> lambda_gen

subgraph subGraph3 ["Distribution Layer"]
    cf_oac
    cf_dist
    s3_policy
    cf_oac --> cf_dist
    cf_dist --> s3_policy
end

subgraph subGraph2 ["API Layer"]
    api_rest
    api_resource_gen
    api_method_gen
    api_integration
    api_deployment
    api_stage
    api_rest --> api_resource_gen
    api_resource_gen --> api_method_gen
    api_method_gen --> api_integration
    api_integration --> api_deployment
    api_deployment --> api_stage
end

subgraph subGraph1 ["Compute Layer"]
    lambda_layer
    lambda_gen
    lambda_chat
    lambda_hist
    lambda_layer --> lambda_gen
    lambda_layer --> lambda_chat
    lambda_layer --> lambda_hist
end

subgraph subGraph0 ["Foundation Layer"]
    s3_bucket
    ddb_table
    iam_lambda_gen
    iam_lambda_chat
    iam_lambda_hist
end
```

**Sources:** [infrastructure/terraform/lambda.tf L57-L87](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L57-L87)

 [infrastructure/terraform/api_gateway.tf L5-L449](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L5-L449)

 [infrastructure/terraform/cloudfront.tf L8-L178](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L8-L178)

### Dependency Types

The infrastructure uses three types of dependencies:

1. **Explicit Dependencies** (solid arrows): Created using Terraform references like `aws_iam_role.lambda_generate_diagram.arn`
2. **Implicit Dependencies** (dashed arrows): Environment variables that reference other resources
3. **Logical Dependencies**: Order enforced through `depends_on` blocks

**Sources:** [infrastructure/terraform/lambda.tf L60-L81](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L60-L81)

---

## Lambda Function Infrastructure Pattern

The Lambda functions follow a consistent infrastructure pattern with shared dependencies and environment variable injection.

### Lambda Layer and Function Structure

```mermaid
flowchart TD

layer_zip["lambda_layer.zip<br>Python packages"]
requirements["requirements.txt<br>requests>=2.28.0"]
gen_func["aws_lambda_function.generate_diagram<br>Timeout: 60s, Memory: 512MB"]
chat_func["aws_lambda_function.chat_crud<br>Timeout: 10s, Memory: 256MB"]
hist_func["aws_lambda_function.get_history<br>Timeout: 10s, Memory: 256MB"]
env_ddb["DYNAMODB_TABLE_NAME"]
env_s3["S3_BUCKET_NAME"]
env_cf["CLOUDFRONT_URL"]
env_llm_ep["LLM_API_ENDPOINT"]
env_llm_key["LLM_API_KEY"]
env_llm_model["LLM_MODEL"]
log_gen["/aws/lambda/...-generate-diagram"]
log_chat["/aws/lambda/...-chat-crud"]
log_hist["/aws/lambda/...-get-history"]

layer_zip --> gen_func
layer_zip --> chat_func
layer_zip --> hist_func
env_ddb --> gen_func
env_ddb --> chat_func
env_ddb --> hist_func
env_s3 --> gen_func
env_cf --> gen_func
env_llm_ep --> gen_func
env_llm_key --> gen_func
env_llm_model --> gen_func
gen_func --> log_gen
chat_func --> log_chat
hist_func --> log_hist

subgraph subGraph3 ["CloudWatch Logs"]
    log_gen
    log_chat
    log_hist
end

subgraph subGraph2 ["Environment Variables"]
    env_ddb
    env_s3
    env_cf
    env_llm_ep
    env_llm_key
    env_llm_model
end

subgraph subGraph1 ["Lambda Functions"]
    gen_func
    chat_func
    hist_func
end

subgraph subGraph0 ["Lambda Layer Package"]
    layer_zip
    requirements
    requirements --> layer_zip
end
```

**Sources:** [infrastructure/terraform/lambda.tf L8-L19](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L8-L19)

 [infrastructure/terraform/lambda.tf L57-L87](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L57-L87)

 [infrastructure/terraform/lambda.tf L89-L97](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L89-L97)

 [infrastructure/scripts/lambda/requirements.txt L1-L2](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/requirements.txt#L1-L2)

### Lambda Configuration Table

| Function | Handler | Runtime | Timeout | Memory | Environment Variables |
| --- | --- | --- | --- | --- | --- |
| `generate_diagram` | `lambda_function.handler` | python3.11 | 60s | 512MB | 7 variables including LLM config |
| `chat_crud` | `lambda_function.handler` | python3.11 | 10s | 256MB | 2 variables: DynamoDB, environment |
| `get_history` | `lambda_function.handler` | python3.11 | 10s | 256MB | 2 variables: DynamoDB, environment |

**Shared Layer:** `aws_lambda_layer_version.shared_dependencies` provides the `requests` library to all functions.

**Sources:** [infrastructure/terraform/lambda.tf L57-L87](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L57-L87)

 [infrastructure/terraform/lambda.tf L105-L130](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L105-L130)

 [infrastructure/terraform/lambda.tf L148-L173](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L148-L173)

---

## API Gateway Resource Hierarchy

The API Gateway is structured as a hierarchical REST API with distinct resource paths and method integrations for each Lambda function.

### API Resource Tree and Lambda Integrations

```mermaid
flowchart TD

root["aws_api_gateway_rest_api.main<br>/"]
api_res["aws_api_gateway_resource.api<br>/api"]
diagram_res["aws_api_gateway_resource.diagram<br>/api/diagram"]
chat_res["aws_api_gateway_resource.chat<br>/api/chat"]
gen_res["aws_api_gateway_resource.diagram_generate<br>/api/diagram/generate"]
hist_res["aws_api_gateway_resource.chat_history<br>/api/chat/history"]
save_res["aws_api_gateway_resource.chat_save<br>/api/chat/save"]
gen_post["aws_api_gateway_method.diagram_generate_post<br>POST"]
gen_options["aws_api_gateway_method.diagram_generate_options<br>OPTIONS"]
hist_get["aws_api_gateway_method.chat_history_get<br>GET"]
hist_options["aws_api_gateway_method.chat_history_options<br>OPTIONS"]
save_post["aws_api_gateway_method.chat_save_post<br>POST"]
save_options["aws_api_gateway_method.chat_save_options<br>OPTIONS"]
int_gen["aws_api_gateway_integration.diagram_generate_post<br>AWS_PROXY → generate_diagram"]
int_hist["aws_api_gateway_integration.chat_history_get<br>AWS_PROXY → get_history"]
int_save["aws_api_gateway_integration.chat_save_post<br>AWS_PROXY → chat_crud"]
deploy["aws_api_gateway_deployment.main"]
stage["aws_api_gateway_stage.main"]

root --> api_res
api_res --> diagram_res
api_res --> chat_res
diagram_res --> gen_res
chat_res --> hist_res
chat_res --> save_res
gen_res --> gen_post
gen_res --> gen_options
hist_res --> hist_get
hist_res --> hist_options
save_res --> save_post
save_res --> save_options
gen_post --> int_gen
hist_get --> int_hist
save_post --> int_save
int_gen --> deploy
int_hist --> deploy
int_save --> deploy
deploy --> stage
```

**Sources:** [infrastructure/terraform/api_gateway.tf L5-L58](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L5-L58)

 [infrastructure/terraform/api_gateway.tf L67-L106](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L67-L106)

 [infrastructure/terraform/api_gateway.tf L390-L448](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L390-L448)

### CORS Configuration Pattern

Each API resource implements CORS through OPTIONS methods with mock integrations. The pattern is consistent across all three endpoints:

1. **OPTIONS Method**: `authorization = "NONE"`, `http_method = "OPTIONS"`
2. **Mock Integration**: Returns `statusCode: 200` without invoking Lambda
3. **Integration Response**: Sets CORS headers: * `Access-Control-Allow-Origin: '*'` * `Access-Control-Allow-Headers: 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'` * `Access-Control-Allow-Methods: 'POST,OPTIONS'` (or GET for history endpoint)

**Sources:** [infrastructure/terraform/api_gateway.tf L111-L157](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L111-L157)

 [infrastructure/terraform/api_gateway.tf L208-L254](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L208-L254)

 [infrastructure/terraform/api_gateway.tf L305-L351](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L305-L351)

---

## CloudFront Distribution Architecture

The CloudFront distribution serves as the unified entry point for both the React frontend and generated diagram files, implementing multi-origin routing and caching strategies.

### CloudFront Origins and Cache Behaviors

```mermaid
flowchart TD

client_root["GET /<br>index.html"]
client_static["GET /static/*<br>JS, CSS"]
client_diagram["GET /diagrams/*<br>PNG, MD"]
cf["aws_cloudfront_distribution.frontend"]
default_behavior["default_cache_behavior<br>frontend_cache_policy<br>TTL: 1-86400s"]
static_behavior["ordered_cache_behavior[0]<br>path_pattern: /static/*<br>frontend_cache_policy"]
diagram_behavior["ordered_cache_behavior[1]<br>path_pattern: /diagrams/*<br>diagrams_cache_policy<br>TTL: 0-3600s"]
origin_fe["S3-frontend<br>origin_path: /frontend"]
origin_diag["S3-diagrams<br>origin_path: ''"]
s3_fe_folder["/frontend/<br>React SPA"]
s3_diag_folder["/diagrams/<br>PNG + MD files"]

client_root --> cf
client_static --> cf
client_diagram --> cf
default_behavior --> origin_fe
static_behavior --> origin_fe
diagram_behavior --> origin_diag
origin_fe --> s3_fe_folder
origin_diag --> s3_diag_folder

subgraph subGraph3 ["S3 Bucket"]
    s3_fe_folder
    s3_diag_folder
end

subgraph subGraph2 ["S3 Origins"]
    origin_fe
    origin_diag
end

subgraph subGraph1 ["CloudFront Distribution"]
    cf
    default_behavior
    static_behavior
    diagram_behavior
    cf --> default_behavior
    cf --> static_behavior
    cf --> diagram_behavior
end

subgraph subGraph0 ["Client Requests"]
    client_root
    client_static
    client_diagram
end
```

**Sources:** [infrastructure/terraform/cloudfront.tf L72-L148](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L72-L148)

 [infrastructure/terraform/cloudfront.tf L21-L64](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L21-L64)

### Cache Policy Configuration

The CloudFront distribution uses two custom cache policies optimized for different content types:

**Frontend Cache Policy** (`aws_cloudfront_cache_policy.frontend_cache`):

* Default TTL: 86400s (1 day)
* Max TTL: 604800s (7 days)
* Min TTL: 3600s (1 hour)
* Compression: Brotli + Gzip enabled
* Used for: React SPA assets (HTML, JS, CSS)

**Diagrams Cache Policy** (`aws_cloudfront_cache_policy.diagrams_cache`):

* Default TTL: 3600s (1 hour)
* Max TTL: 86400s (1 day)
* Min TTL: 0s
* Compression: Brotli + Gzip enabled
* Used for: Generated diagram files (PNG, Markdown)

**Sources:** [infrastructure/terraform/cloudfront.tf L20-L41](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L20-L41)

 [infrastructure/terraform/cloudfront.tf L43-L64](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L43-L64)

---

## Placeholder Lambda Code Strategy

Terraform requires Lambda function code to exist during initial provisioning, but the actual function code is deployed separately by the deployment script. This creates a chicken-and-egg problem solved through placeholder Lambda functions.

### Placeholder Code Pattern

```mermaid
flowchart TD

placeholder["data.archive_file.lambda_placeholder<br>Inline Python placeholder"]
tf_lambda["aws_lambda_function.*<br>Uses placeholder zip"]
real_code["Actual Lambda code<br>src/backend/lambdas/*"]
packaged["lambda_functions.zip<br>Real implementation"]
aws_update["AWS Lambda UpdateFunctionCode"]

aws_update --> tf_lambda

subgraph subGraph1 ["Deployment Script Phase"]
    real_code
    packaged
    aws_update
    real_code --> packaged
    packaged --> aws_update
end

subgraph subGraph0 ["Terraform Apply Phase"]
    placeholder
    tf_lambda
    placeholder --> tf_lambda
end
```

The placeholder code defined in [infrastructure/terraform/lambda.tf L26-L48](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L26-L48)

 provides a minimal viable Lambda function that:

1. Returns HTTP 200 status
2. Includes CORS headers
3. Returns a JSON message: `{'message': 'Placeholder - deploy actual function code'}`

This allows Terraform to create the Lambda function resources, after which the deployment script updates them with the real function code.

**Sources:** [infrastructure/terraform/lambda.tf L26-L48](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L26-L48)

 [infrastructure/terraform/lambda.tf L66-L67](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L66-L67)

 [infrastructure/terraform/lambda.tf L114-L115](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L114-L115)

 [infrastructure/terraform/lambda.tf L157-L158](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L157-L158)

---

## Infrastructure State Management

Terraform maintains the infrastructure state in `terraform.tfstate`, which tracks the mapping between declared resources and actual AWS resources. The state file is critical for detecting drift and planning updates.

### State Management Strategy

| Aspect | Implementation |
| --- | --- |
| **State Storage** | Local file `terraform.tfstate` in `infrastructure/terraform/` |
| **State Locking** | Not implemented (single-user deployment assumed) |
| **State Backup** | `terraform.tfstate.backup` created automatically |
| **Sensitive Data** | Contains sensitive values (API keys, ARNs) - not committed to Git |
| **State Refresh** | Automatic on `terraform plan` and `terraform apply` |

### Deployment Redeployment Triggers

The `aws_api_gateway_deployment` resource uses a SHA-1 hash of all method and integration resource IDs to trigger redeployment when the API structure changes:

```
triggers = {
  redeployment = sha1(jsonencode([
    aws_api_gateway_resource.api.id,
    aws_api_gateway_method.diagram_generate_post.id,
    aws_api_gateway_integration.diagram_generate_post.id,
    ...
  ]))
}
```

This ensures API Gateway stages are updated whenever methods or integrations change.

**Sources:** [infrastructure/terraform/api_gateway.tf L390-L437](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L390-L437)

---

## Resource Naming Convention

All AWS resources follow a consistent naming pattern that includes the project name, resource type, and environment:

**Pattern:** `${var.project_name}-{resource-type}-${var.environment}`

**Examples:**

* Lambda: `architecture-ai-assistant-generate-diagram-dev`
* API Gateway: `architecture-ai-assistant-api-dev`
* S3 Bucket: `architecture-ai-assistant-bucket-dev`
* DynamoDB: `chat_history` (environment-agnostic)
* CloudFront: Tagged as `architecture-ai-assistant-cloudfront`

This naming convention enables:

* Multi-environment deployments (dev, staging, prod)
* Resource identification in AWS Console
* Cost allocation and tracking
* Automated cleanup scripts

**Sources:** [infrastructure/terraform/lambda.tf L58](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L58-L58)

 [infrastructure/terraform/api_gateway.tf L6](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L6-L6)

 [infrastructure/terraform/variables.tf L16-L32](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L16-L32)

---

## Lifecycle Management

Terraform resources implement lifecycle rules to prevent accidental data loss and ensure smooth updates:

### Lambda Layer Lifecycle

```
lifecycle {
  create_before_destroy = true
}
```

Ensures a new layer version is created and attached to Lambda functions before deleting the old version, preventing function downtime.

**Sources:** [infrastructure/terraform/lambda.tf L16-L18](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L16-L18)

### API Gateway Deployment Lifecycle

```
lifecycle {
  create_before_destroy = true
}
```

Creates a new deployment before destroying the old one, ensuring API availability during updates.

**Sources:** [infrastructure/terraform/api_gateway.tf L416-L418](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L416-L418)

---

## Integration with Deployment Script

The Terraform infrastructure is designed to work in conjunction with `deploy.sh`, which orchestrates the complete deployment process:

1. **Phase 1**: Package Lambda layer and function code (outside Terraform)
2. **Phase 2**: Run `terraform init`, `terraform plan`, `terraform apply`
3. **Phase 3**: Build React frontend using Terraform outputs (API Gateway URL)
4. **Phase 4**: Upload frontend to S3 and invalidate CloudFront cache

Terraform provides outputs (`outputs.tf`) that the deployment script uses:

* `cloudfront_url`: Frontend distribution URL
* `api_gateway_url`: Backend API endpoint
* `s3_bucket_name`: Target bucket for frontend upload

**Sources:** See [6.1](/dotpep/architecture-ai-assistant/6.1-deployment-script) for deployment script details

---

## Summary

The Terraform infrastructure implements a modular, maintainable Infrastructure as Code solution with:

* **9 separate configuration files** organized by AWS service
* **50+ AWS resources** provisioned across Lambda, API Gateway, CloudFront, S3, DynamoDB, and IAM
* **Explicit dependency management** ensuring correct creation and deletion order
* **Environment-specific deployments** through variable parameterization
* **Placeholder code strategy** solving the Lambda code bootstrapping problem
* **Consistent naming conventions** for multi-environment support

The infrastructure supports the complete Architecture AI Assistant application stack while maintaining separation of concerns and enabling independent evolution of each component.

**Sources:** [infrastructure/terraform/lambda.tf L1-L184](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf#L1-L184)

 [infrastructure/terraform/api_gateway.tf L1-L449](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L1-L449)

 [infrastructure/terraform/cloudfront.tf L1-L179](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/cloudfront.tf#L1-L179)

 [infrastructure/terraform/variables.tf L1-L53](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf#L1-L53)