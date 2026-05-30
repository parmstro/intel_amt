# Makefile for parmstro.intel_amt collection

.PHONY: help install test lint build clean sanity integration unit all

COLLECTION_NAMESPACE := parmstro
COLLECTION_NAME := intel_amt
COLLECTION_VERSION := $(shell grep '^version:' galaxy.yml | awk '{print $$2}')
COLLECTION_TARBALL := $(COLLECTION_NAMESPACE)-$(COLLECTION_NAME)-$(COLLECTION_VERSION).tar.gz

help:
	@echo "Available targets:"
	@echo "  help        - Show this help message"
	@echo "  lint        - Run ansible-lint on collection"
	@echo "  sanity      - Run ansible-test sanity"
	@echo "  unit        - Run unit tests with pytest"
	@echo "  integration - Run integration tests (requires vault password)"
	@echo "  test        - Run all tests (lint + sanity + unit + integration)"
	@echo "  build       - Build collection tarball"
	@echo "  install     - Install collection locally"
	@echo "  clean       - Remove build artifacts"
	@echo "  all         - Run everything (lint + test + build)"

lint:
	@echo "Running ansible-lint..."
	ansible-lint -v

sanity:
	@echo "Running ansible-test sanity..."
	ansible-test sanity --docker default -v

unit:
	@echo "Running unit tests..."
	@if [ -d tests/unit ]; then \
		pytest tests/unit/ -v --cov=plugins --cov-report=term --cov-report=html; \
	else \
		echo "No unit tests found"; \
	fi

integration:
	@echo "Running integration tests..."
	@if [ ! -f .vault_password ]; then \
		echo "Error: .vault_password file not found"; \
		echo "Create it with: echo 'your_password' > .vault_password && chmod 600 .vault_password"; \
		exit 1; \
	fi
	tests/integration/run_tests.sh

test: lint sanity unit integration
	@echo "All tests completed successfully!"

build:
	@echo "Building collection version $(COLLECTION_VERSION)..."
	ansible-galaxy collection build --force
	@echo "Built: $(COLLECTION_TARBALL)"

install: build
	@echo "Installing collection..."
	ansible-galaxy collection install $(COLLECTION_TARBALL) --force

clean:
	@echo "Cleaning build artifacts..."
	rm -f $(COLLECTION_NAMESPACE)-$(COLLECTION_NAME)-*.tar.gz
	rm -rf tests/output/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage

all: lint test build
	@echo "All tasks completed successfully!"

# Development helpers
format:
	@echo "Formatting Python code..."
	black plugins/ tests/ --line-length 120

check-format:
	@echo "Checking Python code format..."
	black plugins/ tests/ --check --line-length 120

# Pre-commit checks
pre-commit: lint unit
	@echo "Pre-commit checks passed!"

# Release preparation
prepare-release: clean all
	@echo "Collection ready for release!"
	@echo "Version: $(COLLECTION_VERSION)"
	@echo "Tarball: $(COLLECTION_TARBALL)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Review CHANGELOG.md"
	@echo "  2. Tag release: git tag v$(COLLECTION_VERSION)"
	@echo "  3. Push tag: git push origin v$(COLLECTION_VERSION)"
	@echo "  4. Publish to Galaxy: ansible-galaxy collection publish $(COLLECTION_TARBALL)"

.DEFAULT_GOAL := help
