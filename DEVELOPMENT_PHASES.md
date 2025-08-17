# Restaurant Management System (RMS) - Development Phases

## 🎯 Development Strategy Overview

This document outlines a **5-phase development approach** for the Restaurant Management System, starting with core single-restaurant functionality and gradually expanding to multi-tenant enterprise features. The phasing ensures **early value delivery** while building a scalable foundation.

**Core Philosophy**: Build for single restaurant first, but design database and architecture for multi-tenant from day one to avoid costly migrations.

---

## 📊 Phase Overview

| Phase | Duration | Core Focus | Business Value | Team Size |
|-------|----------|------------|----------------|-----------|
| **Phase 1** | 6-8 weeks | Foundation & Basic Menu | Infrastructure Setup | 4-5 developers |
| **Phase 2** | 8-10 weeks | Table & Reservation Management | Customer Experience | 5-6 developers |
| **Phase 3** | 10-12 weeks | Order Management & Kitchen Operations | Operational Efficiency | 6-8 developers |
| **Phase 4** | 10-12 weeks | Multi-Tenant Architecture | Scalability & Growth | 8-10 developers |
| **Phase 5** | 12-14 weeks | Advanced Features & Integrations | Market Differentiation | 10-12 developers |

**Total Timeline**: 46-56 weeks (~11-14 months)

---

## 🏗️ Phase 1: Foundation & Basic Menu (6-8 weeks)
*"Core infrastructure and menu management foundation"*

### **Sprint 1-2: Core Infrastructure (3-4 weeks)**

#### **Infrastructure & Architecture**
```python
# Core modules to implement
rms/
├── app/
│   ├── core/
│   │   ├── app.py                    # FastAPI app setup
│   │   └── deps.py                   # Basic dependencies
│   ├── shared/
│   │   ├── auth/deps.py              # Simple JWT auth
│   │   ├── config/settings.py       # Basic configuration
│   │   ├── database/database.py     # SQLAlchemy setup
│   │   ├── models/base.py           # Base models
│   │   └── security/security.py     # Password hashing
```

#### **Multi-Tenant Database Schema (Day 1 Design)**
```sql
-- Phase 1: Multi-tenant foundation from day one
-- Organization layer (even if unused initially)
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    organization_type VARCHAR(50) DEFAULT 'independent', -- 'franchise', 'chain', 'independent'
    subscription_tier VARCHAR(50) DEFAULT 'basic',
    billing_email VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Restaurants with organization context
CREATE TABLE restaurants (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    address JSONB,
    phone VARCHAR(20),
    email VARCHAR(255),
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Users with organization and restaurant context
CREATE TABLE users (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID REFERENCES restaurants(id), -- NULL for org-level users
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'staff', -- 'admin', 'manager', 'staff'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for multi-tenant performance
CREATE INDEX idx_restaurants_org_id ON restaurants(organization_id);
CREATE INDEX idx_users_org_id ON users(organization_id);
CREATE INDEX idx_users_restaurant_id ON users(restaurant_id);

-- Row Level Security (RLS) setup for tenant isolation
ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- RLS Policies (will be activated in Phase 4)
CREATE POLICY restaurants_isolation ON restaurants
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
    
CREATE POLICY users_isolation ON users
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
```

#### **APIs to Implement**
- **Restaurant Setup**: Basic restaurant configuration
- **User Authentication**: Login/logout with JWT
- **Health Checks**: System monitoring endpoints

### **Sprint 3: Basic Menu Management (3-4 weeks)**

#### **Menu Module Implementation**
```python
# app/modules/menu/
├── models/
│   ├── category.py      # Menu categories
│   ├── item.py          # Menu items  
│   └── modifier.py      # Basic modifiers
├── routes/
│   ├── category_routes.py
│   ├── item_routes.py
│   └── modifier_routes.py
├── services/
│   ├── category_service.py
│   └── item_service.py
```

#### **Multi-Tenant Menu Schema**
```sql
-- Menu categories with full multi-tenant support
CREATE TABLE menu_categories (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Menu items with organization and restaurant context
CREATE TABLE menu_items (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    category_id UUID REFERENCES menu_categories(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    is_available BOOLEAN DEFAULT true,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Modifiers with tenant context
CREATE TABLE modifiers (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50), -- 'size', 'addon', 'substitution'
    price_adjustment DECIMAL(10,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Multi-tenant indexes
CREATE INDEX idx_menu_categories_org_restaurant ON menu_categories(organization_id, restaurant_id);
CREATE INDEX idx_menu_items_org_restaurant ON menu_items(organization_id, restaurant_id);
CREATE INDEX idx_modifiers_org_restaurant ON modifiers(organization_id, restaurant_id);

-- RLS for menu tables
ALTER TABLE menu_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE modifiers ENABLE ROW LEVEL SECURITY;

CREATE POLICY menu_categories_isolation ON menu_categories
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
CREATE POLICY menu_items_isolation ON menu_items
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
CREATE POLICY modifiers_isolation ON modifiers
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
```

#### **Core APIs (30 endpoints)**

1. **Authentication & Users** (7 endpoints)
   - `POST /auth/login` - User login
   - `POST /auth/logout` - User logout
   - `POST /auth/refresh` - Refresh token
   - `GET /auth/me` - Current user info
   - `GET /users` - List restaurant users
   - `POST /users` - Create user
   - `PUT /users/{id}` - Update user

2. **Restaurant Setup** (1 endpoint)
   - `POST /setup` - Submit a new restaurant application

3. **Platform Management** (3 endpoints)
   - `GET /platform/applications` - List pending restaurant applications
   - `POST /platform/applications/{org_id}/approve` - Approve a restaurant application
   - `POST /platform/applications/{org_id}/reject` - Reject a restaurant application

4. **Menu Categories** (5 endpoints)
   - `GET /menu/categories` - List categories
   - `POST /menu/categories` - Create category
   - `GET /menu/categories/{id}` - Get category
   - `PUT /menu/categories/{id}` - Update category
   - `DELETE /menu/categories/{id}` - Delete category

5. **Menu Items** (8 endpoints)
   - `GET /menu/items` - List items with filters
   - `POST /menu/items` - Create item
   - `GET /menu/items/{id}` - Get item details
   - `PUT /menu/items/{id}` - Update item
   - `DELETE /menu/items/{id}` - Delete item
   - `PUT /menu/items/{id}/availability` - Toggle availability
   - `POST /menu/items/{id}/image` - Upload item image
   - `GET /menu/public` - Public menu for customers

6. **Menu Modifiers** (6 endpoints)
   - `POST /menu/modifiers` - Create a new modifier
   - `GET /menu/modifiers` - List all modifiers
   - `PUT /menu/modifiers/{id}` - Update a modifier
   - `DELETE /menu/modifiers/{id}` - Delete a modifier
   - `POST /menu/items/{item_id}/modifiers` - Assign modifier to an item
   - `DELETE /menu/items/{item_id}/modifiers/{modifier_id}` - Remove modifier from an item

### **Phase 1 Implementation Strategy**

#### **Multi-Tenant Database, Single-Tenant Interface**
```python
# Phase 1: All code designed for multi-tenant but simplified for single restaurant usage

# 1. Auto-create organization for each restaurant during setup
async def create_restaurant_setup(restaurant_data: RestaurantCreate):
    """Phase 1: Auto-create org + restaurant for simple setup"""
    organization = await create_organization(
        name=f"{restaurant_data.name} Organization",
        organization_type="independent"
    )
    
    restaurant = await create_restaurant(
        organization_id=organization.id,
        **restaurant_data.dict()
    )
    
    return restaurant

# 2. Tenant context middleware (inactive in Phase 1)
class TenantContextMiddleware:
    async def __call__(self, request: Request, call_next):
        # Phase 1: Single tenant context (hardcoded)
        current_org_id = get_user_organization_id(request)
        
        # Set tenant context for RLS (when activated in Phase 4)
        await set_tenant_context(current_org_id)
        
        response = await call_next(request)
        return response

# 3. All service methods designed for multi-tenant from day 1
class MenuService:
    async def create_category(
        self, 
        category_data: CategoryCreate,
        organization_id: UUID,  # Always required
        restaurant_id: UUID     # Always required
    ):
        """Multi-tenant design from day 1"""
        category = MenuCategory(
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            **category_data.dict()
        )
        return await self.repository.create(category)
```

