# Chat CRUD Function

> **Relevant source files**
> * [infrastructure/scripts/lambda/deploy_lambda.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/deploy_lambda.py)
> * [src/backend/lambda_functions/chat_crud/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py)
> * [src/backend/lambda_functions/generate_diagram/README.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/README.md)
> * [src/backend/lambda_functions/generate_diagram/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py)
> * [src/backend/lambda_functions/get_history/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py)
> * [tests/e2e/e2e_verification.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py)
> * [tests/e2e/verify_deployment.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py)
> * [tests/unit/manual_test_generate_diagram.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/manual_test_generate_diagram.py)
> * [tests/unit/test_chat_crud.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py)
> * [tests/unit/test_generate_diagram.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py)
> * [tests/unit/test_mermaid_components.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py)

## Purpose and Scope

This document describes the `chat_crud` Lambda function, which handles saving chat messages to DynamoDB. This function provides a persistence layer for manually saving chat conversations, separate from the automatic saving performed during diagram generation. For diagram generation functionality, see [Generate Diagram Function](/dotpep/architecture-ai-assistant/4.1-generate-diagram-function). For retrieving saved chat history, see [Get History Function](/dotpep/architecture-ai-assistant/4.3-get-history-function).

**Sources:** [src/backend/lambda_functions/chat_crud/lambda_function.py L1-L160](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L1-L160)

---

## Function Overview

The `chat_crud` Lambda function is a lightweight persistence service that accepts POST requests containing chat message data and stores them in DynamoDB. It serves as a manual save endpoint, allowing users to explicitly save chat sessions that may not have been automatically persisted during diagram generation.

| Property | Value |
| --- | --- |
| **Function Name** | `chat_crud` |
| **Handler** | `lambda_function.handler` |
| **HTTP Methods** | POST, OPTIONS |
| **API Endpoint** | `/api/chat/save` |
| **Primary Operation** | DynamoDB PutItem |

The function implements a simple CRUD pattern focused on Create operations, with validation and error handling to ensure data integrity.

**Sources:** [src/backend/lambda_functions/chat_crud/lambda_function.py L135-L159](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L135-L159)

 [tests/unit/test_chat_crud.py L32-L218](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L32-L218)

---

## Request Processing Flow

### Handler Routing and CORS

```

```

**Diagram: Handler routing logic for HTTP methods and CORS support**

