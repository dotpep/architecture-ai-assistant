# Get History Function

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

This page documents the `get_history` Lambda function, which retrieves paginated chat history from DynamoDB. The function handles GET requests to the `/api/chat/history` endpoint, returning past diagram generation sessions with their associated metadata. For information about saving chat messages, see [Chat CRUD Function](/dotpep/architecture-ai-assistant/4.2-chat-crud-function). For the diagram generation workflow, see [Generate Diagram Function](/dotpep/architecture-ai-assistant/4.1-generate-diagram-function). For DynamoDB schema details, see [Data Storage Architecture](/dotpep/architecture-ai-assistant/2.2-data-storage-architecture).

---

## Overview and Responsibilities

The `get_history` Lambda function is one of three backend Lambda functions in the system. Its primary responsibilities include:

| Responsibility | Implementation |
| --- | --- |
| **Query Chat History** | Scans DynamoDB `chat_history` table to retrieve all stored conversations |
| **Pagination** | Supports paginated retrieval with configurable limit and continuation tokens |
| **Data Transformation** | Converts DynamoDB `Decimal` types to JSON-compatible `int`/`float` types |
| **Sorting** | Orders results by timestamp in descending order (newest first) |
| **CORS Support** | Handles OPTIONS preflight requests and adds CORS headers to responses |

The function is invoked via API Gateway and returns chat records containing user prompts, diagram types, Mermaid code, and CloudFront URLs for generated diagrams.

**Sources:** [src/backend/lambda_functions/get_history/lambda_function.py L1-L194](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L1-L194)

---

## Function Architecture

The following diagram illustrates the request processing flow through the `get_history` Lambda function:

**Handler Flow and Component Interaction**

```

```

**Sources:** [src/backend/lambda_functions/get_history/lambda_function.py L103-L193](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L103-L193)

---

## Request Processing

### Handler Entry Point

The `handler()` function serves as the Lambda entry point and performs initial request routing:

[src/backend/lambda_functions/get_history/lambda_function.py L169-L193](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L169-L193)

Key responsibilities:

* **CORS Preflight Handling**: Returns 200 immediately for OPTIONS requests
* **Method Validation**: Only accepts GET requests, returns 405 for others
* **DynamoDB Initialization**: Creates `DynamoDBHelper` instance for database operations
* **Request Routing**: Delegates to `get_history()` for GET requests

### Query Parameter Parsing

The `get_history()` function extracts and validates query parameters:

[src/backend/lambda_functions/get_history/lambda_function.py L116-L132](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L116-L132)

| Parameter | Type | Default | Validation | Purpose |
| --- | --- | --- | --- | --- |
| `limit` | int | 50 | 1-100 inclusive | Maximum number of records to return |
| `nextToken` | string | None | Base64 validation | Continuation token for pagination |

**Limit Validation:**

```
if limit < 1 or limit > 100:
    return 400 error
```

**NextToken Decoding:**
The `nextToken` parameter is decoded using `decode_next_token()` which:

1. Base64 decodes the token string
2. Parses JSON to reconstruct `LastEvaluatedKey`
3. Returns `None` if token is invalid or malformed

**Sources:** [src/backend/lambda_functions/get_history/lambda_function.py L86-L132](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L86-L132)

---

## Pagination Implementation

The function implements cursor-based pagination using DynamoDB's native pagination mechanism:

**Pagination Token Flow**

```

```

### Token Encoding

The `encode_next_token()` function creates opaque pagination tokens:

[src/backend/lambda_functions/get_history/lambda_function.py L70-L83](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L70-L83)

Process:

1. **Decimal Conversion**: Converts DynamoDB `Decimal` types using `convert_decimals()`
2. **JSON Serialization**: Encodes the key dictionary as JSON
3. **Base64 Encoding**: Encodes the JSON string as base64 for URL safety

### Token Decoding

The `decode_next_token()` function reverses the encoding:

[src/backend/lambda_functions/get_history/lambda_function.py L86-L100](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L86-L100)

Process:

1. **Base64 Decoding**: Decodes the token string
2. **JSON Parsing**: Deserializes to dictionary
3. **Error Handling**: Returns `None` for any decoding errors (invalid tokens are rejected gracefully)

**Sources:** [src/backend/lambda_functions/get_history/lambda_function.py L70-L100](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L70-L100)

---

## DynamoDB Integration

### Scan Operation

The function uses `DynamoDBHelper.scan_all()` to retrieve chat history:

[src/backend/lambda_functions/get_history/lambda_function.py L135-L138](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L135-L138)

Key characteristics:

* **Scan vs Query**: Uses `scan_all()` to retrieve all items (no specific partition key filtering)
* **Limit Parameter**: Passed to DynamoDB to control page size
* **Continuation**: Uses `last_evaluated_key` for cursor-based pagination
* **Return Value**: Dictionary containing `items` array and optional `last_evaluated_key`

### Result Sorting

After scanning, results are sorted by timestamp:

[src/backend/lambda_functions/get_history/lambda_function.py L141](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L141-L141)

```

```

This ensures the frontend receives chats in chronological order (newest first), regardless of DynamoDB scan order.

### Data Type Conversion

DynamoDB returns numeric types as `Decimal` objects, which are not JSON-serializable. The `convert_decimals()` function recursively converts them:

[src/backend/lambda_functions/get_history/lambda_function.py L32-L44](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L32-L44)

Conversion rules:

