# RMS Comprehensive API Tester

A complete testing suite for the Restaurant Management System that includes sample data generation and comprehensive CRUD operation testing. Inspired by the ABC API Modular project's api-tester framework.

## Structure

```
tests/api_tester/
├── shared/                          # Shared utilities and authentication
│   ├── auth.py                     # JWT authentication handling
│   ├── utils.py                    # API testing utilities
│   └── fixtures.py                 # Test data generation helpers
├── sample_data_generator/           # Sample data generation scripts
│   ├── generate_organizations.py   # Organization test data
│   ├── generate_restaurants.py     # Restaurant configurations
│   ├── generate_users.py           # User accounts and roles
│   ├── generate_menu_data.py       # Menu categories and items
│   └── generate_all.py             # Run all generators
├── test_read_operations/            # Read operation tests
│   ├── test_api_health.py          # API health and connectivity tests
│   ├── test_menu_reads.py          # Menu data retrieval tests
│   ├── test_restaurant_reads.py    # Restaurant data access tests
│   ├── test_auth_reads.py          # Authentication flow tests
│   └── run_all_read_tests.py       # Run all read tests
├── test_create_operations/          # Create operation tests
│   ├── test_menu_creation.py       # Menu item and category creation
│   ├── test_user_creation.py       # User account creation
│   ├── test_restaurant_setup.py    # Restaurant onboarding
│   └── run_all_create_tests.py     # Run all creation tests
├── test_update_operations/          # Update operation tests
│   ├── test_menu_updates.py        # Menu modification workflows
│   ├── test_user_updates.py        # User profile and role updates
│   ├── test_restaurant_updates.py  # Restaurant settings updates
│   └── run_all_update_tests.py     # Run all update tests
├── test_delete_operations/          # Delete operation tests
│   ├── test_safe_deletes.py        # Constraint and safety validation
│   ├── test_menu_deletes.py        # Menu item removal workflows
│   ├── test_cascade_deletes.py     # Foreign key cascade testing
│   └── run_all_delete_tests.py     # Run all deletion tests
├── test_business_workflows/         # End-to-end business process testing
│   ├── test_restaurant_onboarding.py     # Complete setup workflow
│   ├── test_menu_management.py           # Full menu lifecycle
│   ├── test_multi_tenant_isolation.py    # Tenant separation verification
│   └── test_user_role_workflows.py       # Permission and access testing
├── run_comprehensive_tests.py      # Master test orchestrator
└── README.md                       # This file
```

## Prerequisites

1. **Server Running**: Make sure the RMS API server is running:
   ```bash
   cd /Users/bi_sapkota/personal_projects/rms
   uv run uvicorn app.main:app --reload --port 8000
   ```

2. **Database Ready**: Ensure PostgreSQL is running and migrations are applied:
   ```bash
   docker-compose up -d postgres
   uv run alembic upgrade head
   ```

3. **Sample Data**: Load basic sample data for testing:
   ```bash
   uv run python scripts/load_fixtures.py
   ```

## Quick Start

### Run Everything
```bash
cd tests/api_tester
python run_comprehensive_tests.py full
```

### Individual Test Categories

#### Generate Sample Data
```bash
python run_comprehensive_tests.py generate
```

#### Test API Health & Connectivity
```bash
python run_comprehensive_tests.py health
```

#### Test Read Operations
```bash
python run_comprehensive_tests.py read
```

#### Test Create Operations
```bash
python run_comprehensive_tests.py create
```

#### Test Update Operations
```bash
python run_comprehensive_tests.py update
```

#### Test Delete Operations (⚠️ Destructive)
```bash
python run_comprehensive_tests.py delete --confirm-deletes
```

#### Test Business Workflows
```bash
python run_comprehensive_tests.py workflows
```

## Detailed Usage

### Sample Data Generator

Located in `sample_data_generator/`, contains all the RMS-specific data generation scripts:
- `generate_organizations.py` - Create test organizations (independent, chain, franchise)
- `generate_restaurants.py` - Create restaurants with varied configurations
- `generate_users.py` - Create user accounts with different roles
- `generate_menu_data.py` - Create menu categories and items
- `generate_all.py` - Run all generators in proper sequence

### Read Logic Tests

Tests all GET endpoints and data retrieval:
- **API Health**: Connectivity, authentication, response times
- **Menu Reads**: List menu items, categories, search, pagination
- **Restaurant Reads**: Restaurant data access, settings, multi-tenant isolation
- **Auth Reads**: User profiles, role verification, permission testing

```bash
cd test_read_operations
python run_all_read_tests.py
```

### Create Logic Tests

Tests POST endpoints and data creation:
- **Menu Creation**: Categories, items, modifiers with proper validation
- **User Creation**: Account registration with role assignment
- **Restaurant Setup**: Complete onboarding workflow testing

```bash
cd test_create_operations
python run_all_create_tests.py
```

### Update Logic Tests

Tests PUT/PATCH endpoints and data modifications:
- **Menu Updates**: Price changes, availability toggles, description updates
- **User Updates**: Profile modifications, role changes, permission updates
- **Restaurant Updates**: Settings changes, configuration modifications

```bash
cd test_update_operations
python run_all_update_tests.py
```

### Delete Logic Tests

Tests DELETE endpoints and constraint handling:
- **Safe Deletes**: Constraint validation, foreign key relationship preservation
- **Menu Deletes**: Category and item deletion with cascade behavior
- **Cascade Deletes**: Complex relationship deletion testing

⚠️ **WARNING**: Delete tests will remove data from your database!

```bash
cd test_delete_operations
python run_all_delete_tests.py
```

### Business Workflow Tests

