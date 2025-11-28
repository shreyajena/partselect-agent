# Test Suite Summary

## Test Coverage

### Unit Tests (79 tests)
- ✅ **test_utils.py** (19 tests) - Utility functions
  - `escape_like()` - SQL escaping
  - `link_metadata()` - Metadata formatting
  - `clean_llm_response()` - Markdown cleanup

- ✅ **test_extractors.py** (27 tests) - Metadata extraction
  - `extract_part_id()` - Part ID extraction
  - `extract_model_number()` - Model number extraction
  - `extract_mpn()` - Manufacturer part number extraction
  - `extract_order_id()` - Order ID extraction
  - `extract_appliance_type()` - Appliance type extraction

- ✅ **test_db_queries.py** (19 tests) - Database queries
  - `find_part_by_id()` - Find part by ID
  - `find_part_by_mpn()` - Find part by MPN
  - `find_part_by_model()` - Find part by model
  - `find_part_by_name()` - Find part by name
  - `resolve_part_identifier()` - Resolve part identifier
  - `check_compatibility()` - Check compatibility
  - `get_order_with_details()` - Get order details
  - `get_model_info()` - Get model info

- ✅ **test_router.py** (14 tests) - Intent routing
  - Product info routing
  - Compatibility check routing
  - Order support routing
  - Repair help routing
  - Policy routing
  - Blog/how-to routing
  - Out of scope routing
  - Clarification routing

### Integration Tests
- ✅ **test_handlers.py** - Handler integration tests
  - Product info handler
  - Compatibility check handler
  - Order support handler
  - Policy handler
  - Clarification handler

- ✅ **test_query_flow.py** - End-to-end query flows
  - Product info flow
  - Compatibility check flow
  - Order support flow
  - Replacement query flow
  - Order ID extraction flow
  - Policy query flow
  - Clarification flow

## Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_utils.py

# Run specific test
pytest tests/unit/test_utils.py::TestEscapeLike::test_escape_percent
```

## Test Status

✅ **All unit tests passing** (79/79)
✅ **Integration tests available** (may require dependencies)

## Notes

- Unit tests use in-memory SQLite database
- LLM calls are mocked in tests
- RAG tests may skip if chromadb is not installed
- All tests are isolated and can run independently

