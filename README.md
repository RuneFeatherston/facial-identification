# Facial Identification Authenticator

A distributed facial recognition authentication system with real-time video processing.

## Architecture

- **`frontend/`** - Web UI application (React/TypeScript/Vite)
- **`gateway-service/`** - API Gateway and WebSocket server (Go)
- **`ml-service/`** - ML Inference service (Python)
- **`db/`** - Database schema and initialization scripts

## Features

- **Real-time Facial Recognition**: Live video stream processing for authentication
- **WebSocket Communication**: Real-time video frame streaming from frontend to backend
- **Face Embedding Storage**: ML-generated face embeddings stored in PostgreSQL
- **JWT Authentication**: Secure token-based authentication system
- **Docker Deployment**: Complete containerized deployment with docker-compose

## Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/RuneFeatherston/facial-identification.git
cd facial-identification

# Start all services with Docker
docker-compose up --build

# Access the application
# Frontend: http://localhost:3002
# Gateway API: http://localhost:8080
# ML Service: http://localhost:8081
# Database Admin: http://localhost:8082 (Adminer)
```

## Development Setup

### Prerequisites

Ensure you have the following installed:
- **Node.js** (for frontend)
- **Go** (for gateway-service)  
- **Python 3** (for ml-service)
- **PostgreSQL** (for database)
- **Make** (for build orchestration)

### Local Development

```bash
# Setup all services at once
make setup

# Build all services
make build

# Run all tests
make test
```
### EXPLANATION

The repository uses a **hierarchical Make system**:

1. **Root Makefile** (`./Makefile`): Orchestrates all services
2. **Service Makefiles** (`./*/Makefile`): Handle service-specific logic
3. **Language Includes** (`./devops/make/*.mk`): Provide language-specific commands

### Example: Running Tests

When you run `make test` from the root:

```bash
make test
# Executes: for each service in [frontend, gateway-service, ml-service]
#   cd {service} && make test
```

Each service's `make test` then:
- Uses appropriate language-specific testing (Jest, Go test, pytest)
- Runs only that service's tests
- Returns results to the orchestrator

### Language-Specific Tooling

Each service includes the appropriate language tooling:

```makefile
# frontend/Makefile
include ../devops/make/node.mk    # Gets npm, jest, eslint commands

# gateway-service/Makefile  
include ../devops/make/go.mk      # Gets go build, test, lint commands

# ml-service/Makefile
include ../devops/make/python.mk  # Gets pytest, black, flake8 commands
```

## CI/CD Pipeline

### Git-Flow Workflow

This project uses a git-flow branching strategy:

- **`main`** - Production-ready code
- **`dev`** - Integration branch for feature development  
- **`feature/*`** - Feature branches (created from `dev`)

### GitHub Actions Strategy

The CI pipeline runs different test suites based on the target branch:

- **Unit & API Tests**: Run on all PRs to `dev` and `main`
  - Service tests (build, lint, unit tests)
  - API contract tests with mocked services
  - No Docker containers needed
  
- **Integration Tests**: Only run on pushes to `main`
  - Full Docker service orchestration
  - End-to-end testing with real service interactions

CI runs the exact same commands developers use locally.

### Branch Protection

- **Feature branches**: No CI runs on commits to feature branches
- **PRs to dev**: Run unit and API tests only
- **PRs to main**: Run unit and API tests only  
- **Pushes to main**: Run full integration tests

### Getting Help

- Check service-specific README files in each service directory
- Run `make help` for available targets
- Check the GitHub Actions logs for CI/CD issues
- Ensure all prerequisites are installed for your target services

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to contribute to this project.