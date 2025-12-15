"""
Diagram renderer for converting Mermaid code to PNG images.
This module provides functionality to render Mermaid diagrams as PNG images.

Requirements: 3.1, 3.2
"""

import json
import os
import requests
from typing import Optional


def render_mermaid_to_png(mermaid_code: str) -> bytes:
    """
    Render Mermaid code to PNG image using Kroki rendering service.
    
    Workflow:
    1. POST mermaid code to /mermaid/png endpoint
    2. Kroki returns PNG data
    3. Return PNG data
    
    Args:
        mermaid_code: The Mermaid diagram code
        
    Returns:
        bytes: PNG image data
        
    Raises:
        Exception: If rendering fails
    """
    try:
        print("Posting mermaid code to Kroki /mermaid/png...")
        
        response = requests.post(
            "https://kroki.io/mermaid/png",
            data=mermaid_code.encode('utf-8'),
            headers={
                'Content-Type': 'text/plain',
                'User-Agent': 'Architecture-AI-Assistant/1.0'
            },
            timeout=30
        )
        
        if response.status_code != 200:
            error_msg = response.text[:500] if response.text else "No error details"
            raise Exception(f"Kroki rendering failed with status {response.status_code}: {error_msg}")
        
        png_data = response.content
        print(f"PNG rendered successfully, size: {len(png_data)} bytes")
        return png_data
            
    except requests.exceptions.Timeout:
        raise Exception("Mermaid rendering service timed out (30s)")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Failed to connect to rendering service: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to render diagram: {str(e)}")


def render_mermaid_to_png_fallback(mermaid_code: str) -> bytes:
    """
    Fallback rendering - retry PNG rendering if primary fails.
    
    Args:
        mermaid_code: The Mermaid diagram code
        
    Returns:
        bytes: PNG image data
    """
    try:
        print("Attempting fallback PNG rendering...")
        
        response = requests.post(
            "https://kroki.io/mermaid/png",
            data=mermaid_code.encode('utf-8'),
            timeout=30,
            headers={
                'Content-Type': 'text/plain',
                'User-Agent': 'Architecture-AI-Assistant/1.0'
            }
        )
        
        print(f"Fallback response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Fallback rendering succeeded, size: {len(response.content)} bytes")
            return response.content
        else:
            raise Exception(f"Fallback failed with status {response.status_code}")
            
    except Exception as e:
        raise Exception(f"Fallback rendering failed: {str(e)}")


def generate_placeholder_png() -> bytes:
    """
    Return a minimal valid PNG as fallback when rendering fails.
    
    Returns:
        bytes: Minimal valid PNG image data (1x1 white pixel)
    """
    # Minimal 1x1 white PNG
    png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\r\xb5\x00\x00\x00\x00IEND\xaeB`\x82'
    return png


def save_diagram_to_s3(s3_helper, chat_id: str, mermaid_code: str) -> tuple[str, str]:
    """
    Save diagram to S3 as both markdown and PNG.
    
    Args:
        s3_helper: S3Helper instance
        chat_id: Unique identifier for the diagram
        mermaid_code: Mermaid diagram code
        
    Returns:
        Tuple of (markdown_url, image_url)
    """
    # Save markdown
    markdown_url = s3_helper.put_diagram_markdown(chat_id, mermaid_code)
    
    # Generate and save PNG with fallback
    png_data = None
    
    try:
        print("Rendering diagram to PNG...")
        png_data = render_mermaid_to_png(mermaid_code)
        print("PNG rendering succeeded")
    except Exception as e:
        print(f"PNG rendering failed: {str(e)}")
        
        # Try fallback rendering
        try:
            print("Attempting fallback rendering...")
            png_data = render_mermaid_to_png_fallback(mermaid_code)
            print("Fallback rendering succeeded")
        except Exception as fallback_error:
            print(f"Fallback rendering also failed: {str(fallback_error)}")
            
            # Use minimal placeholder as last resort
            print("Using minimal placeholder PNG")
            png_data = generate_placeholder_png()
    
    # Save PNG to S3
    image_url = s3_helper.put_diagram_image(chat_id, png_data)
    
    return markdown_url, image_url
