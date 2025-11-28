#!/bin/bash
# Test runner script for PartSelect Agent backend

echo "=========================================="
echo "PartSelect Agent Backend Test Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Run unit tests
echo -e "${YELLOW}Running unit tests...${NC}"
pytest tests/unit/ -v --tb=short
UNIT_EXIT=$?

echo ""
echo -e "${YELLOW}Running integration tests...${NC}"
pytest tests/integration/ -v --tb=short
INTEGRATION_EXIT=$?

echo ""
echo "=========================================="
if [ $UNIT_EXIT -eq 0 ] && [ $INTEGRATION_EXIT -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi

