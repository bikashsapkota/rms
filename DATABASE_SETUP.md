# Database Setup - Restaurant Management System

## ✅ Phase 1 Multi-Tenant Database Schema

The database schema has been successfully created and migrated using Alembic. The implementation follows the **"multi-tenant from day 1"** strategy specified in the Phase 1 requirements.

### 🏗️ Schema Overview

#### **Core Tables:**

1. **`organizations`** - Multi-tenant foundation
   - Primary key: `id` (UUID)
   - Fields: `name`, `organization_type`, `subscription_tier`, `billing_email`
   - Supports: `independent`, `chain`, `franchise` types
   - Tiers: `basic`, `professional`, `enterprise`

2. **`restaurants`** - Belongs to organizations
   - Primary key: `id` (UUID)
   - Foreign key: `organization_id` → `organizations.id`
   - Fields: `name`, `address` (JSON), `phone`, `email`, `settings` (JSON)

3. **`users`** - Multi-tenant user management
   - Primary key: `id` (UUID)
   - Foreign keys: `organization_id` → `organizations.id`, `restaurant_id` → `restaurants.id`
   - Fields: `email` (unique), `full_name`, `role`, `password_hash`
   - Roles: `admin`, `manager`, `staff`

4. **`menu_categories`** - Restaurant-specific menu organization
   - Primary key: `id` (UUID)
   - Foreign keys: `organization_id`, `restaurant_id`
   - Fields: `name`, `description`, `sort_order`

5. **`menu_items`** - Menu items with categories
   - Primary key: `id` (UUID)
   - Foreign keys: `organization_id`, `restaurant_id`, `category_id`
   - Fields: `name`, `description`, `price`, `is_available`, `image_url`

6. **`modifiers`** - Menu item modifiers/add-ons
   - Primary key: `id` (UUID)
   - Foreign keys: `organization_id`, `restaurant_id`
   - Fields: `name`, `type`, `price_adjustment`

### 🔑 Multi-Tenant Architecture

#### **Phase 1 Strategy: Single-Tenant UX with Multi-Tenant Foundation**
- **All tables** include `organization_id` for tenant isolation
- **Restaurant-specific tables** include both `organization_id` + `restaurant_id`
- **Zero-migration path** to full multi-tenancy in Phase 4
- **Row Level Security (RLS)** policies ready but not enforced yet

#### **Tenant Hierarchy:**
```
Organization (Tenant Root)
  ├── Restaurants (Multiple per organization)
  ├── Users (Organization or Restaurant scoped)
  └── Restaurant Data
      ├── Menu Categories
      ├── Menu Items
      └── Modifiers
```

### 🗂️ Database Features

#### **Data Types:**
- **Primary Keys**: UUID v4 (using `uuid_generate_v4()`)
- **Timestamps**: `created_at`, `updated_at` with auto-update triggers
- **JSON Fields**: `address`, `settings` for flexible schema
- **Decimal**: `NUMERIC(10,2)` for prices
- **Foreign Keys**: Proper referential integrity

#### **Indexes:**
- All foreign key columns indexed for performance
- Email uniqueness constraint on users
- Organization/Restaurant composite indexes

#### **Extensions:**
- `uuid-ossp` for UUID generation
- `pg_trgm` for full-text search (future use)

### 🚀 Migration Management

#### **Current Status:**
```bash
# Check migration status
uv run alembic current

# View migration history  
uv run alembic history

# Upgrade to latest
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

#### **Migration File:**
- **File**: `alembic/versions/945555963252_phase_1_initial_multi_tenant_schema_.py`
- **Status**: ✅ Applied successfully
- **Tables Created**: 6 core tables + `alembic_version`

### 🔧 Development Setup

#### **Prerequisites:**
```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Wait for startup
sleep 10

# Verify connection
docker exec rms_postgres psql -U rms_user -d rms_dev -c "SELECT version();"
```

#### **Run Migrations:**
```bash
# Apply all migrations
uv run alembic upgrade head

# Verify schema
./scripts/verify_database.sh
```

#### **Database Connection:**
- **Host**: localhost:5432 (Docker)
- **Database**: rms_dev  
- **User**: rms_user
- **Password**: rms_pass
- **URL**: `postgresql://rms_user:rms_pass@localhost:5432/rms_dev`

### 📊 Schema Verification

Run the verification script to ensure everything is working:

```bash
./scripts/verify_database.sh
```

**Expected Output:**
- ✅ Database connection successful
- ✅ Migration at head revision
- ✅ All 6 tables created
- ✅ 10 foreign key relationships established
- ✅ Proper UUID data types throughout

### 🎯 Phase 1 Compliance

#### **✅ Requirements Met:**
- [x] **Multi-tenant database design from day 1**
- [x] **Organizations** table for tenant isolation
- [x] **Restaurants** belonging to organizations  
- [x] **Users** with organization/restaurant scope
- [x] **Menu management** with full hierarchy
- [x] **Zero-migration path** to Phase 4 multi-tenancy
- [x] **UUID primary keys** throughout
- [x] **Proper foreign key relationships**
- [x] **Database indexes** for performance
- [x] **Alembic migrations** for schema management

#### **🚀 Ready for Phase 2:**
The database schema is fully prepared for Phase 2 features:
- **Table Management** (add tables to restaurants)
- **Reservation System** (add reservations linked to tables)
- **Customer Management** (add customer data)

#### **🏗️ Phase 4 Preparation:**
- **Row Level Security policies** can be activated
- **Tenant context switching** infrastructure ready
- **Multi-organization support** fully implemented
- **Scalable architecture** for thousands of tenants

---

## 📋 Summary

✅ **Phase 1 Database Status: COMPLETE**

The multi-tenant database foundation is successfully implemented and ready for the full Phase 1 API implementation. All requirements from the DEVELOPMENT_PHASES.md have been satisfied with proper Alembic migrations and PostgreSQL best practices.