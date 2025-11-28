# app/router/intents.py

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Intent(str, Enum):
    REPAIR_HELP = "repair_help"              # "dishwasher leaking", "ice maker not working"
    COMPAT_CHECK = "compat_check"            # "is PS11752778 compatible with WDT780SAEM1?"
    PRODUCT_INFO = "product_info"            # "tell me about PS11752778"
    BLOG_HOWTO = "blog_howto"                # "what is eco cycle?", "how to reset bosch dishwasher"
    ORDER_SUPPORT = "order_support"          # "where is my order?", "can I return this?"
    POLICY = "policy"                        # "why shop at partselect?", "return policy?"              # "thanks", "you're great", "hi"
    OUT_OF_SCOPE = "out_of_scope"            # microwaves, random Qs, etc.
    CLARIFICATION = "clarification"          # we need more info first


@dataclass
class RoutingMetadata:
    language: str = "en"
    appliance_type: Optional[str] = None          # "refrigerator", "dishwasher"
    part_id: Optional[str] = None                 # PS11752778
    model_number: Optional[str] = None            # WDT780SAEM1
    manufacturer_part_number: Optional[str] = None  # WPW10321304, 242126602 etc.
    brand: Optional[str] = None
    model: Optional[str] = None
    order_id: Optional[str] = None
    missing_fields: List[str] = field(default_factory=list)


@dataclass
class RouteDecision:
    intent: Intent
    normalized_query: str
    metadata: RoutingMetadata
    debug_reason: Optional[str] = None

    def needs_clarification(self) -> bool:
        return self.intent == Intent.CLARIFICATION or bool(self.metadata.missing_fields)
