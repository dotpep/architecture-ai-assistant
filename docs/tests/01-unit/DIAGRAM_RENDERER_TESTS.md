# Diagram Renderer Unit Tests

## Overview
Comprehensive unit tests for the `diagram_renderer.py` module that handles PNG rendering via Kroki service.

## Test File
- **Location**: `tests/unit/test_diagram_renderer.py`
- **Total Tests**: 19
- **Status**: All passing ✓

## Test Coverage

### 1. TestRenderMermaidToPng (7 tests)
Tests the primary PNG rendering function.

- `test_successful_rendering`: Verifies successful PNG rendering with correct endpoint and headers
- `test_rendering_with_complex_diagram`: Tests rendering of complex multi-node diagrams
- `test_rendering_timeout`: Validates timeout exception handling (30s limit)
- `test_rendering_connection_error`: Tests connection failure handling
- `test_rendering_http_error`: Tests HTTP 400 error handling
- `test_rendering_server_error`: Tests HTTP 500 error handling
- `test_rendering_empty_response`: Tests handling of empty response body

### 2. TestRenderMermaidToPngFallback (3 tests)
Tests the fallback rendering function.

- `test_fallback_successful`: Verifies fallback rendering works correctly
- `test_fallback_http_error`: Tests fallback error handling
- `test_fallback_exception`: Tests fallback exception handling

### 3. TestGeneratePlaceholderPng (3 tests)
Tests placeholder PNG generation.

- `test_placeholder_is_valid_png`: Verifies PNG signature is correct
- `test_placeholder_size`: Validates placeholder is reasonably small
- `test_placeholder_consistency`: Ensures consistent output across calls

### 4. TestSaveDiagramToS3 (4 tests)
Tests S3 saving functionality.

- `test_save_successful`: Verifies successful save to S3
- `test_save_with_fallback`: Tests fallback when primary rendering fails
- `test_save_with_placeholder`: Tests placeholder usage when all rendering fails
- `test_save_with_different_chat_ids`: Tests multiple saves with different IDs

### 5. TestIntegration (2 tests)
Integration tests for complete workflows.

- `test_full_rendering_workflow`: Tests complete rendering pipeline
- `test_s3_save_workflow`: Tests complete S3 save workflow

## Running Tests

### Run all diagram renderer tests
```bash
python -m pytest tests/unit/test_diagram_renderer.py -v
```

### Run specific test class
```bash
python -m pytest tests/unit/test_diagram_renderer.py::TestRenderMermaidToPng -v
```

### Run specific test
```bash
python -m pytest tests/unit/test_diagram_renderer.py::TestRenderMermaidToPng::test_successful_rendering -v
```

### Run with coverage
```bash
python -m pytest tests/unit/test_diagram_renderer.py --cov=src.backend.lambda_functions.generate_diagram.diagram_renderer
```

## Key Features Tested

✓ PNG rendering via Kroki `/mermaid/png` endpoint
✓ Proper HTTP headers (Content-Type: text/plain)
✓ Error handling (timeout, connection, HTTP errors)
✓ Fallback rendering mechanism
✓ Placeholder PNG generation
✓ S3 integration with markdown and image saving
✓ Multi-diagram handling with different chat IDs
✓ Complex diagram support

## Mocking Strategy

- Uses `unittest.mock` for HTTP requests
- Mocks `requests.post` to simulate Kroki responses
- Mocks S3 helper for file operations
- Validates PNG signatures (magic bytes: `\x89PNG\r\n\x1a\n`)

## Dependencies

- pytest
- unittest.mock (built-in)
- requests (mocked)

## Notes

- All tests use mocking to avoid external dependencies
- PNG validation uses magic byte signature checking
- Tests cover both success and failure paths
- Fallback and placeholder mechanisms are thoroughly tested
