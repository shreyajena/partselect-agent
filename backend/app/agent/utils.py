# app/agent/utils.py
"""
Utility functions for handlers.
"""

import re
from typing import Optional


def escape_like(term: str) -> str:
    """
    Escape LIKE wildcards to reduce SQL injection risk.
    
    Args:
        term: String to escape
        
    Returns:
        Escaped string safe for use in SQL LIKE queries
    """
    return (
        term.replace("\\", "\\\\")
        .replace("%", r"\%")
        .replace("_", r"\_")
    )


def link_metadata(links: list[dict]) -> dict:
    """
    Format links into metadata structure for frontend.
    
    Args:
        links: List of link dictionaries with 'label' and 'url' or 'prompt'
        
    Returns:
        Metadata dictionary with type 'links' or empty dict if no valid links
    """
    clean = [
        link
        for link in links
        if link.get("label") and (link.get("url") or link.get("prompt"))
    ]
    if not clean:
        return {}
    return {"type": "links", "links": clean}


def clean_llm_response(text: str) -> str:
    """
    Clean up markdown formatting that might slip through from LLM responses.
    Removes markdown bold/italic, headers, and normalizes spacing.
    
    Args:
        text: Raw LLM response text
        
    Returns:
        Cleaned plain text without markdown formatting
    """
    if not text:
        return text
    
    # Remove markdown bold (**text** or __text__)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    
    # Remove markdown italic (*text* or _text_)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # Remove markdown headers (# Header)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # Remove markdown list markers (1. or - or *)
    text = re.sub(r'^\s*[\d\.\-\*]+\s+', '', text, flags=re.MULTILINE)
    
    # Clean up multiple consecutive newlines (max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Trim whitespace
    text = text.strip()
    
    return text

