# Instalily Backend – Step 1

This directory contains the Step 1 deliverable for the Instalily case study: a minimal backend foundation with SQLite storage and a local Chroma vector store.

## What’s Included

- **SQLAlchemy models** for the finalized schema (see `app/models.py`):
  - `parts` keyed by `partselect_number`.
  - `models` storing appliance model metadata.
  - `part_model_mapping` linking parts ↔ models, storing the model number directly for simpler SQL lookups while maintaining a foreign key to `models.model_number`.
- **Configuration + DB helpers** (`app/config.py`, `app/db.py`).
- **Chroma helper** (`app/vector_store.py`) for persisting repair/blog sections.
- **Seed data** under `data/`:
  - `dishwasher_parts.csv`, `refrigerator_parts.csv`.
  - `dishwasher_parts_crossref.csv`, `refrigerator_parts_crossref.csv`.
  - `repair_guides.json`, `blogs.json`.
- **CLI scripts** in `scripts/`:
  - `python -m scripts.ingest_parts`
  - `python -m scripts.ingest_docs`

## Getting Started

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Export optional overrides (SQLite path, data dir, etc.) through `.env` variables prefixed with `INSTALILY_` (see `app/config.py` for defaults).
LLM settings:
- `INSTALILY_LLM_PROVIDER` = `deepseek` (default) or `openai`
- `INSTALILY_DEEPSEEK_API_KEY` when using DeepSeek
- `INSTALILY_OPENAI_API_KEY` when using OpenAI
- Optional: `INSTALILY_DEEPSEEK_MODEL` / `INSTALILY_OPENAI_MODEL` to override default model names.

## Ingestion Workflow

1. **SQLite seeding (parts + model mappings)**
   ```bash
   cd backend
   python -m scripts.ingest_parts
   ```
   - Removes the previous `instalily.db` (if using the default SQLite file) to match the new schema.
   - Loads both part CSVs and upserts into the `parts` table.
   - Reads the cross-reference CSVs, upserts rows in `models`, and creates entries in `part_model_mapping` keyed by `(part_id, model_number)`.

2. **Vector store indexing**
   ```bash
   cd backend
   python -m scripts.ingest_docs
   ```
   - Creates/updates the local `chroma_db` directory.
   - Indexes repair guide sections and blog sections into the `documents` collection.

These steps complete the data foundation and prepare the repo for the next phase (FastAPI endpoints + DeepSeek agent wiring).

## FastAPI Agent

Run the chat API locally:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Sample request:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I install PS11752778?"}'
```
