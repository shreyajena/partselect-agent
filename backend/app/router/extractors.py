# app/router/extractors.py
"""
Metadata extraction functions for routing.
"""

from __future__ import annotations
import re
from typing import Optional

# Regex patterns
PART_ID_REGEX = r"(PS\d{5,})"
MODEL_REGEX = r"\b([A-Za-z0-9]{4,}[A-Za-z0-9-]*)\b"
MPN_REGEX = r"\b([A-Z][A-Z0-9]{4,})\b"
ORDER_ID_REGEX = r"order\s*#?\s*(\d+)"


def extract_part_id(text: str) -> Optional[str]:
    """Extract PartSelect part ID (e.g., PS734936) from text."""
    m = re.search(PART_ID_REGEX, text.upper())
    return m.group(1) if m else None


def extract_model_number(text: str) -> Optional[str]:
    """
    Extract appliance model number from text.
    - at least 6 chars
    - mix of letters+digits
    - but NOT PS part IDs
    """
    text_up = text.upper()
    candidates = re.findall(MODEL_REGEX, text_up)
    for c in candidates:
        if c.startswith("PS"):
            continue
        if len(c) >= 6 and any(ch.isdigit() for ch in c):
            return c
    return None


def extract_mpn(text: str) -> Optional[str]:
    """
    Extract manufacturer part number from text.
    Examples: W10321304, 242126602, etc.
    """
    text_up = text.upper()
    candidates = re.findall(MPN_REGEX, text_up)
    for token in candidates:
        if token.startswith("PS"):
            continue
        if any(ch.isdigit() for ch in token):
            return token
    return None


def extract_order_id(text: str) -> Optional[str]:
    """
    Extract order ID from text. Handles:
    - "order #83"
    - "order 83"
    - "track order 123"
    - "order number 456"
    - "order number is #4"
    - "orderid #3"
    """
    text_lower = text.lower()
    
    # Try "order number is #X" or "order number #X"
    m = re.search(r"order\s+number\s+(?:is\s+)?#?\s*(\d{1,6})", text_lower)
    if m:
        return m.group(1)
    
    # Try "orderid #X" or "order id #X"
    m = re.search(r"order\s*id\s*#?\s*(\d{1,6})", text_lower)
    if m:
        return m.group(1)
    
    # Try the standard pattern "order #X"
    m = re.search(ORDER_ID_REGEX, text_lower)
    if m:
        return m.group(1)
    
    # Try "order X" (standalone number after "order")
    m = re.search(r"order\s+(\d{1,6})", text_lower)
    if m:
        return m.group(1)
    
    return None


def extract_appliance_type(text: str) -> Optional[str]:
    """Extract appliance type (dishwasher or refrigerator) from text."""
    txt = text.lower()
    if "dishwasher" in txt:
        return "dishwasher"
    if "fridge" in txt or "refrigerator" in txt:
        return "refrigerator"
    return None

