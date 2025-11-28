from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List

from app.config import settings


class PartSelectAPIClient:
    """
    Minimal placeholder for a future PartSelect API client.

    Today it simply reads the existing demo datasets, but the class mirrors
    the shape of a real HTTP client so we can swap in actual API calls later
    without touching the ingestion pipeline.
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url or "https://api.partselect.com"
        self.api_key = api_key

    # ------------------------------------------------------------------
    # Parts + cross-reference data
    # ------------------------------------------------------------------
    def fetch_part_records(self) -> Iterable[Dict]:
        """Yield part metadata rows (simulating a paged API)."""

        sources = [
            ("Dishwasher", settings.data_dir / "dishwasher_parts.csv"),
            ("Refrigerator", settings.data_dir / "refrigerator_parts.csv"),
        ]

        for appliance_type, path in sources:
            yield from self._load_csv(path, extra_fields={"appliance_type": appliance_type})

    def fetch_crossref_records(self) -> Iterable[Dict]:
        """Yield part ↔ model cross-reference rows."""

        sources = [
            ("Dishwasher", settings.data_dir / "dishwasher_parts_crossref.csv"),
            ("Refrigerator", settings.data_dir / "refrigerator_parts_crossref.csv"),
        ]

        for appliance_type, path in sources:
            yield from self._load_csv(path, extra_fields={"appliance_type": appliance_type})

    # ------------------------------------------------------------------
    # Documents for RAG ingestion
    # ------------------------------------------------------------------
    def fetch_blog_documents(self) -> List[Dict]:
        blogs_path = settings.data_dir / "blogs.json"
        return self._load_json_list(blogs_path)

    def fetch_repair_guides(self) -> List[Dict]:
        repair_path = settings.data_dir / "repair_guides.json"
        return self._load_json_list(repair_path)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _load_csv(path: Path, extra_fields: Dict | None = None) -> Iterable[Dict]:
        extra_fields = extra_fields or {}
        if not path.exists():
            return

        with path.open("r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                merged = {**row, **extra_fields}
                yield merged

    @staticmethod
    def _load_json_list(path: Path) -> List[Dict]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            if isinstance(data, dict):
                # Some files are {"blogs": [...]} or {"repairs": [...]}
                for value in data.values():
                    if isinstance(value, list):
                        return value
                return []
            return data

