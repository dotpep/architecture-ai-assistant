"""
Simple test script for Mermaid components (no AWS dependencies).
Tests validator, extractor, and prompt builder.
"""

import sys
import os

# Add backend paths to sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend')
sys.path.insert(0, os.path.join(backend_path, 'lambda_functions', 'generate_diagram'))

# Import modules (these don't require boto3)
from mermaid_validator import validate_mermaid_code
from mermaid_extractor import extract_mermaid_code, clean_mermaid_code
from prompt_builder import build_complete_prompt, get_supported_diagram_types


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
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER {
        int customerId
    }
    ORDER {
        int orderId
    }"""
    is_valid, error = validate_mermaid_code(code, 'erdiagram')
    assert is_valid is True, f"Valid ER diagram should pass: {error}"
    print("✓ Valid ER diagram passes")
    
    # Test valid sequence diagram
    code = """sequenceDiagram
    participant A
    participant B
    A->>B: Request
    B-->>A: Response"""
    is_valid, error = validate_mermaid_code(code, 'sequence')
    assert is_valid is True, f"Valid sequence diagram should pass: {error}"
    print("✓ Valid sequence diagram passes")
    
    # Test valid class diagram
    code = """classDiagram
    class Animal {
        +String name
        +makeSound()
    }
    class Dog {
        +bark()
    }
    Animal <|-- Dog"""
    is_valid, error = validate_mermaid_code(code, 'class')
    assert is_valid is True, f"Valid class diagram should pass: {error}"
    print("✓ Valid class diagram passes")
    
    # Test valid state diagram
    code = """stateDiagram-v2
    [*] --> Idle
    Idle --> Processing
    Processing --> [*]"""
    is_valid, error = validate_mermaid_code(code, 'state')
    assert is_valid is True, f"Valid state diagram should pass: {error}"
    print("✓ Valid state diagram passes")
    
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
    
    # Test no diagram declaration
    code = "A --> B\nB --> C"
    is_valid, error = validate_mermaid_code(code, 'flowchart')
    assert is_valid is False, "Code without declaration should fail"
    print("✓ Code without declaration fails correctly")
    
    # Test unbalanced brackets
    code = """graph TD
    A[Start --> B[End"""
    is_valid, error = validate_mermaid_code(code, 'flowchart')
    assert is_valid is False, "Unbalanced brackets should fail"
    print("✓ Unbalanced brackets fail correctly")


def test_mermaid_extractor():
    """Test Mermaid extraction."""
    print("\n=== Testing Mermaid Extractor ===")
    
    # Test extraction with mermaid tag
    response = """Here's your diagram:

```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```

Hope this helps!"""
    code = extract_mermaid_code(response)
    assert code is not None, "Should extract code"
    assert 'graph TD' in code
    assert '```' not in code
    assert 'A[Start]' in code
    print("✓ Extraction with mermaid tag works")
    
    # Test extraction with multiple blocks
    response = """```mermaid
graph TD
    A --> B
```

And another:

```mermaid
graph LR
    C --> D
```"""
    code = extract_mermaid_code(response)
    assert code is not None
    assert 'graph TD' in code  # Should get first block
    print("✓ Multiple blocks returns first block")
    
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
    
    # Test cleaning already clean code
    code = """graph TD
    A --> B"""
    cleaned = clean_mermaid_code(code)
    assert cleaned == code.strip()
    print("✓ Cleaning already clean code works")


def test_prompt_builder():
    """Test prompt building."""
    print("\n=== Testing Prompt Builder ===")
    
    # Test building complete prompt for flowchart
    prompts = build_complete_prompt('Create a login flow', 'flowchart')
    assert 'system' in prompts
    assert 'user' in prompts
    assert 'graph' in prompts['system']
    assert 'login flow' in prompts['user']
    assert 'flowchart' in prompts['user']
    print("✓ Flowchart prompt building works")
    
    # Test building prompt for ER diagram
    prompts = build_complete_prompt('Create a database schema', 'erdiagram')
    assert 'erDiagram' in prompts['system']
    assert 'database schema' in prompts['user']
    print("✓ ER diagram prompt building works")
    
    # Test building prompt for sequence diagram
    prompts = build_complete_prompt('Show API flow', 'sequence')
    assert 'sequenceDiagram' in prompts['system']
    assert 'participant' in prompts['system']
    print("✓ Sequence diagram prompt building works")
    
    # Test supported types
    types = get_supported_diagram_types()
    assert 'flowchart' in types
    assert 'erdiagram' in types
    assert 'sequence' in types
    assert 'class' in types
    assert 'state' in types
    assert 'architecture' in types
    assert 'dfd' in types
    assert len(types) == 7
    print(f"✓ Supported types ({len(types)}): {', '.join(types)}")
    
    # Test that each type has instructions
    for dtype in types:
        prompts = build_complete_prompt('Test', dtype)
        assert len(prompts['system']) > 100, f"System prompt for {dtype} should be substantial"
    print("✓ All diagram types have substantial instructions")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Test Suite for Mermaid Components")
    print("=" * 60)
    
    try:
        test_mermaid_validator()
        test_mermaid_extractor()
        test_prompt_builder()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