#### **Database Migration Strategy**
```sql
-- Phase 1: Multi-tenant schema ready, single-tenant usage
-- All tables have organization_id/restaurant_id from day 1
-- RLS policies created but not enforced (bypassrls for Phase 1 users)

-- Grant bypass RLS for Phase 1 simplicity
GRANT BYPASSRLS TO restaurant_user_role;

-- Phase 4: Simply revoke bypass and activate policies
REVOKE BYPASSRLS FROM restaurant_user_role;
-- All RLS policies automatically active - zero migration needed!
```

### **Phase 1 Deliverables**
✅ **Multi-tenant database schema implemented from day 1**  
✅ **New restaurants can apply for setup via an application process**
✅ **Admin approval workflow for new restaurant applications**
✅ **Platform admin role for managing applications**
✅ **Staff can log in and manage basic operations (once approved)**
✅ **Menu categories and items can be created**  
✅ **Public menu API for customer viewing**  
✅ **Image upload for menu items**  
✅ **Menu item modifiers can be created, managed, and assigned**
✅ **Basic role-based access (admin, staff)**  
✅ **All code designed for multi-tenant (but used single-tenant)**  
✅ **Zero-migration path to multi-tenant in Phase 4**

### **Testing Strategy**
- **Unit Tests**: 80%+ coverage for services
- **Integration Tests**: API endpoint testing
- **Manual Testing**: Complete menu management workflow
- **Performance**: Single restaurant load testing

---

## 📅 Phase 2: Table & Reservation Management (8-10 weeks)
*"Complete reservation system - the most important customer-facing feature"*

### **Sprint 4-5: Table Management Foundation (4 weeks)**

#### **Table Module Implementation**
```python
# app/modules/tables/
├── models/
│   ├── table.py          # Restaurant tables
│   ├── reservation.py    # Customer reservations
│   └── table_status.py   # Real-time table status
├── routes/
│   ├── table_routes.py
│   ├── reservation_routes.py
│   └── availability_routes.py
├── services/
│   ├── table_service.py
│   ├── reservation_service.py
│   └── availability_service.py
```

#### **Multi-Tenant Tables & Reservations Schema**
```sql
-- Tables with full multi-tenant support
CREATE TABLE tables (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    table_number VARCHAR(10) NOT NULL,
    capacity INTEGER NOT NULL,
    location VARCHAR(100), -- 'main_dining', 'patio', 'private'
    status VARCHAR(50) DEFAULT 'available',
    coordinates JSONB, -- {x: 100, y: 200} for floor plan
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure unique table numbers per restaurant
    UNIQUE(restaurant_id, table_number)
);

-- Reservations with organization context
CREATE TABLE reservations (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    table_id UUID REFERENCES tables(id),
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20),
    customer_email VARCHAR(255),
    party_size INTEGER NOT NULL,
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    duration_minutes INTEGER DEFAULT 90,
    status VARCHAR(50) DEFAULT 'confirmed',
    special_requests TEXT,
    customer_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table status history with tenant context
CREATE TABLE table_status_log (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    table_id UUID NOT NULL REFERENCES tables(id),
    status VARCHAR(50) NOT NULL,
    changed_by UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Waitlist for reservations
CREATE TABLE reservation_waitlist (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20),
    customer_email VARCHAR(255),
    party_size INTEGER NOT NULL,
    preferred_date DATE,
    preferred_time TIME,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'notified', 'seated', 'cancelled'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Multi-tenant indexes for performance
CREATE INDEX idx_tables_org_restaurant ON tables(organization_id, restaurant_id);
CREATE INDEX idx_reservations_org_restaurant ON reservations(organization_id, restaurant_id);
CREATE INDEX idx_reservations_date_time ON reservations(restaurant_id, reservation_date, reservation_time);
CREATE INDEX idx_table_status_log_org ON table_status_log(organization_id);
CREATE INDEX idx_waitlist_org_restaurant ON reservation_waitlist(organization_id, restaurant_id);

-- Row Level Security for all tables
ALTER TABLE tables ENABLE ROW LEVEL SECURITY;
ALTER TABLE reservations ENABLE ROW LEVEL SECURITY;
ALTER TABLE table_status_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE reservation_waitlist ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY tables_isolation ON tables
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
CREATE POLICY reservations_isolation ON reservations
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
CREATE POLICY table_status_log_isolation ON table_status_log
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
CREATE POLICY waitlist_isolation ON reservation_waitlist
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
```

