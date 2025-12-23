# Unit Tests

> **Relevant source files**
> * [docs/tests/DIAGRAM_RENDERER_TESTS.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/tests/DIAGRAM_RENDERER_TESTS.md)
> * [src/backend/lambda_functions/generate_diagram/README.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/README.md)
> * [src/backend/lambda_functions/generate_diagram/diagram_renderer.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/diagram_renderer.py)
> * [tests/unit/manual_test_generate_diagram.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/manual_test_generate_diagram.py)
> * [tests/unit/test_chat_crud.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py)
> * [tests/unit/test_diagram_renderer.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py)
> * [tests/unit/test_generate_diagram.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py)
> * [tests/unit/test_mermaid_components.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py)

This document describes the unit testing approach for the Architecture AI Assistant backend Lambda functions and their supporting modules. Unit tests verify individual components in isolation using mocking to eliminate external dependencies such as AWS services, LLM APIs, and rendering services.

For end-to-end integration testing that validates complete user workflows, see [End-to-End Verification](/dotpep/architecture-ai-assistant/7.2-end-to-end-verification). For the complete testing strategy overview, see [Testing](/dotpep/architecture-ai-assistant/7-testing).

---

## Test Organization

The unit test suite is organized in the `tests/unit/` directory with test files corresponding to the modules they verify. All tests use `pytest` as the test runner and `unittest.mock` for creating mock objects.

### Test File Structure

```

```

**Sources:** [tests/unit/test_chat_crud.py L1-L223](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L1-L223)

 [tests/unit/test_generate_diagram.py L1-L361](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L1-L361)

 [tests/unit/test_diagram_renderer.py L1-L369](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L1-L369)

 [tests/unit/test_mermaid_components.py L1-L240](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L1-L240)

---

## Test Coverage Overview

The test suite covers all major backend components with comprehensive unit tests that verify both success and failure paths.

| Component | Test File | Test Classes | Total Tests | Coverage Focus |
| --- | --- | --- | --- | --- |
| `chat_crud` Lambda | `test_chat_crud.py` | `TestChatCrudLambda` | 8 | Request validation, message saving, DynamoDB operations |
| `generate_diagram` Lambda | `test_generate_diagram.py` | 5 classes | 25 | Request validation, LLM integration, response handling |
| `diagram_renderer` | `test_diagram_renderer.py` | 5 classes | 19 | PNG rendering, fallback logic, S3 storage |
| Mermaid components | `test_mermaid_components.py` | 3 functions | 15+ | Syntax validation, code extraction, prompt building |

**Sources:** [tests/unit/test_chat_crud.py L32-L218](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L32-L218)

 [tests/unit/test_generate_diagram.py L64-L357](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L64-L357)

 [tests/unit/test_diagram_renderer.py L39-L365](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L39-L365)

 [tests/unit/test_mermaid_components.py L19-L209](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L19-L209)

---

## Lambda Function Tests

### chat_crud Lambda Tests

The `TestChatCrudLambda` class verifies the chat message persistence Lambda function, focusing on request validation, chatId generation, and DynamoDB operations.

#### Request Validation Tests

**Sources:** [tests/unit/test_chat_crud.py L35-L76](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L35-L76)

```

```

Key test cases:

* **test_validate_request_success** [tests/unit/test_chat_crud.py L35-L44](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L35-L44) : Verifies that requests with both `userMessage` and `diagramType` pass validation
* **test_validate_request_missing_user_message** [tests/unit/test_chat_crud.py L46-L54](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L46-L54) : Ensures validation fails when `userMessage` is absent
* **test_validate_request_invalid_diagram_type** [tests/unit/test_chat_crud.py L66-L75](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L66-L75) : Confirms that unsupported diagram types are rejected

#### Message Saving Tests

**Sources:** [tests/unit/test_chat_crud.py L77-L167](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L77-L167)

```

```

The `save_message` function tests verify:

* **ChatId generation**: When no `chatId` is provided, the function generates a UUID [tests/unit/test_chat_crud.py L77-L106](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L77-L106)
* **ChatId preservation**: When `chatId` is provided, it is used without modification [tests/unit/test_chat_crud.py L108-L133](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L108-L133)
* **Optional fields**: Fields like `aiResponse`, `mermaidCode`, `imageUrl`, `markdownUrl`, and `status` are correctly saved when present [tests/unit/test_chat_crud.py L135-L166](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L135-L166)

#### Lambda Handler Tests

**Sources:** [tests/unit/test_chat_crud.py L185-L217](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L185-L217)

Tests for the `lambda_handler` function verify CORS handling and HTTP method routing:

* **test_lambda_handler_options_request**: Verifies OPTIONS requests return 200 with CORS headers
* **test_lambda_handler_post_request**: Confirms POST requests are routed to `save_message` and return proper responses

