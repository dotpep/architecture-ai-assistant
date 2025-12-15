"""
Unit tests for generate_diagram Lambda function.
Tests core functionality including validation, Mermaid extraction, and error handling.
"""

import json
import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Mock boto3 before importing modules that use it
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()
sys.modules['botocore.exceptions'] = MagicMock()

# Add backend paths to sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend')
generate_diagram_path = os.path.join(backend_path, 'lambda_functions', 'generate_diagram')
shared_path = os.path.join(backend_path, 'shared')

# Clear sys.path of any conflicting lambda_function modules
sys.path = [p for p in sys.path if 'lambda_functions' not in p]

# Insert generate_diagram path FIRST so it takes precedence
sys.path.insert(0, generate_diagram_path)
sys.path.insert(1, shared_path)

# Import after path setup
import importlib.util

# Import lambda_function
spec = importlib.util.spec_from_file_location("generate_diagram_lambda", os.path.join(generate_diagram_path, "lambda_function.py"))
lambda_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lambda_module)

validate_request = lambda_module.validate_request
create_error_response = lambda_module.create_error_response
create_success_response = lambda_module.create_success_response

# Import other modules
spec = importlib.util.spec_from_file_location("mermaid_validator", os.path.join(generate_diagram_path, "mermaid_validator.py"))
mermaid_validator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mermaid_validator_module)

validate_mermaid_code = mermaid_validator_module.validate_mermaid_code
MermaidValidator = mermaid_validator_module.MermaidValidator

spec = importlib.util.spec_from_file_location("mermaid_extractor", os.path.join(generate_diagram_path, "mermaid_extractor.py"))
mermaid_extractor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mermaid_extractor_module)

extract_mermaid_code = mermaid_extractor_module.extract_mermaid_code
clean_mermaid_code = mermaid_extractor_module.clean_mermaid_code

spec = importlib.util.spec_from_file_location("prompt_builder", os.path.join(generate_diagram_path, "prompt_builder.py"))
prompt_builder_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_builder_module)

build_complete_prompt = prompt_builder_module.build_complete_prompt
get_supported_diagram_types = prompt_builder_module.get_supported_diagram_types


class TestRequestValidation:
    """Test request validation logic."""
    
    def test_valid_request(self):
        """Test validation of a valid request."""
        event = {
            'body': json.dumps({
                'userPrompt': 'Create a flowchart for user login',
                'diagramType': 'flowchart'
            })
        }
        
        is_valid, error, body = validate_request(event)
        
        assert is_valid is True
        assert error is None
        assert body['userPrompt'] == 'Create a flowchart for user login'
        assert body['diagramType'] == 'flowchart'
    
    def test_missing_user_prompt(self):
        """Test validation fails when userPrompt is missing."""
        event = {
            'body': json.dumps({
                'diagramType': 'flowchart'
            })
        }
        
        is_valid, error, body = validate_request(event)
        
        assert is_valid is False
        assert 'userPrompt' in error
    
    def test_missing_diagram_type(self):
        """Test validation fails when diagramType is missing."""
        event = {
            'body': json.dumps({
                'userPrompt': 'Create a diagram'
            })
        }
        
        is_valid, error, body = validate_request(event)
        
        assert is_valid is False
        assert 'diagramType' in error
    
    def test_empty_user_prompt(self):
        """Test validation fails when userPrompt is empty."""
        event = {
            'body': json.dumps({
                'userPrompt': '   ',
                'diagramType': 'flowchart'
            })
        }
        
        is_valid, error, body = validate_request(event)
        
        assert is_valid is False
        assert 'non-empty' in error
    
    def test_invalid_diagram_type(self):
        """Test validation fails for unsupported diagram type."""
        event = {
            'body': json.dumps({
                'userPrompt': 'Create a diagram',
                'diagramType': 'invalid_type'
            })
        }
        
        is_valid, error, body = validate_request(event)
        
        assert is_valid is False
        assert 'Invalid diagram type' in error
    
    def test_invalid_json(self):
        """Test validation fails for invalid JSON."""
        event = {
            'body': 'not valid json'
        }
        
        is_valid, error, body = validate_request(event)
        
        assert is_valid is False
        assert 'Invalid JSON' in error


