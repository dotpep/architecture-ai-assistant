# Testing

> **Relevant source files**
> * [docs/tests/DIAGRAM_RENDERER_TESTS.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/tests/DIAGRAM_RENDERER_TESTS.md)
> * [infrastructure/scripts/lambda/deploy_lambda.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/lambda/deploy_lambda.py)
> * [src/backend/lambda_functions/chat_crud/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py)
> * [src/backend/lambda_functions/generate_diagram/README.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/README.md)
> * [src/backend/lambda_functions/generate_diagram/diagram_renderer.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/diagram_renderer.py)
> * [src/backend/lambda_functions/generate_diagram/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py)
> * [src/backend/lambda_functions/get_history/lambda_function.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/get_history/lambda_function.py)
> * [tests/e2e/e2e_verification.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py)
> * [tests/e2e/verify_deployment.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py)
> * [tests/unit/manual_test_generate_diagram.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/manual_test_generate_diagram.py)
> * [tests/unit/test_chat_crud.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py)
> * [tests/unit/test_diagram_renderer.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py)
> * [tests/unit/test_generate_diagram.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py)
> * [tests/unit/test_mermaid_components.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py)

## Purpose and Scope

This document describes the testing strategy and implementation for the Architecture AI Assistant system. It covers unit testing of backend Lambda functions and shared modules, end-to-end verification of deployed infrastructure, and test execution procedures. The testing approach uses **pytest** for unit tests with extensive mocking to isolate components, and custom Python scripts for end-to-end deployment verification.

For information about the specific Lambda functions being tested, see [Backend Lambda Functions](/dotpep/architecture-ai-assistant/4-backend-lambda-functions). For deployment procedures that trigger verification tests, see [Deployment Guide](/dotpep/architecture-ai-assistant/6-deployment-guide).

**Sources:** [tests/unit/test_generate_diagram.py L1-L10](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L1-L10)

 [tests/e2e/verify_deployment.py L1-L7](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L1-L7)

---

## Testing Architecture Overview

The testing system is organized into two primary layers: **unit tests** that verify individual components in isolation, and **end-to-end tests** that validate the complete deployed system through actual API calls.

### Test Layer Architecture

```

```

**Sources:** [tests/unit/test_generate_diagram.py L1-L62](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L1-L62)

 [tests/unit/test_chat_crud.py L1-L32](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L1-L32)

 [tests/unit/test_diagram_renderer.py L1-L37](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L1-L37)

 [tests/e2e/verify_deployment.py L1-L20](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L1-L20)

---

## Unit Testing Strategy

### Test Organization and Module Loading

Unit tests are organized by Lambda function and shared module. Each test file uses a specialized module loading strategy to avoid import conflicts and properly mock AWS dependencies before any boto3-dependent code loads.

**Module Loading Pattern:**

```

```

This pattern prevents boto3 initialization errors in local testing environments where AWS credentials may not be configured.

**Sources:** [tests/unit/test_generate_diagram.py L10-L35](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L10-L35)

 [tests/unit/test_chat_crud.py L10-L29](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L10-L29)

 [tests/unit/test_diagram_renderer.py L11-L31](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L11-L31)

---

### Lambda Function Test Coverage

#### generate_diagram Lambda Tests

The `test_generate_diagram.py` file contains 40+ test cases organized into five test classes:

| Test Class | Purpose | Key Test Cases |
| --- | --- | --- |
| `TestRequestValidation` | Validates HTTP request parsing and field checking | `test_valid_request`, `test_missing_user_prompt`, `test_invalid_diagram_type`, `test_empty_user_prompt` |
| `TestMermaidValidator` | Tests Mermaid syntax validation for all diagram types | `test_valid_flowchart`, `test_valid_erdiagram`, `test_valid_sequence`, `test_unbalanced_brackets_flowchart` |
| `TestMermaidExtractor` | Tests extraction of Mermaid code from LLM responses | `test_extract_with_mermaid_tag`, `test_extract_multiple_blocks`, `test_extract_no_code_block` |
| `TestPromptBuilder` | Validates prompt construction for different diagram types | `test_build_complete_prompt`, `test_get_supported_types`, `test_prompt_contains_syntax_rules` |
| `TestResponseHelpers` | Tests HTTP response formatting | `test_create_error_response`, `test_create_success_response` |

**Key Functions Under Test:**

* `validate_request(event)` - [src/backend/lambda_functions/generate_diagram/lambda_function.py L26-L67](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L26-L67)
* `validate_mermaid_code(code, diagram_type)` - [src/backend/lambda_functions/generate_diagram/mermaid_validator.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/mermaid_validator.py)
* `extract_mermaid_code(response)` - [src/backend/lambda_functions/generate_diagram/mermaid_extractor.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/mermaid_extractor.py)
* `build_complete_prompt(user_prompt, diagram_type)` - [src/backend/lambda_functions/generate_diagram/prompt_builder.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/prompt_builder.py)

**Sources:** [tests/unit/test_generate_diagram.py L64-L356](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L64-L356)

 [src/backend/lambda_functions/generate_diagram/lambda_function.py L26-L68](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L26-L68)

