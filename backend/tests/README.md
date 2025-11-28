# Backend Tests

This directory contains comprehensive unit and integration tests for the PartSelect Agent backend.

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_utils.py        # Utility function tests
│   ├── test_extractors.py   # Metadata extractor tests
│   ├── test_db_queries.py   # Database query function tests
│   └── test_router.py       # Router tests
└── integration/             # Integration tests
    ├── test_handlers.py     # Handler integration tests
    └── test_query_flow.py   # End-to-end query flow tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Database tests only
pytest -m db
```

### Run specific test file
```bash
pytest tests/unit/test_utils.py
```

### Run with verbose output
```bash
pytest -v
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Test individual functions in isolation
- No database or external dependencies
- Fast execution

### Integration Tests (`@pytest.mark.integration`)
- Test complete workflows
- May use database fixtures
- Test interactions between components

### Database Tests (`@pytest.mark.db`)
- Tests that require database access
- Use in-memory SQLite database
- Each test gets a fresh database

### LLM Tests (`@pytest.mark.llm`)
- Tests that interact with LLM
- LLM calls are mocked
- No actual API calls

## Fixtures

### `db_session`
Provides a fresh in-memory database session for each test.

### `sample_part`
Creates a sample Part object in the database.

### `sample_model`
Creates a sample Model object in the database.

### `sample_order`
Creates a sample Order object in the database.

### `sample_transaction`
Creates a sample Transaction object in the database.

### `mock_llm_response`
Mocks LLM API calls to return predictable responses.

## Writing New Tests

1. **Unit Tests**: Test individual functions with minimal dependencies
   ```python
   @pytest.mark.unit
   def test_my_function():
       result = my_function("input")
       assert result == "expected"
   ```

2. **Integration Tests**: Test complete workflows
   ```python
   @pytest.mark.integration
   @pytest.mark.db
   def test_complete_flow(db_session, sample_part):
       result = handle_query("test query", db_session)
       assert result["reply"] is not None
   ```

3. **Use Fixtures**: Leverage existing fixtures for common test data
   ```python
   def test_with_part(db_session, sample_part):
       # sample_part is already in db_session
       result = find_part_by_id(db_session, "PS123456")
       assert result is not None
   ```

## Test Coverage Goals

- **Unit Tests**: >90% coverage for utility functions
- **Integration Tests**: Cover all major query flows
- **Edge Cases**: Test error handling and boundary conditions

## Continuous Integration

Tests should be run:
- Before committing code
- In CI/CD pipeline
- Before deploying to production

