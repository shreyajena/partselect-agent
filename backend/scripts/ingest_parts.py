"""
CLI utility to ingest part metadata and cross-reference data into SQLite.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from sqlalchemy import select
from sqlalchemy.engine import make_url

from app.config import settings
from app.db import create_tables, session_scope
from app.models import Model, Part, PartModelMapping


PART_SOURCES: List[Tuple[str, Path]] = [
    ("Dishwasher", settings.data_dir / "dishwasher_parts.csv"),
    ("Refrigerator", settings.data_dir / "refrigerator_parts.csv"),
]

CROSSREF_SOURCES: List[Tuple[str, Path]] = [
    ("Dishwasher", settings.data_dir / "dishwasher_parts_crossref.csv"),
    ("Refrigerator", settings.data_dir / "refrigerator_parts_crossref.csv"),
]


def _normalize_price(value) -> float | None:
    if value in ("", None):
        return None
    if isinstance(value, str):
        cleaned = value.replace("$", "").replace(",", "").strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Expected data file at {path}")
    return pd.read_csv(path).fillna("")


def _reset_sqlite_file():
    url = make_url(settings.database_url)
    if url.get_backend_name() != "sqlite":
        return
    if not url.database:
        return
    db_path = Path(url.database)
    if db_path.exists():
        db_path.unlink()


def _upsert_part(session, record: Dict) -> Tuple[bool, bool]:
    part_id = record.get("partselect_number")
    if not part_id:
        return False, False

    instance = session.get(Part, part_id)
    created = False
    if instance is None:
        instance = Part(part_id=part_id)
        session.add(instance)
        created = True

    instance.manufacturer_part_number = record.get("manufacturer_part_number") or None
    instance.part_name = record.get("part_name") or ""
    instance.part_price = _normalize_price(record.get("part_price"))
    instance.description = record.get("description") or None
    instance.symptoms = record.get("symptoms") or None
    instance.install_difficulty = record.get("install_difficulty") or None
    instance.install_time = record.get("install_time") or None
    instance.replace_parts = record.get("replaceable_models") or record.get("replace_parts") or None
    instance.availability = record.get("availability") or None
    instance.brand = record.get("brand") or None
    instance.appliance_type = record.get("appliance_type") or None
    instance.product_url = record.get("product_url") or None

    return created, not created


def _upsert_model(session, record: Dict, appliance_type: str) -> Tuple[Model, bool]:
    model_number = record.get("model_number")
    if not model_number:
        raise ValueError("Missing model_number in cross-reference row.")

    stmt = select(Model).where(Model.model_number == model_number)
    instance = session.execute(stmt).scalar_one_or_none()
    created = False
    if instance is None:
        instance = Model(model_number=model_number)
        session.add(instance)
        created = True

    if record.get("brand"):
        instance.brand = record.get("brand")
    if record.get("description"):
        instance.model_description = record.get("description")
    if appliance_type:
        instance.appliance_type = appliance_type
    if record.get("model_url"):
        instance.model_url = record.get("model_url")

    session.flush()
    return instance, created


def _link_part_to_model(session, part_id: str, model: Model) -> bool:
    if not part_id:
        return False
    part = session.get(Part, part_id)
    if part is None:
        return False

    stmt = select(PartModelMapping).where(
        PartModelMapping.part_id == part_id,
        PartModelMapping.model_number == model.model_number,
    )
    existing = session.execute(stmt).scalar_one_or_none()
    if existing:
        return False

    session.add(PartModelMapping(part_id=part_id, model_number=model.model_number))
    return True


def _ingest_parts(session) -> Tuple[int, int]:
    created = updated = 0
    for appliance_type, path in PART_SOURCES:
        df = _load_csv(path)
        df["appliance_type"] = appliance_type
        for record in df.to_dict(orient="records"):
            was_created, was_updated = _upsert_part(session, record)
            if was_created:
                created += 1
            elif was_updated:
                updated += 1
    session.flush()
    return created, updated


def _ingest_crossrefs(session) -> Tuple[int, int]:
    models_created = mappings_created = 0
    for appliance_type, path in CROSSREF_SOURCES:
        df = _load_csv(path)
        for record in df.to_dict(orient="records"):
            model, created = _upsert_model(session, record, appliance_type)
            if created:
                models_created += 1
            if _link_part_to_model(session, record.get("partselect_number"), model):
                mappings_created += 1
    return models_created, mappings_created


def main() -> None:
    _reset_sqlite_file()
    create_tables()

    with session_scope() as session:
        parts_created, parts_updated = _ingest_parts(session)
        models_created, mappings_created = _ingest_crossrefs(session)

    print(f"Parts ingested → created: {parts_created}, updated: {parts_updated}")
    print(f"Models created: {models_created}")
    print(f"Part/model mappings created: {mappings_created}")


if __name__ == "__main__":
    main()
