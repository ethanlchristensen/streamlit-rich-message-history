.PHONY: install format lint type-check test check all clean

# Install dependencies
install:
	poetry install

# Format code with black and isort
format:
	poetry run black .
	poetry run isort .

# Run linting with flake8
lint:
	poetry run flake8

# Format check only (no changes)
format-check:
	poetry run black --check .
	poetry run isort --check .

# Run type checking with mypy
type-check:
	poetry run mypy streamlit_rich_message_history

# Run tests with pytest
test:
	poetry run pytest

# Run all checks without formatting
check: lint format-check type-check test

# Run all checks and formatting
all: format lint type-check test

# Clean up cache files
clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

release:
	poetry run python release.py