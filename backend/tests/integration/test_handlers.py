"""
Integration tests for handlers.
"""

import pytest
from app.agent.handlers import (
    handle_product_info,
    handle_compat_check,
    handle_order_support,
    handle_repair_help,
    handle_blog_howto,
    handle_policy,
    handle_clarification,
)
from app.router.intents import RouteDecision, RoutingMetadata


@pytest.mark.integration
@pytest.mark.db
class TestHandleProductInfo:
    """Integration tests for handle_product_info."""
    
    def test_handle_product_info_by_part_id(self, db_session, sample_part, mock_llm_response):
        """Test handling product info query with part ID."""
        decision = RouteDecision(
            intent=None,  # Not used in handler
            normalized_query="Tell me about PS123456",
            metadata=RoutingMetadata(part_id="PS123456"),
            debug_reason="test",
        )
        result = handle_product_info(decision, db_session)
        
        assert "reply" in result
        assert result["metadata"]["type"] == "product_info"
        assert result["metadata"]["product"]["id"] == "PS123456"
        assert result["metadata"]["product"]["name"] == "Water Inlet Valve"
    
    def test_handle_product_info_by_mpn(self, db_session, sample_part, mock_llm_response):
        """Test handling product info query with MPN."""
        decision = RouteDecision(
            intent=None,
            normalized_query="What is WPW10321304?",
            metadata=RoutingMetadata(manufacturer_part_number="WPW10321304"),
            debug_reason="test",
        )
        result = handle_product_info(decision, db_session)
        
        assert "reply" in result
        assert result["metadata"]["product"]["id"] == "PS123456"
    
    def test_handle_product_info_not_found(self, db_session):
        """Test handling product info query for non-existent part."""
        decision = RouteDecision(
            intent=None,
            normalized_query="Tell me about PS999999",
            metadata=RoutingMetadata(part_id="PS999999"),
            debug_reason="test",
        )
        result = handle_product_info(decision, db_session)
        
        assert isinstance(result, str)
        assert "couldn't find" in result.lower()


@pytest.mark.integration
@pytest.mark.db
class TestHandleCompatCheck:
    """Integration tests for handle_compat_check."""
    
    def test_handle_compat_check_compatible(self, db_session, sample_part, sample_model, sample_part_model_mapping):
        """Test compatibility check for compatible part."""
        decision = RouteDecision(
            intent=None,
            normalized_query="Is PS123456 compatible with WDT780SAEM1?",
            metadata=RoutingMetadata(
                part_id="PS123456",
                model_number="WDT780SAEM1",
            ),
            debug_reason="test",
        )
        result = handle_compat_check(decision, db_session)
        
        assert "reply" in result
        assert "compatible" in result["reply"].lower()
        assert result["metadata"]["type"] == "links"
    
    def test_handle_compat_check_incompatible(self, db_session, sample_part, sample_model):
        """Test compatibility check for incompatible part."""
        decision = RouteDecision(
            intent=None,
            normalized_query="Is PS123456 compatible with NONEXISTENT?",
            metadata=RoutingMetadata(
                part_id="PS123456",
                model_number="NONEXISTENT",
            ),
            debug_reason="test",
        )
        result = handle_compat_check(decision, db_session)
        
        assert "reply" in result
        assert "not" in result["reply"].lower() or "don't" in result["reply"].lower()


@pytest.mark.integration
@pytest.mark.db
class TestHandleOrderSupport:
    """Integration tests for handle_order_support."""
    
    def test_handle_order_support_with_order_id(self, db_session, sample_order, sample_part, sample_transaction, mock_llm_response):
        """Test handling order support query with order ID."""
        decision = RouteDecision(
            intent=None,
            normalized_query="My order number is #1",
            metadata=RoutingMetadata(order_id="1"),
            debug_reason="test",
        )
        result = handle_order_support(decision, db_session)
        
        assert "reply" in result
        assert result["metadata"]["type"] == "order_info"
        assert result["metadata"]["order"]["id"] == 1
        assert result["metadata"]["order"]["status"] == "shipped"
    
    def test_handle_order_support_not_found(self, db_session):
        """Test handling order support query for non-existent order."""
        decision = RouteDecision(
            intent=None,
            normalized_query="My order number is #999",
            metadata=RoutingMetadata(order_id="999"),
            debug_reason="test",
        )
        result = handle_order_support(decision, db_session)
        
        assert "reply" in result
        assert "not found" in result["reply"].lower()


@pytest.mark.integration
class TestHandlePolicy:
    """Integration tests for handle_policy."""
    
    def test_handle_policy_return_policy(self, db_session):
        """Test handling return policy query."""
        decision = RouteDecision(
            intent=None,
            normalized_query="What is your return policy?",
            metadata=RoutingMetadata(),
            debug_reason="test",
        )
        result = handle_policy(decision, db_session)
        
        assert "reply" in result
        assert result["metadata"]["type"] == "links"
        assert len(result["metadata"]["links"]) > 0
    
    def test_handle_policy_warranty(self, db_session):
        """Test handling warranty query."""
        decision = RouteDecision(
            intent=None,
            normalized_query="What is your warranty?",
            metadata=RoutingMetadata(),
            debug_reason="test",
        )
        result = handle_policy(decision, db_session)
        
        assert "reply" in result
        assert "warranty" in result["reply"].lower()


@pytest.mark.integration
class TestHandleClarification:
    """Integration tests for handle_clarification."""
    
    def test_handle_clarification_missing_part_id(self, db_session):
        """Test handling clarification for missing part ID."""
        decision = RouteDecision(
            intent=None,
            normalized_query="Is this compatible?",
            metadata=RoutingMetadata(missing_fields=["part_id", "model_number"]),
            debug_reason="test",
        )
        result = handle_clarification(decision, db_session)
        
        assert isinstance(result, str)
        assert "part id" in result.lower() or "model number" in result.lower()

