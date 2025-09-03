# Restaurant Management System - Development Guide

## Project Overview
A comprehensive restaurant management system with FastAPI backend and Next.js frontend, supporting multi-tenant architecture for organizations and restaurants.

This project follows a structured 5-phase development plan. See [DEVELOPMENT_PHASES.md](./DEVELOPMENT_PHASES.md) for detailed phase breakdown and implementation roadmap.

## Architecture
- **Backend:** FastAPI with SQLModel/PostgreSQL and Redis caching
- **Frontend:** Next.js 15 with NextAuth.js authentication  
- **Database:** PostgreSQL with multi-tenant support
- **Cache:** Redis for performance optimization
- **Package Management:** UV for Python dependencies

## Development Setup

### Prerequisites
- Docker Desktop
- Node.js 18+ for frontend
- Python 3.12+ with UV package manager

### Backend Development

#### Start Backend Server
```bash
# Using start script (recommended - includes migrations and demo users)
./scripts/start.sh

# Skip demo user creation
./scripts/start.sh --no-seed

# Manual uvicorn startup
uv run uvicorn app.core.app:app --host 0.0.0.0 --port 8000 --reload
```

#### Database Services
```bash
# Start PostgreSQL and Redis services
docker-compose up -d

# Verify services are running
docker ps | grep postgres
docker ps | grep redis
```

#### Database Connection
- **URL:** `postgresql://rms_user:rms_pass@localhost:5432/rms_dev`
- **Async URL:** `postgresql+asyncpg://rms_user:rms_pass@localhost:5432/rms_dev`
- **Test Connection:** `PGPASSWORD=rms_pass psql -h localhost -p 5432 -U rms_user -d rms_dev`

### Frontend Development

#### Start Frontend Server
```bash
cd frontend
npm run dev
# Server runs on http://localhost:3000
```

#### Environment Configuration
Ensure `frontend/.env.local` contains:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_RESTAURANT_ID=a499f8ac-6307-4a84-ab2c-41ab36361b4c
NEXT_PUBLIC_ORGANIZATION_ID=2da4af12-63af-432a-ad0d-51dc68568028
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key
```

## Authentication

### Demo Credentials (Auto-created on startup)
- **Manager:** manager@demorestaurant.com / password123
- **Staff:** staff@demorestaurant.com / password123

### Login Endpoints
- **Frontend:** http://localhost:3000/auth/login
- **Backend API:** http://localhost:8000/api/v1/auth/login

## Testing

### Testing Plan

#### Test Categories
1. **Unit Tests** - Individual component/function testing
2. **Integration Tests** - Module interaction testing
3. **End-to-End Tests** - Full user workflow testing
4. **API Tests** - Endpoint validation and contract testing
5. **Security Tests** - Authentication, authorization, and data validation

#### Backend Testing Strategy

##### Unit Tests
```bash
# Run all unit tests
uv run pytest tests/unit/

# Run specific test file
uv run pytest tests/unit/test_auth_service.py

# Run with coverage
uv run pytest --cov=app tests/unit/
```

##### Integration Tests
```bash
# Run integration tests (requires running services)
uv run pytest tests/integration/

# Test database interactions
uv run pytest tests/integration/test_database.py
```

##### API Tests
```bash
# Run comprehensive API test suite
uv run pytest tests/api/

# Test specific endpoints
uv run pytest tests/api/test_auth_endpoints.py
uv run pytest tests/api/test_menu_endpoints.py
```

#### Frontend Testing Strategy

##### Unit Tests
```bash
cd frontend

# Run Jest unit tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch
```

##### Component Tests
```bash
# Run React Testing Library tests
npm run test:components

# Test specific component
npm test -- MenuComponent.test.js
```

##### End-to-End Tests
```bash
# Run Playwright/Cypress E2E tests
npm run test:e2e

# Run specific E2E test
npm run test:e2e -- auth.spec.js
```

#### Test Data Management

##### Database Test Setup
```bash
# Create test database
PGPASSWORD=rms_pass psql -h localhost -p 5432 -U rms_user -c "CREATE DATABASE rms_test;"

# Run migrations on test DB
TEST_DATABASE_URL=postgresql://rms_user:rms_pass@localhost:5432/rms_test uv run alembic upgrade head
```

##### Test Fixtures
- **Users:** Test users with different roles (admin, manager, staff)
- **Organizations:** Multiple test organizations for multi-tenant testing
- **Restaurants:** Various restaurant configurations
- **Menu Items:** Sample menu data for testing

#### Testing Environments

##### Local Development
```bash
# Set test environment
export ENVIRONMENT=test
export DATABASE_URL=postgresql://rms_user:rms_pass@localhost:5432/rms_test

