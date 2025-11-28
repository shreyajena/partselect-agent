"""
Unit tests for metadata extractors.
"""

import pytest
from app.router.extractors import (
    extract_part_id,
    extract_model_number,
    extract_mpn,
    extract_order_id,
    extract_appliance_type,
)


class TestExtractPartId:
    """Tests for extract_part_id function."""
    
    def test_valid_part_id(self):
        """Test extracting valid PartSelect ID."""
        text = "I need part PS123456"
        result = extract_part_id(text)
        assert result == "PS123456"
    
    def test_part_id_with_hyphen(self):
        """Test extracting part ID with hyphen."""
        text = "I need a replacement for PS734936- not working"
        result = extract_part_id(text)
        assert result == "PS734936"
    
    def test_part_id_lowercase(self):
        """Test extracting part ID from lowercase text."""
        text = "part ps123456"
        result = extract_part_id(text)
        assert result == "PS123456"
    
    def test_part_id_in_sentence(self):
        """Test extracting part ID from sentence."""
        text = "Can you tell me about part PS11752778?"
        result = extract_part_id(text)
        assert result == "PS11752778"
    
    def test_no_part_id(self):
        """Test text with no part ID."""
        text = "I need help with my dishwasher"
        result = extract_part_id(text)
        assert result is None
    
    def test_short_part_id(self):
        """Test that short IDs (less than 5 digits) are not matched."""
        text = "part PS1234"
        result = extract_part_id(text)
        assert result is None


class TestExtractModelNumber:
    """Tests for extract_model_number function."""
    
    def test_valid_model_number(self):
        """Test extracting valid model number."""
        text = "My model is WDT780SAEM1"
        result = extract_model_number(text)
        assert result == "WDT780SAEM1"
    
    def test_model_number_with_hyphens(self):
        """Test extracting model number with hyphens."""
        text = "Model DGHX2655TFB"
        result = extract_model_number(text)
        assert result == "DGHX2655TFB"
    
    def test_model_number_not_part_id(self):
        """Test that PS-prefixed strings are not extracted as model numbers."""
        text = "Part PS123456 for model WDT780SAEM1"
        result = extract_model_number(text)
        assert result == "WDT780SAEM1"
        assert result != "PS123456"
    
    def test_no_model_number(self):
        """Test text with no model number."""
        text = "I need help"
        result = extract_model_number(text)
        assert result is None
    
    def test_short_model_number(self):
        """Test that short strings are not extracted."""
        text = "Model ABC"
        result = extract_model_number(text)
        assert result is None
    
    def test_model_number_without_digits(self):
        """Test that model numbers must have digits."""
        text = "Model ABCDEF"
        result = extract_model_number(text)
        assert result is None


class TestExtractMPN:
    """Tests for extract_mpn function."""
    
    def test_valid_mpn(self):
        """Test extracting valid manufacturer part number."""
        text = "Part number WPW10321304"
        result = extract_mpn(text)
        assert result == "WPW10321304"
    
    def test_mpn_not_part_id(self):
        """Test that PS-prefixed strings are not extracted as MPN."""
        text = "Part PS123456 or WPW10321304"
        result = extract_mpn(text)
        assert result == "WPW10321304"
        assert result != "PS123456"
    
    def test_mpn_with_digits(self):
        """Test extracting MPN with digits."""
        # MPN regex requires uppercase letter at start, so pure numbers won't match
        # This is expected behavior - MPN should start with a letter
        text = "MPN W242126602"
        result = extract_mpn(text)
        assert result == "W242126602"
    
    def test_no_mpn(self):
        """Test text with no MPN."""
        text = "I need help"
        result = extract_mpn(text)
        assert result is None


class TestExtractOrderId:
    """Tests for extract_order_id function."""
    
    def test_order_hash_format(self):
        """Test extracting order ID with # format."""
        text = "My order number is #4"
        result = extract_order_id(text)
        assert result == "4"
    
    def test_order_number_is_format(self):
        """Test extracting 'order number is #X' format."""
        text = "My order number is #4, I need to return my order"
        result = extract_order_id(text)
        assert result == "4"
    
    def test_orderid_format(self):
        """Test extracting 'orderid #X' format."""
        text = "Where is my order with orderid #3"
        result = extract_order_id(text)
        assert result == "3"
    
    def test_order_space_number(self):
        """Test extracting 'order X' format."""
        text = "Track order 123"
        result = extract_order_id(text)
        assert result == "123"
    
    def test_order_id_format(self):
        """Test extracting 'order id #X' format."""
        text = "Order id #5"
        result = extract_order_id(text)
        assert result == "5"
    
    def test_no_order_id(self):
        """Test text with no order ID."""
        text = "I need help"
        result = extract_order_id(text)
        assert result is None


class TestExtractApplianceType:
    """Tests for extract_appliance_type function."""
    
    def test_dishwasher(self):
        """Test extracting dishwasher."""
        text = "My dishwasher is leaking"
        result = extract_appliance_type(text)
        assert result == "dishwasher"
    
    def test_refrigerator(self):
        """Test extracting refrigerator."""
        text = "My refrigerator is not cooling"
        result = extract_appliance_type(text)
        assert result == "refrigerator"
    
    def test_fridge_variant(self):
        """Test extracting fridge variant."""
        text = "My fridge is warm"
        result = extract_appliance_type(text)
        assert result == "refrigerator"
    
    def test_no_appliance_type(self):
        """Test text with no appliance type."""
        text = "I need help"
        result = extract_appliance_type(text)
        assert result is None
    
    def test_case_insensitive(self):
        """Test that extraction is case insensitive."""
        text = "My DISHWASHER is broken"
        result = extract_appliance_type(text)
        assert result == "dishwasher"

