# End-to-End Verification

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

This document explains the end-to-end (E2E) verification suite for the Architecture AI Assistant, which tests complete user workflows from frontend access through diagram generation to data persistence. These tests validate the integration of all system components: CloudFront delivery, API Gateway routing, Lambda function execution, S3 storage, and DynamoDB persistence.

For unit testing of individual Lambda functions and modules, see [Unit Tests](/dotpep/architecture-ai-assistant/7.1-unit-tests). For deployment procedures, see [Deployment Guide](/dotpep/architecture-ai-assistant/6-deployment-guide).

---

## Overview

The E2E verification suite validates the deployed system by simulating real user interactions through HTTP requests to production endpoints. Unlike unit tests which mock AWS services, E2E tests exercise the actual deployed infrastructure to verify end-to-end functionality.

**Sources:** [tests/e2e/verify_deployment.py L1-L310](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L1-L310)

 [tests/e2e/e2e_verification.py L1-L308](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L1-L308)

---

## Verification Scripts

The system includes two E2E verification scripts with slightly different approaches:

| Script | Purpose | Key Features |
| --- | --- | --- |
| `verify_deployment.py` | Primary deployment verification | Tests basic connectivity and core flows |
| `e2e_verification.py` | Comprehensive workflow testing | Tests complete user journey including downloads |

Both scripts are located in [tests/e2e/](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/)

 and can be run independently to verify system health after deployment.

**Sources:** [tests/e2e/verify_deployment.py L1-L15](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L1-L15)

 [tests/e2e/e2e_verification.py L1-L12](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L1-L12)

### Configuration

Both scripts use hardcoded endpoint URLs that must be updated after Terraform deployment:

```

```

These values should be replaced with outputs from `terraform output` after infrastructure provisioning.

**Sources:** [tests/e2e/verify_deployment.py L16-L18](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L16-L18)

 [tests/e2e/e2e_verification.py L14-L18](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L14-L18)

---

## Test Architecture

### Test Execution Flow

The following diagram shows how the E2E verification script interacts with deployed components:

```

```

**Sources:** [tests/e2e/verify_deployment.py L41-L240](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L41-L240)

 [tests/e2e/e2e_verification.py L41-L240](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L41-L240)

---

## Test Scenarios

### 1. CloudFront Accessibility Test

**Function:** `verify_cloudfront_accessible()` [tests/e2e/verify_deployment.py L41-L54](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L41-L54)

**Purpose:** Verifies that the React frontend is accessible via the CloudFront distribution.

**Validation Logic:**

* Sends `GET` request to `CLOUDFRONT_URL`
* Expects HTTP 200 status code
* Validates that response contains HTML content

```

```

**What It Tests:**

* CloudFront distribution is active
* Origin access to S3 frontend bucket works
* DNS resolution is correct
* SSL/TLS certificate is valid

**Sources:** [tests/e2e/verify_deployment.py L41-L54](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L41-L54)

 [tests/e2e/e2e_verification.py L41-L59](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L41-L59)

---

### 2. API Gateway Accessibility Test

**Function:** `verify_api_gateway_accessible()` [tests/e2e/verify_deployment.py L57-L86](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L57-L86)

**Purpose:** Verifies that API Gateway endpoints are reachable and properly configured.

**Validation Logic:**

* Sends test request to `/api/diagram/generate` endpoint
* Accepts status codes 200 (success), 502 (LLM unavailable), or 400 (bad request)
* Rejects 404 (not found) or 403 (forbidden) as failures

```

```

The test intentionally allows 502 errors because the LLM API key may not be configured in test environments.

**What It Tests:**

* API Gateway deployment is active
* CORS headers are configured
* Lambda integration is connected
* Route mappings are correct

**Sources:** [tests/e2e/verify_deployment.py L57-L86](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L57-L86)

 [tests/e2e/e2e_verification.py L62-L92](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L62-L92)

---

### 3. Diagram Generation Test

**Function:** `verify_diagram_generation()` [tests/e2e/verify_deployment.py L89-L133](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L89-L133)

**Purpose:** Tests the complete diagram generation workflow through the `generate_diagram` Lambda function.

**Test Payload:**

```

```

**Expected Response Structure:**

| Field | Type | Description |
| --- | --- | --- |
| `chatId` | string | Unique identifier for the chat |
| `mermaidCode` | string | Generated Mermaid diagram code |
| `imageUrl` | string | CloudFront URL for PNG diagram |
| `markdownUrl` | string | CloudFront URL for markdown source |
| `status` | string | Should be "completed" |

**Validation Steps:**

1. POST request to `/api/diagram/generate`
2. Verify HTTP 200 status code
3. Parse JSON response
4. Check all required fields are present
5. Verify `mermaidCode` is non-empty
6. Confirm `status` equals "completed"

**What It Tests:**

