# Restaurant Management System (RMS)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-brightgreen)](https://fastapi.tiangolo.com)
[![SQLModel](https://img.shields.io/badge/SQLModel-0.0.8+-blue)](https://sqlmodel.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A comprehensive **multi-tenant restaurant management system** built with modern Python stack. Designed to scale from single restaurants to franchise operations with **multi-tenant architecture from day 1**.

## 🚀 Quick Start

### Prerequisites
```bash
# Install astral uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Start PostgreSQL (Docker required)
docker-compose up -d postgres
```

### Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd rms

# Install dependencies with uv
uv sync

# Run database migrations
uv run alembic upgrade head

# Load sample data
uv run python scripts/load_fixtures.py

# Run comprehensive tests
uv run pytest -v

# Start development server
uv run uvicorn app.main:app --reload --port 8000
```

### API Documentation
Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **API Health Check**: http://localhost:8000/health

---

## 🎯 System Overview

### **Multi-Tenant SaaS Architecture**
Built from day 1 to support:
- **Independent Restaurants**: Single location operations
- **Restaurant Chains**: Multiple locations under one organization
- **Franchise Systems**: Multi-organization with shared branding
- **Enterprise Solutions**: Complex hierarchical restaurant groups

### **Core Business Domains**
```
🏢 Organizations (Tenant Root)
  ├── 🍽️  Restaurants (Multiple per organization)
  ├── 👥 Users (Organization or Restaurant scoped)
  ├── 📋 Menu Management (Categories, Items, Modifiers)
  ├── 🪑 Table & Reservation System
  ├── 📱 QR Code Ordering (Multi-person sessions)
  ├── 🛎️  Order Management & Kitchen Operations
  └── 💳 Payment Processing & Split Bills
```

### **Phase 1 Implementation Status**
✅ **Multi-tenant database foundation** (organizations → restaurants)  
✅ **User authentication and role-based access control**  
✅ **Complete menu management** (categories, items, modifiers)  
✅ **Restaurant setup and configuration**  
✅ **UUID-based primary keys** throughout  
✅ **Zero-migration path to full multi-tenancy** (Phase 4)  
✅ **Comprehensive API test suite**  
✅ **Docker development environment**  
✅ **Alembic database migrations**

---

## 🧪 Comprehensive API Testing Framework

> **Inspired by ABC API Modular Project**
> 
> The RMS testing strategy is based on the comprehensive `api-tester` framework from the ABC API Modular project, adapted for restaurant management workflows.

### **Testing Architecture**

```
rms/
├── tests/
│   ├── api_tester/                    # Comprehensive API testing suite
│   │   ├── shared/                    # Shared utilities and authentication
│   │   │   ├── auth.py                # JWT authentication handling
│   │   │   ├── utils.py               # API testing utilities and helpers
│   │   │   └── fixtures.py            # Test data generation
│   │   ├── sample_data_generator/     # Dynamic test data creation
│   │   │   ├── generate_organizations.py  # Organization test data
│   │   │   ├── generate_restaurants.py    # Restaurant configurations
│   │   │   ├── generate_users.py          # User accounts and roles
│   │   │   ├── generate_menu_data.py      # Menu categories and items
│   │   │   └── generate_all.py            # Run all data generators
│   │   ├── test_read_operations/      # GET endpoint comprehensive testing
│   │   │   ├── test_api_health.py         # Health and connectivity tests
│   │   │   ├── test_menu_reads.py         # Menu data retrieval tests
│   │   │   ├── test_restaurant_reads.py   # Restaurant data access tests
│   │   │   ├── test_auth_reads.py         # Authentication flow tests
│   │   │   └── run_all_read_tests.py      # Execute all read tests
│   │   ├── test_create_operations/    # POST endpoint testing
│   │   │   ├── test_menu_creation.py      # Menu item and category creation
│   │   │   ├── test_user_creation.py      # User account creation
│   │   │   ├── test_restaurant_setup.py   # Restaurant onboarding
│   │   │   └── run_all_create_tests.py    # Execute all creation tests
│   │   ├── test_update_operations/    # PUT/PATCH endpoint testing
│   │   │   ├── test_menu_updates.py       # Menu modification workflows
│   │   │   ├── test_user_updates.py       # User profile and role updates
│   │   │   ├── test_restaurant_updates.py # Restaurant settings updates
│   │   │   └── run_all_update_tests.py    # Execute all update tests
│   │   ├── test_delete_operations/    # DELETE endpoint testing (⚠️ Destructive)
│   │   │   ├── test_safe_deletes.py       # Constraint and safety validation
│   │   │   ├── test_menu_deletes.py       # Menu item removal workflows
│   │   │   ├── test_cascade_deletes.py    # Foreign key cascade testing
│   │   │   └── run_all_delete_tests.py    # Execute all deletion tests
│   │   ├── test_business_workflows/   # End-to-end business process testing
│   │   │   ├── test_restaurant_onboarding.py # Complete setup workflow
│   │   │   ├── test_menu_management.py       # Full menu lifecycle
│   │   │   ├── test_multi_tenant_isolation.py # Tenant separation verification
│   │   │   └── test_user_role_workflows.py    # Permission and access testing
│   │   └── run_comprehensive_tests.py # Master test orchestrator
│   ├── unit/                          # Unit tests for individual components
│   ├── integration/                   # Integration tests
│   └── load/                         # Performance and load testing
```

### **Running the Comprehensive Test Suite**

#### **Prerequisites**
```bash
# Ensure API server is running
uv run uvicorn app.main:app --reload --port 8000

# Ensure database is migrated
uv run alembic upgrade head

# Verify API health
curl http://localhost:8000/health
```

#### **Full Test Suite Execution**
```bash
# Run complete comprehensive testing (includes all operations)
cd tests/api_tester
python run_comprehensive_tests.py full

# Output includes:
# ✅ Sample data generation
# ✅ API health and connectivity verification
# ✅ Authentication and authorization testing
# ✅ CRUD operations validation
# ✅ Business workflow verification
# ✅ Multi-tenant isolation confirmation
# ✅ Performance and response time analysis
```

#### **Individual Test Categories**

**1. Generate Fresh Test Data**
```bash
python run_comprehensive_tests.py generate

# Creates realistic test data:
# • 3 organizations (independent, chain, franchise)
# • 8 restaurants across organizations
# • 25 users with various roles (admin, manager, staff)
# • 50+ menu categories and 200+ menu items
# • Proper tenant isolation validation
```

**2. API Health and Connectivity**
```bash
python run_comprehensive_tests.py health

# Validates:
# • API server connectivity and response times
# • Database connection health
# • Authentication endpoint functionality
# • JWT token generation and validation
# • Role-based access control verification
```

**3. Read Operations Testing**
```bash
python run_comprehensive_tests.py read

# Comprehensive GET endpoint testing:
# • Menu data retrieval with pagination
# • Restaurant information access
# • User profile and role verification
# • Search and filtering functionality
# • Multi-tenant data isolation confirmation
```

**4. Create Operations Testing**
```bash
python run_comprehensive_tests.py create

# POST endpoint validation:
# • Menu category and item creation
# • User account registration workflows
# • Restaurant onboarding processes
# • Data validation and constraint checking
# • Multi-tenant context enforcement
```

**5. Update Operations Testing**
```bash
python run_comprehensive_tests.py update

# PUT/PATCH endpoint testing:
# • Menu item price and availability updates
# • User role and profile modifications
# • Restaurant settings and configuration changes
# • Partial update validation
# • Optimistic locking and concurrency handling
```

**6. Delete Operations Testing** ⚠️ **Destructive**
```bash
python run_comprehensive_tests.py delete --confirm-deletes

# DELETE endpoint validation:
# • Safe deletion with constraint checking
# • Cascade deletion behavior verification
# • Soft delete vs hard delete testing
# • Foreign key relationship preservation
# • Multi-tenant deletion isolation
```

**7. Business Workflow Testing**
```bash
python run_comprehensive_tests.py workflows

# End-to-end process validation:
# • Complete restaurant setup and onboarding
# • Menu management lifecycle (create → update → publish)
# • User registration and role assignment workflows
# • Multi-tenant organization management
# • Cross-tenant isolation and security verification
```

### **Test Output and Reporting**

Each test provides **detailed output** including:
```
==================================================
🍽️  RMS API Test: Menu Item Creation
Operation: Create Spicy Margherita Pizza
Endpoint: POST /api/v1/menu/items
Status Code: 201 Created
Response Time: 145ms
Tenant Context: pizzapalace-main (organization: pizzapalace)
--------------------------------------------------
Request Payload:
{
  "name": "Spicy Margherita Pizza",
  "description": "Classic margherita with jalapeños",
  "price": 16.99,
  "category_id": "cat_pizza_123",
  "is_available": true
}
--------------------------------------------------
Response Data:
{
  "id": "item_456789",
  "name": "Spicy Margherita Pizza",
  "price": 16.99,
  "organization_id": "org_pizzapalace",
  "restaurant_id": "rest_pizzapalace_main",
  "created_at": "2024-08-17T10:30:45Z"
}
✅ SUCCESS: Menu item created with proper tenant isolation
==================================================
```

### **Performance and Load Testing**

```bash
# Performance benchmarking
python run_comprehensive_tests.py performance

# Load testing (requires locust)
pip install locust
locust -f tests/load/restaurant_load_test.py --host=http://localhost:8000
```

### **Test Configuration and Customization**

**Authentication Setup** (`tests/api_tester/shared/auth.py`):
```python
# Default test credentials
TEST_API_BASE_URL = "http://localhost:8000"
TEST_ADMIN_EMAIL = "admin@testrestaurant.com"
TEST_ADMIN_PASSWORD = "secure_test_password"

# Automatic JWT token management
# Role-based access testing
# Multi-tenant context switching
```

**Custom Test Data** (`tests/api_tester/shared/fixtures.py`):
```python
# Realistic restaurant test data
# • Different cuisine types (Italian, Mexican, Asian, American)
# • Various restaurant sizes and configurations
# • Complex menu hierarchies with modifiers
# • Multi-tenant organization structures
```

### **API Testing Best Practices**

1. **Always run read tests first** to verify basic API functionality
2. **Generate fresh sample data** before comprehensive testing
3. **Review test output** for performance bottlenecks or unexpected behavior
4. **Use delete tests cautiously** and only with dedicated test data
5. **Run tests in sequence** (generate → health → read → create → update → delete)
6. **Monitor response times** and database performance during testing
7. **Validate multi-tenant isolation** in every test scenario

### **Continuous Integration Integration**

```yaml
# .github/workflows/comprehensive-testing.yml
name: RMS Comprehensive API Testing

on: [push, pull_request]

jobs:
  api-testing:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: rms_test
          POSTGRES_USER: rms_test_user
          POSTGRES_PASSWORD: rms_test_pass
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
        
      - name: Install dependencies
        run: uv sync
        
      - name: Run migrations
        run: uv run alembic upgrade head
        
      - name: Start API server
        run: uv run uvicorn app.main:app --port 8000 &
        
      - name: Wait for API
        run: sleep 10
        
      - name: Run comprehensive API tests
        run: |
          cd tests/api_tester
          python run_comprehensive_tests.py full
```

---

## 🏗️ Architecture & Technology Stack

### **Backend Technologies**
- **FastAPI 0.104+**: Modern async Python web framework
- **SQLModel 0.0.8+**: Type-safe ORM with Pydantic integration
- **PostgreSQL 15+**: Primary database with JSON and UUID support
- **Alembic**: Database migrations and schema management
- **astral/uv**: Modern Python package and project management
- **JWT Authentication**: Secure token-based authentication
- **pytest**: Comprehensive testing framework

### **Key Architectural Decisions**

#### **1. Multi-Tenant from Day 1**
```sql
-- Every table includes organization_id for tenant isolation
CREATE TABLE menu_items (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    -- ... other fields
);

-- Row Level Security (RLS) prepared for Phase 4 activation
CREATE POLICY menu_items_isolation ON menu_items
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
```

#### **2. UUID Primary Keys**
- **Security**: No sequential ID enumeration attacks
- **Scalability**: Distributed system compatibility
- **Integration**: External system integration friendly

#### **3. Domain-Driven Design (DDD)**
```python
# Clear domain boundaries
app/
├── modules/
│   ├── auth/           # Authentication & authorization
│   ├── menu/           # Menu management domain
│   ├── restaurant/     # Restaurant configuration
│   └── users/          # User management
└── shared/             # Cross-cutting concerns
    ├── database/       # Database infrastructure
    ├── security/       # Security utilities
    └── config/         # Configuration management
```

#### **4. API-First Design**
- **OpenAPI/Swagger**: Auto-generated documentation
- **Type Safety**: Pydantic models for request/response validation
- **Async/Await**: High-performance async request handling
- **RESTful**: Standard HTTP methods and status codes

---

## 🗃️ Database Schema & Multi-Tenancy

### **Tenant Hierarchy**
```
🏢 Organization (Tenant Root)
  ├── 📍 Restaurants (Multiple locations)
  ├── 👥 Users (Org-wide or restaurant-specific)
  └── 📊 All Data (Isolated by organization_id)
      ├── 🍽️  Menu Categories & Items
      ├── 🪑 Tables & Reservations (Phase 2)
      ├── 📱 Orders & Payments (Phase 3)
      └── 📈 Analytics & Reports
```

### **Core Tables (Phase 1)**

| Table | Purpose | Multi-Tenant Fields |
|-------|---------|--------------------|
| `organizations` | Tenant root entities | `id` (primary) |
| `restaurants` | Individual restaurant locations | `organization_id` |
| `users` | User accounts with roles | `organization_id`, `restaurant_id` |
| `menu_categories` | Menu organization | `organization_id`, `restaurant_id` |
| `menu_items` | Individual menu items | `organization_id`, `restaurant_id` |
| `modifiers` | Menu item add-ons | `organization_id`, `restaurant_id` |

### **Data Isolation Strategy**
- **Phase 1-3**: Application-level tenant filtering (BYPASSRLS granted)
- **Phase 4**: Database-level Row Level Security (RLS) activation
- **Zero Migration**: All tables designed for RLS from day 1

### **Sample Multi-Tenant Data**
```json
{
  "organization": {
    "id": "org_pizzapalace_001",
    "name": "Pizza Palace Chain",
    "type": "chain",
    "subscription_tier": "professional"
  },
  "restaurants": [
    {
      "id": "rest_pp_downtown",
      "name": "Pizza Palace Downtown",
      "organization_id": "org_pizzapalace_001"
    },
    {
      "id": "rest_pp_mall", 
      "name": "Pizza Palace Mall Location",
      "organization_id": "org_pizzapalace_001"
    }
  ]
}
```

---

## 👥 User Roles & Permissions

### **Role Hierarchy**

| Role | Scope | Permissions | Use Case |
|------|-------|-------------|----------|
| **Super Admin** | Platform | System management, approve/reject new restaurants | Platform maintenance, onboarding new clients |
| **Org Admin** | Organization | All restaurants in organization | Chain/franchise owner |
| **Restaurant Manager** | Restaurant | Single restaurant management | Restaurant manager |
| **Staff** | Restaurant | Limited operations (menu viewing, order processing) | Waitstaff, kitchen |
| **Customer** | Public | Menu viewing, order placement | End customers |

### **Permission Matrix**

| Action | Super Admin | Org Admin | Manager | Staff | Customer |
|--------|-------------|-----------|---------|-------|----------|
| Approve/Reject Restaurants | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create organization | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage restaurant settings | ✅ | ✅ | ✅ | ❌ | ❌ |
| Create/update menu items | ✅ | ✅ | ✅ | ❌ | ❌ |
| View menu items | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manage users | ✅ | ✅ (org scope) | ✅ (restaurant scope) | ❌ | ❌ |
| Process orders | ✅ | ✅ | ✅ | ✅ | ❌ |
| View analytics | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## 🚦 API Endpoints Overview

### **Phase 1: Foundation & Menu Management (30 endpoints)**

#### **Authentication & Users** (7 endpoints)
- `POST /auth/login` - User authentication
- `POST /auth/logout` - Session termination
- `POST /auth/refresh` - Token refresh
- `GET /auth/me` - Current user profile
- `GET /users` - List users (filtered by permissions)
- `POST /users` - Create user account
- `PUT /users/{id}` - Update user profile

#### **Restaurant Setup** (1 endpoint)
- `POST /setup` - Submit a new restaurant application

#### **Platform Management** (3 endpoints)
- `GET /platform/applications` - List pending restaurant applications
- `POST /platform/applications/{org_id}/approve` - Approve a restaurant application
- `POST /platform/applications/{org_id}/reject` - Reject a restaurant application

#### **Menu Categories** (5 endpoints)
- `GET /menu/categories` - List categories
- `POST /menu/categories` - Create category
- `GET /menu/categories/{id}` - Get category details
- `PUT /menu/categories/{id}` - Update category
- `DELETE /menu/categories/{id}` - Delete category

#### **Menu Items** (8 endpoints)
- `GET /menu/items` - List menu items with filtering
- `POST /menu/items` - Create menu item
- `GET /menu/items/{id}` - Get item details
- `PUT /menu/items/{id}` - Update menu item
- `DELETE /menu/items/{id}` - Delete menu item
- `PUT /menu/items/{id}/availability` - Toggle availability
- `POST /menu/items/{id}/image` - Upload item image
- `GET /menu/public` - Public menu for customers

#### **Menu Modifiers** (6 endpoints)
- `POST /menu/modifiers` - Create a new modifier
- `GET /menu/modifiers` - List all modifiers
- `PUT /menu/modifiers/{id}` - Update a modifier
- `DELETE /menu/modifiers/{id}` - Delete a modifier
- `POST /menu/items/{item_id}/modifiers` - Assign modifier to an item
- `DELETE /menu/items/{item_id}/modifiers/{modifier_id}` - Remove modifier from an item

### **Future Phases Preview**
- **Phase 2**: +35 endpoints (Tables & Reservations)
- **Phase 3**: +45 endpoints (Orders & Kitchen Operations)
- **Phase 4**: +25 endpoints (Multi-tenant platform administration)
- **Phase 5**: +30 endpoints (Advanced features & integrations)

**Total System**: ~160 comprehensive API endpoints

---

## 🧪 Development & Testing

### **Local Development Environment**
```bash
# Complete development setup
git clone <repository-url>
cd rms

# Install astral uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment with dependencies
uv sync

# Start PostgreSQL database
docker-compose up -d postgres

# Run database migrations
uv run alembic upgrade head

# Load realistic sample data
uv run python scripts/load_fixtures.py

# Start development server with auto-reload
uv run uvicorn app.main:app --reload --port 8000

# In another terminal: run comprehensive tests
cd tests/api_tester
python run_comprehensive_tests.py full
```

### **Testing Strategy**

#### **1. Unit Tests** (`tests/unit/`)
```bash
# Test individual components in isolation
uv run pytest tests/unit/ -v

# Coverage report
uv run pytest tests/unit/ --cov=app --cov-report=html
```

#### **2. Integration Tests** (`tests/integration/`)
```bash
# Test API endpoints and database integration
uv run pytest tests/integration/ -v
```

#### **3. Comprehensive API Testing** (`tests/api_tester/`)
```bash
# Full business workflow testing
cd tests/api_tester
python run_comprehensive_tests.py full
```

#### **4. Load Testing** (`tests/load/`)
```bash
# Performance and scalability testing
uv run locust -f tests/load/restaurant_load_test.py
```

### **Database Management**

#### **Migrations**
```bash
# Create new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

#### **Database Verification**
```bash
# Verify database schema and relationships
./scripts/verify_database.sh

# Sample output:
# ✅ Database connection successful
# ✅ Migration at head revision: 945555963252
# ✅ 6 core tables created
# ✅ 10 foreign key relationships established
# ✅ Multi-tenant indexes in place
```

### **Sample Data & Fixtures**

```bash
# Load comprehensive sample data
uv run python scripts/load_fixtures.py

# Sample data includes:
# • 3 different organization types (independent, chain, franchise)
# • 8 restaurants with varied cuisines and settings
# • 25 users across all roles and permission levels
# • 50+ menu categories organized by cuisine type
# • 200+ menu items with realistic prices and descriptions
# • Proper multi-tenant data isolation demonstration
```

---

## 🚀 Deployment & Production

### **Docker Production Setup**
```bash
# Build production image
docker build -t rms-api:latest .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d

# Environment variables for production
DATABASE_URL=postgresql://user:pass@db:5432/rms_prod
JWT_SECRET_KEY=your-secure-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### **Health Monitoring**
```bash
# API health endpoint
curl http://localhost:8000/health

# Database connection health
curl http://localhost:8000/health/db

# Detailed system status
curl http://localhost:8000/health/detailed
```

---

## 📚 Documentation

### **API Documentation**
- **Interactive Swagger UI**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI JSON Schema**: http://localhost:8000/openapi.json

### **Project Documentation**
- [`DEVELOPMENT_PHASES.md`](DEVELOPMENT_PHASES.md) - Complete 5-phase development roadmap
- [`API_PLANS.md`](API_PLANS.md) - Comprehensive API specifications and examples
- [`DATABASE_SETUP.md`](DATABASE_SETUP.md) - Database schema and multi-tenant architecture
- [`SHORTCOMINGS.md`](SHORTCOMINGS.md) - Known limitations and future improvements

### **Testing Documentation**
- [`tests/api_tester/README.md`](tests/api_tester/README.md) - Comprehensive API testing guide
- Unit test coverage reports in `htmlcov/`
- Integration test documentation

---

## 🤝 Contributing

### **Development Workflow**
1. **Fork the repository** and create a feature branch
2. **Follow the architecture patterns** established in existing modules
3. **Write comprehensive tests** for new functionality
4. **Run the full test suite** including API tests
5. **Update documentation** for API changes
6. **Submit a pull request** with detailed description

### **Code Standards**
- **Type Hints**: All functions must include type annotations
- **Pydantic Models**: Use for all API request/response validation
- **Async/Await**: Prefer async patterns for database and I/O operations
- **Multi-Tenant**: All new features must include tenant isolation
- **Testing**: Minimum 80% test coverage for new code

### **Architecture Guidelines**
- **Domain Separation**: Keep business domains in separate modules
- **Database Design**: Include `organization_id` in all tables
- **API Design**: Follow RESTful conventions and OpenAPI standards
- **Security**: Implement proper authentication and authorization

---

## 📈 Roadmap & Future Phases

### **Current Status: Phase 1 Complete** ✅
- Multi-tenant foundation and menu management
- Comprehensive API testing framework
- Production-ready authentication and authorization

### **Upcoming Development**

#### **Phase 2: Table & Reservation Management** (8-10 weeks)
- Complete table management with floor plan configuration
- Advanced reservation system with customer preferences
- Public customer reservation interface
- Waitlist management and optimization

#### **Phase 3: Order Management & Kitchen Operations** (10-12 weeks)
- Complete order lifecycle management
- Kitchen display system with real-time updates
- QR code table ordering without customer accounts
- Multi-person ordering with split payment capabilities

#### **Phase 4: Multi-Tenant Architecture** (10-12 weeks)
- Full multi-tenant platform activation
- Organization and restaurant management
- SaaS subscription and billing system
- Platform administration dashboard

#### **Phase 5: Advanced Features & Integrations** (12-14 weeks)
- Delivery partner integrations (Uber Eats, DoorDash, Grubhub)
- POS system integrations (Square, Toast)
- Advanced inventory and staff management
- Customer loyalty programs and analytics

**Total Development Timeline**: ~46-56 weeks (~11-14 months)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **ABC API Modular Project**: Inspiration for comprehensive API testing framework
- **FastAPI Community**: For the excellent modern Python web framework
- **SQLModel**: For bridging the gap between Pydantic and SQLAlchemy
- **astral/uv**: For modern Python package management

---

*Built with ❤️ for the restaurant industry. From single restaurants to enterprise franchise operations.*
