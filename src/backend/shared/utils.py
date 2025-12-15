"""
Shared utility functions for the Architecture AI Assistant backend.
"""

import uuid
import time
from datetime import datetime
from typing import Optional


def generate_chat_id() -> str:
    """
    Generate a unique chat ID using UUID4.
    
    Returns:
        str: A unique UUID string
    """
    return str(uuid.uuid4())


def get_current_timestamp() -> int:
    """
    Get the current Unix timestamp in seconds.
    
    Returns:
        int: Current Unix timestamp
    """
    return int(time.time())


def timestamp_to_iso(timestamp: int) -> str:
    """
    Convert Unix timestamp to ISO 8601 format string.
    
    Args:
        timestamp: Unix timestamp in seconds
        
    Returns:
        str: ISO 8601 formatted datetime string
    """
    return datetime.fromtimestamp(timestamp).isoformat()


def iso_to_timestamp(iso_string: str) -> int:
    """
    Convert ISO 8601 format string to Unix timestamp.
    
    Args:
        iso_string: ISO 8601 formatted datetime string
        
    Returns:
        int: Unix timestamp in seconds
    """
    dt = datetime.fromisoformat(iso_string)
    return int(dt.timestamp())


def validate_diagram_type(diagram_type: str) -> bool:
    """
    Validate if the provided diagram type is supported.
    
    Args:
        diagram_type: The diagram type to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    valid_types = {
        'flowchart',
        'erdiagram',
        'sequence',
        'class',
        'state',
        'architecture',
        'dfd'
    }
    return diagram_type.lower() in valid_types


def sanitize_s3_key(key: str) -> str:
    """
    Sanitize a string to be used as an S3 key.
    
    Args:
        key: The string to sanitize
        
    Returns:
        str: Sanitized S3 key
    """
    # Remove or replace characters that might cause issues in S3 keys
    sanitized = key.replace(' ', '_').replace('/', '_')
    return sanitized


def generate_session_id() -> str:
    """
    Generate a unique session ID using UUID4.
    
    Returns:
        str: A unique UUID string for a session
    """
    return str(uuid.uuid4())


def extract_session_title(message: str, max_length: int = 50) -> str:
    """
    Extract a session title from the first user message.
    Truncates to max_length characters and appends ellipsis if needed.
    
    Args:
        message: The user message to extract title from
        max_length: Maximum length of the title (default: 50)
        
    Returns:
        str: Extracted and potentially truncated session title
    """
    if not message:
        return "New Chat"
    
    # Strip whitespace and get first max_length characters
    cleaned_message = message.strip()
    
    if len(cleaned_message) <= max_length:
        return cleaned_message
    
    # Truncate and add ellipsis
    return cleaned_message[:max_length] + "..."


def validate_session_id(session_id: str) -> bool:
    """
    Validate if the provided session ID is a valid UUID format.
    
    Args:
        session_id: The session ID to validate
        
    Returns:
        bool: True if valid UUID format, False otherwise
    """
    try:
        uuid.UUID(session_id)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def generate_message_id() -> str:
    """
    Generate a unique message ID using UUID4.
    
    Returns:
        str: A unique UUID string for a message
    """
    return str(uuid.uuid4())
