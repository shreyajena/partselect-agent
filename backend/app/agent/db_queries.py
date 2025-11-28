# app/agent/db_queries.py
"""
Database query helpers for common operations.
"""

from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Part, PartModelMapping, Model, Order, Transaction
from app.agent.utils import escape_like


def find_part_by_id(db: Session, part_id: str) -> Optional[Part]:
    """
    Find part by PartSelect ID.
    
    Args:
        db: Database session
        part_id: PartSelect part ID (e.g., PS734936)
        
    Returns:
        Part object or None if not found
    """
    return db.query(Part).filter(Part.part_id == part_id).one_or_none()


def find_part_by_mpn(db: Session, mpn: str) -> Optional[Part]:
    """
    Find part by manufacturer part number (fuzzy match).
    
    Args:
        db: Database session
        mpn: Manufacturer part number
        
    Returns:
        Part object or None if not found
    """
    escaped_mpn = escape_like(mpn)
    return (
        db.query(Part)
        .filter(Part.manufacturer_part_number.ilike(f"%{escaped_mpn}%", escape="\\"))
        .first()
    )


def find_part_by_model(db: Session, model_number: str) -> Optional[Part]:
    """
    Find a part by model number (returns first matching part).
    
    Args:
        db: Database session
        model_number: Appliance model number
        
    Returns:
        Part object or None if not found
    """
    return (
        db.query(Part)
        .join(PartModelMapping, Part.part_id == PartModelMapping.part_id)
        .join(Model, Model.model_number == PartModelMapping.model_number)
        .filter(Model.model_number == model_number)
        .first()
    )


def find_part_by_name(db: Session, name_query: str) -> Optional[Part]:
    """
    Find part by name (fuzzy search).
    
    Args:
        db: Database session
        name_query: Search term for part name
        
    Returns:
        Part object or None if not found
    """
    escaped_query = escape_like(name_query)
    return (
        db.query(Part)
        .filter(Part.part_name.ilike(f"%{escaped_query}%", escape="\\"))
        .first()
    )


def resolve_part_identifier(db: Session, part_id: Optional[str], mpn: Optional[str]) -> Optional[Part]:
    """
    Resolve part using either part_id or MPN.
    Prefers explicit PartSelect ID if available.
    
    Args:
        db: Database session
        part_id: PartSelect part ID
        mpn: Manufacturer part number
        
    Returns:
        Part object or None if not found
    """
    if part_id:
        part = find_part_by_id(db, part_id)
        if part:
            return part
    
    if mpn:
        part = find_part_by_mpn(db, mpn)
        if part:
            return part
    
    return None


def check_compatibility(db: Session, part_id: str, model_number: str) -> bool:
    """
    Check if a part is compatible with a model number.
    
    Args:
        db: Database session
        part_id: PartSelect part ID
        model_number: Appliance model number
        
    Returns:
        True if compatible, False otherwise
    """
    compat = (
        db.query(PartModelMapping)
        .filter(
            PartModelMapping.part_id == part_id,
            PartModelMapping.model_number == model_number,
        )
        .one_or_none()
    )
    return compat is not None


def get_order_with_details(db: Session, order_id: int) -> Optional[dict]:
    """
    Get order with related part and transaction information.
    
    Args:
        db: Database session
        order_id: Order ID
        
    Returns:
        Dictionary with order, part, and transaction, or None if order not found
    """
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        return None
    
    part = None
    if order.part_id:
        part = find_part_by_id(db, order.part_id)
    
    transaction = db.query(Transaction).filter(Transaction.order_id == order_id).first()
    
    return {
        "order": order,
        "part": part,
        "transaction": transaction,
    }


def get_model_info(db: Session, model_number: str) -> Optional[Model]:
    """
    Get model information by model number.
    
    Args:
        db: Database session
        model_number: Appliance model number
        
    Returns:
        Model object or None if not found
    """
    return db.query(Model).filter(Model.model_number == model_number).one_or_none()

