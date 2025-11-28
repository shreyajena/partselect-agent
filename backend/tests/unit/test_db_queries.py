"""
Unit tests for database query functions.
"""

import pytest
from app.agent.db_queries import (
    find_part_by_id,
    find_part_by_mpn,
    find_part_by_model,
    find_part_by_name,
    resolve_part_identifier,
    check_compatibility,
    get_order_with_details,
    get_model_info,
)


@pytest.mark.unit
@pytest.mark.db
class TestFindPartById:
    """Tests for find_part_by_id function."""
    
    def test_find_existing_part(self, db_session, sample_part):
        """Test finding an existing part by ID."""
        result = find_part_by_id(db_session, "PS123456")
        assert result is not None
        assert result.part_id == "PS123456"
        assert result.part_name == "Water Inlet Valve"
    
    def test_find_nonexistent_part(self, db_session):
        """Test finding a non-existent part."""
        result = find_part_by_id(db_session, "PS999999")
        assert result is None


@pytest.mark.unit
@pytest.mark.db
class TestFindPartByMPN:
    """Tests for find_part_by_mpn function."""
    
    def test_find_by_exact_mpn(self, db_session, sample_part):
        """Test finding part by exact MPN."""
        result = find_part_by_mpn(db_session, "WPW10321304")
        assert result is not None
        assert result.part_id == "PS123456"
    
    def test_find_by_partial_mpn(self, db_session, sample_part):
        """Test finding part by partial MPN."""
        result = find_part_by_mpn(db_session, "WPW103")
        assert result is not None
        assert result.part_id == "PS123456"
    
    def test_find_nonexistent_mpn(self, db_session):
        """Test finding non-existent MPN."""
        result = find_part_by_mpn(db_session, "NONEXISTENT")
        assert result is None


@pytest.mark.unit
@pytest.mark.db
class TestFindPartByModel:
    """Tests for find_part_by_model function."""
    
    def test_find_part_by_model(self, db_session, sample_part, sample_model, sample_part_model_mapping):
        """Test finding part by model number."""
        result = find_part_by_model(db_session, "WDT780SAEM1")
        assert result is not None
        assert result.part_id == "PS123456"
    
    def test_find_nonexistent_model(self, db_session):
        """Test finding part for non-existent model."""
        result = find_part_by_model(db_session, "NONEXISTENT")
        assert result is None


@pytest.mark.unit
@pytest.mark.db
class TestFindPartByName:
    """Tests for find_part_by_name function."""
    
    def test_find_by_exact_name(self, db_session, sample_part):
        """Test finding part by exact name."""
        result = find_part_by_name(db_session, "Water Inlet Valve")
        assert result is not None
        assert result.part_id == "PS123456"
    
    def test_find_by_partial_name(self, db_session, sample_part):
        """Test finding part by partial name."""
        result = find_part_by_name(db_session, "Water Inlet")
        assert result is not None
        assert result.part_id == "PS123456"
    
    def test_find_nonexistent_name(self, db_session):
        """Test finding non-existent part name."""
        result = find_part_by_name(db_session, "NonExistent Part")
        assert result is None


@pytest.mark.unit
@pytest.mark.db
class TestResolvePartIdentifier:
    """Tests for resolve_part_identifier function."""
    
    def test_resolve_by_part_id(self, db_session, sample_part):
        """Test resolving by part ID."""
        result = resolve_part_identifier(db_session, "PS123456", None)
        assert result is not None
        assert result.part_id == "PS123456"
    
    def test_resolve_by_mpn(self, db_session, sample_part):
        """Test resolving by MPN."""
        result = resolve_part_identifier(db_session, None, "WPW10321304")
        assert result is not None
        assert result.part_id == "PS123456"
    
    def test_prefer_part_id_over_mpn(self, db_session, sample_part):
        """Test that part ID is preferred over MPN."""
        result = resolve_part_identifier(db_session, "PS123456", "WPW10321304")
        assert result is not None
        assert result.part_id == "PS123456"
    
    def test_resolve_nonexistent(self, db_session):
        """Test resolving non-existent identifier."""
        result = resolve_part_identifier(db_session, "PS999999", "NONEXISTENT")
        assert result is None


@pytest.mark.unit
@pytest.mark.db
class TestCheckCompatibility:
    """Tests for check_compatibility function."""
    
    def test_compatible_part_model(self, db_session, sample_part, sample_model, sample_part_model_mapping):
        """Test checking compatible part and model."""
        result = check_compatibility(db_session, "PS123456", "WDT780SAEM1")
        assert result is True
    
    def test_incompatible_part_model(self, db_session, sample_part, sample_model):
        """Test checking incompatible part and model."""
        result = check_compatibility(db_session, "PS123456", "NONEXISTENT")
        assert result is False


@pytest.mark.unit
@pytest.mark.db
class TestGetOrderWithDetails:
    """Tests for get_order_with_details function."""
    
    def test_get_order_with_details(self, db_session, sample_order, sample_part, sample_transaction):
        """Test getting order with all details."""
        result = get_order_with_details(db_session, 1)
        assert result is not None
        assert result["order"].order_id == 1
        assert result["part"].part_id == "PS123456"
        assert float(result["transaction"].amount) == 45.99
    
    def test_get_order_without_part(self, db_session):
        """Test getting order without part."""
        from datetime import date
        from app.models import Order
        # Create order without part_id
        order = Order(
            order_id=2,
            user_id=1,
            part_id=None,
            order_status="pending",
            order_date=date(2024, 1, 15),
            shipping_type="Standard",
            return_eligible=False,
        )
        db_session.add(order)
        db_session.commit()
        
        result = get_order_with_details(db_session, 2)
        assert result is not None
        assert result["order"].order_id == 2
        assert result["part"] is None
    
    def test_get_nonexistent_order(self, db_session):
        """Test getting non-existent order."""
        result = get_order_with_details(db_session, 999)
        assert result is None


@pytest.mark.unit
@pytest.mark.db
class TestGetModelInfo:
    """Tests for get_model_info function."""
    
    def test_get_existing_model(self, db_session, sample_model):
        """Test getting existing model."""
        result = get_model_info(db_session, "WDT780SAEM1")
        assert result is not None
        assert result.model_number == "WDT780SAEM1"
        assert result.brand == "Whirlpool"
    
    def test_get_nonexistent_model(self, db_session):
        """Test getting non-existent model."""
        result = get_model_info(db_session, "NONEXISTENT")
        assert result is None

