.PHONY: install install-dev test lint clean format check fix

VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
UV := $(VENV_DIR)/bin/uv
PYTEST := $(VENV_DIR)/bin/pytest
RUFF := $(VENV_DIR)/bin/ruff

# Create virtual environment and install dependencies
install:
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/python -m pip install uv
	$(UV) pip install -r requirements.txt

# Install development dependencies
install-dev: install
	$(UV) pip install -r requirements-dev.txt

# Run tests
test:
	PYTHONPATH=. $(PYTEST) tests/  -v --cov=custom_components --cov-report=term-missing

# Run linting
lint:
	$(RUFF) check --fix custom_components/ tests/

# Format code
format:
	$(RUFF) format custom_components/ tests/

# Fix all auto-fixable issues
fix:
	$(RUFF) format custom_components/ tests/
	$(RUFF) check --fix custom_components/ tests/

# Run all checks (format, lint, test)
check: format lint test

# Clean up generated files
clean:
	rm -rf $(VENV_DIR)
	rm -rf *.egg-info
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -r {} + 