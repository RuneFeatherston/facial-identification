# Python specific Make targets
# Include this in service Makefiles that use Python

# Default Python commands - override these in your service Makefile if needed
PYTHON := python3
PIP := pip3
VENV_DIR := venv

# Tool configuration
PYTEST_FLAGS ?= -v
BLACK_FLAGS ?= --line-length=88
PYLINT_FLAGS ?= --disable=missing-docstring,too-few-public-methods,invalid-name,redefined-builtin,unnecessary-pass
PYLINT_TARGET ?= src/

# Virtual environment management
.PHONY: python-venv python-venv-clean python-install python-install-dev
python-venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip setuptools wheel

python-venv-clean:
	rm -rf $(VENV_DIR)

python-install:
	@if [ ! -d "$(VENV_DIR)" ]; then $(MAKE) python-venv; fi
	$(VENV_DIR)/bin/pip install -r requirements.txt

python-install-dev:
	@if [ ! -d "$(VENV_DIR)" ]; then $(MAKE) python-venv; fi
	$(VENV_DIR)/bin/pip install -r requirements-dev.txt

# Testing
.PHONY: python-test python-test-coverage
python-test:
	$(VENV_DIR)/bin/pytest $(PYTEST_FLAGS)

python-test-coverage:
	$(VENV_DIR)/bin/pytest $(PYTEST_FLAGS) --cov=src --cov-report=html --cov-report=xml --cov-report=term

# Linting and formatting
.PHONY: python-lint python-format python-format-check python-lint-score
python-lint:
	$(VENV_DIR)/bin/pylint $(PYLINT_FLAGS) $(PYLINT_TARGET)

python-lint-score:
	@echo "Checking Python code quality with minimum score requirement..."
	@output=$$($(VENV_DIR)/bin/pylint $(PYLINT_FLAGS) $(PYLINT_TARGET) 2>&1); \
	score=$$(echo "$$output" | grep "Your code has been rated" | grep -oE "[0-9]+\.[0-9]+" | head -1); \
	if [ -z "$$score" ]; then \
		echo "❌ Could not extract pylint score from output:"; \
		echo "$$output"; \
		exit 1; \
	fi; \
	echo "Current pylint score: $$score/10"; \
	if [ $$(echo "$$score < 8.0" | bc -l) -eq 1 ]; then \
		echo "❌ Code quality below threshold ($$score < 8.0)"; \
		echo "Please improve code quality before proceeding"; \
		echo "Issues found:"; \
		echo "$$output" | head -20; \
		exit 1; \
	else \
		echo "✅ Code quality meets requirements ($$score >= 8.0)"; \
	fi

python-format:
	$(VENV_DIR)/bin/black $(BLACK_FLAGS) src/ tests/

python-format-check:
	$(VENV_DIR)/bin/black $(BLACK_FLAGS) --check src/ tests/

# Cleanup
.PHONY: python-clean
python-clean:
	rm -rf $(VENV_DIR)/ __pycache__/ .pytest_cache/ .coverage htmlcov/ *.egg-info/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