* Request validation in `validate_request()` [src/backend/lambda_functions/generate_diagram/lambda_function.py L26-L67](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L26-L67)
* LLM API integration via `call_llm_api()` [src/backend/lambda_functions/generate_diagram/lambda_function.py L70-L135](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L70-L135)
* Mermaid code extraction using `extract_mermaid_code()` [src/backend/lambda_functions/generate_diagram/lambda_function.py L228](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L228-L228)
* Code validation via `validate_mermaid_code()` [src/backend/lambda_functions/generate_diagram/lambda_function.py L240](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L240-L240)
* S3 storage through `save_diagram_to_s3()` [src/backend/lambda_functions/generate_diagram/lambda_function.py L252](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L252-L252)
* DynamoDB persistence via `put_item()` [src/backend/lambda_functions/generate_diagram/lambda_function.py L276](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L276-L276)

**Sources:** [tests/e2e/verify_deployment.py L89-L133](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L89-L133)

 [tests/e2e/e2e_verification.py L95-L135](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L95-L135)

---

### 4. Chat Save Test

**Function:** `verify_chat_save()` [tests/e2e/verify_deployment.py L136-L167](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L136-L167)

**Purpose:** Verifies that chat messages can be persisted to DynamoDB through the `chat_crud` Lambda function.

**Test Payload:**

```

```

**Expected Response Structure:**

| Field | Type | Description |
| --- | --- | --- |
| `success` | boolean | Should be true |
| `chatId` | string | Generated or provided chat ID |
| `timestamp` | integer | Unix timestamp of creation |

**Validation Logic:**

* POST request to `/api/chat/save`
* Expects HTTP 200 status code
* Verifies `success` field is true
* Confirms `chatId` is present in response

**What It Tests:**

* Request validation in `validate_request()` [src/backend/lambda_functions/chat_crud/lambda_function.py L42-L64](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L42-L64)
* Chat ID generation via `generate_chat_id()` [src/backend/lambda_functions/chat_crud/lambda_function.py L88](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L88-L88)
* DynamoDB write through `put_item()` [src/backend/lambda_functions/chat_crud/lambda_function.py L119](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L119-L119)
* Response formatting in `create_response()` [src/backend/lambda_functions/chat_crud/lambda_function.py L19-L39](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L19-L39)

**Sources:** [tests/e2e/verify_deployment.py L136-L167](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L136-L167)

 [tests/e2e/e2e_verification.py L208-L239](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L208-L239)

---

### 5. Chat History Retrieval Test

**Function:** `verify_chat_history()` [tests/e2e/verify_deployment.py L170-L202](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L170-L202)

**Purpose:** Tests paginated retrieval of chat history from DynamoDB through the `get_history` Lambda function.

**Request Format:**

```
GET /api/chat/history?limit=10
```

**Expected Response Structure:**

| Field | Type | Description |
| --- | --- | --- |
| `chats` | array | Array of chat message objects |
| `count` | integer | Number of chats returned |
| `nextToken` | string\|null | Pagination token or null if no more results |

**Validation Logic:**

* GET request with `limit` query parameter
* Expects HTTP 200 status code
* Verifies response contains `chats` array and `count` field
* Optionally checks if recently created chat appears in history

The test includes a 1-second delay before querying to account for DynamoDB eventual consistency: [tests/e2e/e2e_verification.py L175](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L175-L175)

**What It Tests:**