Tests complete business processes end-to-end:
- **Restaurant Onboarding**: Complete setup from organization to menu
- **Menu Management**: Full lifecycle from creation to deletion
- **Multi-Tenant Isolation**: Verify proper data separation
- **User Role Workflows**: Permission and access control testing

```bash
cd test_business_workflows
python test_restaurant_onboarding.py
```

## Test Output

Each test provides detailed output including:
- HTTP status codes and response times
- Request/response details with proper formatting
- Multi-tenant context verification
- Data validation results
- Success/failure indicators with clear messaging

Example output:
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

## Configuration

### Authentication
Default credentials are configured in `shared/auth.py`:
- Base URL: `http://localhost:8000`
- Test Admin Email: `admin@testrestaurant.com`
- Test Admin Password: `secure_test_password`
- JWT token automatic management
- Multi-tenant context switching

### Customization
You can modify the test behavior by editing:
- `shared/utils.py` - API request utilities and helpers
- `shared/fixtures.py` - Test data generation and fixtures
- Individual test files - Test cases and scenarios
- `run_comprehensive_tests.py` - Main test orchestration

## Safety Features

1. **Test Data Isolation**: Many tests create their own test data to avoid affecting existing data
2. **Multi-Tenant Validation**: All tests verify proper tenant context and data isolation
3. **Constraint Validation**: Tests verify that the API properly handles constraint violations
4. **Confirmation Required**: Delete tests require explicit confirmation flags
5. **Error Handling**: Comprehensive error handling and reporting with context
6. **Transaction Rollback**: Database transactions properly rolled back on test failures

## RMS-Specific Features

### Multi-Tenant Testing
- **Organization Isolation**: Verify data separation between organizations
- **Restaurant Scoping**: Test restaurant-specific data access
- **Role-Based Access**: Validate permission enforcement across tenant boundaries
- **Context Switching**: Test switching between different tenant contexts

### Restaurant Domain Testing
- **Menu Management**: Complete menu lifecycle testing
- **User Roles**: Test admin, manager, staff, and customer role permissions
- **Restaurant Configuration**: Test settings, preferences, and configuration management
- **Data Relationships**: Test complex foreign key relationships and constraints

### Business Workflow Integration
- **Complete Onboarding**: Test full restaurant setup process
- **Menu Publication**: Test menu creation, modification, and publication workflows
- **User Management**: Test user creation, role assignment, and permission management
- **Cross-Module Integration**: Test interactions between different business domains

## Performance Testing

### Response Time Monitoring
```bash
# Run tests with performance metrics
python run_comprehensive_tests.py full --performance
```

### Load Testing Integration
```bash
# Install locust for load testing
uv add locust

# Run load tests
locust -f ../load/restaurant_load_test.py --host=http://localhost:8000
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Make sure the RMS API server is running on port 8000
   - Check if PostgreSQL database is running
   - Verify database migrations are applied

2. **Authentication Failed**
   - Verify test admin user exists with correct credentials
   - Check if JWT authentication is working properly
   - Ensure proper tenant context is set

3. **Multi-Tenant Isolation Errors**
   - Verify organization_id is properly set in all requests
   - Check that test data includes proper tenant relationships
   - Ensure RLS policies are not interfering (should be bypassed in Phase 1)

4. **Import Errors**
   - Make sure you're running from the correct directory
   - Verify all required files are present
   - Check Python path and virtual environment

### Getting Help

1. Check the RMS API documentation at `http://localhost:8000/docs`
2. Review server logs for backend errors
3. Use individual test scripts for more focused debugging
4. Check the main README.md for comprehensive setup instructions

## Integration with RMS Architecture

The RMS api-tester follows the same architectural principles as the main application:

### Domain-Driven Organization
Tests are organized by business domain (menu, users, restaurants) rather than technical concerns, matching the application structure.

### Multi-Tenant from Day 1
All tests include tenant context validation and isolation verification, preparing for Phase 4 multi-tenant activation.

### Type Safety
Tests use the same Pydantic models as the application for request/response validation and type safety.

### Async/Await Support
Test utilities support async operations for performance and consistency with the FastAPI application.

## Best Practices

1. **Always run health tests first** to verify basic API functionality
2. **Generate fresh sample data** before running comprehensive test suites
3. **Review test output carefully** for any unexpected behavior or performance issues
4. **Use delete tests cautiously** and only with dedicated test databases
5. **Run tests in logical sequence** (health → read → create → update → delete → workflows)
6. **Monitor response times** and database performance during testing
7. **Validate multi-tenant isolation** in every test scenario
8. **Keep test data realistic** but clearly distinguishable from production data

## Future Enhancements

As the RMS evolves through its development phases, the api-tester will expand to include:

### Phase 2: Table & Reservation Testing
- Table management and floor plan configuration tests
- Reservation creation, modification, and cancellation workflows
- Availability checking and optimization testing
- Waitlist management and notification testing

### Phase 3: Order & Kitchen Testing
- Complete order lifecycle testing (placement → fulfillment)
- Kitchen display system and workflow testing
- QR code ordering and multi-person session testing
- Payment processing and split bill testing

### Phase 4: Multi-Tenant Platform Testing
- Full multi-tenant activation and isolation testing
- Organization and restaurant management testing
- Platform administration and billing testing
- Cross-tenant analytics and reporting testing

### Phase 5: Integration Testing
- Delivery partner integration testing (Uber Eats, DoorDash, Grubhub)
- POS system integration testing (Square, Toast)
- Advanced feature testing (inventory, staff management, loyalty programs)
- Performance and scalability testing at enterprise scale

The api-tester framework provides a solid foundation for testing the RMS throughout its entire development lifecycle, ensuring quality and reliability at every phase.