**Sources:** [tests/unit/test_chat_crud.py L32-L218](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L32-L218)

---

### generate_diagram Lambda Tests

The `test_generate_diagram.py` file contains five test classes that comprehensively verify the diagram generation pipeline.

#### Test Class: TestRequestValidation

**Sources:** [tests/unit/test_generate_diagram.py L64-L147](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L64-L147)

Validates incoming API Gateway events before processing:

| Test Method | Validates | Expected Outcome |
| --- | --- | --- |
| `test_valid_request` | Complete request with `userPrompt` and `diagramType` | `is_valid=True`, body parsed correctly |
| `test_missing_user_prompt` | Request without `userPrompt` | `is_valid=False`, error contains 'userPrompt' |
| `test_missing_diagram_type` | Request without `diagramType` | `is_valid=False`, error contains 'diagramType' |
| `test_empty_user_prompt` | Request with whitespace-only prompt | `is_valid=False`, error contains 'non-empty' |
| `test_invalid_diagram_type` | Request with unsupported type | `is_valid=False`, error contains 'Invalid diagram type' |
| `test_invalid_json` | Malformed JSON in request body | `is_valid=False`, error contains 'Invalid JSON' |

The `validate_request` function returns a tuple: `(is_valid: bool, error: str, body: dict)`.

**Sources:** [tests/unit/test_generate_diagram.py L64-L147](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L64-L147)

#### Test Class: TestMermaidValidator

**Sources:** [tests/unit/test_generate_diagram.py L149-L236](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L149-L236)

```

```

The validator performs comprehensive checks:

* **Diagram type declaration**: Ensures code starts with proper declaration (`graph TD`, `erDiagram`, `sequenceDiagram`, etc.)
* **Multi-line requirement**: Diagrams must have content beyond the declaration line
* **Fence marker detection**: Code should be clean without ``` markdown fence markers
* **Bracket balancing**: For flowcharts, validates that `[`, `]`, `{`, `}`, `(`, `)` are balanced
* **Type-specific validation**: Each diagram type has specific requirements (e.g., ER diagrams need relationships, sequence diagrams need participants)

**Sources:** [tests/unit/test_generate_diagram.py L149-L236](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L149-L236)

#### Test Class: TestMermaidExtractor

**Sources:** [tests/unit/test_generate_diagram.py L238-L299](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L238-L299)

Tests the multi-tier extraction strategy for extracting Mermaid code from LLM responses:

```

```

Key extraction test cases:

* **test_extract_with_mermaid_tag** [tests/unit/test_generate_diagram.py L241-L258](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L241-L258) : Extracts code from explicit `\```mermaid` blocks
* **test_extract_multiple_blocks** [tests/unit/test_generate_diagram.py L259-L277](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L259-L277) : Returns first valid block when multiple exist
* **test_extract_no_code_block** [tests/unit/test_generate_diagram.py L279-L285](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L279-L285) : Returns `None` when no code blocks found
* **test_clean_mermaid_code** [tests/unit/test_generate_diagram.py L287-L298](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L287-L298) : Verifies fence marker removal and whitespace cleanup

**Sources:** [tests/unit/test_generate_diagram.py L238-L299](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L238-L299)

#### Test Class: TestPromptBuilder

**Sources:** [tests/unit/test_generate_diagram.py L301-L333](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L301-L333)

Validates prompt construction for different diagram types:

| Test Method | Verifies |
| --- | --- |
| `test_build_complete_prompt` | Returns dict with 'system' and 'user' keys, includes diagram type in user prompt |
| `test_get_supported_types` | Returns all 7 supported types: flowchart, erdiagram, sequence, class, state, architecture, dfd |
| `test_prompt_contains_syntax_rules` | System prompts contain Mermaid syntax rules (e.g., 'sequenceDiagram', 'participant') |

The `build_complete_prompt` function returns:

```

```

**Sources:** [tests/unit/test_generate_diagram.py L301-L333](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L301-L333)

#### Test Class: TestResponseHelpers

**Sources:** [tests/unit/test_generate_diagram.py L335-L357](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L335-L357)

Tests response formatting functions:

* **create_error_response(status_code, message)**: Returns API Gateway response with error in JSON body and CORS headers
* **create_success_response(data)**: Returns 200 response with data in JSON body and CORS headers

Both functions ensure the `Access-Control-Allow-Origin` header is present for frontend access.

**Sources:** [tests/unit/test_generate_diagram.py L335-L357](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L335-L357)

---

## Component Tests

### Diagram Renderer Tests

The `test_diagram_renderer.py` file contains 19 tests organized into 5 test classes that verify PNG rendering, fallback mechanisms, and S3 storage.

#### Rendering Pipeline Test Coverage