* Query parameter parsing [src/backend/lambda_functions/get_history/lambda_function.py L116-L119](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L116-L119)
* DynamoDB scan with pagination via `scan_all()` [src/backend/lambda_functions/get_history/lambda_function.py L135-L138](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L135-L138)
* Decimal-to-JSON conversion using `DecimalEncoder` [src/backend/lambda_functions/get_history/lambda_function.py L20-L29](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L20-L29)
* Pagination token encoding/decoding [src/backend/lambda_functions/get_history/lambda_function.py L70-L100](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L70-L100)
* Response sorting by timestamp [src/backend/lambda_functions/get_history/lambda_function.py L141](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py#L141-L141)

**Sources:** [tests/e2e/verify_deployment.py L170-L202](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L170-L202)

 [tests/e2e/e2e_verification.py L169-L205](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L169-L205)

---

### 6. Download URL Verification Test

**Function:** `verify_download_urls()` [tests/e2e/verify_deployment.py L205-L240](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L205-L240)

**Purpose:** Verifies that generated diagram files are accessible through CloudFront URLs.

**Test Flow:**

1. First generates a diagram to obtain `imageUrl` and `markdownUrl`
2. Issues `HEAD` requests to both URLs to check accessibility
3. Expects HTTP 200 status code for both

**Validation Logic:**

```

```

**What It Tests:**

* S3 object creation by `save_diagram_to_s3()` [src/backend/lambda_functions/generate_diagram/lambda_function.py L252](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L252-L252)
* CloudFront URL generation in `S3Helper` methods
* CloudFront cache behavior and origin access
* Public read permissions on S3 objects

**Sources:** [tests/e2e/verify_deployment.py L205-L240](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L205-L240)

 [tests/e2e/e2e_verification.py L138-L166](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L138-L166)

---

## Test Execution Flow

### Sequential Test Execution

The E2E verification script executes tests in a specific order to build upon previous results:

```

```

**Sources:** [tests/e2e/verify_deployment.py L243-L305](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L243-L305)

---

## Running the Verification Tests

### Prerequisites

1. System must be deployed via Terraform
2. Python 3.9+ with `requests` library installed
3. Endpoint URLs must be configured in the script

### Execution

Run the primary verification script:

```

```

Or the comprehensive workflow test:

```

```

### Expected Output

The script prints colored status messages for each test:

```yaml
============================================================
  Architecture AI Assistant - End-to-End Verification
============================================================

ℹ Verifying CloudFront frontend accessibility...
✓ CloudFront frontend is accessible

ℹ Verifying API Gateway accessibility...
✓ API Gateway is accessible

ℹ Testing diagram generation endpoint...
✓ Diagram generation successful
  Chat ID: abc-123-def
  Status: completed
  Mermaid code length: 145 characters

...

============================================================
  Verification Summary
============================================================
✓ PASS: Cloudfront
✓ PASS: Api Gateway
✓ PASS: Diagram Generation
✓ PASS: Chat Save
✓ PASS: Chat History
✓ PASS: Download Urls

✓ All 6 tests passed!
```

**Sources:** [tests/e2e/verify_deployment.py L287-L305](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L287-L305)

---

## Result Interpretation

### Success Criteria

A test passes when:

* HTTP response status code matches expected values (typically 200)
* Response body contains all required fields
* Field values meet validation criteria (non-empty strings, correct types)
* Resources are accessible (URLs return 200)

### Handling Failures

The test suite is designed to be resilient to certain expected failures:

| Test | Expected Failure Scenario | Handling |
| --- | --- | --- |
| API Gateway | LLM API key not configured | Accepts 502 status code as success |
| Diagram Generation | LLM service unavailable | Logs warning, continues testing |
| Chat History | DynamoDB eventual consistency | Waits 1 second before querying |
| Download URLs | CloudFront cache not populated | Uses `HEAD` request to avoid large downloads |

**Sources:** [tests/e2e/verify_deployment.py L69-L86](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L69-L86)

 [tests/e2e/verify_deployment.py L124-L126](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L124-L126)

---

## Exit Codes

The verification scripts return standard exit codes for automation integration:

* **Exit 0:** All tests passed
* **Exit 1:** One or more tests failed

This allows the script to be integrated into CI/CD pipelines: [tests/e2e/verify_deployment.py L308-L309](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L308-L309)

```

```

**Sources:** [tests/e2e/verify_deployment.py L243-L309](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L243-L309)

 [tests/e2e/e2e_verification.py L242-L307](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L242-L307)

---

## Test Data

Both scripts use consistent test data to ensure repeatable results:

```

```

The test prompt is deliberately simple to:

* Minimize LLM processing time
* Reduce test execution duration
* Generate predictable diagram structures
* Avoid LLM API rate limits

**Sources:** [tests/e2e/verify_deployment.py L21-L22](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L21-L22)

 [tests/e2e/e2e_verification.py L21-L22](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L21-L22)

---

## Differences Between Verification Scripts

### verify_deployment.py vs e2e_verification.py

| Aspect | verify_deployment.py | e2e_verification.py |
| --- | --- | --- |
| **Primary Focus** | Post-deployment connectivity | Complete user workflows |
| **Test Count** | 6 tests | 6 tests |
| **Frontend Test** | Basic HTML check | DOCTYPE validation |
| **API Test** | Single endpoint probe | Multiple endpoint checks |
| **Error Handling** | More lenient (accepts 502) | Strict validation |
| **Use Case** | Quick deployment verification | Comprehensive E2E validation |

Both scripts test the same core functionality but with different levels of strictness and validation depth.

**Sources:** [tests/e2e/verify_deployment.py L1-L310](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L1-L310)

 [tests/e2e/e2e_verification.py L1-L308](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L1-L308)

---

## Integration with Unit Tests

The E2E verification suite complements the unit test suite by testing different layers:

```

```

**Key Differences:**

* **Unit tests** validate individual functions with mocked dependencies: [tests/unit/test_generate_diagram.py L10-L14](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L10-L14)
* **E2E tests** validate deployed infrastructure with real AWS services: [tests/e2e/verify_deployment.py L57-L86](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L57-L86)

**Sources:** [tests/unit/test_generate_diagram.py L1-L361](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L1-L361)

 [tests/unit/test_chat_crud.py L1-L223](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L1-L223)

 [tests/e2e/verify_deployment.py L1-L310](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L1-L310)