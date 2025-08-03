# Root Makefile: thin wrapper around centralized runner script
SERVICES := frontend gateway-service ml-service

.PHONY: build test lint format clean setup help test-api test-integration service-tests pipeline frontend-% gateway-service-% ml-service-%

# Default target
help:
	@echo "Available targets:"
	@echo "  setup            - Setup dependencies for all services"
	@echo "  build            - Build all services"
	@echo "  test             - Run unit tests for all services"
	@echo "  lint             - Lint all services"
	@echo "  format           - Format all services"
	@echo "  clean            - Clean all services"
	@echo ""
	@echo "Testing workflows:"
	@echo "  service-tests    - Run service tests (build, lint, unit tests)"
	@echo "  test-integration - Run integration tests with Docker services"
	@echo "  test-api         - Run API contract tests (mocked services)"
	@echo ""
	@echo "For service-specific commands, cd into the service directory and run make."

# All operations delegated to runner script
setup:
	@python .github/scripts/runner.py --context local --mode setup

build:
	@python .github/scripts/runner.py --context local --mode build

test:
	@python .github/scripts/runner.py --context local --mode test

lint:
	@python .github/scripts/runner.py --context local --mode lint

format:
	@python .github/scripts/runner.py --context local --mode format

clean:
	@python .github/scripts/runner.py --context local --mode clean

# Testing workflows
service-tests:
	@python .github/scripts/runner.py --context local --mode service-tests

pipeline:
	@python .github/scripts/runner.py --context ci --mode service-tests

test-integration:
	@python .github/scripts/runner.py --context local --mode integration

test-integration-ci:
	@python .github/scripts/runner.py --context ci --mode integration

# Individual service targets (passthrough)
frontend-%:
	@python .github/scripts/runner.py --context local --mode service --service "frontend" --target "$*"

gateway-service-%:
	@python .github/scripts/runner.py --context local --mode service --service "gateway-service" --target "$*"

ml-service-%:
	@python .github/scripts/runner.py --context local --mode service --service "ml-service" --target "$*"

# API contract testing
test-api:
	@python .github/scripts/runner.py --context local --mode test-api
