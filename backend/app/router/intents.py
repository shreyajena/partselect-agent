# app/router/intents.py

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Intent(str, Enum):
    REPAIR_HELP = "repair_help"
    COMPAT_CHECK = "compat_check"
    PRODUCT_INFO = "product_info"
    BLOG_HOWTO = "blog_howto"
    ORDER_SUPPORT = "order_support"
    POLICY = "policy"
    SMALL_TALK = "small_talk"
    OUT_OF_SCOPE = "out_of_scope"
    CLARIFICATION = "clarification"


@dataclass
class RoutingMetadata:
    part_id: Optional[str] = None
    model_number: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    order_id: Optional[str] = None
    appliance_type: Optional[str] = None
    brand: Optional[str] = None
    missing_fields: list[str] = field(default_factory=list)


@dataclass
class RouteDecision:
    intent: Intent
    normalized_query: str
    metadata: RoutingMetadata
    debug_reason: Optional[str] = None
