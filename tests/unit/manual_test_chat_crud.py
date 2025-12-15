"""
Manual test for chat_crud Lambda function logic.
Tests the core logic without AWS dependencies.
"""

import json
import sys
import os

# Add backend modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/backend/lambda_functions/chat_crud'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/backend/shared'))


def test_validate_request():
    """Test request validation logic."""
    from lambda_function import validate_request
    
    print("Testing validate_request...")
    
    # Test valid request
    body = {
        'userMessage': 'Create a flowchart',
        'diagramType': 'flowchart'
    }
    is_valid, error = validate_request(body)
    assert is_valid is True, f"Expected valid, got error: {error}"
    print("✓ Valid request passes")
    
    # Test missing userMessage
    body = {'diagramType': 'flowchart'}
    is_valid, error = validate_request(body)
    assert is_valid is False, "Expected invalid for missing userMessage"
    assert 'userMessage' in error, f"Expected userMessage in error, got: {error}"
    print("✓ Missing userMessage detected")
    
    # Test missing diagramType
    body = {'userMessage': 'Create a diagram'}
    is_valid, error = validate_request(body)
    assert is_valid is False, "Expected invalid for missing diagramType"
    assert 'diagramType' in error, f"Expected diagramType in error, got: {error}"
    print("✓ Missing diagramType detected")
    
    # Test invalid diagram type
    body = {
        'userMessage': 'Create a diagram',
        'diagramType': 'invalid_type'
    }
    is_valid, error = validate_request(body)
    assert is_valid is False, "Expected invalid for invalid diagram type"
    assert 'Invalid diagram type' in error, f"Expected invalid type error, got: {error}"
    print("✓ Invalid diagram type detected")
    
    # Test all valid diagram types
    valid_types = ['flowchart', 'erdiagram', 'sequence', 'class', 'state', 'architecture', 'dfd']
    for diagram_type in valid_types:
        body = {
            'userMessage': f'Create a {diagram_type}',
            'diagramType': diagram_type
        }
        is_valid, error = validate_request(body)
        assert is_valid is True, f"Expected {diagram_type} to be valid, got error: {error}"
    print(f"✓ All {len(valid_types)} diagram types validated")
    
    print("\n✅ All validate_request tests passed!\n")


def test_create_response():
    """Test response creation logic."""
    from lambda_function import create_response
    
    print("Testing create_response...")
    
    # Test success response
    response = create_response(200, {'success': True, 'chatId': 'test-123'})
    assert response['statusCode'] == 200
    assert 'Access-Control-Allow-Origin' in response['headers']
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['chatId'] == 'test-123'
    print("✓ Success response formatted correctly")
    
    # Test error response
    response = create_response(400, {'error': 'Bad request'})
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error'] == 'Bad request'
    print("✓ Error response formatted correctly")
    
    print("\n✅ All create_response tests passed!\n")


def test_integration_with_utils():
    """Test integration with shared utilities."""
    from utils import generate_chat_id, get_current_timestamp, validate_diagram_type
    
    print("Testing integration with shared utilities...")
    
    # Test generate_chat_id
    chat_id = generate_chat_id()
    assert isinstance(chat_id, str), "chat_id should be a string"
    assert len(chat_id) > 0, "chat_id should not be empty"
    print(f"✓ Generated chat_id: {chat_id}")
    
    # Test get_current_timestamp
    timestamp = get_current_timestamp()
    assert isinstance(timestamp, int), "timestamp should be an integer"
    assert timestamp > 0, "timestamp should be positive"
    print(f"✓ Generated timestamp: {timestamp}")
    
    # Test validate_diagram_type
    assert validate_diagram_type('flowchart') is True
    assert validate_diagram_type('invalid') is False
    print("✓ Diagram type validation works")
    
    print("\n✅ All utility integration tests passed!\n")


def main():
    """Run all manual tests."""
    print("=" * 60)
    print("MANUAL TEST: chat_crud Lambda Function")
    print("=" * 60)
    print()
    
    try:
        test_validate_request()
        test_create_response()
        test_integration_with_utils()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
