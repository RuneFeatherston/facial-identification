# Frontend Service Makefile
# Node.js-based frontend application

# Include language-specific targets
include ../.github/scripts/make/node.mk

# Service-specific configuration
SERVICE_NAME := frontend

# Terminal colors
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

.PHONY: build test lint format clean setup dev

# Setup dependencies
setup:
	@echo "$(YELLOW)Setting up $(SERVICE_NAME)...$(RESET)"
	@echo "$(GREEN)Frontend setup completed (no dependencies yet)$(RESET)"

# Build the application
build:
	@echo "$(BLUE)Building $(SERVICE_NAME)...$(RESET)"
	$(MAKE) node-build

# Run unit tests
test:
	@echo "$(GREEN)Running unit tests for $(SERVICE_NAME)...$(RESET)"
	$(MAKE) node-test

# Lint the codebase
lint:
	@echo "$(BLUE)Linting $(SERVICE_NAME)...$(RESET)"
	$(MAKE) node-lint-score

# Format the codebase
format:
	@echo "$(YELLOW)Formatting $(SERVICE_NAME)...$(RESET)"
	$(MAKE) node-format

# Clean build artifacts and dependencies
clean:
	@echo "$(RED)Cleaning $(SERVICE_NAME)...$(RESET)"
	$(MAKE) node-clean

# Development server
dev:
	@echo "$(GREEN)Starting development server for $(SERVICE_NAME)...$(RESET)"
	$(MAKE) node-dev
