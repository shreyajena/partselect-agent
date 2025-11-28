# app/router/router.py

from __future__ import annotations

from .intents import Intent, RouteDecision, RoutingMetadata
from .extractors import (
    extract_part_id,
    extract_model_number,
    extract_mpn,
    extract_order_id,
    extract_appliance_type,
)
from .keywords import (
    POLICY_KEYWORDS,
    ORDER_KEYWORDS,
    COMPAT_KEYWORDS,
    GENERAL_REPAIR_WORDS,
    REPAIR_KEYWORDS,
    HOWTO_KEYWORDS,
)


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
    # -----------------------------
    if any(k in msg for k in POLICY_KEYWORDS):
        return RouteDecision(
            intent=Intent.POLICY,
            normalized_query=user_message,
            metadata=metadata,
            debug_reason="policy",
        )

    # -----------------------------
    # 2. ORDER SUPPORT (when order_id present or order-related keywords)
    # -----------------------------
    if order_id or any(k in msg for k in ORDER_KEYWORDS):
        return RouteDecision(
            intent=Intent.ORDER_SUPPORT,
            normalized_query=user_message,
            metadata=metadata,
            debug_reason="order_support",
        )

    # -----------------------------
    # 3. COMPATIBILITY CHECK
    # -----------------------------
    if any(k in msg for k in COMPAT_KEYWORDS):
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
    
    # General repair detection: appliance type + repair words + no part ID
    if (appliance_type and 
        not part_id and 
        not manufacturer_part_number and
        any(k in msg for k in GENERAL_REPAIR_WORDS)):
        return RouteDecision(
            intent=Intent.REPAIR_HELP,
            normalized_query=user_message,
            metadata=metadata,
            debug_reason="repair_appliance_type_general",
        )
    
    # Specific symptom keywords
    if any(k in msg for k in REPAIR_KEYWORDS):
        return RouteDecision(
            intent=Intent.REPAIR_HELP,
            normalized_query=user_message,
            metadata=metadata,
            debug_reason="repair_symptom_keywords",
        )

    # -----------------------------
    # 5. BLOG HOW-TO / USAGE
    # -----------------------------
    if any(k in msg for k in HOWTO_KEYWORDS):
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
