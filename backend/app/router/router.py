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
    Try to capture model-like tokens (WDT780SAEM1, WRX735SDHZ04, etc.)
    while avoiding PS part IDs.
    """
    text_up = text.upper()
    candidates = re.findall(MODEL_REGEX, text_up)
    for c in candidates:
        if c.startswith("PS"):
            continue
        if len(c) >= 6 and any(char.isdigit() for char in c):
            return c
    return None


def extract_mpn(text: str) -> Optional[str]:
    """
    Attempt to capture manufacturer part numbers like W10195416, 242126602, etc.
    """
    text_up = text.upper()
    candidates = re.findall(MPN_REGEX, text_up)
    for token in candidates:
        if token.startswith("PS"):
            continue
        if any(char.isdigit() for char in token):
            return token
    return None


def extract_order_id(text: str) -> Optional[str]:
    m = re.search(ORDER_ID_REGEX, text.lower())
    return m.group(1) if m else None


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
        missing_fields=[],
        order_id=order_id,
    )

    # -----------------------------
    # 1. SMALL TALK
    # -----------------------------
    small_talk_keywords = ["hi", "hello", "thanks", "thank you", "hey"]
    looks_like_small_talk = any(re.search(rf"\b{k}\b", msg) for k in small_talk_keywords)
    if looks_like_small_talk and len(msg.split()) <= 4 and not (part_id or model_number or manufacturer_part_number):
        return RouteDecision(
            intent=Intent.SMALL_TALK,
            normalized_query=user_message,
            metadata=metadata,
        )

    # -----------------------------
    # 2. ORDER SUPPORT
    # -----------------------------
    if order_id or "order" in msg or "tracking" in msg:
        return RouteDecision(
            intent=Intent.ORDER_SUPPORT,
            normalized_query=user_message,
            metadata=metadata,
        )

    # -----------------------------
    # 3. POLICY
    # -----------------------------
    if any(k in msg for k in ["return policy", "return window", "policy", "why shop", "warranty"]):
        return RouteDecision(
            intent=Intent.POLICY,
            normalized_query=user_message,
            metadata=metadata,
        )

    # -----------------------------
    # 4. COMPATIBILITY CHECK
    # -----------------------------
    compat_keywords = ["compatible", "fit", "work with"]
    if any(k in msg for k in compat_keywords):
        missing = []
        if not part_id:
            missing.append("part_id")
        if not model_number:
            missing.append("model_number")

        if missing:
            metadata.missing_fields = missing
            return RouteDecision(
                intent=Intent.CLARIFICATION,
                normalized_query=user_message,
                metadata=metadata,
            )

        return RouteDecision(
            intent=Intent.COMPAT_CHECK,
            normalized_query=user_message,
            metadata=metadata,
        )

    # -----------------------------
    # 5. PRODUCT INFO (any ID → SQL-first)
    # -----------------------------
    if part_id or manufacturer_part_number or model_number:
        return RouteDecision(
            intent=Intent.PRODUCT_INFO,
            normalized_query=user_message,
            metadata=metadata,
        )

    # -----------------------------
    # 6. REPAIR HELP (symptom detection)
    # -----------------------------
    repair_keywords = [
        "leak", "noisy", "won't start", "wont start", "not starting",
        "not working", "not dispensing", "not making ice", "warm", "too warm",
        "too cold", "smell", "error", "won't fill", "won't drain", "stuck",
        "overflow", "flood", "dripping",
    ]

    if any(k in msg for k in repair_keywords):
        return RouteDecision(
            intent=Intent.REPAIR_HELP,
            normalized_query=user_message,
            metadata=metadata,
        )

    # -----------------------------
    # 7. BLOG HOW-TO / USAGE HELP
    # -----------------------------
    howto_keywords = [
        "how to", "what is", "explain", "cycle", "mode", "eco", "settings",
        "reset", "clean cycle", "sanitize cycle",
    ]

    if any(k in msg for k in howto_keywords):
        return RouteDecision(
            intent=Intent.BLOG_HOWTO,
            normalized_query=user_message,
            metadata=metadata,
        )

    # -----------------------------
    # 8. OUT OF SCOPE
    # -----------------------------
    return RouteDecision(
        intent=Intent.OUT_OF_SCOPE,
        normalized_query=user_message,
        metadata=metadata,
    )
