# API Gateway Configuration

> **Relevant source files**
> * [.kiro/specs/architecture-ai-assistant/tasks.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/.kiro/specs/architecture-ai-assistant/tasks.md)
> * [infrastructure/terraform/api_gateway.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf)
> * [infrastructure/terraform/lambda.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf)

## Purpose and Scope

This document details the Terraform configuration for the AWS API Gateway REST API that serves as the HTTP interface for the Architecture AI Assistant backend. The API Gateway routes frontend requests to the appropriate Lambda functions and handles CORS for cross-origin access. For Lambda function infrastructure details, see [Lambda Infrastructure](/dotpep/architecture-ai-assistant/5.1-lambda-infrastructure). For IAM security policies governing API access, see [IAM Roles and Security](/dotpep/architecture-ai-assistant/5.4-iam-roles-and-security).

**Sources:** [infrastructure/terraform/api_gateway.tf L1-L449](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L1-L449)

---

## REST API Resource Structure

The API Gateway uses a hierarchical resource structure to organize endpoints. The root REST API resource branches into `/api`, which further divides into `/diagram` and `/chat` namespaces.

### Resource Hierarchy Diagram

```

```

**Sources:** [infrastructure/terraform/api_gateway.tf L5-L58](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L5-L58)

### REST API Definition

The REST API is defined with a REGIONAL endpoint configuration and named using the `project_name` and `environment` variables.

| Attribute | Value |
| --- | --- |
| Resource Type | `aws_api_gateway_rest_api` |
| Resource Name | `main` |
| Endpoint Type | `REGIONAL` |
| Naming Pattern | `${var.project_name}-api-${var.environment}` |

**Sources:** [infrastructure/terraform/api_gateway.tf L5-L16](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L5-L16)

---

## Endpoint Definitions

The API Gateway exposes three primary endpoints, each mapped to a specific Lambda function using AWS_PROXY integration.

### Endpoint to Lambda Mapping

```

```

**Sources:** [infrastructure/terraform/api_gateway.tf L62-L351](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L62-L351)

### POST /api/diagram/generate

This endpoint handles diagram generation requests by invoking the `generate_diagram` Lambda function.

**Resource Hierarchy:**

* Method: `aws_api_gateway_method.diagram_generate_post` [infrastructure/terraform/api_gateway.tf L67-L72](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L67-L72)
* Integration: `aws_api_gateway_integration.diagram_generate_post` [infrastructure/terraform/api_gateway.tf L75-L82](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L75-L82)
* Method Response: `aws_api_gateway_method_response.diagram_generate_post_200` [infrastructure/terraform/api_gateway.tf L85-L94](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L85-L94)
* Integration Response: `aws_api_gateway_integration_response.diagram_generate_post_200` [infrastructure/terraform/api_gateway.tf L97-L106](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L97-L106)

**Key Configuration:**

| Parameter | Value |
| --- | --- |
| HTTP Method | `POST` |
| Authorization | `NONE` |
| Integration Type | `AWS_PROXY` |
| Integration HTTP Method | `POST` |
| Lambda Function | `aws_lambda_function.generate_diagram.invoke_arn` |

**Sources:** [infrastructure/terraform/api_gateway.tf L62-L107](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L62-L107)

### GET /api/chat/history

This endpoint retrieves chat history with pagination by invoking the `get_history` Lambda function.

**Resource Hierarchy:**

* Method: `aws_api_gateway_method.chat_history_get` [infrastructure/terraform/api_gateway.tf L166-L171](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L166-L171)
* Integration: `aws_api_gateway_integration.chat_history_get` [infrastructure/terraform/api_gateway.tf L174-L181](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L174-L181)
* Method Response: `aws_api_gateway_method_response.chat_history_get_200` [infrastructure/terraform/api_gateway.tf L184-L193](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L184-L193)
* Integration Response: `aws_api_gateway_integration_response.chat_history_get_200` [infrastructure/terraform/api_gateway.tf L196-L205](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L196-L205)

**Key Configuration:**

| Parameter | Value |
| --- | --- |
| HTTP Method | `GET` |
| Authorization | `NONE` |
| Integration Type | `AWS_PROXY` |
| Integration HTTP Method | `POST` (Lambda always uses POST) |
| Lambda Function | `aws_lambda_function.get_history.invoke_arn` |

**Sources:** [infrastructure/terraform/api_gateway.tf L160-L205](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L160-L205)

### POST /api/chat/save

This endpoint saves chat messages to DynamoDB by invoking the `chat_crud` Lambda function.

**Resource Hierarchy:**

* Method: `aws_api_gateway_method.chat_save_post` [infrastructure/terraform/api_gateway.tf L263-L268](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L263-L268)
* Integration: `aws_api_gateway_integration.chat_save_post` [infrastructure/terraform/api_gateway.tf L271-L278](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L271-L278)
* Method Response: `aws_api_gateway_method_response.chat_save_post_200` [infrastructure/terraform/api_gateway.tf L281-L290](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L281-L290)
* Integration Response: `aws_api_gateway_integration_response.chat_save_post_200` [infrastructure/terraform/api_gateway.tf L293-L302](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L293-L302)

