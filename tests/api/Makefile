# API Testing Makefile
# Uses pytest + requests for API contract testing

# Configuration
PYTHON := python3
PIP := pip3
PYTEST := pytest

# Terminal colors
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Environment variables with defaults
GATEWAY_BASE_URL ?= http://localhost:8080
ML_BASE_URL ?= http://localhost:8000

.PHONY: help setup test test-gateway test-ml test-integration test-file check-services clean

# Default target
help:
	@echo "$(BLUE)API Testing Commands:$(RESET)"
	@echo "  setup              - Install testing dependencies"
	@echo "  test               - Run all API tests"
	@echo "  test-gateway       - Test gateway service only"
	@echo "  test-ml        - Test ml service only" 
	@echo "  test-integration   - Test cross-service integration"
	@echo "  test-file FILE=... - Test specific file"
	@echo "  check-services     - Verify services are running"
	@echo "  clean              - Remove test artifacts"

# Install dependencies
setup:
	@echo "$(BLUE)Installing API testing dependencies...$(RESET)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(RESET)"

# Run all tests
test:
	@echo "$(BLUE)Running all API tests...$(RESET)"
	GATEWAY_BASE_URL=$(GATEWAY_BASE_URL) ML_BASE_URL=$(ML_BASE_URL) $(PYTEST) -v

# Test gateway service only
test-gateway:
	@echo "$(BLUE)Testing Gateway Service...$(RESET)"
	GATEWAY_BASE_URL=$(GATEWAY_BASE_URL) $(PYTEST) test_gateway/ -v

# Test ml service only  
test-ml:
	@echo "$(BLUE)Testing ML Service...$(RESET)"  
	ML_BASE_URL=$(ML_BASE_URL) $(PYTEST) test_ml/ -v

# Test integration between services
test-integration:
	@echo "$(BLUE)Testing Service Integration...$(RESET)"
	GATEWAY_BASE_URL=$(GATEWAY_BASE_URL) ML_BASE_URL=$(ML_BASE_URL) $(PYTEST) test_integration/ -v

# Test specific file
test-file:
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: FILE parameter required. Usage: make test-file FILE=path/to/test.py$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Testing $(FILE)...$(RESET)"
	GATEWAY_BASE_URL=$(GATEWAY_BASE_URL) ML_BASE_URL=$(ML_BASE_URL) $(PYTEST) $(FILE) -v

# Check if services are running
check-services:
	@echo "$(BLUE)Checking service availability...$(RESET)"
	@echo "Gateway ($(GATEWAY_BASE_URL)):"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" $(GATEWAY_BASE_URL)/health || echo "$(RED)✗ Gateway not responding$(RESET)"
	@echo "ML ($(ML_BASE_URL)):"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" $(ML_BASE_URL)/health || echo "$(RED)✗ ML not responding$(RESET)"

# Clean test artifacts
clean:
	@echo "$(YELLOW)Cleaning test artifacts...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(RESET)"
