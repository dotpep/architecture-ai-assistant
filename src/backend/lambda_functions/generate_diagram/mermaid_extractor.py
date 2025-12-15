"""
Mermaid code extractor for parsing LLM responses.
Extracts Mermaid diagram code from various response formats.
"""

import re
from typing import Optional, List


def extract_mermaid_code(llm_response: str) -> Optional[str]:
    """
    Extract Mermaid code from LLM response.
    Handles multiple code blocks and returns the first valid one.
    
    Args:
        llm_response: The complete response text from the LLM
        
    Returns:
        str: Extracted Mermaid code without delimiters, or None if not found
    """
    if not llm_response or not isinstance(llm_response, str):
        return None
    
    # Pattern 1: ```mermaid ... ``` (most common)
    mermaid_blocks = re.findall(
        r'```mermaid\s*\n(.*?)```',
        llm_response,
        re.DOTALL | re.IGNORECASE
    )
    
    if mermaid_blocks:
        # Return the first non-empty block
        for block in mermaid_blocks:
            cleaned = block.strip()
            if cleaned:
                return cleaned
    
    # Pattern 2: ``` ... ``` without explicit mermaid tag (fallback)
    # Only use if it looks like Mermaid syntax
    generic_blocks = re.findall(
        r'```\s*\n(.*?)```',
        llm_response,
        re.DOTALL
    )
    
    if generic_blocks:
        for block in generic_blocks:
            cleaned = block.strip()
            # Check if it looks like Mermaid code
            if cleaned and is_likely_mermaid(cleaned):
                return cleaned
    
    # Pattern 3: No code blocks, but contains Mermaid keywords (last resort)
    # Look for lines that start with common Mermaid diagram types
    if is_likely_mermaid(llm_response):
        return llm_response.strip()
    
    return None


def is_likely_mermaid(text: str) -> bool:
    """
    Check if text is likely to be Mermaid code based on keywords.
    
    Args:
        text: Text to check
        
    Returns:
        bool: True if text appears to be Mermaid code
    """
    if not text:
        return False
    
    # Common Mermaid diagram type declarations
    mermaid_keywords = [
        r'^\s*graph\s+(TD|LR|TB|RL|BT)',
        r'^\s*flowchart\s+(TD|LR|TB|RL|BT)',
        r'^\s*sequenceDiagram',
        r'^\s*classDiagram',
        r'^\s*stateDiagram',
        r'^\s*stateDiagram-v2',
        r'^\s*erDiagram',
        r'^\s*C4Context',
        r'^\s*C4Container',
        r'^\s*C4Component',
        r'^\s*C4Deployment',
        r'^\s*journey',
        r'^\s*gantt',
        r'^\s*pie',
        r'^\s*gitGraph'
    ]
    
    text_lower = text.lower()
    
    for pattern in mermaid_keywords:
        if re.search(pattern, text_lower, re.MULTILINE | re.IGNORECASE):
            return True
    
    return False


def extract_all_mermaid_blocks(llm_response: str) -> List[str]:
    """
    Extract all Mermaid code blocks from LLM response.
    
    Args:
        llm_response: The complete response text from the LLM
        
    Returns:
        List[str]: List of all extracted Mermaid code blocks
    """
    if not llm_response or not isinstance(llm_response, str):
        return []
    
    blocks = []
    
    # Extract all ```mermaid ... ``` blocks
    mermaid_blocks = re.findall(
        r'```mermaid\s*\n(.*?)```',
        llm_response,
        re.DOTALL | re.IGNORECASE
    )
    
    for block in mermaid_blocks:
        cleaned = block.strip()
        if cleaned:
            blocks.append(cleaned)
    
    return blocks


def validate_mermaid_structure(mermaid_code: str) -> bool:
    """
    Perform basic validation on Mermaid code structure.
    
    Args:
        mermaid_code: The Mermaid code to validate
        
    Returns:
        bool: True if code has valid basic structure
    """
    if not mermaid_code or not isinstance(mermaid_code, str):
        return False
    
    # Must have some content
    if len(mermaid_code.strip()) < 5:
        return False
    
    # Must start with a valid Mermaid diagram type
    if not is_likely_mermaid(mermaid_code):
        return False
    
    # Should have at least one line break (multi-line diagram)
    if '\n' not in mermaid_code:
        # Single line might be valid for very simple diagrams, but unlikely
        return False
    
    return True


def clean_mermaid_code(mermaid_code: str) -> str:
    """
    Clean and normalize Mermaid code.
    
    Args:
        mermaid_code: Raw Mermaid code
        
    Returns:
        str: Cleaned Mermaid code
    """
    if not mermaid_code:
        return ""
    
    # Remove leading/trailing whitespace
    cleaned = mermaid_code.strip()
    
    # Remove any remaining code fence markers that might have been missed
    cleaned = re.sub(r'^```mermaid\s*\n?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\n?```\s*$', '', cleaned)
    
    # Normalize line endings
    cleaned = cleaned.replace('\r\n', '\n')
    
    return cleaned
