# Generate Diagram Function

> **Relevant source files**
> * [docs/tests/DIAGRAM_RENDERER_TESTS.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/tests/DIAGRAM_RENDERER_TESTS.md)
> * [src/backend/lambda_functions/generate_diagram/README.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/README.md)
> * [src/backend/lambda_functions/generate_diagram/diagram_renderer.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/diagram_renderer.py)
> * [src/backend/lambda_functions/generate_diagram/mermaid_extractor.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/mermaid_extractor.py)
> * [src/backend/lambda_functions/generate_diagram/mermaid_validator.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/mermaid_validator.py)
> * [src/backend/lambda_functions/generate_diagram/prompt_builder.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/prompt_builder.py)
> * [tests/unit/manual_test_generate_diagram.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/manual_test_generate_diagram.py)
> * [tests/unit/test_chat_crud.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_chat_crud.py)
> * [tests/unit/test_diagram_renderer.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py)
> * [tests/unit/test_generate_diagram.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py)
> * [tests/unit/test_mermaid_components.py](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py)

## Purpose and Scope

The `generate_diagram` Lambda function is the core backend service responsible for converting natural language descriptions into validated Mermaid diagram code and rendered PNG images. This function orchestrates LLM API calls, Mermaid code validation, diagram rendering via Kroki, and persistence to S3 and DynamoDB.

This page provides an overview of the Lambda's architecture, request flow, and module integration. For detailed information about specific components:

* Mermaid validation rules and type-specific checks: see [Mermaid Code Validation](/dotpep/architecture-ai-assistant/4.1.1-mermaid-code-validation)
* Multi-tier code extraction strategies: see [Mermaid Code Extraction](/dotpep/architecture-ai-assistant/4.1.2-mermaid-code-extraction)
* PNG rendering and S3 storage workflows: see [Diagram Rendering and Storage](/dotpep/architecture-ai-assistant/4.1.3-diagram-rendering-and-storage)
* Prompt construction and LLM instruction engineering: see [Prompt Builder](/dotpep/architecture-ai-assistant/4.1.4-prompt-builder)

