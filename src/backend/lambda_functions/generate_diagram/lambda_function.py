"""
Lambda function for generating architecture diagrams using LLM.
Handles diagram generation requests, validates input, calls LLM API,
extracts Mermaid code, and stores results in S3 and DynamoDB.

Requirements: 2.1, 5.1, 5.2, 5.3, 7.1
"""

import json
import os
import sys
import traceback
from typing import Dict, Any, Optional

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from utils import generate_chat_id, get_current_timestamp, validate_diagram_type
from aws_helpers import DynamoDBHelper, S3Helper
from prompt_builder import build_complete_prompt, get_supported_diagram_types
from mermaid_extractor import extract_mermaid_code, validate_mermaid_structure, clean_mermaid_code
from mermaid_validator import validate_mermaid_code
from diagram_renderer import save_diagram_to_s3


def validate_request(event: Dict[str, Any]) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate the incoming request.
    
    Args:
        event: Lambda event object
        
    Returns:
        Tuple of (is_valid, error_message, parsed_body)
    """
    # Parse body
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
    except json.JSONDecodeError:
        return False, "Invalid JSON in request body", None
    
    # Validate required fields
    if 'userPrompt' not in body:
        return False, "Missing required field: userPrompt", None
    
    if 'diagramType' not in body:
        return False, "Missing required field: diagramType", None
    
    user_prompt = body['userPrompt']
    diagram_type = body['diagramType']
    
    # Validate userPrompt
    if not isinstance(user_prompt, str) or not user_prompt.strip():
        return False, "userPrompt must be a non-empty string", None
    
    # Validate diagramType
    if not isinstance(diagram_type, str):
        return False, "diagramType must be a string", None
    
    if not validate_diagram_type(diagram_type):
        supported = ', '.join(get_supported_diagram_types())
        return False, f"Invalid diagram type: {diagram_type}. Supported types: {supported}", None
    
    return True, None, body


def call_llm_api(system_prompt: str, user_prompt: str) -> str:
    """
    Call the LLM API to generate diagram code.
    
    Args:
        system_prompt: System instructions for the LLM
        user_prompt: User's diagram request
        
    Returns:
        str: LLM response text
        
    Raises:
        Exception: If LLM API call fails
    """
    import requests
    
    llm_endpoint = os.environ.get('LLM_API_ENDPOINT')
    llm_api_key = os.environ.get('LLM_API_KEY')
    
    if not llm_endpoint:
        raise Exception("LLM_API_ENDPOINT environment variable not set")
    
    if not llm_api_key:
        raise Exception("LLM_API_KEY environment variable not set")
    
    # Prepare request based on common LLM API formats
    # This is a generic implementation that works with OpenAI-compatible APIs
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {llm_api_key}'
    }
    
    payload = {
        'model': os.environ.get('LLM_MODEL', 'gpt-3.5-turbo'),
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    try:
        response = requests.post(
            llm_endpoint,
            headers=headers,
            json=payload,
            timeout=50  # 50 second timeout (Lambda has 60s total)
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Extract content from response (OpenAI format)
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        elif 'content' in result:
            return result['content']
        else:
            raise Exception(f"Unexpected LLM API response format: {result}")
            
    except requests.exceptions.Timeout:
        raise Exception("LLM API request timed out")
    except requests.exceptions.RequestException as e:
        raise Exception(f"LLM API request failed: {str(e)}")


def create_cors_headers() -> Dict[str, str]:
    """Create CORS headers for API Gateway response."""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    }


def create_error_response(status_code: int, error_message: str) -> Dict[str, Any]:
    """
    Create an error response.
    
    Args:
        status_code: HTTP status code
        error_message: Error message
        
    Returns:
        Dict: Lambda response object
    """
    return {
        'statusCode': status_code,
        'headers': create_cors_headers(),
        'body': json.dumps({
            'error': error_message
        })
    }


def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a success response.
    
    Args:
        data: Response data
        
    Returns:
        Dict: Lambda response object
    """
    return {
        'statusCode': 200,
        'headers': create_cors_headers(),
        'body': json.dumps(data)
    }