| DynamoDB Type | Conversion Logic | Example |
| --- | --- | --- |
| `Decimal` (whole number) | `int(obj)` | `Decimal('42')` → `42` |
| `Decimal` (float) | `float(obj)` | `Decimal('42.5')` → `42.5` |
| `list` | Recursive conversion | `[Decimal('1'), Decimal('2')]` → `[1, 2]` |
| `dict` | Recursive conversion | `{'count': Decimal('5')}` → `{'count': 5}` |

A custom `DecimalEncoder` JSON encoder is also used as a fallback:

[src/backend/lambda_functions/get_history/lambda_function.py L20-L29](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L20-L29)

**Sources:** [src/backend/lambda_functions/get_history/lambda_function.py L20-L145](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L20-L145)

 [src/backend/shared/aws_helpers.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/shared/aws_helpers.py)

---

## Response Format

### Standard Response Structure

The `create_response()` function generates standardized API Gateway responses:

[src/backend/lambda_functions/get_history/lambda_function.py L47-L67](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L47-L67)

**Success Response (200 OK):**

```

```

| Field | Type | Description |
| --- | --- | --- |
| `chats` | array | Array of chat objects, sorted by timestamp descending |
| `count` | int | Number of chats in this page (not total count) |
| `nextToken` | string\|null | Base64 token for next page, or `null` if no more results |

**CORS Headers:**

[src/backend/lambda_functions/get_history/lambda_function.py L60-L64](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L60-L64)

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: GET, OPTIONS
```

### Response Assembly

The response is assembled in `get_history()`:

[src/backend/lambda_functions/get_history/lambda_function.py L147-L158](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L147-L158)

Logic:

1. **Items Array**: Sorted and converted chat records
2. **Count**: Length of items array (current page only)
3. **NextToken**: Encoded `last_evaluated_key` if more results exist, otherwise `null`

**Sources:** [src/backend/lambda_functions/get_history/lambda_function.py L47-L158](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L47-L158)

---

## Error Handling

The function implements comprehensive error handling:

**Error Response Flow**

```

```

### Error Cases

| Error Type | Status Code | Condition | Error Message |
| --- | --- | --- | --- |
| Invalid Limit | 400 | `limit < 1` or `limit > 100` | "Limit must be between 1 and 100" |
| Invalid Token | 400 | Base64 decode or JSON parse fails | "Invalid nextToken" |
| Invalid Parameter | 400 | `ValueError` during processing | "Invalid parameter: {details}" |
| Server Error | 500 | DynamoDB failure or unexpected exception | "Failed to retrieve chat history" |
| Method Not Allowed | 405 | HTTP method not GET | "Method {method} not allowed" |

### Exception Logging

Server errors are logged with full context:

[src/backend/lambda_functions/get_history/lambda_function.py L160-L166](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L160-L166)

```

```

This enables debugging through CloudWatch Logs while returning safe error messages to clients.

**Sources:** [src/backend/lambda_functions/get_history/lambda_function.py L120-L166](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L120-L166)

---

## Testing and Verification

### Unit Testing

The function's behavior is verified through end-to-end tests rather than isolated unit tests. The E2E tests validate:

**Test Coverage from E2E Suite:**

| Test Function | Validation | Source |
| --- | --- | --- |
| `verify_chat_history()` | API accessibility, response structure, pagination | [tests/e2e/verify_deployment.py L170-L202](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L170-L202) |
| `test_chat_history()` | Chat retrieval, data consistency, eventual consistency handling | [tests/e2e/e2e_verification.py L169-L205](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L169-L205) |

### E2E Test Flow

[tests/e2e/verify_deployment.py L170-L202](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L170-L202)

The verification script:

1. Calls `GET /api/chat/history?limit=10`
2. Verifies response contains `chats` and `count` fields
3. Checks chat record structure (chatId, timestamp, etc.)
4. Logs the number of returned chats

Example output:

```
ℹ Testing chat history endpoint...
✓ Chat history retrieval successful
  Total chats: 10
  Returned chats: 10
  Latest chat ID: abc-123-def
```

### Integration with Chat CRUD

The E2E tests verify the integration between `get_history` and `chat_crud`:

[tests/e2e/e2e_verification.py L169-L205](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L169-L205)

Test sequence:

1. Save a new chat using `POST /api/chat/save`
2. Wait 1 second for DynamoDB eventual consistency
3. Retrieve history using `GET /api/chat/history`
4. Verify the saved chat appears in the results

This validates the complete write-then-read flow through DynamoDB.

**Sources:** [tests/e2e/verify_deployment.py L170-L202](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L170-L202)

 [tests/e2e/e2e_verification.py L169-L205](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L169-L205)

---

## API Gateway Integration

The Lambda function integrates with API Gateway through the following endpoint configuration:

| Configuration | Value |
| --- | --- |
| **HTTP Method** | GET |
| **Endpoint Path** | `/api/chat/history` |
| **Integration Type** | Lambda Proxy Integration |
| **Authorization** | None (public endpoint with CORS) |
| **Timeout** | 29 seconds (API Gateway maximum) |

The function expects API Gateway to provide the event in this format:

```

```

For Terraform configuration of this API Gateway endpoint, see [API Gateway Configuration](/dotpep/architecture-ai-assistant/5.2-api-gateway-configuration).

**Sources:** [src/backend/lambda_functions/get_history/lambda_function.py L169-L193](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L169-L193)

 [tests/e2e/verify_deployment.py L174](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L174-L174)