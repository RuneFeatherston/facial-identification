# API Contract Testing

This directory contains centralized API contract tests using pytest with mocked service clients. These tests verify API client behavior without requiring running services.

## Structure

```
tests/api/
├── Makefile                    # API testing orchestration
├── requirements.txt           # Testing dependencies (pytest, requests, etc.)
├── conftest.py               # pytest configuration and fixtures
├── clients/                  # API client wrapper classes
│   ├── __init__.py
│   ├── gateway_client.py     # Gateway service client
│   └── ml_client.py          # ML service client
├── test_gateway/             # Gateway service tests
│   └── test_health.py
├── test_ml/                  # ML service tests  
│   └── test_health.py
└── test_integration/         # Cross-service integration tests
    └── test_services.py
```

## Quick Start

### Setup
```bash
# From repository root
make setup-api-tests

# Or directly in this directory
cd tests/api
make setup
```

### Run Tests
```bash
# From repository root - run all API tests (mocked, no services needed)
make test-api

# From repository root - full integration testing (starts services)
make test-integration

# From this directory - run specific test suites (mocked)
make test-gateway     # Test gateway service APIs
make test-ml          # Test ml service APIs
make test-integration # Test cross-service workflows
```

## Writing Tests

### Basic Test Structure

```python
# Example: test_gateway/test_health.py
def test_health_endpoint_returns_200(gateway_client):
    """Test that health endpoint returns HTTP 200."""
    response = gateway_client.health()
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Using Client Classes

The client classes in `clients/` provide a clean interface to each service:

```python
# Gateway client usage
gateway_client = GatewayClient("http://localhost:8080")
```python
# Gateway client usage
gateway_client = GatewayClient("http://localhost:8080")
response = gateway_client.health()

# ML client usage  
ml_client = MLClient("http://localhost:8000")
response = ml_client.health()
```

### Mocked Testing Approach

The API clients use a mocked approach for unit testing:
- **No real HTTP calls** are made during `make test-api`
- **Service methods return placeholder values** (currently `None`)
- **Tests verify client interfaces** without requiring running services
- **Full integration testing** with real services happens in `make test-integration`

### Environment Variables

Tests use these base URLs (can be overridden):
- `GATEWAY_BASE_URL`: Default `http://localhost:8080`
- `ML_BASE_URL`: Default `http://localhost:8000`

## Available Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install testing dependencies |
| `make test-all` | Run all API contract tests |
| `make test-gateway` | Test gateway service APIs only |
| `make test-ml` | Test ml service APIs only |
| `make test-integration` | Test cross-service workflows |
| `make test-file FILE=path/to/test.py` | Test individual file |
| `make check-services` | Verify services are running |
| `make clean` | Remove test artifacts |

## 🔧 Development Workflow

1. **Start Services**: Ensure your services are running
   ```bash
   docker-compose up -d
   ```

2. **Write Tests**: Add `.py` test files in appropriate directories

3. **Test Locally**: Run specific test suites during development
   ```bash
   make test-gateway
   ```

4. **Full Integration**: Test complete workflows
   ```bash
   make test-integration
   ```

## Integration with CI/CD

These tests are automatically run in CI/CD:
- **Unit Tests**: Run first (in parallel by service)
- **API Tests**: Run after unit tests pass
- **Integration**: Full service startup + API testing

The same `make` commands work in both local development and CI environments.

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Requests Documentation](https://requests.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