# Run full test suite
./scripts/run_tests.sh
```

##### CI/CD Pipeline
- **GitHub Actions** for automated testing
- **Docker containers** for consistent test environment
- **Test reporting** and coverage metrics
- **Parallel test execution** for faster feedback

#### Manual Testing

##### Backend API Testing
```bash
# Health check
curl http://localhost:8000/health

# Authentication test
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "manager@demorestaurant.com", "password": "password123"}'

# Menu API test
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/menu/items

# Order creation test
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"items": [{"id": "item_id", "quantity": 2}]}'
```

##### Frontend Manual Testing
- **Authentication Flow:** Login/logout, role-based access
- **Menu Management:** CRUD operations, image uploads
- **Order Processing:** Create, update, track orders
- **User Management:** Role assignment, permissions
- **Multi-tenant Isolation:** Data separation between organizations

#### Performance Testing
```bash
# Load testing with wrk
wrk -t12 -c400 -d30s http://localhost:8000/api/v1/menu/items

# Database performance
uv run pytest tests/performance/ --benchmark-only
```

#### Security Testing
```bash
# SQL injection tests
uv run pytest tests/security/test_sql_injection.py

# Authentication bypass tests
uv run pytest tests/security/test_auth_bypass.py

# Input validation tests
uv run pytest tests/security/test_input_validation.py
```

#### Test Configuration

##### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    slow: Slow running tests
```

##### Test Commands Reference
```bash
# Backend tests
uv run pytest                              # All tests
uv run pytest -m unit                      # Unit tests only
uv run pytest -m integration               # Integration tests only
uv run pytest -m "not slow"                # Skip slow tests
uv run pytest --lf                         # Last failed tests
uv run pytest -x                           # Stop on first failure
uv run pytest -v                           # Verbose output

# Frontend tests  
cd frontend && npm test                     # All tests
cd frontend && npm run test:watch          # Watch mode
cd frontend && npm run test:coverage       # With coverage
cd frontend && npm run test:e2e           # End-to-end tests
```

## Common Issues & Solutions

### Backend Server Won't Start
1. **Port 8000 in use:** `lsof -ti:8000 | xargs kill -9`
2. **Database connection refused:** Ensure Docker is running and PostgreSQL container is up
3. **AsyncPG missing:** `uv add asyncpg`

### Database Connectivity Issues
1. **Docker daemon not running:** Start Docker Desktop
2. **Container not running:** `docker-compose up -d`
3. **Connection refused:** Check container logs with `docker logs rms-postgres`

### Frontend Authentication Errors
1. **Backend not running:** Start backend with `uv run uvicorn app.core.app:app --host 0.0.0.0 --port 8000 --reload`
2. **Invalid credentials:** Use demo credentials above
3. **CORS issues:** Backend CORS is configured for localhost:3000

## API Documentation
- **Swagger UI:** http://localhost:8000/docs (when backend is running)
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

## Development Commands

### Package Management
```bash
# Add new dependency
uv add package-name

# Install dependencies
uv sync

# Run with UV
uv run <command>
```

### Database Management
```bash
# Connect to database
PGPASSWORD=rms_pass psql -h localhost -p 5432 -U rms_user -d rms_dev

# View tables
\dt

# Check users
SELECT email, role FROM users;
```

## Project Structure
```
├── app/                    # FastAPI backend
│   ├── core/              # Core configuration
│   ├── modules/           # Feature modules (auth, menu, etc.)
│   └── shared/            # Shared utilities
├── frontend/              # Next.js frontend
│   ├── src/               # Source code
│   └── public/            # Static assets
├── tests/                 # Test suites
└── docker-compose.yml     # Service definitions
```

## Multi-Tenant Architecture
- Organizations contain multiple restaurants
- Users belong to organizations and optionally specific restaurants
- All API calls include tenant context headers
- Database queries are filtered by tenant IDs

## Production Considerations
- Use environment variables for secrets
- Configure proper CORS origins
- Set up SSL/TLS certificates
- Configure production database
- Set up monitoring and logging

## Important Instructions for Claude
**EXCEPTION:** Claude MUST implement and maintain a CHANGELOG.md file to track all significant changes, features, and fixes made to the project. This overrides the general rule against creating documentation files.