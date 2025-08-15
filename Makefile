# Makefile for MiniCRM development

.PHONY: help install dev-install test lint format check clean build docs

# Default target
help:
	@echo "MiniCRM Development Commands"
	@echo "============================"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install production dependencies"
	@echo "  dev-install  Install development dependencies and setup pre-commit"
	@echo ""
	@echo "Development:"
	@echo "  test         Run tests with coverage"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code and fix issues"
	@echo "  check        Run all quality checks"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        Clean up generated files"
	@echo "  build        Build distribution packages"
	@echo "  docs         Generate documentation"
	@echo ""

# Installation
install:
	uv sync

dev-install:
	uv sync --dev
	uv run pre-commit install
	uv run pre-commit install --hook-type commit-msg

# Testing
test:
	uv run pytest

test-verbose:
	uv run pytest -v

test-coverage:
	uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Code quality - 标准模式
lint:
	uv run ruff check src/ tests/

lint-fix:
	uv run ruff check src/ tests/ --fix

# Code quality - 宽松模式 (开发阶段推荐)
lint-relaxed:
	uv run ruff check src/ tests/ --config ruff.toml

lint-fix-relaxed:
	uv run ruff check src/ tests/ --config ruff.toml --fix

format:
	uv run ruff format src/ tests/
	uv run docformatter --in-place --recursive src/

type-check:
	uv run mypy src/

# Comprehensive checks
check:
	@echo "Running comprehensive code quality checks..."
	./scripts/check-code.sh

# 宽松模式检查 (开发阶段推荐)
check-relaxed:
	@echo "Running relaxed code quality checks..."
	RELAXED_MODE=true ./scripts/check-code.sh

# Security
security:
	uv run bandit -r src/
	uv run detect-secrets scan --baseline .secrets.baseline

# Documentation
docs:
	@echo "Documentation generation not yet implemented"

# Maintenance
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

# Build
build: clean
	uv build

# Development server (when implemented)
run:
	uv run python -m minicrm

# Database migrations (when implemented)
migrate:
	@echo "Database migrations not yet implemented"

# Pre-commit hooks
pre-commit-all:
	uv run pre-commit run --all-files

# Update dependencies
update:
	uv lock --upgrade

# Performance commands
perf-check:
	./scripts/performance-check.sh

perf-example:
	uv run python examples/performance_usage_examples.py

perf-config:
	uv run python src/minicrm/config/performance_config.py

# Memory profiling
profile-memory:
	uv run python -m memory_profiler examples/performance_usage_examples.py

# Line profiling (requires line_profiler)
profile-line:
	uv run kernprof -l -v examples/performance_usage_examples.py

# Show project info
info:
	@echo "Project: MiniCRM"
	@echo "Python: $(shell python --version)"
	@echo "UV: $(shell uv --version)"
	@echo "Virtual Environment: $(VIRTUAL_ENV)"
	@echo ""
	@echo "Dependencies:"
	@uv tree
	@echo ""
	@echo "Performance Commands:"
	@echo "  make perf-check     - Run performance check"
	@echo "  make perf-example   - Run performance examples"
	@echo "  make perf-config    - Show performance config"
	@echo "  make profile-memory - Memory profiling"
	@echo "  make profile-line   - Line-by-line profiling"
	@echo ""
	@echo "Code Quality (Relaxed Mode):"
	@echo "  make check-relaxed  - Run relaxed quality checks"
	@echo "  make lint-relaxed   - Run relaxed linting"
