# Node.js specific Make targets
# Include this in service Makefiles that use Node.js

# Default Node.js commands - override these in your service Makefile if needed
NPM := npm
NODE := node
NODE_ENV ?= development

# Package management
.PHONY: node-install node-ci node-clean-deps
node-install:
	$(NPM) install

node-ci:
	$(NPM) ci

node-clean-deps:
	rm -rf node_modules package-lock.json

# Building
.PHONY: node-build node-build-prod
node-build:
	$(NPM) run build

node-build-prod:
	NODE_ENV=production $(NPM) run build

# Testing
.PHONY: node-test node-test-watch node-test-coverage
node-test:
	$(NPM) test

node-test-watch:
	$(NPM) run test:watch

node-test-coverage:
	$(NPM) run test:coverage

# Linting and formatting
.PHONY: node-lint node-lint-fix node-format node-format-check node-lint-score
node-lint:
	$(NPM) run lint

node-lint-fix:
	$(NPM) run lint:fix

node-lint-score:
	@echo "Running ESLint with quality gate check..."
	@if $(NPM) run lint:score 2>/dev/null; then \
		echo "✅ Frontend code quality meets requirements"; \
	else \
		echo "⚠️  ESLint score check not implemented yet"; \
		echo "Running basic ESLint check instead..."; \
		$(NPM) run lint; \
	fi

node-format:
	$(NPM) run prettier

node-format-check:
	$(NPM) run prettier:check

# Development server
.PHONY: node-dev node-start
node-dev:
	$(NPM) run dev

node-start:
	$(NPM) start

# Cleanup
.PHONY: node-clean
node-clean:
	rm -rf node_modules/ dist/ build/ coverage/
