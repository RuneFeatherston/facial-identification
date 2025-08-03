# Gateway Service Makefile
# Go-based API gateway service

# Include language-specific targets
include ../.github/scripts/make/go.mk

# Service-specific configuration
SERVICE_NAME := gateway-service

# Terminal colors
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

.PHONY: build test lint format clean setup dev run

# Setup dependencies
setup:
	@echo "$(YELLOW)Setting up $(SERVICE_NAME)...$(RESET)"
	go mod tidy

# Build the service binary
build:
	@echo "$(BLUE)Building $(SERVICE_NAME)...$(RESET)"
	$(MAKE) go-build

# Run unit tests
test:
	@echo "$(GREEN)Running unit tests for $(SERVICE_NAME)...$(RESET)"
	$(MAKE) go-test

# Lint the codebase
lint:
	@echo "$(BLUE)Linting $(SERVICE_NAME)...$(RESET)"
	$(MAKE) go-lint-quality

# Format the codebase
format:
	@echo "$(YELLOW)Formatting $(SERVICE_NAME)...$(RESET)"
	$(MAKE) go-fmt

# Clean build artifacts
clean:
	@echo "$(RED)Cleaning $(SERVICE_NAME)...$(RESET)"
	$(MAKE) go-clean

# Development server
dev:
	@echo "$(GREEN)Starting $(SERVICE_NAME) in development mode...$(RESET)"
	go run cmd/main.go

# Run production binary
run:
	@echo "$(GREEN)Starting $(SERVICE_NAME)...$(RESET)"
	./bin/main