The `handler()` function at [lambda_function.py L135-L159](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/lambda_function.py#L135-L159)

 serves as the entry point, initializing a `DynamoDBHelper` instance and routing requests based on the HTTP method. OPTIONS requests return immediately with CORS headers for browser preflight checks.

**Sources:** [src/backend/lambda_functions/chat_crud/lambda_function.py L135-L159](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L135-L159)

 [tests/unit/test_chat_crud.py L186-L195](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L186-L195)

---

## Request Validation

### Validation Logic

```

```

**Diagram: Request validation workflow ensuring required fields and valid diagram types**

The `validate_request()` function at [lambda_function.py L42-L64](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/lambda_function.py#L42-L64)

 performs three checks:

1. **userMessage presence**: Required field containing the user's prompt
2. **diagramType presence**: Required field specifying the diagram type
3. **diagramType validity**: Validates against supported types using `validate_diagram_type()` from the shared `utils` module

Validation failures return HTTP 400 responses with descriptive error messages.

**Sources:** [src/backend/lambda_functions/chat_crud/lambda_function.py L42-L64](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L42-L64)

 [tests/unit/test_chat_crud.py L35-L76](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L35-L76)

---

## Data Persistence

### DynamoDB Item Structure

The `save_message()` function at [lambda_function.py L67-L132](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/lambda_function.py#L67-L132)

 constructs a DynamoDB item with the following structure:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `chatId` | String | Yes | Unique identifier (generated if not provided) |
| `timestamp` | Integer | Yes | Unix timestamp in seconds |
| `userMessage` | String | Yes | User's input prompt |
| `diagramType` | String | Yes | Type of diagram (flowchart, erdiagram, etc.) |
| `status` | String | Yes | Status indicator (default: "pending") |
| `aiResponse` | String | No | LLM's response text |
| `mermaidCode` | String | No | Generated Mermaid diagram code |
| `imageUrl` | String | No | CloudFront URL for PNG image |
| `markdownUrl` | String | No | CloudFront URL for markdown file |
| `diagramImageS3Key` | String | No | S3 key for PNG image |
| `diagramMarkdownS3Key` | String | No | S3 key for markdown file |

### Message Persistence Flow

```

```

**Diagram: Message persistence flow showing chatId generation and DynamoDB storage**

The function uses two utility functions from the shared `utils` module:

* `generate_chat_id()`: Creates a UUID-based unique identifier
* `get_current_timestamp()`: Returns the current Unix timestamp in seconds

Optional fields are conditionally added to the DynamoDB item at [lambda_function.py L103-L116](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/lambda_function.py#L103-L116)

 if present in the request body. This allows the function to save partial chat data (e.g., when a user manually saves before diagram generation completes) or complete chat data (including diagram URLs and Mermaid code).

**Sources:** [src/backend/lambda_functions/chat_crud/lambda_function.py L67-L132](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L67-L132)

 [tests/unit/test_chat_crud.py L77-L167](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L77-L167)

---

## Response Format

### Standardized Response Structure

The `create_response()` helper function at [lambda_function.py L19-L39](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/lambda_function.py#L19-L39)

 ensures consistent response formatting with proper CORS headers:

**Success Response (HTTP 200):**

```

```

**Error Responses:**

| Status Code | Scenario | Response Body |
| --- | --- | --- |
| 400 | Missing userMessage | `{"error": "Missing required field: userMessage"}` |
| 400 | Missing diagramType | `{"error": "Missing required field: diagramType"}` |
| 400 | Invalid diagramType | `{"error": "Invalid diagram type: {type}"}` |
| 400 | Invalid JSON | `{"error": "Invalid JSON in request body"}` |
| 405 | Wrong HTTP method | `{"error": "Method {method} not allowed"}` |
| 500 | DynamoDB failure | `{"error": "Failed to save chat message"}` |

All responses include CORS headers:

* `Access-Control-Allow-Origin: *`
* `Access-Control-Allow-Headers: Content-Type`
* `Access-Control-Allow-Methods: POST, OPTIONS`

**Sources:** [src/backend/lambda_functions/chat_crud/lambda_function.py L19-L39](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L19-L39)

 [tests/unit/test_chat_crud.py L169-L183](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L169-L183)

---

## Integration with System Components

### Component Dependencies

```

```

**Diagram: Component dependencies showing shared utilities and AWS integration**

The function depends on:

1. **Shared Utilities** ([src/backend/shared/utils.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/shared/utils.py) ): Provides `generate_chat_id()`, `get_current_timestamp()`, and `validate_diagram_type()` functions
2. **AWS Helpers** ([src/backend/shared/aws_helpers.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/shared/aws_helpers.py) ): Provides `DynamoDBHelper` class for DynamoDB operations
3. **Lambda Layer**: Both shared modules are packaged in a Lambda layer at runtime path `/opt/python`

**Sources:** [src/backend/lambda_functions/chat_crud/lambda_function.py L11-L16](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L11-L16)

 [src/backend/lambda_functions/chat_crud/lambda_function.py L135-L151](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L135-L151)

---

## Relationship with Generate Diagram Function

### Usage Pattern Comparison

```

```

**Diagram: Automatic vs manual save paths to the chat_history table**

The `chat_crud` function differs from `generate_diagram` in several ways:

| Aspect | chat_crud | generate_diagram |
| --- | --- | --- |
| **Purpose** | Manual save endpoint | Diagram generation and auto-save |
| **Complexity** | Simple persistence only | LLM call, validation, rendering, S3 storage |
| **ChatId** | Uses provided or generates new | Always generates new |
| **Required Fields** | userMessage, diagramType only | userPrompt, diagramType |
| **Optional Fields** | All diagram-related fields | None (all generated) |
| **Status Default** | "pending" | "completed" |

The `chat_crud` function is typically used for:

* Saving draft chat messages before diagram generation
* Persisting user notes or prompts without generating diagrams
* Re-saving existing chats with updated information

In contrast, `generate_diagram` always creates complete chat records with all diagram artifacts (Mermaid code, PNG URL, markdown URL).

**Sources:** [src/backend/lambda_functions/chat_crud/lambda_function.py L94-L116](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L94-L116)

 [src/backend/lambda_functions/generate_diagram/lambda_function.py L262-L277](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L262-L277)

---

## Error Handling Strategy

### Error Types and Handling

```

```

**Diagram: Error handling flow with specific error types and responses**

The function implements a defensive error handling strategy:

1. **JSON Parsing** ([lambda_function.py L80](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/lambda_function.py#L80-L80) ): Catches `json.JSONDecodeError` and returns HTTP 400 with "Invalid JSON in request body"
2. **Validation Errors** ([lambda_function.py L83-L85](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/lambda_function.py#L83-L85) ): Returns HTTP 400 with specific validation failure message from `validate_request()`
3. **DynamoDB Errors** ([lambda_function.py L130-L132](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/lambda_function.py#L130-L132) ): Catches all exceptions during DynamoDB operations, logs the error, and returns HTTP 500 with generic error message
4. **Logging**: Uses `print()` statements at [lambda_function.py L131](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/lambda_function.py#L131-L131)  for CloudWatch logging of errors

The function does not throw exceptions; all errors are converted to appropriate HTTP responses with CORS headers.

**Sources:** [src/backend/lambda_functions/chat_crud/lambda_function.py L78-L132](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L78-L132)

 [tests/unit/test_chat_crud.py L169-L183](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L169-L183)

---

## Testing Coverage

### Unit Test Structure

The test suite at [tests/unit/test_chat_crud.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py)

 validates all critical paths:

| Test Category | Test Cases | Lines |
| --- | --- | --- |
| **Request Validation** | Valid request, missing userMessage, missing diagramType, invalid diagram type | [35-76](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/35-76) |
| **ChatId Handling** | Auto-generation, provided chatId | [77-133](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/77-133) |
| **Optional Fields** | Inclusion of aiResponse, mermaidCode, URLs, status | [135-167](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/135-167) |
| **Error Handling** | Invalid JSON, malformed requests | [169-183](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/169-183) |
| **HTTP Methods** | OPTIONS for CORS, POST for save | [186-217](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/186-217) |

### Key Test Patterns

**Test 1: ChatId Generation**

```

```

**Test 2: Using Provided ChatId**

```

```

The test suite uses `unittest.mock` to isolate the Lambda function from AWS dependencies, allowing fast unit testing without requiring AWS credentials or active services.

**Sources:** [tests/unit/test_chat_crud.py L32-L218](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L32-L218)

---

## Environment Configuration

The function relies on environment variables set by Terraform during deployment:

| Variable | Purpose | Set By |
| --- | --- | --- |
| `DYNAMODB_TABLE_NAME` | Target DynamoDB table name | Terraform [infrastructure/terraform/lambda.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf) |
| `AWS_REGION` | AWS region for services | Lambda runtime |

The `DynamoDBHelper` class automatically reads `DYNAMODB_TABLE_NAME` from the environment to determine which table to use for persistence operations.

**Sources:** [src/backend/lambda_functions/chat_crud/lambda_function.py L11-L16](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L11-L16)

 [src/backend/shared/aws_helpers.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/shared/aws_helpers.py)

---

## Deployment and Packaging

The function is deployed as part of the Lambda infrastructure:

1. **Packaging**: The `deploy.sh` script packages the function code with shared dependencies
2. **Lambda Layer**: Shared utilities (`utils.py`, `aws_helpers.py`) are deployed as a Lambda layer accessible at `/opt/python`
3. **API Gateway**: Integrated with API Gateway at `/api/chat/save` endpoint via Terraform configuration

The function is stateless and can be invoked concurrently, with DynamoDB handling concurrent writes using the `chatId` partition key.

**Sources:** [infrastructure/scripts/lambda/deploy_lambda.py L94-L141](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/deploy_lambda.py#L94-L141)

 [tests/e2e/verify_deployment.py L136-L168](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L136-L168)