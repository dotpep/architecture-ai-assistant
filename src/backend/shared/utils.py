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