**Sources:** [tests/unit/test_diagram_renderer.py L39-L152](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L39-L152)

```

```

#### Primary Rendering Tests: TestRenderMermaidToPng

**Sources:** [tests/unit/test_diagram_renderer.py L39-L152](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L39-L152)

The primary rendering function `render_mermaid_to_png(mermaid_code)` is tested with:

| Test | Scenario | Mock Strategy | Assertion |
| --- | --- | --- | --- |
| `test_successful_rendering` | Normal rendering | Mock `requests.post` returns 200 with PNG bytes | Verifies PNG signature `\x89PNG\r\n\x1a\n`, correct endpoint, headers |
| `test_rendering_with_complex_diagram` | Multi-node diagram | Mock successful response | PNG bytes returned |
| `test_rendering_timeout` | Kroki timeout | Mock raises `requests.exceptions.Timeout` | Exception contains 'timed out' |
| `test_rendering_connection_error` | Network failure | Mock raises `ConnectionError` | Exception contains 'Failed to connect' |
| `test_rendering_http_error` | Invalid Mermaid code | Mock returns 400 with error text | Exception contains '400' and 'Kroki rendering failed' |
| `test_rendering_server_error` | Kroki service error | Mock returns 500 | Exception contains '500' |

The function posts to `https://kroki.io/mermaid/png` with:

* `Content-Type: text/plain` header
* `User-Agent: Architecture-AI-Assistant/1.0` header
* 30-second timeout

