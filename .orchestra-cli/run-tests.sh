#!/bin/bash
# Test runner script for the agent orchestrator

set -e

echo "Running Agent Orchestrator Tests"
echo "================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest is not installed"
    echo "Install with: pip install pytest"
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH=.:$PYTHONPATH

# Run tests
pytest cli/tests/ "$@"

echo ""
echo "================================="
echo "Tests completed!"

