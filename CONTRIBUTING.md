# Contributing to Wordova Web
This document provides guidelines for contributing to our multi-service web application.

## Getting Started

### Prerequisites

Before contributing, ensure you have the following installed:
- **Node.js** (v16 or higher) - for frontend development
- **Go** (v1.19 or higher) - for gateway service development  
- **Python 3.8+** - for ML inference service development
- **Make** - for build orchestration
- **Git** - for version control

### Initial Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/wordova-web.git
   cd wordova-web
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Wordova/wordova-web.git
   ```
4. **Setup all services**:
   ```bash
   make setup  # This installs dependencies for all services
   ```
5. **Verify everything works**:
   ```bash
   make test   # Run all tests
   make build  # Build all services
   ```

## Development Workflow

### Branch Strategy

- **main** - Production-ready code
- **dev** - Integration branch for new features
- **feature/*** - Individual feature branches
- **bugfix/*** - Bug fixes
- **hotfix/*** - Critical production fixes

### Making Changes

1. **Create a feature branch** off of `dev`:
   ```bash
   git checkout dev
   git pull upstream dev
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** in the appropriate service directory:
   - Frontend changes: `frontend/`
   - API Gateway changes: `gateway-service/`
   - ML Service changes: `ml-service/`
   - DevOps/Build changes: `devops/`, root `Makefile`, `.github/`

3. **Test your changes locally**:
   ```bash
   # Test everything
   make test
   
   # Or test specific service
   make frontend-test
   make gateway-service-test
   make ml-service-test
   ```

4. **Lint and format your code**:
   ```bash
   make lint    # Check code style
   make format  # Auto-format code
   ```

5. **Write/update tests**:
   - Frontend: Jest tests in `frontend/tests/`
   - Gateway: Go tests alongside source files (`*_test.go`)
   - ML: pytest tests in `ml-service/tests/`
   - API tests: Tavern YAML in `tests/api/tavern/`

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
- `feat(frontend): add user authentication flow`
- `fix(gateway): resolve CORS headers issue`
- `docs: update API testing guide`
- `test(ml): add model loading integration tests`

## Testing Guidelines

### Unit Tests

- **Coverage requirement**: Minimum 80% code coverage
- **Test naming**: Descriptive test names that explain the scenario
- **Test structure**: Arrange-Act-Assert pattern

### Integration Tests

- **API Tests**: Use Tavern for API contract testing
- **Service Tests**: Test service interactions via HTTP
- **Database Tests**: Use test databases, clean up after tests

## Code Style Guidelines

### Language-Specific Style

- **Go**: Follow [Effective Go](https://golang.org/doc/effective_go.html) guidelines
- **JavaScript/React**: Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- **Python**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)

## Pull Request Process

### Before Submitting

1. **Rebase on latest dev**:
   ```bash
   git fetch upstream
   git rebase upstream/dev
   ```

2. **Run full test suite**:
   ```bash
   make test
   make lint
   ```

3. **Update documentation** if needed

### Submitting the PR

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub:
   - Target the `dev` branch (not `main`)
   - Use descriptive title and description
   - Reference any related issues
   - Include screenshots for UI changes

3. **PR Description Template**:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature  
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

## Release Steps

1. **Create release branch** from `dev`
2. **Update version numbers** in package files
3. **Update CHANGELOG.md**
4. **Create release PR** to `main`
5. **Tag release** after merge
6. **Deploy to production**