class TestMermaidValidator:
    """Test Mermaid code validation."""
    
    def test_valid_flowchart(self):
        """Test validation of valid flowchart."""
        code = """graph TD
    A[Start] --> B[Process]
    B --> C[End]"""
        
        is_valid, error = validate_mermaid_code(code, 'flowchart')
        
        assert is_valid is True
        assert error is None
    
    def test_valid_erdiagram(self):
        """Test validation of valid ER diagram."""
        code = """erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER {
        int orderId
        date orderDate
    }"""
        
        is_valid, error = validate_mermaid_code(code, 'erdiagram')
        
        assert is_valid is True
        assert error is None
    
    def test_valid_sequence(self):
        """Test validation of valid sequence diagram."""
        code = """sequenceDiagram
    participant A
    participant B
    A->>B: Request
    B-->>A: Response"""
        
        is_valid, error = validate_mermaid_code(code, 'sequence')
        
        assert is_valid is True
        assert error is None
    
    def test_empty_code(self):
        """Test validation fails for empty code."""
        is_valid, error = validate_mermaid_code('', 'flowchart')
        
        assert is_valid is False
        assert 'empty' in error.lower()
    
    def test_code_with_fence_markers(self):
        """Test validation fails for code with fence markers."""
        code = """```mermaid
graph TD
    A --> B
```"""
        
        is_valid, error = validate_mermaid_code(code, 'flowchart')
        
        assert is_valid is False
        assert 'fence' in error.lower()
    
    def test_no_diagram_declaration(self):
        """Test validation fails without diagram type declaration."""
        code = "A --> B\nB --> C"
        
        is_valid, error = validate_mermaid_code(code, 'flowchart')
        
        assert is_valid is False
        assert 'declaration' in error.lower()
    
    def test_single_line_code(self):
        """Test validation fails for single-line code."""
        code = "graph TD"
        
        is_valid, error = validate_mermaid_code(code, 'flowchart')
        
        assert is_valid is False
        assert 'multiple lines' in error.lower()
    
    def test_unbalanced_brackets_flowchart(self):
        """Test validation fails for unbalanced brackets."""
        code = """graph TD
    A[Start --> B[End"""
        
        is_valid, error = validate_mermaid_code(code, 'flowchart')
        
        assert is_valid is False
        assert 'bracket' in error.lower()


class TestMermaidExtractor:
    """Test Mermaid code extraction from LLM responses."""
    
    def test_extract_with_mermaid_tag(self):
        """Test extraction from response with mermaid tag."""
        response = """Here's your diagram:

```mermaid
graph TD
    A --> B
```

Hope this helps!"""
        
        code = extract_mermaid_code(response)
        
        assert code is not None
        assert 'graph TD' in code
        assert 'A --> B' in code
        assert '```' not in code
    
    def test_extract_multiple_blocks(self):
        """Test extraction returns first block when multiple exist."""
        response = """```mermaid
graph TD
    A --> B
```

And here's another:

```mermaid
graph LR
    C --> D
```"""
        
        code = extract_mermaid_code(response)
        
        assert code is not None
        assert 'graph TD' in code
        assert 'A --> B' in code
    
    def test_extract_no_code_block(self):
        """Test extraction returns None when no code block found."""
        response = "This is just text without any code blocks."
        
        code = extract_mermaid_code(response)
        
        assert code is None
    
    def test_clean_mermaid_code(self):
        """Test cleaning of Mermaid code."""
        code = """```mermaid
graph TD
    A --> B
```"""
        
        cleaned = clean_mermaid_code(code)
        
        assert '```' not in cleaned
        assert 'graph TD' in cleaned
        assert cleaned.startswith('graph TD')


class TestPromptBuilder:
    """Test prompt building functionality."""
    
    def test_build_complete_prompt(self):
        """Test building complete prompt with system and user messages."""
        prompts = build_complete_prompt('Create a login flow', 'flowchart')
        
        assert 'system' in prompts
        assert 'user' in prompts
        assert 'graph TD' in prompts['system'] or 'graph LR' in prompts['system']
        assert 'login flow' in prompts['user']
        assert 'flowchart' in prompts['user']
    
    def test_get_supported_types(self):
        """Test getting list of supported diagram types."""
        types = get_supported_diagram_types()
        
        assert 'flowchart' in types
        assert 'erdiagram' in types
        assert 'sequence' in types
        assert 'class' in types
        assert 'state' in types
        assert 'architecture' in types
        assert 'dfd' in types
    
    def test_prompt_contains_syntax_rules(self):
        """Test that prompts contain Mermaid syntax rules."""
        prompts = build_complete_prompt('Create a diagram', 'sequence')
        
        assert 'sequenceDiagram' in prompts['system']
        assert 'participant' in prompts['system']
        assert 'mermaid' in prompts['system'].lower()


class TestResponseHelpers:
    """Test response helper functions."""
    
    def test_create_error_response(self):
        """Test creating error response."""
        response = create_error_response(400, 'Bad request')
        
        assert response['statusCode'] == 400
        assert 'error' in json.loads(response['body'])
        assert json.loads(response['body'])['error'] == 'Bad request'
        assert 'Access-Control-Allow-Origin' in response['headers']
    
    def test_create_success_response(self):
        """Test creating success response."""
        data = {'chatId': '123', 'status': 'completed'}
        response = create_success_response(data)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['chatId'] == '123'
        assert body['status'] == 'completed'
        assert 'Access-Control-Allow-Origin' in response['headers']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
