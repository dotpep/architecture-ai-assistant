"""
Unit tests for diagram_renderer module.
Tests PNG rendering functionality using Kroki service.
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Mock boto3 before importing modules that use it
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()
sys.modules['botocore.exceptions'] = MagicMock()

# Add backend paths to sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend')
generate_diagram_path = os.path.join(backend_path, 'lambda_functions', 'generate_diagram')

# Insert path
sys.path.insert(0, generate_diagram_path)

# Import after path setup
import importlib.util

spec = importlib.util.spec_from_file_location(
    "diagram_renderer",
    os.path.join(generate_diagram_path, "diagram_renderer.py")
)
diagram_renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagram_renderer)

render_mermaid_to_png = diagram_renderer.render_mermaid_to_png
render_mermaid_to_png_fallback = diagram_renderer.render_mermaid_to_png_fallback
generate_placeholder_png = diagram_renderer.generate_placeholder_png
save_diagram_to_s3 = diagram_renderer.save_diagram_to_s3


class TestRenderMermaidToPng:
    """Test primary PNG rendering function."""
    
    @patch('diagram_renderer.requests.post')
    def test_successful_rendering(self, mock_post):
        """Test successful PNG rendering from Kroki."""
        # Mock PNG response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'\x89PNG\r\n\x1a\n' + b'fake_png_data'
        mock_post.return_value = mock_response
        
        mermaid_code = "graph TD\nA[Start] --> B[End]"
        result = render_mermaid_to_png(mermaid_code)
        
        assert result == mock_response.content
        assert result.startswith(b'\x89PNG')
        mock_post.assert_called_once()
        
        # Verify correct endpoint and headers
        call_args = mock_post.call_args
        assert 'https://kroki.io/mermaid/png' in call_args[0]
        assert call_args[1]['headers']['Content-Type'] == 'text/plain'
        assert 'Architecture-AI-Assistant' in call_args[1]['headers']['User-Agent']
    
    @patch('diagram_renderer.requests.post')
    def test_rendering_with_complex_diagram(self, mock_post):
        """Test rendering with complex Mermaid code."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'\x89PNG\r\n\x1a\n' + b'complex_diagram'
        mock_post.return_value = mock_response
        
        mermaid_code = """graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[End]
    C --> E[Complete]"""
        
        result = render_mermaid_to_png(mermaid_code)
        
        assert result.startswith(b'\x89PNG')
        assert len(result) > 0
    
    @patch('diagram_renderer.requests.post')
    def test_rendering_timeout(self, mock_post):
        """Test handling of timeout exception."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        mermaid_code = "graph TD\nA --> B"
        
        with pytest.raises(Exception) as exc_info:
            render_mermaid_to_png(mermaid_code)
        
        assert 'timed out' in str(exc_info.value).lower()
    
    @patch('diagram_renderer.requests.post')
    def test_rendering_connection_error(self, mock_post):
        """Test handling of connection error."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        mermaid_code = "graph TD\nA --> B"
        
        with pytest.raises(Exception) as exc_info:
            render_mermaid_to_png(mermaid_code)
        
        assert 'Failed to connect' in str(exc_info.value)
    
    @patch('diagram_renderer.requests.post')
    def test_rendering_http_error(self, mock_post):
        """Test handling of HTTP error response."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Error 400: Invalid diagram"
        mock_post.return_value = mock_response
        
        mermaid_code = "invalid mermaid code"
        
        with pytest.raises(Exception) as exc_info:
            render_mermaid_to_png(mermaid_code)
        
        assert '400' in str(exc_info.value)
        assert 'Kroki rendering failed' in str(exc_info.value)
    
    @patch('diagram_renderer.requests.post')
    def test_rendering_server_error(self, mock_post):
        """Test handling of server error (500)."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        mermaid_code = "graph TD\nA --> B"
        
        with pytest.raises(Exception) as exc_info:
            render_mermaid_to_png(mermaid_code)
        
        assert '500' in str(exc_info.value)
    
    @patch('diagram_renderer.requests.post')
    def test_rendering_empty_response(self, mock_post):
        """Test handling of empty response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b''
        mock_post.return_value = mock_response
        
        mermaid_code = "graph TD\nA --> B"
        result = render_mermaid_to_png(mermaid_code)
        
        assert result == b''


class TestRenderMermaidToPngFallback:
    """Test fallback PNG rendering function."""
    
    @patch('diagram_renderer.requests.post')
    def test_fallback_successful(self, mock_post):
        """Test successful fallback rendering."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'\x89PNG\r\n\x1a\n' + b'fallback_png'
        mock_post.return_value = mock_response
        
        mermaid_code = "graph TD\nA --> B"
        result = render_mermaid_to_png_fallback(mermaid_code)
        
        assert result.startswith(b'\x89PNG')
        mock_post.assert_called_once()
    
    @patch('diagram_renderer.requests.post')
    def test_fallback_http_error(self, mock_post):
        """Test fallback handling of HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_post.return_value = mock_response
        
        mermaid_code = "graph TD\nA --> B"
        
        with pytest.raises(Exception) as exc_info:
            render_mermaid_to_png_fallback(mermaid_code)
        
        assert 'Fallback failed' in str(exc_info.value)
    
    @patch('diagram_renderer.requests.post')
    def test_fallback_exception(self, mock_post):
        """Test fallback handling of general exception."""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        mermaid_code = "graph TD\nA --> B"
        
        with pytest.raises(Exception) as exc_info:
            render_mermaid_to_png_fallback(mermaid_code)
        
        assert 'Fallback rendering failed' in str(exc_info.value)


class TestGeneratePlaceholderPng:
    """Test placeholder PNG generation."""
    
    def test_placeholder_is_valid_png(self):
        """Test that placeholder is a valid PNG."""
        png_data = generate_placeholder_png()
        
        # Check PNG signature
        assert png_data[:8] == b'\x89PNG\r\n\x1a\n'
        assert len(png_data) > 0
    
    def test_placeholder_size(self):
        """Test placeholder PNG size is reasonable."""
        png_data = generate_placeholder_png()
        
        # Should be small (1x1 pixel)
        assert len(png_data) < 200
    
    def test_placeholder_consistency(self):
        """Test that placeholder is consistent across calls."""
        png1 = generate_placeholder_png()
        png2 = generate_placeholder_png()
        
        assert png1 == png2


class TestSaveDiagramToS3:
    """Test S3 saving functionality."""
    
    @patch('diagram_renderer.render_mermaid_to_png')
    def test_save_successful(self, mock_render):
        """Test successful diagram save to S3."""
        # Mock rendering
        mock_render.return_value = b'\x89PNG\r\n\x1a\n' + b'diagram_data'
        
        # Mock S3 helper
        mock_s3_helper = Mock()
        mock_s3_helper.put_diagram_markdown.return_value = 'https://s3.example.com/diagram.md'
        mock_s3_helper.put_diagram_image.return_value = 'https://s3.example.com/diagram.png'
        
        mermaid_code = "graph TD\nA --> B"
        chat_id = "test-chat-123"
        
        markdown_url, image_url = save_diagram_to_s3(mock_s3_helper, chat_id, mermaid_code)
        
        assert markdown_url == 'https://s3.example.com/diagram.md'
        assert image_url == 'https://s3.example.com/diagram.png'
        mock_s3_helper.put_diagram_markdown.assert_called_once_with(chat_id, mermaid_code)
        mock_s3_helper.put_diagram_image.assert_called_once()
    
    @patch('diagram_renderer.requests.post')
    def test_save_with_fallback(self, mock_post):
        """Test save with fallback when primary rendering fails."""
        # Mock S3 helper
        mock_s3_helper = Mock()
        mock_s3_helper.put_diagram_markdown.return_value = 'https://s3.example.com/diagram.md'
        mock_s3_helper.put_diagram_image.return_value = 'https://s3.example.com/diagram.png'
        
        mermaid_code = "graph TD\nA --> B"
        chat_id = "test-chat-123"
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'\x89PNG\r\n\x1a\n' + b'fallback_data'
        mock_post.return_value = mock_response
        
        markdown_url, image_url = save_diagram_to_s3(mock_s3_helper, chat_id, mermaid_code)
        
        assert markdown_url == 'https://s3.example.com/diagram.md'
        assert image_url == 'https://s3.example.com/diagram.png'
        mock_s3_helper.put_diagram_markdown.assert_called_once_with(chat_id, mermaid_code)
        mock_s3_helper.put_diagram_image.assert_called_once()
    
    @patch('diagram_renderer.requests.post')
    def test_save_with_placeholder(self, mock_post):
        """Test save with placeholder when both rendering methods fail."""
        # Mock S3 helper
        mock_s3_helper = Mock()
        mock_s3_helper.put_diagram_markdown.return_value = 'https://s3.example.com/diagram.md'
        mock_s3_helper.put_diagram_image.return_value = 'https://s3.example.com/diagram.png'
        
        mermaid_code = "graph TD\nA --> B"
        chat_id = "test-chat-123"
        
        # Mock failed response to trigger placeholder
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_post.return_value = mock_response
        
        markdown_url, image_url = save_diagram_to_s3(mock_s3_helper, chat_id, mermaid_code)
        
        # Should still save with placeholder
        assert markdown_url == 'https://s3.example.com/diagram.md'
        assert image_url == 'https://s3.example.com/diagram.png'
        mock_s3_helper.put_diagram_markdown.assert_called_once_with(chat_id, mermaid_code)
        mock_s3_helper.put_diagram_image.assert_called_once()
    
    @patch('diagram_renderer.render_mermaid_to_png')
    def test_save_with_different_chat_ids(self, mock_render):
        """Test saving multiple diagrams with different chat IDs."""
        mock_render.return_value = b'\x89PNG\r\n\x1a\n' + b'data'
        
        mock_s3_helper = Mock()
        mock_s3_helper.put_diagram_markdown.return_value = 'https://s3.example.com/diagram.md'
        mock_s3_helper.put_diagram_image.return_value = 'https://s3.example.com/diagram.png'
        
        mermaid_code = "graph TD\nA --> B"
        
        # Save with different chat IDs
        save_diagram_to_s3(mock_s3_helper, "chat-1", mermaid_code)
        save_diagram_to_s3(mock_s3_helper, "chat-2", mermaid_code)
        
        # Verify both were saved with correct IDs
        assert mock_s3_helper.put_diagram_markdown.call_count == 2
        calls = mock_s3_helper.put_diagram_markdown.call_args_list
        assert calls[0][0][0] == "chat-1"
        assert calls[1][0][0] == "chat-2"


class TestIntegration:
    """Integration tests for diagram rendering workflow."""
    
    @patch('diagram_renderer.requests.post')
    def test_full_rendering_workflow(self, mock_post):
        """Test complete rendering workflow."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'\x89PNG\r\n\x1a\n' + b'complete_workflow'
        mock_post.return_value = mock_response
        
        mermaid_code = """graph TD
    A[Start] --> B{Check}
    B -->|Yes| C[Process]
    B -->|No| D[Skip]
    C --> E[End]"""
        
        # Test primary rendering
        result = render_mermaid_to_png(mermaid_code)
        assert result.startswith(b'\x89PNG')
        
        # Test fallback
        result_fallback = render_mermaid_to_png_fallback(mermaid_code)
        assert result_fallback.startswith(b'\x89PNG')
        
        # Test placeholder
        result_placeholder = generate_placeholder_png()
        assert result_placeholder.startswith(b'\x89PNG')
    
    @patch('diagram_renderer.render_mermaid_to_png')
    def test_s3_save_workflow(self, mock_render):
        """Test complete S3 save workflow."""
        mock_render.return_value = b'\x89PNG\r\n\x1a\n' + b'workflow_data'
        
        mock_s3_helper = Mock()
        mock_s3_helper.put_diagram_markdown.return_value = 'https://s3.example.com/md'
        mock_s3_helper.put_diagram_image.return_value = 'https://s3.example.com/png'
        
        mermaid_code = "graph TD\nA --> B"
        chat_id = "workflow-test"
        
        md_url, img_url = save_diagram_to_s3(mock_s3_helper, chat_id, mermaid_code)
        
        assert md_url == 'https://s3.example.com/md'
        assert img_url == 'https://s3.example.com/png'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
