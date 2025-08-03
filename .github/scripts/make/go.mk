# Go specific Make targets
# Include this in service Makefiles that use Go

# Default Go commands - override these in your service Makefile if needed
GO := go
GOFMT := gofmt
GO_BUILD_FLAGS ?= -v
GO_TEST_FLAGS ?= -v -race -timeout=30s

# Building
.PHONY: go-build go-build-prod go-install
go-build:
	$(GO) build $(GO_BUILD_FLAGS) -o bin/ ./...

go-build-prod:
	CGO_ENABLED=0 GOOS=linux $(GO) build -a -installsuffix cgo -ldflags="-w -s" -o bin/main ./cmd/...

go-install:
	$(GO) install ./...

# Testing
.PHONY: go-test go-test-short go-test-coverage go-test-bench
go-test:
	$(GO) test $(GO_TEST_FLAGS) ./...

go-test-short:
	$(GO) test -short ./...

go-test-coverage:
	$(GO) test -coverprofile=coverage.out -covermode=atomic ./...
	$(GO) tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: coverage.html"

go-test-bench:
	$(GO) test -bench=. -benchmem ./...

# Linting and formatting - using Go's built-in tools
.PHONY: go-lint go-fmt go-fmt-check go-vet go-lint-quality
go-lint:
	$(GO) vet ./...

go-lint-quality:
	@echo "Running comprehensive Go quality checks..."
	@echo "Step 1: go vet (detect suspicious code)"
	@$(GO) vet ./... || (echo "❌ go vet failed - fix issues before proceeding" && exit 1)
	@echo "✅ go vet passed"
	@echo "Step 2: gofmt (code formatting)"
	@if [ -n "$$($(GOFMT) -l .)" ]; then \
		echo "❌ Code formatting issues detected:"; \
		$(GOFMT) -l .; \
		echo "Run 'make go-fmt' to fix formatting"; \
		exit 1; \
	else \
		echo "✅ Code formatting is correct"; \
	fi
	@echo "✅ All Go quality checks passed"

go-fmt:
	$(GOFMT) -w .

go-fmt-check:
	@test -z "$$($(GOFMT) -l .)" || (echo "Go code is not formatted. Run 'make go-fmt' to fix." && exit 1)

go-vet:
	$(GO) vet ./...

# Cleanup
.PHONY: go-clean
go-clean:
	$(GO) clean ./...
	rm -rf bin/ coverage.out coverage.html