**Sources:** [tests/unit/test_diagram_renderer.py L39-L152](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L39-L152)

 [src/backend/lambda_functions/generate_diagram/diagram_renderer.py L14-L59](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/diagram_renderer.py#L14-L59)

#### Fallback and Placeholder Tests

**Sources:** [tests/unit/test_diagram_renderer.py L154-L223](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L154-L223)

The three-tier resilience strategy is tested:

1. **Primary rendering**: `render_mermaid_to_png()` [diagram_renderer.py L14-L59](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/diagram_renderer.py#L14-L59)
2. **Fallback rendering**: `render_mermaid_to_png_fallback()` [diagram_renderer.py L61-L94](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/diagram_renderer.py#L61-L94)
3. **Placeholder**: `generate_placeholder_png()` [diagram_renderer.py L96-L106](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/diagram_renderer.py#L96-L106)

The placeholder is a minimal 1x1 white pixel PNG (67 bytes) that ensures the system never completely fails to produce an image.

**Test validations:**

* Placeholder starts with PNG signature `\x89PNG\r\n\x1a\n`
* Placeholder size is under 200 bytes
* Placeholder is consistent across multiple calls

**Sources:** [tests/unit/test_diagram_renderer.py L199-L223](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L199-L223)

 [src/backend/lambda_functions/generate_diagram/diagram_renderer.py L96-L106](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/diagram_renderer.py#L96-L106)

#### S3 Storage Tests: TestSaveDiagramToS3

**Sources:** [tests/unit/test_diagram_renderer.py L225-L318](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L225-L318)

The `save_diagram_to_s3(s3_helper, chat_id, mermaid_code)` function is tested with various rendering outcomes:

```

```

Tests verify:

* Both markdown and image are saved to S3
* S3 helper methods are called with correct `chat_id` parameter
* CloudFront URLs are returned for both files
* Function succeeds even when rendering completely fails (uses placeholder)

**Sources:** [tests/unit/test_diagram_renderer.py L225-L318](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L225-L318)

 [src/backend/lambda_functions/generate_diagram/diagram_renderer.py L108-L149](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/diagram_renderer.py#L108-L149)

### Mermaid Component Tests

The `test_mermaid_components.py` file provides standalone tests for validator, extractor, and prompt builder modules without AWS dependencies.

**Sources:** [tests/unit/test_mermaid_components.py L1-L240](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L1-L240)

#### Validator Component Tests

**Sources:** [tests/unit/test_mermaid_components.py L19-L103](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L19-L103)

Function-based tests for `mermaid_validator.py`:

* **Valid diagram types**: Tests for flowchart, erdiagram, sequence, class, state diagrams
* **Invalid scenarios**: Empty code, fence markers, missing declaration, unbalanced brackets
* **Type-specific rules**: Each diagram type has specific validation requirements

Example test structure:

```

```

**Sources:** [tests/unit/test_mermaid_components.py L19-L103](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L19-L103)

#### Extractor Component Tests

**Sources:** [tests/unit/test_mermaid_components.py L105-L165](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L105-L165)

Tests for `mermaid_extractor.py`:

* **Extraction strategies**: Tests `\```mermaid` blocks, generic code blocks, raw text
* **Multiple blocks**: Verifies first block is returned
* **No code block**: Returns `None` when no code found
* **Cleaning**: Tests `clean_mermaid_code()` removes fence markers

**Sources:** [tests/unit/test_mermaid_components.py L105-L165](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L105-L165)

#### Prompt Builder Component Tests

**Sources:** [tests/unit/test_mermaid_components.py L167-L209](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L167-L209)

Tests for `prompt_builder.py`:

* **Complete prompts**: Verifies system and user prompts are generated
* **Supported types**: Confirms all 7 diagram types are supported
* **Syntax rules**: Ensures each diagram type has substantial instructions (>100 chars)

The `get_supported_diagram_types()` function returns:

```

```

**Sources:** [tests/unit/test_mermaid_components.py L167-L209](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L167-L209)

---

## Mocking Strategies

All unit tests use `unittest.mock` to isolate components from external dependencies. The primary mocking patterns are:

### AWS Service Mocking

**Sources:** [tests/unit/test_chat_crud.py L8-L13](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L8-L13)

 [tests/unit/test_generate_diagram.py L8-L15](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L8-L15)

```

```

This prevents `ImportError` when modules import AWS SDK components. The `DynamoDBHelper` and `S3Helper` classes are then mocked at the instance level:

```

```

**Sources:** [tests/unit/test_chat_crud.py L79-L102](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L79-L102)

### HTTP Request Mocking

**Sources:** [tests/unit/test_diagram_renderer.py L42-L62](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L42-L62)

The `requests.post` function is mocked using `@patch` decorator:

```

```

This simulates Kroki API responses without making network calls.

**Sources:** [tests/unit/test_diagram_renderer.py L42-L62](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L42-L62)

### Module Import Isolation

**Sources:** [tests/unit/test_generate_diagram.py L30-L61](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L30-L61)

Tests use `importlib.util` to load modules explicitly:

```

```

This prevents module naming conflicts when testing multiple Lambda functions that all have `lambda_function.py` files.

**Sources:** [tests/unit/test_generate_diagram.py L30-L36](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L30-L36)

 [tests/unit/test_chat_crud.py L26-L29](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L26-L29)

---

## Running Tests

### Prerequisites

Install test dependencies:

```

```

**Sources:** [docs/tests/DIAGRAM_RENDERER_TESTS.md L93-L96](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/tests/DIAGRAM_RENDERER_TESTS.md#L93-L96)

### Running All Tests

Execute the complete test suite:

```

```

### Running Specific Test Files

Run tests for a single component:

```

```

**Sources:** [docs/tests/DIAGRAM_RENDERER_TESTS.md L52-L67](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/tests/DIAGRAM_RENDERER_TESTS.md#L52-L67)

### Running Specific Test Classes

Execute a single test class:

```

```

### Running Individual Tests

Execute a single test method:

```

```

**Sources:** [docs/tests/DIAGRAM_RENDERER_TESTS.md L59-L67](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/tests/DIAGRAM_RENDERER_TESTS.md#L59-L67)

### Running with Coverage

Generate coverage reports:

```

```

**Sources:** [docs/tests/DIAGRAM_RENDERER_TESTS.md L69-L72](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/tests/DIAGRAM_RENDERER_TESTS.md#L69-L72)

### Manual Test Scripts

For quick verification without pytest, run standalone test scripts:

```

```

These scripts use simple assertions and print test results directly.

**Sources:** [tests/unit/test_mermaid_components.py L211-L236](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L211-L236)

 [tests/unit/manual_test_generate_diagram.py L176-L204](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/manual_test_generate_diagram.py#L176-L204)

---

## Test Assertions and Patterns

### Common Assertion Patterns

**Sources:** Throughout test files

```

```

### Validation Function Testing Pattern

**Sources:** [tests/unit/test_generate_diagram.py L64-L147](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L64-L147)

 [tests/unit/test_chat_crud.py L35-L76](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L35-L76)

Validation functions return tuples that are tested comprehensively:

```

```

### Mock Verification Pattern

**Sources:** [tests/unit/test_chat_crud.py L101-L106](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L101-L106)

Tests verify mocks were called with correct arguments:

```

```

---

## Test-Driven Component Structure

The test organization mirrors the module structure, creating a clear mapping between tests and implementation:

```

```

This structure ensures:

* Every Lambda function has comprehensive unit tests
* Core modules (validator, extractor, prompt builder, renderer) have both integration tests (via Lambda tests) and standalone component tests
* Mocking is consistent across all test files
* Test isolation prevents cascading failures

**Sources:** [tests/unit/test_chat_crud.py L1-L223](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py#L1-L223)

 [tests/unit/test_generate_diagram.py L1-L361](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L1-L361)

 [tests/unit/test_diagram_renderer.py L1-L369](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L1-L369)

 [tests/unit/test_mermaid_components.py L1-L240](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L1-L240)