**Key Configuration:**

| Parameter | Value |
| --- | --- |
| HTTP Method | `POST` |
| Authorization | `NONE` |
| Integration Type | `AWS_PROXY` |
| Integration HTTP Method | `POST` |
| Lambda Function | `aws_lambda_function.chat_crud.invoke_arn` |

**Sources:** [infrastructure/terraform/api_gateway.tf L257-L302](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L257-L302)

---

## AWS_PROXY Integration Pattern

All three endpoints use the `AWS_PROXY` integration type, which provides a streamlined integration between API Gateway and Lambda. This pattern passes the entire HTTP request to the Lambda function as an event object and expects the Lambda to return a properly formatted HTTP response.

**Integration Characteristics:**

| Aspect | Detail |
| --- | --- |
| Integration Type | `AWS_PROXY` |
| Integration HTTP Method | `POST` (regardless of endpoint method) |
| Request Passthrough | Complete HTTP request mapped to Lambda event |
| Response Handling | Lambda returns full HTTP response with status code, headers, body |
| CORS Headers | Handled by Lambda function and integration responses |

The Lambda functions receive events containing `httpMethod`, `path`, `queryStringParameters`, `headers`, `body`, and other request metadata. They must return responses with `statusCode`, `headers`, and `body` fields.

**Sources:** [infrastructure/terraform/api_gateway.tf L75-L82](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L75-L82)

 [infrastructure/terraform/api_gateway.tf L174-L181](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L174-L181)

 [infrastructure/terraform/api_gateway.tf L271-L278](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L271-L278)

---

## CORS Configuration

Cross-Origin Resource Sharing (CORS) is configured for each endpoint using OPTIONS methods with MOCK integrations. This enables the React frontend hosted on CloudFront to make API calls from the browser.

### CORS Request Flow

```

```

**Sources:** [infrastructure/terraform/api_gateway.tf L110-L157](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L110-L157)

 [infrastructure/terraform/api_gateway.tf L207-L254](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L207-L254)

 [infrastructure/terraform/api_gateway.tf L304-L351](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L304-L351)

### CORS Headers Configuration

Each endpoint has a corresponding OPTIONS method that returns CORS headers:

| Header | Value | Purpose |
| --- | --- | --- |
| `Access-Control-Allow-Origin` | `*` | Allows requests from any origin |
| `Access-Control-Allow-Methods` | Endpoint-specific (e.g., `POST,OPTIONS`) | Specifies allowed HTTP methods |
| `Access-Control-Allow-Headers` | `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token` | Specifies allowed request headers |

**Example OPTIONS Configuration:**

For `/api/diagram/generate`, the OPTIONS method is defined as:

* Method: `aws_api_gateway_method.diagram_generate_options` [infrastructure/terraform/api_gateway.tf L111-L116](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L111-L116)
* Integration: `aws_api_gateway_integration.diagram_generate_options` (type: `MOCK`) [infrastructure/terraform/api_gateway.tf L118-L127](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L118-L127)
* Method Response: `aws_api_gateway_method_response.diagram_generate_options` [infrastructure/terraform/api_gateway.tf L129-L144](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L129-L144)
* Integration Response: `aws_api_gateway_integration_response.diagram_generate_options` [infrastructure/terraform/api_gateway.tf L146-L157](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L146-L157)

The MOCK integration uses a request template `{"statusCode": 200}` to return a static response without invoking any backend service.

**Sources:** [infrastructure/terraform/api_gateway.tf L110-L157](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L110-L157)

 [infrastructure/terraform/api_gateway.tf L207-L254](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L207-L254)

 [infrastructure/terraform/api_gateway.tf L304-L351](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L304-L351)

---

## Lambda Invocation Permissions

API Gateway requires explicit permissions to invoke Lambda functions. These are granted using `aws_lambda_permission` resources.

### Permission Resources

```

```

**Sources:** [infrastructure/terraform/api_gateway.tf L354-L383](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L354-L383)

### Permission Configuration

Each permission resource follows this pattern:

| Attribute | Value |
| --- | --- |
| `statement_id` | `AllowAPIGatewayInvoke` |
| `action` | `lambda:InvokeFunction` |
| `function_name` | Reference to specific Lambda function |
| `principal` | `apigateway.amazonaws.com` |
| `source_arn` | `${aws_api_gateway_rest_api.main.execution_arn}/*/*` |

The `source_arn` pattern `/*/*` allows any stage and any resource path within the API to invoke the Lambda function.

**Permission Resources:**

* `aws_lambda_permission.api_gateway_generate_diagram` [infrastructure/terraform/api_gateway.tf L359-L365](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L359-L365)
* `aws_lambda_permission.api_gateway_chat_crud` [infrastructure/terraform/api_gateway.tf L368-L374](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L368-L374)
* `aws_lambda_permission.api_gateway_get_history` [infrastructure/terraform/api_gateway.tf L377-L383](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L377-L383)