def handler(event, context):
    """
    Main Lambda handler for diagram generation.
    
    Args:
        event: Lambda event object from API Gateway
        context: Lambda context object
        
    Returns:
        Dict: API Gateway response object
    """
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Validate request
        is_valid, error_msg, body = validate_request(event)
        if not is_valid:
            return create_error_response(400, error_msg)
        
        user_prompt = body['userPrompt']
        diagram_type = body['diagramType']
        
        print(f"Processing request - Type: {diagram_type}, Prompt: {user_prompt[:100]}...")
        
        # Generate unique chat ID and timestamp
        chat_id = generate_chat_id()
        timestamp = get_current_timestamp()
        
        # Build prompts for LLM
        prompts = build_complete_prompt(user_prompt, diagram_type)
        system_prompt = prompts['system']
        llm_user_prompt = prompts['user']
        
        print(f"Calling LLM API...")
        
        # Call LLM API
        try:
            llm_response = call_llm_api(system_prompt, llm_user_prompt)
            print(f"LLM response received: {len(llm_response)} characters")
        except Exception as e:
            print(f"LLM API error: {str(e)}")
            return create_error_response(502, f"LLM service error: {str(e)}")
        
        # Extract Mermaid code from response
        mermaid_code = extract_mermaid_code(llm_response)
        
        if not mermaid_code:
            print("Failed to extract Mermaid code from LLM response")
            return create_error_response(500, "Failed to extract valid Mermaid code from LLM response")
        
        # Clean the Mermaid code
        mermaid_code = clean_mermaid_code(mermaid_code)
        
        print(f"Extracted Mermaid code: {len(mermaid_code)} characters")
        
        # Validate Mermaid syntax
        is_valid, validation_error = validate_mermaid_code(mermaid_code, diagram_type)
        if not is_valid:
            print(f"Mermaid code validation failed: {validation_error}")
            return create_error_response(400, f"Invalid Mermaid code: {validation_error}")
        
        # Initialize AWS helpers
        s3_helper = S3Helper()
        dynamodb_helper = DynamoDBHelper()
        
        # Save diagram to S3 (both markdown and PNG)
        print(f"Saving diagram to S3...")
        try:
            markdown_url, image_url = save_diagram_to_s3(s3_helper, chat_id, mermaid_code)
            print(f"Markdown saved: {markdown_url}")
            print(f"Image saved: {image_url}")
        except Exception as e:
            print(f"Failed to save diagram to S3: {str(e)}")
            return create_error_response(500, f"Failed to save diagram: {str(e)}")
        
        # Save to DynamoDB
        print(f"Saving to DynamoDB...")
        try:
            # Check if sessionId is provided - if so, save with session-based PK/SK pattern
            session_id = body.get('sessionId')
            
            if session_id:
                # Save with session-based pattern for session messages
                dynamodb_item = {
                    'PK': f'SESSION#{session_id}',
                    'SK': f'MSG#{timestamp}',
                    'chatId': chat_id,
                    'messageId': chat_id,
                    'sessionId': session_id,
                    'timestamp': timestamp,
                    'userMessage': user_prompt,
                    'diagramType': diagram_type,
                    'aiResponse': llm_response,
                    'mermaidCode': mermaid_code,
                    'diagramImageS3Key': f"diagrams/{chat_id}.png",
                    'diagramMarkdownS3Key': f"diagrams/{chat_id}.md",
                    'imageUrl': image_url,
                    'markdownUrl': markdown_url,
                    'status': 'completed'
                }
            else:
                # Legacy pattern without session
                dynamodb_item = {
                    'chatId': chat_id,
                    'timestamp': timestamp,
                    'userMessage': user_prompt,
                    'diagramType': diagram_type,
                    'aiResponse': llm_response,
                    'mermaidCode': mermaid_code,
                    'diagramImageS3Key': f"diagrams/{chat_id}.png",
                    'diagramMarkdownS3Key': f"diagrams/{chat_id}.md",
                    'imageUrl': image_url,
                    'markdownUrl': markdown_url,
                    'status': 'completed'
                }
            
            dynamodb_helper.put_item(dynamodb_item)
            print(f"Saved to DynamoDB: {chat_id} (session: {session_id})")
        except Exception as e:
            print(f"Failed to save to DynamoDB: {str(e)}")
            # Continue even if DynamoDB save fails - we have the diagram in S3
            print("Warning: DynamoDB save failed, but diagram is in S3")
        
        # Prepare response
        response_data = {
            'chatId': chat_id,
            'timestamp': timestamp,
            'mermaidCode': mermaid_code,
            'imageUrl': image_url,
            'markdownUrl': markdown_url,
            'status': 'completed'
        }
        
        print(f"Request completed successfully: {chat_id}")
        return create_success_response(response_data)
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return create_error_response(500, f"Internal server error: {str(e)}")