**Sources:** [src/backend/lambda_functions/generate_diagram/README.md L1-L132](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/README.md#L1-L132)

 [src/backend/lambda_functions/generate_diagram/lambda_function.py L1-L50](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L1-L50)

---

## Lambda Handler Entry Point

The Lambda function is invoked by API Gateway and handles HTTP POST requests containing diagram generation parameters. The main entry point is the `lambda_handler` function.

### Request Structure

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `userPrompt` | string | Yes | Natural language description of the diagram |
| `diagramType` | string | Yes | One of: `flowchart`, `erdiagram`, `sequence`, `class`, `state`, `architecture`, `dfd` |
| `chatId` | string | No | Optional existing chat ID to associate with |

### Response Structure

**Success Response (200):**

```json
{
  "chatId": "uuid-string",
  "timestamp": 1702564800,
  "mermaidCode": "graph TD\\n  A[Start] --> B[End]",
  "imageUrl": "https://cloudfront-url/diagrams/uuid.png",
  "markdownUrl": "https://cloudfront-url/diagrams/uuid.md",
  "status": "completed"
}
```

**Error Response (400/500/502):**

```json
{
  "error": "Error message describing the failure"
}
```

**Sources:** [src/backend/lambda_functions/generate_diagram/README.md L62-L99](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/README.md#L62-L99)

 [tests/unit/test_generate_diagram.py L69-L82](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L69-L82)

---

## Request Validation Pipeline

The `validate_request` function performs comprehensive input validation before proceeding with diagram generation.

### Validation Flow

```mermaid
flowchart TD

Start["lambda_handler invoked"]
ParseJSON["Parse event['body'] as JSON"]
CheckPrompt["Check userPrompt exists"]
ReturnError1["Return 400: Invalid JSON"]
ReturnError2["Return 400: Missing userPrompt"]
CheckEmpty["Check userPrompt.strip() not empty"]
ReturnError3["Return 400: userPrompt must be non-empty"]
CheckType["Check diagramType exists"]
ReturnError4["Return 400: Missing diagramType"]
ValidateType["Validate diagramType in SUPPORTED_TYPES"]
ReturnError5["Return 400: Invalid diagram type"]
Success["Return is_valid=True, body"]

Start --> ParseJSON
ParseJSON --> CheckPrompt
ParseJSON --> ReturnError1
CheckPrompt --> ReturnError2
CheckPrompt --> CheckEmpty
CheckEmpty --> ReturnError3
CheckEmpty --> CheckType
CheckType --> ReturnError4
CheckType --> ValidateType
ValidateType --> ReturnError5
ValidateType --> Success
```

### Supported Diagram Types

The function validates against a fixed set of supported diagram types defined in `SUPPORTED_DIAGRAM_TYPES`:

| Type | Mermaid Declaration | Use Case |
| --- | --- | --- |
| `flowchart` | `graph TD/LR` or `flowchart TD/LR` | Process flows, decision trees |
| `erdiagram` | `erDiagram` | Database schemas, entity relationships |
| `sequence` | `sequenceDiagram` | API interactions, message flows |
| `class` | `classDiagram` | Object-oriented design, class hierarchies |
| `state` | `stateDiagram-v2` | State machines, workflow states |
| `architecture` | `graph TD/LR` | System architecture, component diagrams |
| `dfd` | `graph TD/LR` | Data flow diagrams, process mapping |

**Sources:** [src/backend/lambda_functions/generate_diagram/lambda_function.py L30-L80](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L30-L80)

 [tests/unit/test_generate_diagram.py L64-L146](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L64-L146)

 [src/backend/lambda_functions/generate_diagram/prompt_builder.py L300-L307](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/prompt_builder.py#L300-L307)

---

## LLM Integration Workflow

The Lambda function integrates with an external OpenAI-compatible LLM API to generate Mermaid diagram code from natural language descriptions.

### LLM Call Sequence

```mermaid
sequenceDiagram
  participant lambda_handler
  participant prompt_builder.build_complete_prompt
  participant External LLM API
  participant mermaid_extractor.extract_mermaid_code
  participant mermaid_validator.validate

  lambda_handler->>prompt_builder.build_complete_prompt: build_complete_prompt(userPrompt, diagramType)
  prompt_builder.build_complete_prompt-->>lambda_handler: {system: prompt, user: prompt}
  lambda_handler->>External LLM API: POST /chat/completions
  note over lambda_handler,External LLM API: Headers: Authorization: Bearer {LLM_API_KEY}
  External LLM API-->>lambda_handler: {choices: [{message: {content: "..."}}]}
  lambda_handler->>mermaid_extractor.extract_mermaid_code: extract_mermaid_code(llm_response)
  note over mermaid_extractor.extract_mermaid_code: Multi-tier extraction:
  mermaid_extractor.extract_mermaid_code-->>lambda_handler: mermaid_code or None
  lambda_handler->>mermaid_validator.validate: validate(mermaid_code, diagramType)
  note over mermaid_validator.validate: Checks:
  mermaid_validator.validate-->>lambda_handler: (is_valid, error_message)
```

### Environment Variables for LLM Configuration

The function reads LLM configuration from environment variables set by Terraform:

| Variable | Purpose | Example |
| --- | --- | --- |
| `LLM_API_ENDPOINT` | LLM API base URL | `https://api.openai.com/v1` |
| `LLM_API_KEY` | Authentication key | `sk-...` |
| `LLM_MODEL` | Model identifier | `gpt-3.5-turbo` (default) |

**Sources:** [src/backend/lambda_functions/generate_diagram/README.md L53-L61](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/README.md#L53-L61)

 [src/backend/lambda_functions/generate_diagram/lambda_function.py L100-L150](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L100-L150)

---

## Core Processing Pipeline

The following diagram shows the complete processing flow with actual function names and module boundaries.

### Complete Processing Flow with Code Entities

```mermaid
flowchart TD

APIGW["POST /api/diagram/generate"]
Handler["lambda_handler(event, context)"]
Validate["validate_request(event)<br>Returns: (is_valid, error, body)"]
ErrorResp["create_error_response(status, msg)<br>Returns: HTTP response dict"]
SuccessResp["create_success_response(data)<br>Returns: HTTP response dict"]
BuildPrompt["build_complete_prompt(user_desc, diagram_type)<br>Returns: {system: str, user: str}"]
SysPrompt["build_system_prompt(diagram_type)<br>Uses: DIAGRAM_INSTRUCTIONS dict"]
LLM["LLM API POST /chat/completions<br>Endpoint: LLM_API_ENDPOINT env var"]
Extract["extract_mermaid_code(llm_response)<br>Returns: str or None"]
Clean["clean_mermaid_code(code)<br>Removes fence markers"]
ValidateMermaid["MermaidValidator.validate(code, type)<br>Returns: (bool, Optional[str])"]
TypeSpecific["_validate_type_specific(code, type)<br>Calls: _validate_flowchart, _validate_erdiagram, etc."]
SaveS3["save_diagram_to_s3(s3_helper, chat_id, code)<br>Returns: (markdown_url, image_url)"]
RenderPNG["render_mermaid_to_png(code)<br>POST to Kroki API"]
Fallback["render_mermaid_to_png_fallback(code)<br>Retry mechanism"]
Placeholder["generate_placeholder_png()<br>Returns: 1x1 white PNG bytes"]
S3Helper["S3Helper.put_diagram_markdown(chat_id, code)<br>S3Helper.put_diagram_image(chat_id, png_data)"]
DDBHelper["DynamoDBHelper.put_item(item)<br>Saves to DYNAMODB_TABLE_NAME"]

APIGW --> Handler
Validate --> BuildPrompt
BuildPrompt --> LLM
LLM --> Extract
Clean --> ValidateMermaid
ValidateMermaid --> ErrorResp
ValidateMermaid --> SaveS3
RenderPNG --> S3Helper
Fallback --> S3Helper
Placeholder --> S3Helper
DDBHelper --> SuccessResp
ErrorResp --> APIGW
SuccessResp --> APIGW

subgraph aws_helpers.py ["aws_helpers.py"]
    S3Helper
    DDBHelper
    S3Helper --> DDBHelper
end

subgraph diagram_renderer.py ["diagram_renderer.py"]
    SaveS3
    RenderPNG
    Fallback
    Placeholder
    SaveS3 --> RenderPNG
    RenderPNG --> Fallback
    Fallback --> Placeholder
end

subgraph mermaid_validator.py ["mermaid_validator.py"]
    ValidateMermaid
    TypeSpecific
    ValidateMermaid --> TypeSpecific
end

subgraph mermaid_extractor.py ["mermaid_extractor.py"]
    Extract
    Clean
    Extract --> Clean
end

subgraph subGraph3 ["External LLM"]
    LLM
end

subgraph prompt_builder.py ["prompt_builder.py"]
    BuildPrompt
    SysPrompt
    BuildPrompt --> SysPrompt
end

subgraph lambda_function.py ["lambda_function.py"]
    Handler
    Validate
    ErrorResp
    SuccessResp
    Handler --> Validate
    Validate --> ErrorResp
end

subgraph subGraph0 ["API Gateway"]
    APIGW
end
```

**Sources:** [src/backend/lambda_functions/generate_diagram/lambda_function.py L1-L250](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L1-L250)

 [tests/unit/test_generate_diagram.py L1-L361](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L1-L361)

---

## Module Architecture and Responsibilities

The `generate_diagram` Lambda function is composed of five specialized modules, each with distinct responsibilities.

### Module Dependency Map

```mermaid
flowchart TD

LF["lambda_function.py<br>Main handler<br>Orchestration logic"]
PB["prompt_builder.py<br>build_complete_prompt()<br>build_system_prompt()<br>build_user_prompt()<br>DIAGRAM_INSTRUCTIONS"]
ME["mermaid_extractor.py<br>extract_mermaid_code()<br>clean_mermaid_code()<br>is_likely_mermaid()"]
MV["mermaid_validator.py<br>MermaidValidator.validate()<br>_validate_flowchart()<br>_validate_erdiagram()<br>_validate_sequence()"]
DR["diagram_renderer.py<br>render_mermaid_to_png()<br>render_mermaid_to_png_fallback()<br>generate_placeholder_png()<br>save_diagram_to_s3()"]
AH["aws_helpers.py<br>S3Helper<br>DynamoDBHelper"]

LF --> PB
LF --> ME
LF --> MV
LF --> DR
DR --> AH
LF --> AH

subgraph subGraph5 ["AWS Integration"]
    AH
end

subgraph subGraph4 ["Rendering & Storage"]
    DR
end

subgraph Validation ["Validation"]
    MV
end

subgraph subGraph2 ["LLM Response Processing"]
    ME
end

subgraph subGraph1 ["Prompt Engineering"]
    PB
end

subgraph subGraph0 ["Core Lambda"]
    LF
end
```

### Module Function Summary

| Module | Key Functions | Primary Responsibility |
| --- | --- | --- |
| `lambda_function.py` | `lambda_handler`, `validate_request`, `create_error_response`, `create_success_response` | Request orchestration, LLM API calls |
| `prompt_builder.py` | `build_complete_prompt`, `build_system_prompt`, `build_user_prompt`, `get_supported_diagram_types` | Construct diagram-type-specific prompts with Mermaid syntax rules |
| `mermaid_extractor.py` | `extract_mermaid_code`, `clean_mermaid_code`, `is_likely_mermaid`, `extract_all_mermaid_blocks` | Parse and extract Mermaid code from LLM text responses |
| `mermaid_validator.py` | `MermaidValidator.validate`, `_validate_flowchart`, `_validate_erdiagram`, `_validate_sequence`, `_validate_class`, `_validate_state` | Type-specific syntax validation and structural checks |
| `diagram_renderer.py` | `render_mermaid_to_png`, `render_mermaid_to_png_fallback`, `generate_placeholder_png`, `save_diagram_to_s3` | PNG rendering via Kroki, fallback handling, S3 persistence |

**Sources:** [src/backend/lambda_functions/generate_diagram/lambda_function.py L1-L50](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L1-L50)

 [src/backend/lambda_functions/generate_diagram/prompt_builder.py L1-L308](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/prompt_builder.py#L1-L308)

 [src/backend/lambda_functions/generate_diagram/mermaid_extractor.py L1-L181](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/mermaid_extractor.py#L1-L181)

 [src/backend/lambda_functions/generate_diagram/mermaid_validator.py L1-L222](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/mermaid_validator.py#L1-L222)

 [src/backend/lambda_functions/generate_diagram/diagram_renderer.py L1-L149](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/diagram_renderer.py#L1-L149)

---

## Error Handling Strategy

The Lambda implements comprehensive error handling at multiple stages of the processing pipeline.

### Error Categories and HTTP Status Codes

| Error Category | Status Code | Trigger Conditions | Response Function |
| --- | --- | --- | --- |
| Invalid Request | 400 | Missing/empty `userPrompt`, invalid `diagramType`, malformed JSON | `create_error_response(400, error)` |
| Validation Failure | 400 | Mermaid code fails validation (syntax errors, unbalanced brackets, missing declarations) | `create_error_response(400, error)` |
| LLM API Error | 502 | LLM endpoint unreachable, authentication failure, timeout | `create_error_response(502, error)` |
| Internal Error | 500 | Unexpected exceptions, S3/DynamoDB failures | `create_error_response(500, error)` |

### Graceful Degradation for PNG Rendering

The rendering pipeline implements a three-tier fallback strategy to ensure the function never fails completely due to rendering issues:

```mermaid
flowchart TD

Start["save_diagram_to_s3 called"]
Primary["render_mermaid_to_png(code)"]
SavePNG["s3_helper.put_diagram_image(chat_id, png_data)"]
Fallback["render_mermaid_to_png_fallback(code)"]
Placeholder["generate_placeholder_png()"]
SaveMD["s3_helper.put_diagram_markdown(chat_id, mermaid_code)"]
Return["Return (markdown_url, image_url)"]

Start --> Primary
Primary --> SavePNG
Primary --> Fallback
Fallback --> SavePNG
Fallback --> Placeholder
Placeholder --> SavePNG
SavePNG --> SaveMD
SaveMD --> Return
```

This ensures that even if both Kroki rendering attempts fail, the function still saves the markdown source and a placeholder PNG, allowing the system to remain operational.

**Sources:** [src/backend/lambda_functions/generate_diagram/diagram_renderer.py L108-L149](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/diagram_renderer.py#L108-L149)

 [src/backend/lambda_functions/generate_diagram/lambda_function.py L200-L250](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L200-L250)

 [tests/unit/test_diagram_renderer.py L225-L318](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L225-L318)

---

## Configuration and Environment Variables

The Lambda function requires several environment variables to be set by Terraform during deployment.

### Required Environment Variables

| Variable | Type | Purpose | Set By |
| --- | --- | --- | --- |
| `DYNAMODB_TABLE_NAME` | string | DynamoDB table name for chat history persistence | [infrastructure/terraform/lambda.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf) |
| `S3_BUCKET_NAME` | string | S3 bucket name for diagram storage (markdown + PNG) | [infrastructure/terraform/lambda.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf) |
| `CLOUDFRONT_URL` | string | CloudFront distribution URL for generating public diagram URLs | [infrastructure/terraform/lambda.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf) |
| `LLM_API_ENDPOINT` | string | Base URL for LLM API (e.g., `https://api.openai.com/v1`) | [infrastructure/terraform/variables.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf) |
| `LLM_API_KEY` | string | API authentication key for LLM service | [infrastructure/terraform/variables.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/variables.tf) <br>  (sensitive) |
| `LLM_MODEL` | string | LLM model identifier (default: `gpt-3.5-turbo`) | [infrastructure/terraform/lambda.tf](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/lambda.tf) |

### AWS Service Integration

The function integrates with three AWS services:

* **DynamoDB**: Stores chat metadata including `chatId`, `timestamp`, `userMessage`, `diagramType`, `mermaidCode`, `imageUrl`, `markdownUrl`, and `status`
* **S3**: Stores diagram files in two formats: * `/diagrams/{chatId}.md` - Mermaid markdown source * `/diagrams/{chatId}.png` - Rendered PNG image
* **CloudFront**: Serves diagrams via CDN with URL pattern `https://{cloudfront-domain}/diagrams/{chatId}.{md|png}`

**Sources:** [src/backend/lambda_functions/generate_diagram/README.md L53-L61](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/README.md#L53-L61)

 [src/backend/lambda_functions/generate_diagram/lambda_function.py L10-L30](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/src/backend/lambda_functions/generate_diagram/lambda_function.py#L10-L30)

---

## Testing Coverage

The Lambda function has comprehensive unit test coverage across all modules.

### Test Files

| Test File | Lines | Test Classes | Key Coverage |
| --- | --- | --- | --- |
| `test_generate_diagram.py` | 361 | `TestRequestValidation`, `TestMermaidValidator`, `TestMermaidExtractor`, `TestPromptBuilder`, `TestResponseHelpers` | End-to-end request validation, all diagram types validation, extraction strategies, prompt construction |
| `test_diagram_renderer.py` | 369 | `TestRenderMermaidToPng`, `TestRenderMermaidToPngFallback`, `TestGeneratePlaceholderPng`, `TestSaveDiagramToS3`, `TestIntegration` | PNG rendering, fallback mechanisms, S3 saving, error handling |
| `test_mermaid_components.py` | 240 | N/A (script-based) | Quick validation of validator, extractor, and prompt builder without AWS mocking |

### Test Execution

```markdown
# Run all generate_diagram tests
python -m pytest tests/unit/test_generate_diagram.py -v

# Run diagram renderer tests
python -m pytest tests/unit/test_diagram_renderer.py -v

# Run quick component tests (no pytest required)
python tests/unit/test_mermaid_components.py
```

**Sources:** [tests/unit/test_generate_diagram.py L1-L361](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_generate_diagram.py#L1-L361)

 [tests/unit/test_diagram_renderer.py L1-L369](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_diagram_renderer.py#L1-L369)

 [tests/unit/test_mermaid_components.py L1-L240](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/tests/unit/test_mermaid_components.py#L1-L240)

 [docs/tests/DIAGRAM_RENDERER_TESTS.md L1-L104](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/tests/DIAGRAM_RENDERER_TESTS.md#L1-L104)