### **Sprint 6-7: Advanced Reservation Features (4-6 weeks)**

#### **Enhanced Reservation Features**
```python
# Advanced reservation capabilities
├── customer_preferences/
│   ├── seating_preferences.py  # Window, quiet section, etc.
│   ├── dietary_restrictions.py # Allergies, dietary needs
│   └── special_occasions.py    # Birthdays, anniversaries
├── waitlist/
│   ├── waitlist_management.py  # Handle overbooked periods
│   └── notification_system.py  # SMS/email notifications
└── reporting/
    ├── occupancy_analytics.py   # Table utilization reports
    └── no_show_tracking.py      # No-show patterns and prevention
```

#### **Core APIs (35 endpoints)**

1. **Table Management** (10 endpoints)
   - `GET /tables` - List all tables with filters
   - `POST /tables` - Create table
   - `GET /tables/{id}` - Get table details
   - `PUT /tables/{id}` - Update table
   - `DELETE /tables/{id}` - Delete table
   - `PUT /tables/{id}/status` - Update table status
   - `GET /tables/layout` - Get restaurant floor plan
   - `PUT /tables/layout` - Update floor plan layout
   - `GET /tables/availability` - Real-time availability
   - `GET /tables/analytics` - Table utilization analytics

2. **Core Reservations** (12 endpoints)
   - `GET /reservations` - List reservations with filters
   - `POST /reservations` - Create reservation
   - `GET /reservations/{id}` - Get reservation details
   - `PUT /reservations/{id}` - Update reservation
   - `DELETE /reservations/{id}` - Cancel reservation
   - `POST /reservations/{id}/checkin` - Check-in customer
   - `POST /reservations/{id}/seat` - Assign table
   - `POST /reservations/{id}/no-show` - Mark as no-show
   - `GET /reservations/today` - Today's reservations
   - `GET /reservations/calendar` - Calendar view
   - `POST /reservations/bulk-import` - Import reservations
   - `GET /reservations/analytics` - Reservation analytics

3. **Availability & Scheduling** (6 endpoints)
   - `GET /availability/slots` - Available time slots
   - `GET /availability/calendar` - Monthly availability
   - `PUT /availability/blackout` - Block time periods
   - `GET /availability/capacity` - Capacity planning
   - `PUT /availability/rules` - Set availability rules
   - `GET /availability/optimization` - Optimization suggestions

4. **Waitlist Management** (4 endpoints)
   - `GET /waitlist` - Current waitlist
   - `POST /waitlist` - Add to waitlist
   - `PUT /waitlist/{id}/notify` - Notify customer
   - `DELETE /waitlist/{id}` - Remove from waitlist

5. **Customer Preferences** (3 endpoints)
   - `GET /customers/{id}/preferences` - Get preferences
   - `PUT /customers/{id}/preferences` - Update preferences
   - `GET /preferences/analytics` - Preference analytics

#### **Customer-Facing Reservation APIs**
```python
# Public APIs for customers (no auth required)
@router.get("/public/availability")
async def get_public_availability(
    date: date,
    party_size: int,
    time_preference: Optional[str] = None
):
    """Get available reservation slots for customers"""
    
@router.post("/public/reservations")
async def create_public_reservation(
    reservation: PublicReservationCreate
):
    """Allow customers to make reservations"""
```

### **Phase 2 Deliverables**
✅ **Complete table management and floor plan configuration**  
✅ **Advanced reservation system with customer preferences**  
✅ **Public customer reservation interface (no account required)**  
✅ **Waitlist management for peak periods**  
✅ **Real-time table status and availability tracking**  
✅ **Reservation analytics and occupancy optimization**  
✅ **No-show tracking and prevention system**  
✅ **Staff reservation management dashboard**  
✅ **Customer check-in and seating workflow**  
✅ **SMS/Email notification system for reservations**

---

## 🍽️ Phase 3: Order Management & Kitchen Operations (10-12 weeks)
*"Complete order lifecycle from placement to fulfillment"*

### **Sprint 8-9: Core Order Management (4 weeks)**

#### **Orders Module Implementation**
```python
# app/modules/orders/
├── models/
│   ├── order.py           # Order aggregate root
│   ├── order_item.py      # Order line items
│   ├── order_status.py    # Order state machine
│   └── payment.py         # Payment tracking
├── routes/
│   ├── order_routes.py
│   ├── order_tracking_routes.py
│   └── payment_routes.py
├── services/
│   ├── order_service.py
│   ├── order_state_machine.py
│   └── payment_service.py
```

