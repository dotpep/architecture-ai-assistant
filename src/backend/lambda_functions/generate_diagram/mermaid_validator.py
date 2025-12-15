"""
Mermaid diagram syntax validator.
Validates Mermaid code syntax for different diagram types.

Requirements: 2.5, 5.4
"""

import re
from typing import Dict, List, Optional, Tuple


class MermaidValidator:
    """Validator for Mermaid diagram syntax."""
    
    # Diagram type patterns - each diagram must start with one of these
    DIAGRAM_TYPE_PATTERNS = {
        'flowchart': [
            r'^\s*graph\s+(TD|LR|TB|RL|BT)',
            r'^\s*flowchart\s+(TD|LR|TB|RL|BT)'
        ],
        'erdiagram': [
            r'^\s*erDiagram'
        ],
        'sequence': [
            r'^\s*sequenceDiagram'
        ],
        'class': [
            r'^\s*classDiagram'
        ],
        'state': [
            r'^\s*stateDiagram',
            r'^\s*stateDiagram-v2'
        ],
        'architecture': [
            r'^\s*graph\s+(TD|LR|TB|RL|BT)',
            r'^\s*flowchart\s+(TD|LR|TB|RL|BT)'
        ],
        'dfd': [
            r'^\s*graph\s+(TD|LR|TB|RL|BT)',
            r'^\s*flowchart\s+(TD|LR|TB|RL|BT)'
        ]
    }
    
    @staticmethod
    def validate(mermaid_code: str, diagram_type: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate Mermaid code syntax.
        
        Args:
            mermaid_code: The Mermaid code to validate
            diagram_type: Expected diagram type (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not mermaid_code or not isinstance(mermaid_code, str):
            return False, "Mermaid code is empty or not a string"
        
        code = mermaid_code.strip()
        
        # Check minimum length
        if len(code) < 5:
            return False, "Mermaid code is too short to be valid"
        
        # Check for code fence markers (should be cleaned)
        if '```' in code:
            return False, "Mermaid code contains code fence markers (```)"
        
        # Validate diagram type declaration
        has_valid_declaration = False
        detected_type = None
        
        for dtype, patterns in MermaidValidator.DIAGRAM_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, code, re.MULTILINE | re.IGNORECASE):
                    has_valid_declaration = True
                    detected_type = dtype
                    break
            if has_valid_declaration:
                break
        
        if not has_valid_declaration:
            return False, "Mermaid code does not start with a valid diagram type declaration"
        
        # If diagram type is specified, verify it matches
        if diagram_type:
            diagram_type_lower = diagram_type.lower()
            if detected_type != diagram_type_lower:
                return False, f"Diagram type mismatch: expected {diagram_type}, detected {detected_type}"
        
        # Check for multi-line content (diagrams should have multiple lines)
        if '\n' not in code:
            return False, "Mermaid code should contain multiple lines"
        
        # Perform type-specific validation
        if detected_type:
            is_valid, error = MermaidValidator._validate_type_specific(code, detected_type)
            if not is_valid:
                return False, error
        
        return True, None
    
    @staticmethod
    def _validate_type_specific(code: str, diagram_type: str) -> Tuple[bool, Optional[str]]:
        """
        Perform diagram-type-specific validation.
        
        Args:
            code: Mermaid code
            diagram_type: Type of diagram
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if diagram_type in ['flowchart', 'architecture', 'dfd']:
            return MermaidValidator._validate_flowchart(code)
        elif diagram_type == 'erdiagram':
            return MermaidValidator._validate_erdiagram(code)
        elif diagram_type == 'sequence':
            return MermaidValidator._validate_sequence(code)
        elif diagram_type == 'class':
            return MermaidValidator._validate_class(code)
        elif diagram_type == 'state':
            return MermaidValidator._validate_state(code)
        
        return True, None
    
    @staticmethod
    def _validate_flowchart(code: str) -> Tuple[bool, Optional[str]]:
        """Validate flowchart/graph syntax."""
        # Check for at least one node definition or connection
        has_nodes = bool(re.search(r'[A-Za-z0-9_]+\[.+?\]', code))
        has_connections = bool(re.search(r'--+>|---+|\.\.+>', code))
        
        if not (has_nodes or has_connections):
            return False, "Flowchart must contain at least one node or connection"
        
        # Check for balanced brackets
        if code.count('[') != code.count(']'):
            return False, "Unbalanced square brackets in flowchart"
        
        if code.count('(') != code.count(')'):
            return False, "Unbalanced parentheses in flowchart"
        
        if code.count('{') != code.count('}'):
            return False, "Unbalanced curly braces in flowchart"
        
        return True, None
    
    @staticmethod
    def _validate_erdiagram(code: str) -> Tuple[bool, Optional[str]]:
        """Validate ER diagram syntax."""
        # Check for at least one relationship
        has_relationship = bool(re.search(r'\|\|--|\}o--|\|o--|\}\|--', code))
        
        if not has_relationship:
            return False, "ER diagram must contain at least one relationship"
        
        # Check for balanced braces (for entity attributes)
        # Remove relationship syntax that contains braces before counting
        code_without_relationships = re.sub(r'\|\|--[o\|]?\{|\}[o\|]?--', '', code)
        if code_without_relationships.count('{') != code_without_relationships.count('}'):
            return False, "Unbalanced curly braces in ER diagram"
        
        return True, None
    
    @staticmethod
    def _validate_sequence(code: str) -> Tuple[bool, Optional[str]]:
        """Validate sequence diagram syntax."""
        # Check for at least one message
        has_message = bool(re.search(r'->>|-->>|->>?[+\-]?|-->>?[+\-]?', code))
        
        if not has_message:
            return False, "Sequence diagram must contain at least one message"
        
        return True, None
    
    @staticmethod
    def _validate_class(code: str) -> Tuple[bool, Optional[str]]:
        """Validate class diagram syntax."""
        # Check for at least one class definition or relationship
        has_class = bool(re.search(r'class\s+\w+', code))
        has_relationship = bool(re.search(r'<\|--|--\*|--o|-->|\.\.>', code))
        
        if not (has_class or has_relationship):
            return False, "Class diagram must contain at least one class or relationship"
        
        # Check for balanced braces
        if code.count('{') != code.count('}'):
            return False, "Unbalanced curly braces in class diagram"
        
        return True, None
    
    @staticmethod
    def _validate_state(code: str) -> Tuple[bool, Optional[str]]:
        """Validate state diagram syntax."""
        # Check for at least one state or transition
        has_state = bool(re.search(r'state\s+', code))
        has_transition = bool(re.search(r'-->', code))
        has_start_end = bool(re.search(r'\[\*\]', code))
        
        if not (has_state or has_transition or has_start_end):
            return False, "State diagram must contain at least one state or transition"
        
        return True, None


def validate_mermaid_code(mermaid_code: str, diagram_type: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Convenience function to validate Mermaid code.
    
    Args:
        mermaid_code: The Mermaid code to validate
        diagram_type: Expected diagram type (optional)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    return MermaidValidator.validate(mermaid_code, diagram_type)
