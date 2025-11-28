"""
CLI utility to seed demo users, orders, and transactions for testing order support features.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from app.config import settings
from app.db import create_tables, session_scope
from app.models import User, Order, Transaction, Part


def _ensure_part_exists(session, part_id: str) -> bool:
    """Check if a part exists, create a dummy one if not."""
    part = session.query(Part).filter(Part.part_id == part_id).first()
    if part:
        return True
    
    # Create a dummy part if it doesn't exist
    dummy_part = Part(
        part_id=part_id,
        part_name=f"Dummy Part {part_id}",
        part_price=Decimal("29.99"),
        appliance_type="refrigerator",
    )
    session.add(dummy_part)
    session.flush()
    return True


def seed_demo_data() -> None:
    """Seed 3-5 demo users with orders and transactions."""
    
    create_tables()
    
    with session_scope() as session:
        # Clear existing demo data (optional - comment out if you want to keep existing data)
        session.query(Transaction).delete()
        session.query(Order).delete()
        session.query(User).delete()
        session.flush()
        
        # Demo User 1: John Doe - Active customer with multiple orders
        user1 = User(
            name="John Doe",
            email="john.doe@example.com"
        )
        session.add(user1)
        session.flush()
        
        # Ensure parts exist
        _ensure_part_exists(session, "PS11752778")
        _ensure_part_exists(session, "PS12345678")
        
        # Order 1 for John: Recent order, shipped
        order1 = Order(
            user_id=user1.user_id,
            part_id="PS11752778",
            order_date=datetime.utcnow() - timedelta(days=3),
            shipping_type="standard",
            order_status="shipped",
            return_eligible=True,
            price_match_eligible=True,
        )
        session.add(order1)
        session.flush()
        
        transaction1 = Transaction(
            transaction_id=f"TXN-{order1.order_id:04d}",
            order_id=order1.order_id,
            amount=Decimal("45.99"),
            status="completed",
            timestamp=order1.order_date,
            payment_method="credit_card",
        )
        session.add(transaction1)
        
        # Order 2 for John: Delivered order, return eligible
        order2 = Order(
            user_id=user1.user_id,
            part_id="PS12345678",
            order_date=datetime.utcnow() - timedelta(days=15),
            shipping_type="express",
            order_status="delivered",
            return_eligible=True,
            price_match_eligible=False,
        )
        session.add(order2)
        session.flush()
        
        transaction2 = Transaction(
            transaction_id=f"TXN-{order2.order_id:04d}",
            order_id=order2.order_id,
            amount=Decimal("67.50"),
            status="completed",
            timestamp=order2.order_date,
            payment_method="paypal",
        )
        session.add(transaction2)
        
        # Demo User 2: Jane Smith - Single order, pending return
        user2 = User(
            name="Jane Smith",
            email="jane.smith@example.com"
        )
        session.add(user2)
        session.flush()
        
        _ensure_part_exists(session, "PS87654321")
        
        order3 = Order(
            user_id=user2.user_id,
            part_id="PS87654321",
            order_date=datetime.utcnow() - timedelta(days=8),
            shipping_type="standard",
            order_status="returned",
            return_eligible=False,  # Already returned
            price_match_eligible=True,
        )
        session.add(order3)
        session.flush()
        
        transaction3 = Transaction(
            transaction_id=f"TXN-{order3.order_id:04d}",
            order_id=order3.order_id,
            amount=Decimal("89.99"),
            status="refunded",
            timestamp=order3.order_date,
            payment_method="credit_card",
        )
        session.add(transaction3)
        
        # Demo User 3: Bob Johnson - Recent order, processing
        user3 = User(
            name="Bob Johnson",
            email="bob.johnson@example.com"
        )
        session.add(user3)
        session.flush()
        
        _ensure_part_exists(session, "PS11111111")
        
        order4 = Order(
            user_id=user3.user_id,
            part_id="PS11111111",
            order_date=datetime.utcnow() - timedelta(days=1),
            shipping_type="overnight",
            order_status="processing",
            return_eligible=True,
            price_match_eligible=True,
        )
        session.add(order4)
        session.flush()
        
        transaction4 = Transaction(
            transaction_id=f"TXN-{order4.order_id:04d}",
            order_id=order4.order_id,
            amount=Decimal("125.00"),
            status="completed",
            timestamp=order4.order_date,
            payment_method="debit_card",
        )
        session.add(transaction4)
        
        # Demo User 4: Alice Williams - Old order, delivered
        user4 = User(
            name="Alice Williams",
            email="alice.williams@example.com"
        )
        session.add(user4)
        session.flush()
        
        _ensure_part_exists(session, "PS22222222")
        
        order5 = Order(
            user_id=user4.user_id,
            part_id="PS22222222",
            order_date=datetime.utcnow() - timedelta(days=30),
            shipping_type="standard",
            order_status="delivered",
            return_eligible=False,  # Outside return window
            price_match_eligible=False,
        )
        session.add(order5)
        session.flush()
        
        transaction5 = Transaction(
            transaction_id=f"TXN-{order5.order_id:04d}",
            order_id=order5.order_id,
            amount=Decimal("34.99"),
            status="completed",
            timestamp=order5.order_date,
            payment_method="credit_card",
        )
        session.add(transaction5)
        
        session.commit()
        
        print(f"✅ Seeded demo data:")
        print(f"   - {4} users")
        print(f"   - {5} orders")
        print(f"   - {5} transactions")
        print(f"\nDemo users:")
        print(f"   1. John Doe (john.doe@example.com) - Orders: {order1.order_id}, {order2.order_id}")
        print(f"   2. Jane Smith (jane.smith@example.com) - Order: {order3.order_id}")
        print(f"   3. Bob Johnson (bob.johnson@example.com) - Order: {order4.order_id}")
        print(f"   4. Alice Williams (alice.williams@example.com) - Order: {order5.order_id}")


if __name__ == "__main__":
    seed_demo_data()