#### **Multi-Tenant Orders Schema**
```sql
-- Orders with full multi-tenant support from day 1
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    table_id UUID REFERENCES tables(id) NULL,
    order_number VARCHAR(20) NOT NULL, -- Unique per restaurant
    order_type VARCHAR(20) NOT NULL, -- 'dine_in', 'takeout', 'delivery'
    status VARCHAR(50) DEFAULT 'pending',
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),
    customer_email VARCHAR(255),
    subtotal DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    tip_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    special_instructions TEXT,
    scheduled_delivery_time TIMESTAMP NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure unique order numbers per restaurant
    UNIQUE(restaurant_id, order_number)
);

-- Order items with tenant context
CREATE TABLE order_items (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL REFERENCES menu_items(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    special_instructions TEXT,
    modifiers JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Order status history with tenant tracking
CREATE TABLE order_status_history (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    order_id UUID NOT NULL REFERENCES orders(id),
    status VARCHAR(50) NOT NULL,
    changed_by UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- QR ordering sessions (multi-tenant from day 1)
CREATE TABLE qr_ordering_sessions (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    table_id UUID NOT NULL REFERENCES tables(id),
    session_token VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'completed', 'expired'
    participants JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL
);

-- Individual participant orders within QR sessions
CREATE TABLE session_participant_orders (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    session_id UUID NOT NULL REFERENCES qr_ordering_sessions(id),
    participant_id VARCHAR(100) NOT NULL,
    participant_name VARCHAR(255),
    order_data JSONB NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Multi-tenant indexes for performance
CREATE INDEX idx_orders_org_restaurant ON orders(organization_id, restaurant_id);
CREATE INDEX idx_orders_status_date ON orders(restaurant_id, status, created_at);
CREATE INDEX idx_order_items_org ON order_items(organization_id);
CREATE INDEX idx_order_status_history_org ON order_status_history(organization_id);
CREATE INDEX idx_qr_sessions_org_restaurant ON qr_ordering_sessions(organization_id, restaurant_id);
CREATE INDEX idx_session_orders_org ON session_participant_orders(organization_id);

-- Row Level Security for all order tables
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_status_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE qr_ordering_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_participant_orders ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY orders_isolation ON orders
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
CREATE POLICY order_items_isolation ON order_items
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
CREATE POLICY order_status_history_isolation ON order_status_history
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
CREATE POLICY qr_sessions_isolation ON qr_ordering_sessions
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
CREATE POLICY session_orders_isolation ON session_participant_orders
    USING (organization_id = current_setting('app.current_organization_id')::UUID);
```

### **Sprint 10-11: Kitchen Display & Order Tracking (4 weeks)**

#### **Kitchen Module Implementation**
```python
# app/modules/kitchen/
├── models/
│   ├── kitchen_order.py    # Kitchen view of orders
│   ├── preparation_time.py # Prep time estimates
│   └── station.py          # Kitchen stations
├── routes/
│   ├── kitchen_routes.py
│   └── display_routes.py
├── services/
│   ├── kitchen_service.py
│   └── preparation_service.py
```

### **Sprint 12-13: QR Code Table Ordering & Payment Integration (4 weeks)**

#### **QR Code Integration**
```python
# app/modules/qr_ordering/
├── models/
│   ├── qr_session.py      # Table ordering sessions
│   └── guest_order.py     # Guest customer orders
├── routes/
│   ├── qr_routes.py
│   └── guest_ordering_routes.py
├── services/
│   ├── qr_service.py
│   └── guest_order_service.py
```

#### **Core APIs (45 endpoints)**

1. **Order Management** (15 endpoints)
   - `GET /orders` - List orders with filters
   - `POST /orders` - Create order
   - `GET /orders/{id}` - Get order details
   - `PUT /orders/{id}` - Update order
   - `DELETE /orders/{id}` - Cancel order
   - `POST /orders/{id}/items` - Add items to order
   - `PUT /orders/{id}/items/{item_id}` - Update order item
   - `DELETE /orders/{id}/items/{item_id}` - Remove order item
   - `PUT /orders/{id}/status` - Update order status
   - `GET /orders/{id}/history` - Order status history
   - `GET /orders/today` - Today's orders
   - `GET /orders/analytics` - Order analytics
   - `POST /orders/bulk-update` - Bulk status updates
   - `GET /orders/delivery-slots` - Available delivery times
   - `POST /orders/{id}/schedule` - Schedule order delivery

