"""
Manual test script for generate_diagram Lambda function.
Run this to verify basic functionality without pytest.
"""

import json
import sys
import os

# Add backend paths to sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.join(backend_path, 'shared'))
sys.path.insert(0, os.path.join(backend_path, 'lambda_functions', 'generate_diagram'))

# Import modules
from lambda_function import validate_request, create_error_response, create_success_response
from mermaid_validator import validate_mermaid_code
from mermaid_extractor import extract_mermaid_code, clean_mermaid_code
from prompt_builder import build_complete_prompt, get_supported_diagram_types


def test_request_validation():
    """Test request validation."""
    print("\n=== Testing Request Validation ===")
    
    # Test valid request
    event = {
        'body': json.dumps({
            'userPrompt': 'Create a flowchart for user login',
            'diagramType': 'flowchart'
        })
    }
    is_valid, error, body = validate_request(event)
    assert is_valid is True, "Valid request should pass"
    print("✓ Valid request passes")
    
    # Test missing userPrompt
    event = {'body': json.dumps({'diagramType': 'flowchart'})}
    is_valid, error, body = validate_request(event)
    assert is_valid is False, "Missing userPrompt should fail"
    assert 'userPrompt' in error
    print("✓ Missing userPrompt fails correctly")
    
    # Test invalid diagram type
    event = {
        'body': json.dumps({
            'userPrompt': 'Create a diagram',
            'diagramType': 'invalid_type'
        })
    }
    is_valid, error, body = validate_request(event)
    assert is_valid is False, "Invalid diagram type should fail"
    print("✓ Invalid diagram type fails correctly")


def test_mermaid_validator():
    """Test Mermaid validation."""
    print("\n=== Testing Mermaid Validator ===")
    
    # Test valid flowchart
    code = """graph TD
    A[Start] --> B[Process]
    B --> C[End]"""
    is_valid, error = validate_mermaid_code(code, 'flowchart')
    assert is_valid is True, f"Valid flowchart should pass: {error}"
    print("✓ Valid flowchart passes")
    
    # Test valid ER diagram
    code = """erDiagram
    CUSTOMER ||--o{ ORDER : places"""
    is_valid, error = validate_mermaid_code(code, 'erdiagram')
    assert is_valid is True, f"Valid ER diagram should pass: {error}"
    print("✓ Valid ER diagram passes")
    
    # Test valid sequence diagram
    code = """sequenceDiagram
    participant A
    A->>B: Request"""
    is_valid, error = validate_mermaid_code(code, 'sequence')
    assert is_valid is True, f"Valid sequence diagram should pass: {error}"
    print("✓ Valid sequence diagram passes")
    
    # Test empty code
    is_valid, error = validate_mermaid_code('', 'flowchart')
    assert is_valid is False, "Empty code should fail"
    print("✓ Empty code fails correctly")
    
    # Test code with fence markers
    code = """```mermaid
graph TD
    A --> B
```"""
    is_valid, error = validate_mermaid_code(code, 'flowchart')
    assert is_valid is False, "Code with fence markers should fail"
    print("✓ Code with fence markers fails correctly")


def test_mermaid_extractor():
    """Test Mermaid extraction."""
    print("\n=== Testing Mermaid Extractor ===")
    
    # Test extraction with mermaid tag
    response = """Here's your diagram:

```mermaid
graph TD
    A --> B
```

Hope this helps!"""
    code = extract_mermaid_code(response)
    assert code is not None, "Should extract code"
    assert 'graph TD' in code
    assert '```' not in code
    print("✓ Extraction with mermaid tag works")
    
    # Test extraction with no code block
    response = "This is just text without any code blocks."
    code = extract_mermaid_code(response)
    assert code is None, "Should return None for no code block"
    print("✓ No code block returns None")
    
    # Test cleaning
    code = """```mermaid
graph TD
    A --> B
```"""
    cleaned = clean_mermaid_code(code)
    assert '```' not in cleaned
    assert cleaned.startswith('graph TD')
    print("✓ Code cleaning works")


def test_prompt_builder():
    """Test prompt building."""
    print("\n=== Testing Prompt Builder ===")
    
    # Test building complete prompt
    prompts = build_complete_prompt('Create a login flow', 'flowchart')
    assert 'system' in prompts
    assert 'user' in prompts
    assert 'graph' in prompts['system']
    assert 'login flow' in prompts['user']
    print("✓ Complete prompt building works")
    
    # Test supported types
    types = get_supported_diagram_types()
    assert 'flowchart' in types
    assert 'erdiagram' in types
    assert 'sequence' in types
    print(f"✓ Supported types: {', '.join(types)}")


def test_response_helpers():
    """Test response helpers."""
    print("\n=== Testing Response Helpers ===")
    
    # Test error response
    response = create_error_response(400, 'Bad request')
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert body['error'] == 'Bad request'
    print("✓ Error response works")
    
    # Test success response
    data = {'chatId': '123', 'status': 'completed'}
    response = create_success_response(data)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['chatId'] == '123'
    print("✓ Success response works")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Manual Test Suite for generate_diagram Lambda Function")
    print("=" * 60)
    
    try:
        test_request_validation()
        test_mermaid_validator()
        test_mermaid_extractor()
        test_prompt_builder()
        test_response_helpers()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
