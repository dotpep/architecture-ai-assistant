"""
Diagram renderer for converting Mermaid code to PNG images.
This module provides functionality to render Mermaid diagrams as PNG images.

Requirements: 3.1, 3.2
"""

import base64
import io
import json
import os
import requests
from typing import Optional

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def render_mermaid_to_png(mermaid_code: str) -> bytes:
    """
    Render Mermaid code to PNG image using Kroki rendering service.
    
    Kroki is a free, open-source rendering service that supports Mermaid diagrams.
    It's reliable and doesn't require any local dependencies.
    
    Args:
        mermaid_code: The Mermaid diagram code
        
    Returns:
        bytes: PNG image data
        
    Raises:
        Exception: If rendering fails
    """
    try:
        # Use Kroki rendering service with base64 encoding (simpler, more reliable)
        # Encode the diagram source in base64
        encoded = base64.b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        kroki_url = f"https://kroki.io/mermaid/png/{encoded}"
        
        print(f"Calling Kroki API: {kroki_url[:100]}...")
        
        # Call Kroki API with GET request
        response = requests.get(
            kroki_url,
            timeout=30,
            headers={'User-Agent': 'Architecture-AI-Assistant/1.0'}
        )
        
        print(f"Kroki response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Successfully rendered diagram, size: {len(response.content)} bytes")
            return response.content
        else:
            error_msg = response.text[:500] if response.text else "No error details"
            raise Exception(f"Kroki rendering failed with status {response.status_code}: {error_msg}")
            
    except requests.exceptions.Timeout:
        raise Exception("Mermaid rendering service timed out (30s)")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Failed to connect to rendering service: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to render diagram: {str(e)}")


def render_mermaid_to_png_fallback(mermaid_code: str) -> bytes:
    """
    Fallback rendering using POST request to Kroki.
    
    Args:
        mermaid_code: The Mermaid diagram code
        
    Returns:
        bytes: PNG image data
    """
    try:
        print("Trying fallback rendering with POST request...")
        
        kroki_url = "https://kroki.io/mermaid/png"
        
        # Use form data instead of JSON
        data = {
            'diagram_source': mermaid_code
        }
        
        response = requests.post(
            kroki_url,
            data=data,
            timeout=30,
            headers={'User-Agent': 'Architecture-AI-Assistant/1.0'}
        )
        
        print(f"Fallback Kroki response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Fallback rendering succeeded, size: {len(response.content)} bytes")
            return response.content
        else:
            raise Exception(f"Fallback Kroki rendering failed with status {response.status_code}")
            
    except Exception as e:
        raise Exception(f"Fallback rendering also failed: {str(e)}")


def generate_placeholder_png_with_code(mermaid_code: str) -> bytes:
    """
    Generate a placeholder PNG with the diagram code displayed.
    This is used as a last resort when rendering services are unavailable.
    
    Args:
        mermaid_code: The Mermaid diagram code
        
    Returns:
        bytes: PNG image data
    """
    if not PIL_AVAILABLE:
        # Return a minimal valid PNG if PIL is not available
        return base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        )
    
    try:
        # Create image with diagram code
        width, height = 1000, 600
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([(10, 10), (width-10, height-10)], outline='#cccccc', width=2)
        
        # Try to use a readable font
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            font_code = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 10)
        except:
            font_title = ImageFont.load_default()
            font_code = ImageFont.load_default()
        
        # Add title
        draw.text((20, 20), "Mermaid Diagram Code", fill='#333333', font=font_title)
        
        # Add code lines
        lines = mermaid_code.split('\n')[:20]  # Show first 20 lines
        y_pos = 60
        for line in lines:
            if y_pos > height - 40:
                draw.text((20, y_pos), "...", fill='#666666', font=font_code)
                break
            draw.text((20, y_pos), line[:100], fill='#333333', font=font_code)
            y_pos += 20
        
        # Add note
        draw.text((20, height - 30), "Note: Diagram rendering service unavailable. Showing code preview.", 
                 fill='#999999', font=font_code)
        
        # Convert to PNG
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes.read()
        
    except Exception as e:
        print(f"Failed to generate placeholder PNG: {str(e)}")
        # Return minimal PNG as last resort
        return base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        )


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
    
    # Generate and save PNG with multiple fallbacks
    png_data = None
    
    # Try primary rendering
    try:
        print("Attempting primary Kroki rendering...")
        png_data = render_mermaid_to_png(mermaid_code)
        print("Primary rendering succeeded")
    except Exception as e:
        print(f"Primary rendering failed: {str(e)}")
        
        # Try fallback rendering
        try:
            print("Attempting fallback Kroki rendering...")
            png_data = render_mermaid_to_png_fallback(mermaid_code)
            print("Fallback rendering succeeded")
        except Exception as fallback_error:
            print(f"Fallback rendering also failed: {str(fallback_error)}")
            
            # Use placeholder as last resort
            print("Using placeholder PNG with code preview")
            png_data = generate_placeholder_png_with_code(mermaid_code)
    
    # Save PNG to S3
    image_url = s3_helper.put_diagram_image(chat_id, png_data)
    
    return markdown_url, image_url
