# app/router/router.py

from __future__ import annotations
import re
from typing import Optional

from .intents import Intent, RouteDecision, RoutingMetadata


# ------------------------------------------------------------
# Regex extractors
# ------------------------------------------------------------

PART_ID_REGEX = r"(PS\d{5,})"
MODEL_REGEX = r"\b([A-Za-z0-9]{4,}[A-Za-z0-9-]*)\b"
MPN_REGEX = r"\b([A-Z][A-Z0-9]{4,})\b"
ORDER_ID_REGEX = r"order\s*#?\s*(\d+)"


def extract_part_id(text: str) -> Optional[str]:
    m = re.search(PART_ID_REGEX, text.upper())
    return m.group(1) if m else None


def extract_model_number(text: str) -> Optional[str]:
    """
    Grab things that look like appliance model numbers:
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
    Manufacturer part numbers like W10321304, 242126602, etc.
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
    """
    # Try the standard pattern first
    m = re.search(ORDER_ID_REGEX, text.lower())
    if m:
        return m.group(1)
    
    # Try "order number X" or "order X" (standalone number after "order")
    m = re.search(r"order\s+(?:number\s+)?(\d{1,6})", text.lower())
    if m:
        return m.group(1)
    
    # Try standalone number that might be an order ID (context-dependent)
    # This is less reliable, so we'll be conservative
    return None


def extract_appliance_type(text: str) -> Optional[str]:
    txt = text.lower()
    if "dishwasher" in txt:
        return "dishwasher"
    if "fridge" in txt or "refrigerator" in txt:
        return "refrigerator"
    return None


# ------------------------------------------------------------
# Main routing
# ------------------------------------------------------------

def route_intent(user_message: str) -> RouteDecision:
    msg = user_message.lower().strip()

    # -----------------------------
    # Metadata extraction
    # -----------------------------
    part_id = extract_part_id(user_message)
    model_number = extract_model_number(user_message)
    manufacturer_part_number = extract_mpn(user_message)
    order_id = extract_order_id(user_message)
    appliance_type = extract_appliance_type(user_message)

    metadata = RoutingMetadata(
        appliance_type=appliance_type,
        part_id=part_id,
        model_number=model_number,
        manufacturer_part_number=manufacturer_part_number,
        brand=None,
        order_id=order_id,
        missing_fields=[],
    )

    # -----------------------------
    # 1. POLICY (check before order support to catch "return policy" etc.)
    # Only match explicit policy questions, not order return status
    # -----------------------------
    if any(k in msg for k in ["return policy", "return window", "policy", "why shop", "warranty", "guarantee", "shipping policy", "price match"]):
        return RouteDecision(
            intent=Intent.POLICY,
            normalized_query=user_message,
            metadata=metadata,
            debug_reason="policy",
        )

    # -----------------------------
    # 2. ORDER SUPPORT (fuzzy)
    # -----------------------------
    if order_id or any(
        k in msg
        for k in ["order", "ordr", "oder", "oroder", "tracking", "track shipment", "track", "shipment", "shipping", "my order", "order status", "refund my", "my return", "return status", "is my return"]
    ):
        return RouteDecision(
            intent=Intent.ORDER_SUPPORT,
            normalized_query=user_message,
            metadata=metadata,
            debug_reason="order_support",
        )

    # -----------------------------
    # 3. COMPATIBILITY CHECK
    # -----------------------------
    compat_keywords = ["compatible", "fit", "work with"]
    if any(k in msg for k in compat_keywords):
        missing = []
        if not (part_id):
            missing.append("part_id")
        if not model_number:
            missing.append("model_number")

        if missing:
            metadata.missing_fields = missing
            return RouteDecision(
                intent=Intent.CLARIFICATION,
                normalized_query=user_message,
                metadata=metadata,
                debug_reason="compat_missing_fields",
            )

        return RouteDecision(
            intent=Intent.COMPAT_CHECK,
            normalized_query=user_message,
            metadata=metadata,
            debug_reason="compat_full",
        )

    # -----------------------------
    # 5. PRODUCT INFO (any ID)
    # -----------------------------
    if part_id or manufacturer_part_number:
        return RouteDecision(
            intent=Intent.PRODUCT_INFO,
            normalized_query=user_message,
            metadata=metadata,
            debug_reason="product_info_by_id_or_model",
        )

    # -----------------------------
    # 4. REPAIR HELP (symptoms)
    # -----------------------------
    repair_keywords = [
        "leak", "leaking",
        "noisy", "noise",
        "won't start", "wont start", "not starting",
        "not working", "stopped working",
        "not dispensing", "not making ice",
        "warm", "too warm", "not cooling", "not cold",
        "freezing up", "icing up",
        "smell", "odor",
        "won't fill", "wont fill",
        "won't drain", "wont drain",
        "stuck", "jammed",
        "overflow", "flooding",
    ]

    if any(k in msg for k in repair_keywords):
        return RouteDecision(
            intent=Intent.REPAIR_HELP,
            normalized_query=user_message,
            metadata=metadata,
            debug_reason="repair_symptom_keywords",
        )

    # -----------------------------
    # 5. BLOG HOW-TO / USAGE
    # -----------------------------
    howto_keywords = [
        "how to", "how do i",
        "what is", "what does",
        "explain",
        "cycle", "mode", "eco", "sanitize", "quick wash", "settings",
        "reset", "clean cycle",
    ]

    if any(k in msg for k in howto_keywords):
        return RouteDecision(
            intent=Intent.BLOG_HOWTO,
            normalized_query=user_message,
            metadata=metadata,
            debug_reason="usage_keywords",
        )

    # -----------------------------
    # 6. OUT OF SCOPE
    # -----------------------------
    return RouteDecision(
        intent=Intent.OUT_OF_SCOPE,
        normalized_query=user_message,
        metadata=metadata,
        debug_reason="fallback_out_of_scope",
    )