**Sources:** [infrastructure/terraform/api_gateway.tf L354-L383](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L354-L383)

---

## Deployment and Staging

The API Gateway requires explicit deployment after configuration changes. The deployment resource triggers redeployment when any API configuration changes.

### Deployment Resource

The `aws_api_gateway_deployment` resource creates a snapshot of the API configuration and makes it available at a stage URL.

**Key Configuration:**

| Attribute | Purpose |
| --- | --- |
| `rest_api_id` | References the REST API |
| `triggers` | SHA1 hash of all resource IDs to detect changes |
| `depends_on` | Explicit dependencies on all methods and integrations |
| `lifecycle.create_before_destroy` | Ensures zero-downtime deployments |

The `triggers` block computes a SHA1 hash of all resource IDs, method IDs, integration IDs, and response IDs. When any of these change, Terraform detects the change and creates a new deployment [infrastructure/terraform/api_gateway.tf L393-L414](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L393-L414)

**Sources:** [infrastructure/terraform/api_gateway.tf L390-L437](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L390-L437)

### Stage Resource

The `aws_api_gateway_stage` resource creates a named stage that references the deployment.

**Configuration:**

| Attribute | Value |
| --- | --- |
| Resource Name | `aws_api_gateway_stage.main` |
| `deployment_id` | `aws_api_gateway_deployment.main.id` |
| `stage_name` | `${var.environment}` (e.g., "dev", "prod") |

The stage URL pattern is: `https://{api-id}.execute-api.{region}.amazonaws.com/{stage-name}/`

**Sources:** [infrastructure/terraform/api_gateway.tf L440-L448](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L440-L448)

### Redeployment Triggers

The deployment triggers include all resources that affect API behavior:

* Resource IDs: `api`, `diagram`, `diagram_generate`, `chat`, `chat_history`, `chat_save`
* Method IDs: `diagram_generate_post`, `chat_history_get`, `chat_save_post`
* Integration IDs: All three endpoint integrations
* Response IDs: Method responses and integration responses for all endpoints

This comprehensive trigger list ensures that any configuration change results in a new deployment, making the changes immediately available.

**Sources:** [infrastructure/terraform/api_gateway.tf L393-L414](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L393-L414)

---

## Integration with Frontend

The frontend consumes the API Gateway URL from Terraform outputs and uses it to construct requests. The deployment script injects this URL into the frontend build as an environment variable.

### API URL Pattern

The complete API endpoint URLs follow this pattern:

```
https://{api-gateway-id}.execute-api.{region}.amazonaws.com/{environment}/api/diagram/generate
https://{api-gateway-id}.execute-api.{region}.amazonaws.com/{environment}/api/chat/history
https://{api-gateway-id}.execute-api.{region}.amazonaws.com/{environment}/api/chat/save
```

The API Gateway ID, region, and environment stage are determined during Terraform provisioning.

**Sources:** [infrastructure/terraform/api_gateway.tf L5-L16](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L5-L16)

 [infrastructure/terraform/api_gateway.tf L440-L448](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L440-L448)

---

## Configuration Summary

### Resource Count

| Resource Type | Count | Purpose |
| --- | --- | --- |
| `aws_api_gateway_rest_api` | 1 | REST API definition |
| `aws_api_gateway_resource` | 6 | Resource hierarchy (`/api`, `/diagram`, `/chat`, and endpoints) |
| `aws_api_gateway_method` | 6 | 3 endpoint methods + 3 OPTIONS methods |
| `aws_api_gateway_integration` | 6 | 3 Lambda integrations + 3 MOCK integrations |
| `aws_api_gateway_method_response` | 6 | Response definitions for all methods |
| `aws_api_gateway_integration_response` | 6 | Response mappings for all integrations |
| `aws_lambda_permission` | 3 | Lambda invocation grants |
| `aws_api_gateway_deployment` | 1 | API deployment snapshot |
| `aws_api_gateway_stage` | 1 | Environment stage |

**Sources:** [infrastructure/terraform/api_gateway.tf L1-L449](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L1-L449)

### Key Design Patterns

1. **AWS_PROXY Integration**: Simplifies request/response handling by delegating HTTP concerns to Lambda functions
2. **CORS with MOCK Integration**: Provides preflight responses without backend processing
3. **Trigger-Based Redeployment**: Automatically deploys API changes using SHA1 hashing of resource IDs
4. **Hierarchical Resource Structure**: Organizes endpoints into logical namespaces (`/api/diagram/*`, `/api/chat/*`)
5. **Wildcard Lambda Permissions**: Uses `/*/*` pattern to allow any stage/path to invoke functions
6. **Create-Before-Destroy Lifecycle**: Ensures zero-downtime deployments

**Sources:** [infrastructure/terraform/api_gateway.tf L1-L449](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/api_gateway.tf#L1-L449)