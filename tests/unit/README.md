# Unit Tests

Unit tests for individual components and functions of the Architecture AI Assistant.

## Overview

Unit tests verify the correctness of individual functions, classes, and modules in isolation.

## Test Structure

```
unit/
├── README.md
├── backend/
│   ├── test_prompt_builder.py
│   ├── test_mermaid_extractor.py
│   ├── test_mermaid_validator.py
│   └── test_aws_helpers.py
└── frontend/
    ├── test_api_service.ts
    ├── test_mermaid_parser.ts
    └── test_components.test.tsx
```

## Backend Unit Tests

### test_prompt_builder.py
Tests the LLM prompt construction logic:
- Verify system prompts contain diagram-type-specific instructions
- Test prompt formatting and escaping
- Validate prompt length and structure

### test_mermaid_extractor.py
Tests Mermaid code extraction from LLM responses:
- Extract code from ```mermaid blocks
- Handle multiple code blocks
- Handle missing or malformed blocks

### test_mermaid_validator.py
Tests Mermaid syntax validation:
- Validate flowchart syntax
- Validate ERD syntax
- Validate sequence diagram syntax
- Detect invalid syntax

### test_aws_helpers.py
Tests AWS service helper functions:
- DynamoDB operations
- S3 operations
- Error handling

## Frontend Unit Tests

### test_api_service.ts
Tests API service functions:
- Request formatting
- Response parsing
- Error handling
- Retry logic

### test_mermaid_parser.ts
Tests Mermaid to React Flow conversion:
- Parse flowchart syntax
- Parse ERD syntax
- Parse sequence diagrams
- Handle invalid input

### test_components.test.tsx
Tests React components:
- Component rendering
- Event handling
- State management
- Props validation

## Running Unit Tests

### Backend Tests

```bash
# Run all backend unit tests
pytest tests/unit/backend/

# Run specific test file
pytest tests/unit/backend/test_prompt_builder.py

# Run with coverage
pytest tests/unit/backend/ --cov=src/backend
```

### Frontend Tests

```bash
# Run all frontend unit tests
npm test -- tests/unit/frontend/

# Run specific test file
npm test -- tests/unit/frontend/test_api_service.ts

# Run with coverage
npm test -- tests/unit/frontend/ --coverage
```

## Test Coverage Goals

- **Backend**: Minimum 80% code coverage
- **Frontend**: Minimum 75% code coverage
- **Critical paths**: 100% coverage

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Test names should describe what is being tested
3. **Arrange-Act-Assert**: Follow AAA pattern
4. **Mocking**: Mock external dependencies
5. **Edge Cases**: Test boundary conditions and error cases

## Example Unit Test

### Backend Example (pytest)

```python
import pytest
from src.backend.shared.prompt_builder import build_system_prompt

def test_build_system_prompt_flowchart():
    """Test that system prompt contains flowchart-specific instructions"""
    prompt = build_system_prompt('flowchart')
    
    assert 'graph TD' in prompt or 'graph LR' in prompt
    assert 'Mermaid' in prompt
    assert 'flowchart' in prompt.lower()

def test_build_system_prompt_erdiagram():
    """Test that system prompt contains ERD-specific instructions"""
    prompt = build_system_prompt('erdiagram')
    
    assert 'erDiagram' in prompt
    assert 'relationship' in prompt.lower()
```

### Frontend Example (Vitest)

```typescript
import { describe, it, expect } from 'vitest'
import { parseFlowchart } from '@/utils/mermaidParser'

describe('Mermaid Parser', () => {
  it('should parse simple flowchart', () => {
    const mermaidCode = `graph TD
      A[Start] --> B[End]`
    
    const result = parseFlowchart(mermaidCode)
    
    expect(result.nodes).toHaveLength(2)
    expect(result.edges).toHaveLength(1)
  })

  it('should handle invalid syntax', () => {
    const invalidCode = 'invalid mermaid code'
    
    expect(() => parseFlowchart(invalidCode)).toThrow()
  })
})
```

## Future Enhancements

- [ ] Snapshot testing for components
- [ ] Performance benchmarking
- [ ] Mutation testing
- [ ] Contract testing
- [ ] Visual regression testing