2. **Kitchen Display System** (8 endpoints)
   - `GET /kitchen/orders/active` - Active kitchen orders
   - `GET /kitchen/orders/queue` - Order preparation queue
   - `PUT /kitchen/orders/{id}/start` - Start preparation
   - `PUT /kitchen/orders/{id}/ready` - Mark item ready
   - `GET /kitchen/stations` - Kitchen station status
   - `PUT /kitchen/stations/{id}/status` - Update station
   - `GET /kitchen/prep-times` - Preparation time estimates
   - `PUT /kitchen/prep-times/{item_id}` - Update prep times

3. **QR Code Table Ordering** (10 endpoints)
   - `GET /qr/{table_qr_code}` - Access table ordering
   - `POST /qr/{table_qr_code}/join` - Join ordering session
   - `GET /ordering-sessions/{session_id}` - Get session info
   - `POST /ordering-sessions/{session_id}/orders` - Place order
   - `POST /ordering-sessions/{session_id}/split-bill` - Split payment
   - `POST /ordering-sessions/{session_id}/bills/{bill_id}/payment` - Individual payment
   - `GET /ordering-sessions/{session_id}/status` - Session status
   - `WebSocket /ws/ordering-sessions/{session_id}` - Real-time updates
   - `GET /public/menu/{restaurant_id}` - Public menu access
   - `POST /public/orders` - Guest order placement

4. **Payment Processing** (7 endpoints)
   - `POST /payments/process` - Process payment
   - `GET /payments/{id}` - Payment details
   - `POST /payments/{id}/refund` - Process refund
   - `GET /payments/methods` - Available payment methods
   - `GET /payments/reports` - Payment reports
   - `POST /payments/split` - Split payment processing
   - `POST /payments/tips` - Handle tip payments

### **Phase 3 Deliverables**
✅ **Complete order lifecycle management (pending → delivered)**  
✅ **Advanced kitchen display system with prep time tracking**  
✅ **QR code table ordering without customer accounts**  
✅ **Multi-person ordering with individual split payments**  
✅ **Scheduled delivery with restaurant approval workflow**  
✅ **Order tracking and real-time status updates**  
✅ **Payment processing with tips and refund management**  
✅ **Order analytics and kitchen performance reporting**  
✅ **Real-time WebSocket notifications for all stakeholders**  
✅ **Integration with table reservations for seamless dining**

---

## 🏢 Phase 4: Multi-Tenant Architecture (10-12 weeks)
*"Scale from single restaurant to multi-restaurant platform"*

### **Sprint 14-16: Tenant Architecture Foundation (6 weeks)**

#### **Multi-Tenancy Implementation**
```python
# Major architectural changes
rms/
├── app/
│   ├── modules/
│   │   ├── tenancy/              # NEW: Multi-tenant management
│   │   │   ├── models/
│   │   │   │   ├── organization.py  # Restaurant organizations
│   │   │   │   ├── restaurant.py    # Individual locations
│   │   │   │   └── subscription.py  # SaaS billing
│   │   │   ├── routes/
│   │   │   └── services/
│   │   └── platform/             # NEW: Platform administration
│   │       ├── models/
│   │       ├── routes/
│   │       └── services/
```

