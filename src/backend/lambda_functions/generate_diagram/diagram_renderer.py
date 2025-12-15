"""
Diagram renderer for converting Mermaid code to PNG images.
This module provides functionality to render Mermaid diagrams as PNG images.

Requirements: 3.1, 3.2
"""

import base64
import io
from typing import Optional


def generate_placeholder_png(mermaid_code: str, width: int = 800, height: int = 600) -> bytes:
    """
    Generate a placeholder PNG image for a Mermaid diagram.
    
    This is a simple implementation that creates a placeholder image.
    In production, this would use a proper Mermaid rendering service or library.
    
    Args:
        mermaid_code: The Mermaid diagram code
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        bytes: PNG image data
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a white background image
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw a border
        draw.rectangle([(10, 10), (width-10, height-10)], outline='black', width=2)
        
        # Add text indicating this is a placeholder
        try:
            # Try to use a default font
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Add title
        title = "Mermaid Diagram"
        draw.text((width//2 - 80, 30), title, fill='black', font=font)
        
        # Add diagram type info
        first_line = mermaid_code.split('\n')[0] if mermaid_code else ""
        draw.text((30, 80), f"Type: {first_line[:50]}", fill='gray', font=font)
        
        # Add note about rendering
        note = "Note: This is a placeholder image."
        draw.text((30, height - 60), note, fill='gray', font=font)
        note2 = "Full rendering requires mermaid-cli or rendering service."
        draw.text((30, height - 35), note2, fill='gray', font=font)
        
        # Convert to PNG bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr.read()
        
    except ImportError:
        # If PIL is not available, return a minimal PNG
        return generate_minimal_png()


def generate_minimal_png() -> bytes:
    """
    Generate a minimal valid PNG image (1x1 pixel).
    This is used as a fallback when PIL is not available.
    
    Returns:
        bytes: Minimal PNG image data
    """
    # This is a base64-encoded 1x1 white PNG
    minimal_png_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    )
    return base64.b64decode(minimal_png_base64)


def render_mermaid_to_png(mermaid_code: str) -> bytes:
    """
    Render Mermaid code to PNG image.
    
    This function attempts to render the Mermaid diagram to a PNG image.
    Currently uses a placeholder implementation. In production, this would:
    1. Use mermaid-cli (mmdc) if available in Lambda layer
    2. Call an external rendering service
    3. Use puppeteer/playwright to render in headless browser
    
    Args:
        mermaid_code: The Mermaid diagram code
        
    Returns:
        bytes: PNG image data
    """
    # For now, generate a placeholder
    # TODO: Implement actual Mermaid rendering using:
    # - mermaid-cli in Lambda layer
    # - External rendering service API
    # - Headless browser rendering
    
    return generate_placeholder_png(mermaid_code)


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
    
    # Generate and save PNG
    png_data = render_mermaid_to_png(mermaid_code)
    image_url = s3_helper.put_diagram_image(chat_id, png_data)
    
    return markdown_url, image_url
