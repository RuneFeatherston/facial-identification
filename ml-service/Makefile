# ML Service Makefile  
# Python-based ML inference service

# Include language-specific targets
include ../.github/scripts/make/python.mk

# Service-specific configuration
SERVICE_NAME := ml-service

# Terminal colors (for any custom targets)
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Service-specific targets that provide actual functionality
.PHONY: dev run build test lint clean help

# Generic target aliases (for compatibility with runner script)
build: python-install-dev
test: python-install-dev python-test
lint: python-install-dev python-lint-score
clean: python-clean

# Help target
help:
	@echo "$(BLUE)$(SERVICE_NAME) Commands:$(RESET)"
	@echo "  dev                - Start development server"
	@echo "  run                - Start production server"
	@echo "  build              - Install dependencies"
	@echo "  test               - Run tests"
	@echo "  lint               - Run linting"
	@echo "  clean              - Clean build artifacts"

# Development server
dev:
	@echo "$(GREEN)Starting $(SERVICE_NAME) in development mode...$(RESET)"
	$(VENV_DIR)/bin/python src/main.py

# Production server
run:
	@echo "$(GREEN)Starting $(SERVICE_NAME)...$(RESET)"
	$(VENV_DIR)/bin/python src/main.py