#### **Database Migration to Multi-Tenant**
```sql
-- Add organization layer
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    organization_type VARCHAR(50), -- 'franchise', 'chain', 'independent'
    subscription_tier VARCHAR(50) DEFAULT 'basic',
    billing_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Update existing tables to include organization_id
ALTER TABLE restaurants ADD COLUMN organization_id UUID REFERENCES organizations(id);
ALTER TABLE users ADD COLUMN organization_id UUID REFERENCES organizations(id);

-- Add tenant context to all existing tables
CREATE OR REPLACE FUNCTION add_tenant_context() RETURNS void AS $$
DECLARE
    table_name text;
BEGIN
    FOR table_name IN 
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT IN ('organizations', 'alembic_version')
    LOOP
        EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS organization_id UUID REFERENCES organizations(id)', table_name);
        EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%s_org_id ON %I(organization_id)', table_name, table_name);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### **Sprint 17-19: Platform Administration (4-6 weeks)**

#### **Platform APIs (25 endpoints)**
1. **Organization Management** (8 endpoints)
2. **Restaurant Management** (7 endpoints)  
3. **User & Role Management** (6 endpoints)
4. **Subscription & Billing** (4 endpoints)

### **Phase 4 Deliverables**
✅ **Multi-tenant data isolation and security**  
✅ **Organization and restaurant management**  
✅ **Hierarchical role-based access control**  
✅ **SaaS subscription and billing system**  
✅ **Platform administration dashboard**  
✅ **Tenant provisioning and configuration**  
✅ **Cross-tenant analytics and reporting**

---

## 🚀 Phase 5: Advanced Features & Integrations (12-14 weeks)
*"Market-differentiating features and third-party integrations"*

### **Sprint 20-22: Delivery Partner Integrations (6 weeks)**

#### **Delivery Integration Module**
```python
# app/modules/integrations/
├── delivery_partners/
│   ├── uber_eats/
│   ├── doordash/
│   └── grubhub/
├── pos_systems/
│   ├── square/
│   └── toast/
└── payment_gateways/
    ├── stripe/
    └── paypal/
```

### **Sprint 23-25: Advanced Features (6 weeks)**

#### **Advanced Features Implementation**
- **Inventory Management**: Stock tracking and supplier integration
- **Staff Management**: Employee scheduling and performance
- **Customer Loyalty**: Points, rewards, and retention programs
- **Analytics Dashboard**: Business intelligence and insights
- **Multi-language Support**: Internationalization

### **Sprint 26: Polish & Optimization (2 weeks)**

#### **Final System Optimization**
- **Performance optimization**
- **Security hardening**
- **Documentation completion**
- **Deployment automation**

### **Phase 5 Deliverables**
✅ **Uber Eats, DoorDash, Grubhub integrations**  
✅ **POS system integrations (Square, Toast)**  
✅ **Advanced inventory and supplier management**  
✅ **Staff scheduling and management system**  
✅ **Customer loyalty and marketing programs**  
✅ **Comprehensive analytics and reporting**  
✅ **Multi-language and localization support**  
✅ **Production-ready deployment and monitoring**

---

## 📋 Implementation Guidelines

### **Architecture Principles**
1. **Start Simple**: Build for single tenant, design for multi-tenant
2. **API-First**: All functionality exposed via REST APIs
3. **Domain-Driven**: Clear module boundaries aligned with business domains
4. **Test-Driven**: Comprehensive testing at each phase
5. **Security-First**: Authentication and authorization from day one

### **Technology Stack**
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Authentication**: JWT with role-based access control
- **Database**: PostgreSQL with tenant isolation
- **Testing**: Pytest, Alembic for migrations
- **Documentation**: OpenAPI/Swagger auto-generation

### **Team Scaling Strategy**
- **Phase 1-2**: Small core team (4-6 developers)
- **Phase 3**: Add frontend and mobile developers (6-8 team)
- **Phase 4**: Scale to full-stack teams (8-10 developers)
- **Phase 5**: Multiple specialized teams (10-12 developers)

### **Risk Mitigation**
- **Early Customer Validation**: Deploy Phase 1 with pilot restaurants
- **Iterative Feedback**: Regular customer feedback incorporation
- **Technical Debt Management**: Refactoring sprints between phases
- **Performance Testing**: Load testing at each major milestone

---

## 🎯 Success Metrics by Phase

| Phase | Key Metrics | Success Criteria |
|-------|-------------|------------------|
| **Phase 1** | Foundation & Menu | 3 restaurants live with complete menu setup |
| **Phase 2** | Reservations | 200+ reservations processed weekly across pilot restaurants |
| **Phase 3** | Orders & Kitchen | 1,000+ orders processed daily with <5min avg kitchen prep |
| **Phase 4** | Multi-Tenant | 15+ organizations, 75+ restaurants successfully migrated |
| **Phase 5** | Integrations | 3+ delivery partners, 2+ POS integrations, 95% uptime |

This phased approach ensures **early value delivery** while building towards a comprehensive, scalable restaurant management platform that can serve everything from single restaurants to large franchise operations.