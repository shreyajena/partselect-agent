"""
Unit tests for router.
"""

import pytest
from app.router.router import route_intent
from app.router.intents import Intent


@pytest.mark.unit
class TestRouter:
    """Tests for route_intent function."""
    
    def test_route_product_info_by_part_id(self):
        """Test routing to PRODUCT_INFO with part ID."""
        decision = route_intent("Tell me about PS123456")
        assert decision.intent == Intent.PRODUCT_INFO
        assert decision.metadata.part_id == "PS123456"
    
    def test_route_product_info_by_mpn(self):
        """Test routing to PRODUCT_INFO with MPN."""
        decision = route_intent("What is WPW10321304?")
        assert decision.intent == Intent.PRODUCT_INFO
        assert decision.metadata.manufacturer_part_number == "WPW10321304"
    
    def test_route_compat_check(self):
        """Test routing to COMPAT_CHECK."""
        decision = route_intent("Is PS123456 compatible with WDT780SAEM1?")
        assert decision.intent == Intent.COMPAT_CHECK
        assert decision.metadata.part_id == "PS123456"
        assert decision.metadata.model_number == "WDT780SAEM1"
    
    def test_route_order_support_with_order_id(self):
        """Test routing to ORDER_SUPPORT with order ID."""
        decision = route_intent("My order number is #4")
        assert decision.intent == Intent.ORDER_SUPPORT
        assert decision.metadata.order_id == "4"
    
    def test_route_order_support_with_keywords(self):
        """Test routing to ORDER_SUPPORT with keywords."""
        decision = route_intent("Where is my order?")
        assert decision.intent == Intent.ORDER_SUPPORT
    
    def test_route_repair_help_with_symptoms(self):
        """Test routing to REPAIR_HELP with symptoms."""
        decision = route_intent("My dishwasher is leaking")
        assert decision.intent == Intent.REPAIR_HELP
        assert decision.metadata.appliance_type == "dishwasher"
    
    def test_route_repair_help_general(self):
        """Test routing to REPAIR_HELP with general repair words."""
        decision = route_intent("My dishwasher is not working")
        assert decision.intent == Intent.REPAIR_HELP
        assert decision.metadata.appliance_type == "dishwasher"
    
    def test_route_repair_help_draining(self):
        """Test routing to REPAIR_HELP with draining issue."""
        decision = route_intent("My dishwasher isn't draining — what should I check?")
        assert decision.intent == Intent.REPAIR_HELP
    
    def test_route_policy(self):
        """Test routing to POLICY."""
        decision = route_intent("What is your return policy?")
        assert decision.intent == Intent.POLICY
    
    def test_route_blog_howto(self):
        """Test routing to BLOG_HOWTO."""
        decision = route_intent("What is eco mode on a dishwasher?")
        assert decision.intent == Intent.BLOG_HOWTO
    
    def test_route_out_of_scope(self):
        """Test routing to OUT_OF_SCOPE."""
        decision = route_intent("Tell me about microwaves")
        assert decision.intent == Intent.OUT_OF_SCOPE
    
    def test_route_clarification_missing_fields(self):
        """Test routing to CLARIFICATION when fields are missing."""
        decision = route_intent("Is this compatible?")
        assert decision.intent == Intent.CLARIFICATION
        assert "part_id" in decision.metadata.missing_fields or "model_number" in decision.metadata.missing_fields