---

#### chat_crud Lambda Tests

The `test_chat_crud.py` file tests the chat message persistence Lambda:

```

```

**Test Coverage:**

* Request validation with required fields (`userMessage`, `diagramType`)
* ChatId generation using `generate_chat_id()` when not provided
* Optional field handling (`aiResponse`, `mermaidCode`, `imageUrl`, `markdownUrl`, `status`)
* DynamoDB `put_item()` invocation verification
* CORS preflight (OPTIONS) request handling

**Sources:** [tests/unit/test_chat_crud.py L32-L218](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L32-L218)

 [src/backend/lambda_functions/chat_crud/lambda_function.py L42-L132](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/chat_crud/lambda_function.py#L42-L132)

---

#### diagram_renderer Tests

The `test_diagram_renderer.py` file contains 19 tests covering PNG rendering resilience:

| Test Class | Tests | Focus Area |
| --- | --- | --- |
| `TestRenderMermaidToPng` | 7 | Primary Kroki API rendering via `https://kroki.io/mermaid/png` |
| `TestRenderMermaidToPngFallback` | 3 | Fallback retry mechanism |
| `TestGeneratePlaceholderPng` | 3 | 1x1 white PNG placeholder generation |
| `TestSaveDiagramToS3` | 4 | Complete S3 save workflow with markdown + image |
| `TestIntegration` | 2 | Full rendering pipeline integration |

**Three-Tier Resilience Strategy:**

```

```

**Key Test Validations:**

* HTTP headers: `Content-Type: text/plain`, `User-Agent: Architecture-AI-Assistant/1.0`
* Timeout handling (30 second timeout)
* PNG magic byte signature validation (`\x89PNG\r\n\x1a\n`)
* Error propagation (connection errors, HTTP 400/500 errors)

**Sources:** [tests/unit/test_diagram_renderer.py L39-L365](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L39-L365)

 [src/backend/lambda_functions/generate_diagram/diagram_renderer.py L14-L148](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/diagram_renderer.py#L14-L148)

 [docs/tests/DIAGRAM_RENDERER_TESTS.md L1-L104](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/tests/DIAGRAM_RENDERER_TESTS.md#L1-L104)

---

### Mermaid Component Tests

The `test_mermaid_components.py` file provides lightweight tests for Mermaid modules without AWS dependencies:

**Test Coverage by Function:**

| Function | Tests | Validation Focus |
| --- | --- | --- |
| `test_mermaid_validator()` | 9 | Valid diagrams (flowchart, ER, sequence, class, state), empty code, fence markers, missing declaration, unbalanced brackets |
| `test_mermaid_extractor()` | 5 | Code extraction from ```mermaid blocks, multiple blocks, no blocks, code cleaning, already-clean code |
| `test_prompt_builder()` | 5 | Complete prompt building, diagram-specific instructions, all 7 supported types |

**Supported Diagram Types Validated:**

```

```

**Example Validation Test:**

```

```

**Sources:** [tests/unit/test_mermaid_components.py L19-L209](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L19-L209)

 [tests/unit/manual_test_generate_diagram.py L23-L174](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/manual_test_generate_diagram.py#L23-L174)

---

## End-to-End Verification

### Deployment Verification Script

The `verify_deployment.py` script performs post-deployment validation of the complete system:

```

```

**Verification Functions and Expected Results:**

| Function | HTTP Method | Endpoint | Success Criteria |
| --- | --- | --- | --- |
| `verify_cloudfront_accessible()` | GET | `CLOUDFRONT_URL` | Status 200, HTML content |
| `verify_api_gateway_accessible()` | POST | `/api/diagram/generate` | Status 200 or 502 (LLM unavailable is acceptable) |
| `verify_diagram_generation()` | POST | `/api/diagram/generate` | Status 200, fields: `chatId`, `mermaidCode`, `imageUrl`, `markdownUrl`, `status: completed` |
| `verify_chat_save()` | POST | `/api/chat/save` | Status 200, fields: `success: true`, `chatId`, `timestamp` |
| `verify_chat_history()` | GET | `/api/chat/history?limit=10` | Status 200, fields: `chats[]`, `count`, `nextToken` |
| `verify_download_urls()` | HEAD | CloudFront diagram URLs | Status 200 for markdown and image URLs |

**Test Payload:**

```

```

**Sources:** [tests/e2e/verify_deployment.py L41-L241](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L41-L241)

 [tests/e2e/verify_deployment.py L15-L22](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L15-L22)

---

### E2E Verification Tests

The `e2e_verification.py` script provides a comprehensive integration test suite:

**Test Flow Architecture:**

```

```

**Configuration Variables:**

* `CLOUDFRONT_URL`: `"https://d1to0rasl28a6e.cloudfront.net"`
* `API_GATEWAY_URL`: `"https://weuo4z7252.execute-api.us-east-1.amazonaws.com/dev"`
* `DYNAMODB_TABLE`: `"architecture-ai-assistant-chat_history-dev"`
* `S3_BUCKET`: `"architecture-ai-assistant-bucket-dev"`
* `AWS_REGION`: `"us-east-1"`

**Sources:** [tests/e2e/e2e_verification.py L13-L19](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L13-L19)

 [tests/e2e/e2e_verification.py L41-L240](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L41-L240)

---

## Test Execution and Coverage

### Running Unit Tests

**Execute all unit tests:**

```

```

**Run with coverage reporting:**

```

```

**Manual test execution (no pytest required):**

```

```

**Sources:** [docs/tests/DIAGRAM_RENDERER_TESTS.md L52-L72](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/tests/DIAGRAM_RENDERER_TESTS.md#L52-L72)

 [tests/unit/test_mermaid_components.py L211-L239](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L211-L239)

---

### Running End-to-End Tests

**Execute deployment verification:**

```

```

**Expected Output:**

```yaml
==============================================================
  End-to-End Verification - Architecture AI Assistant
==============================================================

ℹ Testing frontend accessibility...
✓ CloudFront frontend is accessible

ℹ Verifying API Gateway accessibility...
✓ API Gateway is accessible

ℹ Testing diagram generation endpoint...
✓ Diagram generation successful
  Chat ID: 550e8400-e29b-41d4-a716-446655440000
  Status: completed
  Mermaid code length: 156 characters

==============================================================
  Verification Summary
==============================================================
✓ PASS: Cloudfront
✓ PASS: Api Gateway
✓ PASS: Diagram Generation
✓ PASS: Chat Save
✓ PASS: Chat History
✓ PASS: Download Urls

Total: 6/6 tests passed
```

**Sources:** [tests/e2e/verify_deployment.py L243-L309](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L243-L309)

 [tests/e2e/e2e_verification.py L242-L307](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L242-L307)

---

### Test Coverage Summary

**Unit Test Coverage by Component:**

| Component | Test File | Test Classes | Test Count | Coverage Focus |
| --- | --- | --- | --- | --- |
| `generate_diagram` Lambda | `test_generate_diagram.py` | 5 | 40+ | Request validation, Mermaid validation, extraction, prompt building |
| `chat_crud` Lambda | `test_chat_crud.py` | 1 | 11 | Request validation, DynamoDB persistence, chatId generation |
| `get_history` Lambda | N/A | 0 | 0 | No dedicated unit tests (tested via E2E) |
| `diagram_renderer` module | `test_diagram_renderer.py` | 5 | 19 | Kroki API, fallback rendering, placeholder generation, S3 integration |
| Mermaid validators/extractors | `test_mermaid_components.py` | N/A | 19 | All diagram types, extraction strategies, prompt construction |

**End-to-End Test Coverage:**

| Test Script | Tests | API Endpoints Covered | AWS Services Validated |
| --- | --- | --- | --- |
| `verify_deployment.py` | 6 | `/api/diagram/generate`, `/api/chat/save`, `/api/chat/history` | CloudFront, API Gateway, Lambda, DynamoDB, S3 |
| `e2e_verification.py` | 6 | Same as above | Same as above |

**Mocking Strategy:**

* **boto3/botocore**: Mocked at module level before any imports
* **requests.post**: Mocked using `@patch('diagram_renderer.requests.post')`
* **S3Helper/DynamoDBHelper**: Mocked using `MagicMock()` instances
* **External LLM API**: Not mocked in E2E tests (actual failures are acceptable)

**Sources:** [tests/unit/test_generate_diagram.py L64-L356](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L64-L356)

 [tests/unit/test_chat_crud.py L32-L218](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L32-L218)

 [tests/unit/test_diagram_renderer.py L39-L318](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L39-L318)

 [docs/tests/DIAGRAM_RENDERER_TESTS.md L11-L84](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/tests/DIAGRAM_RENDERER_TESTS.md#L11-L84)

---

## Integration with Deployment

### Post-Deployment Verification

The deployment script (`deploy.sh`) can optionally trigger E2E verification after successful infrastructure deployment:

```

```

**Verification Timing:**

* **Immediate**: CloudFront accessibility, API Gateway routing
* **1-2 seconds**: Lambda function invocation, DynamoDB writes
* **5-10 seconds**: CloudFront cache propagation for diagram URLs

**Common Failure Scenarios and Debugging:**

| Failure | Possible Cause | Debugging Steps |
| --- | --- | --- |
| CloudFront 403 | Origin Access Control misconfigured | Check S3 bucket policy, OAC settings in Terraform |
| API Gateway 404 | Route not deployed | Verify `terraform apply` completed, check API Gateway console |
| Diagram generation 502 | LLM API key not set or invalid | Verify `LLM_API_KEY` environment variable in Lambda |
| DynamoDB write failure | IAM permissions missing | Check Lambda execution role has `dynamodb:PutItem` permission |
| S3 upload failure | Bucket policy or CORS issue | Verify S3 bucket policy allows Lambda role, check CORS configuration |

**Sources:** [tests/e2e/verify_deployment.py L243-L309](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/verify_deployment.py#L243-L309)

 [tests/e2e/e2e_verification.py L242-L307](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/e2e/e2e_verification.py#L242-L307)