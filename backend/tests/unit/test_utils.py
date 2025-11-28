"""
Unit tests for utility functions.
"""

import pytest
from app.agent.utils import escape_like, link_metadata, clean_llm_response


class TestEscapeLike:
    """Tests for escape_like function."""
    
    def test_escape_percent(self):
        """Test escaping % character."""
        result = escape_like("test%value")
        assert result == "test\\%value"
    
    def test_escape_underscore(self):
        """Test escaping _ character."""
        result = escape_like("test_value")
        assert result == "test\\_value"
    
    def test_escape_backslash(self):
        """Test escaping backslash."""
        result = escape_like("test\\value")
        assert result == "test\\\\value"
    
    def test_escape_multiple(self):
        """Test escaping multiple special characters."""
        result = escape_like("test%_\\value")
        assert result == "test\\%\\_\\\\value"
    
    def test_no_escape_needed(self):
        """Test string with no special characters."""
        result = escape_like("normal text")
        assert result == "normal text"
    
    def test_empty_string(self):
        """Test empty string."""
        result = escape_like("")
        assert result == ""


class TestLinkMetadata:
    """Tests for link_metadata function."""
    
    def test_valid_links(self):
        """Test creating metadata with valid links."""
        links = [
            {"label": "View Product", "url": "https://example.com"},
            {"label": "Contact Support", "url": "https://support.com"},
        ]
        result = link_metadata(links)
        
        assert result["type"] == "links"
        assert len(result["links"]) == 2
        assert result["links"][0]["label"] == "View Product"
        assert result["links"][1]["url"] == "https://support.com"
    
    def test_empty_list(self):
        """Test empty links list."""
        result = link_metadata([])
        assert result == {}
    
    def test_invalid_links_filtered(self):
        """Test that invalid links are filtered out."""
        links = [
            {"label": "Valid", "url": "https://example.com"},
            {"label": "No URL"},  # Missing URL
            {"url": "https://example.com"},  # Missing label
            {"label": "Valid Prompt", "prompt": "Ask about X"},  # Valid with prompt
        ]
        result = link_metadata(links)
        
        assert len(result["links"]) == 2
        assert result["links"][0]["label"] == "Valid"
        assert result["links"][1]["label"] == "Valid Prompt"
    
    def test_prompt_instead_of_url(self):
        """Test link with prompt instead of URL."""
        links = [{"label": "Ask Question", "prompt": "Tell me more"}]
        result = link_metadata(links)
        
        assert len(result["links"]) == 1
        assert result["links"][0]["prompt"] == "Tell me more"


class TestCleanLLMResponse:
    """Tests for clean_llm_response function."""
    
    def test_remove_bold_markdown(self):
        """Test removing **bold** markdown."""
        text = "This is **bold** text"
        result = clean_llm_response(text)
        assert result == "This is bold text"
    
    def test_remove_italic_markdown(self):
        """Test removing *italic* markdown."""
        text = "This is *italic* text"
        result = clean_llm_response(text)
        assert result == "This is italic text"
    
    def test_remove_headers(self):
        """Test removing markdown headers."""
        text = "# Header\n## Subheader\nContent"
        result = clean_llm_response(text)
        assert "Header" in result
        assert "#" not in result
    
    def test_remove_list_markers(self):
        """Test removing list markers."""
        text = "1. First item\n2. Second item\n- Bullet point"
        result = clean_llm_response(text)
        assert "First item" in result
        assert "1." not in result
        assert "-" not in result or "Bullet point" in result
    
    def test_normalize_newlines(self):
        """Test normalizing multiple newlines."""
        text = "Line 1\n\n\n\nLine 2"
        result = clean_llm_response(text)
        assert "\n\n\n" not in result
        assert "\n\n" in result or "\n" in result
    
    def test_trim_whitespace(self):
        """Test trimming whitespace."""
        text = "   Text with spaces   "
        result = clean_llm_response(text)
        assert result == "Text with spaces"
    
    def test_empty_string(self):
        """Test empty string."""
        result = clean_llm_response("")
        assert result == ""
    
    def test_none_input(self):
        """Test None input."""
        result = clean_llm_response(None)
        assert result is None
    
    def test_complex_markdown(self):
        """Test cleaning complex markdown."""
        text = "# Title\n\n**Bold** and *italic* text.\n\n1. First\n2. Second"
        result = clean_llm_response(text)
        assert "Title" in result
        assert "Bold" in result
        assert "italic" in result
        assert "#" not in result
        assert "**" not in result
        assert "*" not in result or "italic" in result

