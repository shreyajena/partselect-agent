"""
End-to-end query flow tests.
"""

import pytest
from app.agent.chat_agent import handle_message
from app.router.router import route_intent


@pytest.mark.integration
@pytest.mark.db
class TestQueryFlow:
    """End-to-end tests for complete query flows."""
    
    def test_product_info_flow(self, db_session, sample_part, mock_llm_response):
        """Test complete flow for product info query."""
        query = "Tell me about PS123456"
        response = handle_message(query, db_session)
        
        assert "reply" in response
        assert response["metadata"]["type"] == "product_info"
        assert response["metadata"]["product"]["id"] == "PS123456"
    
    def test_compatibility_check_flow(self, db_session, sample_part, sample_model, sample_part_model_mapping):
        """Test complete flow for compatibility check."""
        query = "Is PS123456 compatible with WDT780SAEM1?"
        response = handle_message(query, db_session)
        
        assert "reply" in response
        assert "compatible" in response["reply"].lower()
    
    def test_order_support_flow(self, db_session, sample_order, sample_part, sample_transaction, mock_llm_response):
        """Test complete flow for order support query."""
        query = "My order number is #1, what is the status?"
        response = handle_message(query, db_session)
        
        assert "reply" in response
        assert response["metadata"]["type"] == "order_info"
        assert response["metadata"]["order"]["id"] == 1
    
    def test_repair_help_flow(self, db_session, mock_llm_response, monkeypatch):
        """Test complete flow for repair help query."""
        query = "My dishwasher is leaking"
        # Mock RAG retrieval
        try:
            from app.rag import retrieval
            
            def mock_retrieve(*args, **kwargs):
                return [{"text": "Check the water inlet valve and hoses for leaks."}]
            
            monkeypatch.setattr(retrieval, "retrieve_documents", mock_retrieve)
            
            response = handle_message(query, db_session)
            assert "reply" in response
            assert response["metadata"]["type"] == "links"
        except ImportError:
            pytest.skip("RAG dependencies not available")
    
    def test_replacement_query_flow(self, db_session, sample_part, mock_llm_response):
        """Test complete flow for replacement query."""
        query = "I need a replacement for PS123456- not working"
        response = handle_message(query, db_session)
        
        assert "reply" in response
        assert response["metadata"]["type"] == "product_info"
        # Should use replace_parts field in LLM context
    
    def test_order_id_extraction_flow(self, db_session, sample_order, sample_part, sample_transaction, mock_llm_response):
        """Test order ID extraction in various formats."""
        queries = [
            "My order number is #1",
            "Where is my order with orderid #1",
            "Track order 1",
        ]
        
        for query in queries:
            response = handle_message(query, db_session)
            assert "reply" in response
            assert response["metadata"]["type"] == "order_info"
            assert response["metadata"]["order"]["id"] == 1
    
    def test_policy_query_flow(self, db_session):
        """Test complete flow for policy query."""
        query = "What is your return policy?"
        response = handle_message(query, db_session)
        
        assert "reply" in response
        assert response["metadata"]["type"] == "links"
        assert len(response["metadata"]["links"]) > 0
    
    def test_clarification_flow(self, db_session):
        """Test complete flow for clarification request."""
        query = "Is this compatible?"
        response = handle_message(query, db_session)
        
        assert "reply" in response
        # Should ask for missing information
        assert "part id" in response["reply"].lower() or "model number" in response["reply"].lower()

