"""
ORM models backing the SQLite storage.
"""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .db import Base


class Part(Base):
    __tablename__ = "parts"

    part_id = Column(String(32), primary_key=True)
    manufacturer_part_number = Column(String(64), nullable=True)
    part_name = Column(String(255), nullable=False)
    part_price = Column(Numeric(10, 2), nullable=True)
    description = Column(Text, nullable=True)
    symptoms = Column(Text, nullable=True)
    install_difficulty = Column(String(64), nullable=True)
    install_time = Column(String(64), nullable=True)
    replace_parts = Column(Text, nullable=True)
    availability = Column(String(64), nullable=True)
    brand = Column(String(64), nullable=True)
    appliance_type = Column(String(64), nullable=True)
    product_url = Column(String(255), nullable=True)

    model_mappings = relationship(
        "PartModelMapping",
        back_populates="part",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Part part_id={self.part_id} part_name={self.part_name!r}>"


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_number = Column(String(64), unique=True, nullable=False, index=True)
    brand = Column(String(64), nullable=True)
    model_description = Column(Text, nullable=True)
    appliance_type = Column(String(64), nullable=True)
    model_url = Column(String(255), nullable=True)

    part_mappings = relationship(
        "PartModelMapping",
        back_populates="model",
        cascade="all, delete-orphan",
        passive_deletes=True,
        primaryjoin="Model.model_number==PartModelMapping.model_number",
        foreign_keys="PartModelMapping.model_number",
    )

    def __repr__(self) -> str:
        return f"<Model model_number={self.model_number}>"


class PartModelMapping(Base):
    __tablename__ = "part_model_mapping"
    __table_args__ = (
        UniqueConstraint("part_id", "model_number", name="uix_part_model"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_id = Column(String(32), ForeignKey("parts.part_id", ondelete="CASCADE"), nullable=False)
    model_number = Column(String(64), ForeignKey("models.model_number", ondelete="CASCADE"), nullable=False, index=True)

    part = relationship("Part", back_populates="model_mappings")
    model = relationship(
        "Model",
        back_populates="part_mappings",
        primaryjoin="PartModelMapping.model_number==Model.model_number",
        foreign_keys=[model_number],
    )

    def __repr__(self) -> str:
        return f"<PartModelMapping part_id={self.part_id} model_number={self.model_number}>"
