"""
Pytest configuration and fixtures for all tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.models import Part, Model, PartModelMapping, Order, Transaction, User


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh in-memory database for each test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_part(db_session):
    """Create a sample part for testing."""
    part = Part(
        part_id="PS123456",
        manufacturer_part_number="WPW10321304",
        part_name="Water Inlet Valve",
        part_price=45.99,
        description="Replaces water inlet valve for dishwasher",
        symptoms="Dishwasher not filling, leaking water",
        install_difficulty="Easy",
        install_time="15-30 minutes",
        replace_parts="PS123457, PS123458",
        availability="In Stock",
        brand="Whirlpool",
        appliance_type="dishwasher",
        product_url="https://www.partselect.com/PS123456",
    )
    db_session.add(part)
    db_session.commit()
    return part


@pytest.fixture
def sample_model(db_session):
    """Create a sample model for testing."""
    model = Model(
        model_number="WDT780SAEM1",
        brand="Whirlpool",
        model_description="Whirlpool Dishwasher",
        appliance_type="dishwasher",
        model_url="https://www.partselect.com/WDT780SAEM1",
    )
    db_session.add(model)
    db_session.commit()
    return model


@pytest.fixture
def sample_part_model_mapping(db_session, sample_part, sample_model):
    """Create a part-model mapping for testing."""
    mapping = PartModelMapping(
        part_id=sample_part.part_id,
        model_number=sample_model.model_number,
    )
    db_session.add(mapping)
    db_session.commit()
    return mapping


@pytest.fixture
def sample_order(db_session, sample_part):
    """Create a sample order for testing."""
    from datetime import date
    order = Order(
        order_id=1,
        user_id=1,
        part_id=sample_part.part_id,
        order_status="shipped",
        order_date=date(2024, 1, 15),
        shipping_type="Standard",
        return_eligible=True,
    )
    db_session.add(order)
    db_session.commit()
    return order


@pytest.fixture
def sample_transaction(db_session, sample_order):
    """Create a sample transaction for testing."""
    transaction = Transaction(
        transaction_id=1,
        order_id=sample_order.order_id,
        amount=45.99,
        status="completed",
    )
    db_session.add(transaction)
    db_session.commit()
    return transaction


@pytest.fixture
def mock_llm_response(monkeypatch):
    """Mock LLM responses for testing."""
    def mock_llm_answer(*args, **kwargs):
        return "Mock LLM response"
    
    import app.agent.handlers
    monkeypatch.setattr(app.agent.handlers, "llm_answer", mock_llm_answer)
    return mock_llm_answer

