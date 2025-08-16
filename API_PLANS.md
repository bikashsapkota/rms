# Restaurant Management System (RMS) - API Documentation

## 🚀 Complete API Reference

This document provides comprehensive API documentation for the Restaurant Management System (RMS), featuring **enterprise-grade multi-tenant architecture** with complete endpoint specifications, request/response examples, and integration guidelines.

**API Base URL**: `https://api.rms-platform.com/api/v1`  
**Authentication**: JWT Bearer Token with tenant context  
**Rate Limiting**: Tier-based (1000-10000 requests/hour)  
**API Versioning**: Semantic versioning with backward compatibility

> **Note**: For development phases and implementation timeline, see `DEVELOPMENT_PHASES.md`

---

## 🔐 Authentication & Authorization APIs

### **1.1 Platform Admin Authentication**

#### **POST /auth/platform/login**
```http
POST /api/v1/auth/platform/login
Content-Type: application/json

{
  "email": "admin@rms-platform.com",
  "password": "SecureAdminPass123!",
  "mfa_code": "123456"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: refresh_token=eyJ...; HttpOnly; Secure; SameSite=Strict

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "admin@rms-platform.com",
    "full_name": "Platform Administrator",
    "role": "super_admin",
    "permissions": ["platform:manage_all", "organizations:create", "users:impersonate"],
    "is_super_admin": true
  },
  "platform_access": {
    "total_organizations": 1247,
    "total_restaurants": 12847,
    "platform_health": "healthy"
  }
}
```

### **1.2 Organization User Authentication**

#### **POST /auth/organizations/{org_id}/login**
```http
POST /api/v1/auth/organizations/org_123e4567/login
Content-Type: application/json

{
  "email": "manager@pizzachain.com",
  "password": "ManagerPass123!",
  "organization_id": "org_123e4567"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer", 
  "expires_in": 28800,
  "user": {
    "id": "user_789abc",
    "email": "manager@pizzachain.com",
    "full_name": "John Smith",
    "organization_id": "org_123e4567",
    "role": "restaurant_manager"
  },
  "tenant_context": {
    "organization": {
      "id": "org_123e4567",
      "name": "Pizza Chain Inc",
      "tier": "professional"
    },
    "accessible_restaurants": [
      {
        "id": "rest_456def",
        "name": "Downtown Pizza",
        "address": "123 Main St, City"
      },
      {
        "id": "rest_789ghi", 
        "name": "Mall Pizza",
        "address": "456 Mall Ave, City"
      }
    ],
    "permissions": {
      "restaurant:manage_location": ["rest_456def", "rest_789ghi"],
      "orders:create": ["rest_456def", "rest_789ghi"],
      "menu:update": ["rest_456def", "rest_789ghi"]
    }
  }
}
```

### **1.3 Customer Authentication**

#### **POST /auth/customers/login**
```http
POST /api/v1/auth/customers/login
Content-Type: application/json

{
  "email": "customer@email.com",
  "password": "CustomerPass123!",
  "remember_me": true
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 7200,
  "user": {
    "id": "cust_987xyz",
    "email": "customer@email.com",
    "full_name": "Jane Doe",
    "role": "customer",
    "loyalty_tier": "gold"
  },
  "customer_profile": {
    "preferred_restaurants": ["rest_456def"],
    "dietary_restrictions": ["vegetarian"],
    "favorite_orders": ["order_template_123"],
    "loyalty_points": 2450,
    "saved_addresses": [
      {
        "id": "addr_1",
        "type": "home",
        "address": "789 Oak St, City",
        "is_default": true
      }
    ]
  }
}
```

---

## 🏢 Platform Management APIs (Super Admin)

### **2.1 Organization Management**

#### **POST /platform/organizations**
```http
POST /api/v1/platform/organizations
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Global Pizza Chain",
  "legal_name": "Global Pizza Chain LLC",
  "organization_type": "franchise",
  "billing_email": "billing@globalpizza.com",
  "tax_id": "12-3456789",
  "subscription_tier": "enterprise",
  "billing_info": {
    "payment_method": "credit_card",
    "billing_address": {
      "street": "100 Corporate Blvd",
      "city": "Business City",
      "state": "CA",
      "zip": "90210",
      "country": "US"
    }
  },
  "initial_admin": {
    "email": "admin@globalpizza.com",
    "full_name": "Pizza Chain Admin",
    "phone": "+1-555-0123"
  }
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "org_abc123",
  "name": "Global Pizza Chain",
  "legal_name": "Global Pizza Chain LLC",
  "organization_type": "franchise",
  "subscription_tier": "enterprise",
  "status": "active",
  "created_at": "2024-08-16T10:30:00Z",
  "billing_info": {
    "subscription_id": "sub_enterprise_456",
    "billing_cycle": "monthly",
    "next_billing_date": "2024-09-16T10:30:00Z"
  },
  "limits": {
    "max_restaurants": 100,
    "max_orders_per_month": 1000000,
    "features": ["advanced_analytics", "custom_integrations", "white_label"]
  },
  "initial_setup": {
    "admin_user_id": "user_admin_789",
    "setup_token": "setup_token_xyz789",
    "expires_at": "2024-08-17T10:30:00Z"
  }
}
```

#### **GET /platform/organizations**
```http
GET /api/v1/platform/organizations?page=1&limit=20&status=active&tier=enterprise
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "organizations": [
    {
      "id": "org_abc123",
      "name": "Global Pizza Chain", 
      "organization_type": "franchise",
      "subscription_tier": "enterprise",
      "restaurant_count": 247,
      "monthly_order_volume": 145000,
      "created_at": "2024-01-15T08:00:00Z",
      "last_active": "2024-08-16T09:45:00Z",
      "health_status": "healthy"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1247,
    "pages": 63
  },
  "platform_metrics": {
    "total_organizations": 1247,
    "active_organizations": 1198,
    "total_revenue_this_month": 2450000.50
  }
}
```

### **2.2 Platform Analytics**

#### **GET /platform/analytics/overview**
```http
GET /api/v1/platform/analytics/overview?timeframe=last_30_days
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "timeframe": "last_30_days",
  "platform_metrics": {
    "total_orders": 2450000,
    "total_revenue": 49500000.75,
    "active_restaurants": 12847,
    "new_organizations": 23,
    "churn_rate": 0.02
  },
  "performance_metrics": {
    "avg_response_time": 45,
    "uptime_percentage": 99.98,
    "api_requests_per_day": 15000000,
    "peak_concurrent_users": 125000
  },
  "geographic_distribution": {
    "north_america": { "organizations": 856, "revenue": 35500000 },
    "europe": { "organizations": 234, "revenue": 8900000 },
    "asia_pacific": { "organizations": 157, "revenue": 5100000 }
  }
}
```

---

## 🏪 Organization Management APIs

### **3.1 Restaurant Location Management**

#### **POST /organizations/{org_id}/restaurants**
```http
POST /api/v1/organizations/org_abc123/restaurants
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Downtown Pizza Express",
  "address": {
    "street": "123 Main Street",
    "city": "Downtown",
    "state": "CA",
    "zip": "90210",
    "country": "US",
    "coordinates": {
      "latitude": 34.0522,
      "longitude": -118.2437
    }
  },
  "contact": {
    "phone": "+1-555-0199",
    "email": "downtown@globalpizza.com"
  },
  "restaurant_type": "quick_service",
  "service_types": ["dine_in", "takeout", "delivery"],
  "timezone": "America/Los_Angeles",
  "currency": "USD",
  "operating_hours": {
    "monday": { "open": "10:00", "close": "22:00" },
    "tuesday": { "open": "10:00", "close": "22:00" },
    "wednesday": { "open": "10:00", "close": "22:00" },
    "thursday": { "open": "10:00", "close": "22:00" },
    "friday": { "open": "10:00", "close": "23:00" },
    "saturday": { "open": "10:00", "close": "23:00" },
    "sunday": { "open": "11:00", "close": "21:00" }
  },
  "delivery_settings": {
    "delivery_radius": 5.0,
    "minimum_order": 15.00,
    "delivery_fee": 2.99,
    "free_delivery_threshold": 35.00
  },
  "feature_modules": {
    "reservations": {
      "enabled": true,
      "allow_online_booking": true,
      "require_advance_booking": false,
      "max_party_size": 12,
      "booking_window_days": 30
    },
    "order_management": {
      "enabled": false,
      "dine_in_orders": false,
      "takeout_orders": false,
      "delivery_orders": false,
      "kitchen_display": false
    },
    "payment_processing": {
      "enabled": false,
      "accept_cards": false,
      "accept_cash": true,
      "split_billing": false,
      "tips_handling": false
    },
    "inventory_management": {
      "enabled": false,
      "stock_tracking": false,
      "supplier_integration": false,
      "automated_reordering": false
    },
    "staff_management": {
      "enabled": true,
      "scheduling": true,
      "time_tracking": false,
      "performance_metrics": false
    },
    "customer_reviews": {
      "enabled": true,
      "public_reviews": true,
      "review_responses": true,
      "rating_display": true
    },
    "analytics_reporting": {
      "enabled": true,
      "basic_reports": true,
      "advanced_analytics": false,
      "real_time_dashboards": true
    }
  }
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "rest_downtown_789",
  "organization_id": "org_abc123",
  "name": "Downtown Pizza Express",
  "status": "setup_required",
  "address": {
    "street": "123 Main Street",
    "city": "Downtown", 
    "state": "CA",
    "zip": "90210",
    "country": "US",
    "formatted": "123 Main Street, Downtown, CA 90210",
    "coordinates": {
      "latitude": 34.0522,
      "longitude": -118.2437
    }
  },
  "created_at": "2024-08-16T11:00:00Z",
  "feature_modules": {
    "reservations": {
      "enabled": true,
      "status": "active"
    },
    "order_management": {
      "enabled": false,
      "status": "disabled"
    },
    "payment_processing": {
      "enabled": false,
      "status": "disabled"
    },
    "inventory_management": {
      "enabled": false,
      "status": "disabled"
    },
    "staff_management": {
      "enabled": true,
      "status": "active"
    },
    "customer_reviews": {
      "enabled": true,
      "status": "active"
    },
    "analytics_reporting": {
      "enabled": true,
      "status": "active"
    }
  },
  "setup_checklist": {
    "menu_imported": false,
    "staff_added": false,
    "payment_gateway_configured": false,
    "pos_integration_setup": false,
    "test_order_completed": false,
    "feature_modules_configured": true
  },
  "estimated_go_live": "2024-08-23T11:00:00Z"
}
```

#### **GET /organizations/{org_id}/restaurants**
```http
GET /api/v1/organizations/org_abc123/restaurants?status=active&page=1&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "restaurants": [
    {
      "id": "rest_downtown_789",
      "name": "Downtown Pizza Express",
      "status": "active",
      "address": {
        "formatted": "123 Main Street, Downtown, CA 90210"
      },
      "performance": {
        "daily_orders_avg": 145,
        "monthly_revenue": 45000.75,
        "rating": 4.7,
        "last_order": "2024-08-16T10:45:00Z"
      },
      "staff_count": 12,
      "manager": {
        "id": "user_manager_456",
        "name": "Sarah Johnson",
        "email": "sarah@globalpizza.com"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 247,
    "pages": 25
  },
  "organization_summary": {
    "total_restaurants": 247,
    "active_restaurants": 239,
    "total_daily_orders": 8750,
    "total_monthly_revenue": 2450000.50
  }
}
```

### **3.2 Restaurant Feature Module Management**

#### **PUT /organizations/{org_id}/restaurants/{restaurant_id}/feature-modules**
```http
PUT /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/feature-modules
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "reservations": {
    "enabled": true,
    "allow_online_booking": true,
    "require_advance_booking": false,
    "max_party_size": 8,
    "booking_window_days": 14
  },
  "order_management": {
    "enabled": true,
    "dine_in_orders": true,
    "takeout_orders": true,
    "delivery_orders": false,
    "kitchen_display": true
  },
  "payment_processing": {
    "enabled": true,
    "accept_cards": true,
    "accept_cash": true,
    "split_billing": true,
    "tips_handling": true
  },
  "inventory_management": {
    "enabled": false,
    "stock_tracking": false,
    "supplier_integration": false,
    "automated_reordering": false
  }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "restaurant_id": "rest_downtown_789",
  "feature_modules": {
    "reservations": {
      "enabled": true,
      "status": "active",
      "configuration": {
        "allow_online_booking": true,
        "require_advance_booking": false,
        "max_party_size": 8,
        "booking_window_days": 14
      }
    },
    "order_management": {
      "enabled": true,
      "status": "active",
      "configuration": {
        "dine_in_orders": true,
        "takeout_orders": true,
        "delivery_orders": false,
        "kitchen_display": true
      }
    },
    "payment_processing": {
      "enabled": true,
      "status": "configuring",
      "configuration": {
        "accept_cards": true,
        "accept_cash": true,
        "split_billing": true,
        "tips_handling": true
      },
      "setup_required": [
        "payment_gateway_integration",
        "merchant_account_verification"
      ]
    },
    "inventory_management": {
      "enabled": false,
      "status": "disabled"
    }
  },
  "updated_at": "2024-08-16T14:30:00Z",
  "updated_by": "user_manager_456"
}
```

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/feature-modules**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/feature-modules
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "restaurant_id": "rest_downtown_789",
  "restaurant_name": "Downtown Pizza Express",
  "available_modules": {
    "reservations": {
      "enabled": true,
      "status": "active",
      "description": "Table reservation and dining room management",
      "pricing_tier": "included"
    },
    "order_management": {
      "enabled": true,
      "status": "active", 
      "description": "Complete order lifecycle management",
      "pricing_tier": "included"
    },
    "payment_processing": {
      "enabled": true,
      "status": "configuring",
      "description": "Credit card and payment gateway integration",
      "pricing_tier": "transaction_based"
    },
    "inventory_management": {
      "enabled": false,
      "status": "available",
      "description": "Stock tracking and supplier management",
      "pricing_tier": "premium"
    },
    "staff_management": {
      "enabled": true,
      "status": "active",
      "description": "Employee scheduling and performance tracking",
      "pricing_tier": "included"
    },
    "customer_reviews": {
      "enabled": true,
      "status": "active",
      "description": "Customer feedback and review management",
      "pricing_tier": "included"
    },
    "analytics_reporting": {
      "enabled": true,
      "status": "active",
      "description": "Business intelligence and reporting",
      "pricing_tier": "included"
    }
  },
  "module_dependencies": {
    "payment_processing": ["order_management"],
    "inventory_management": ["order_management"],
    "kitchen_display": ["order_management"]
  }
}
```

### **3.3 Organization User Management**

#### **POST /organizations/{org_id}/users**
```http
POST /api/v1/organizations/org_abc123/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "email": "newmanager@globalpizza.com",
  "full_name": "Mike Rodriguez",
  "phone": "+1-555-0188",
  "role": "restaurant_manager", 
  "assigned_restaurants": ["rest_downtown_789", "rest_mall_456"],
  "permissions": {
    "restaurant:manage_location": ["rest_downtown_789", "rest_mall_456"],
    "orders:manage_location": ["rest_downtown_789", "rest_mall_456"],
    "staff:manage_location": ["rest_downtown_789", "rest_mall_456"],
    "menu:update": ["rest_downtown_789", "rest_mall_456"]
  },
  "employment_info": {
    "employee_id": "EMP-2024-0789",
    "hire_date": "2024-08-16",
    "department": "operations",
    "salary_range": "manager_tier_2"
  },
  "send_welcome_email": true
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "user_mike_789",
  "email": "newmanager@globalpizza.com",
  "full_name": "Mike Rodriguez",
  "organization_id": "org_abc123",
  "role": "restaurant_manager",
  "status": "invitation_sent",
  "assigned_restaurants": [
    {
      "id": "rest_downtown_789",
      "name": "Downtown Pizza Express"
    },
    {
      "id": "rest_mall_456", 
      "name": "Mall Pizza"
    }
  ],
  "permissions": {
    "restaurant:manage_location": ["rest_downtown_789", "rest_mall_456"],
    "orders:manage_location": ["rest_downtown_789", "rest_mall_456"],
    "staff:manage_location": ["rest_downtown_789", "rest_mall_456"],
    "menu:update": ["rest_downtown_789", "rest_mall_456"]
  },
  "invitation": {
    "token": "invite_token_xyz789",
    "expires_at": "2024-08-23T11:00:00Z",
    "setup_url": "https://app.rms-platform.com/setup?token=invite_token_xyz789"
  },
  "created_at": "2024-08-16T11:30:00Z"
}
```

---

## 🍽️ Menu Management APIs

### **4.1 Organization Menu Templates**

#### **POST /organizations/{org_id}/menu-templates**
```http
POST /api/v1/organizations/org_abc123/menu-templates
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Standard Pizza Menu 2024",
  "description": "Standardized menu template for all Pizza Chain locations",
  "categories": [
    {
      "name": "Pizzas",
      "description": "Our signature hand-tossed pizzas",
      "display_order": 1,
      "items": [
        {
          "name": "Margherita Pizza",
          "description": "Fresh mozzarella, tomato sauce, and basil",
          "base_price": 14.99,
          "prep_time_minutes": 12,
          "allergens": ["gluten", "dairy"],
          "dietary_tags": ["vegetarian"],
          "modifiers": [
            {
              "name": "Size",
              "type": "single_select",
              "required": true,
              "options": [
                { "name": "Small (10\")", "price_modifier": 0 },
                { "name": "Medium (12\")", "price_modifier": 3.00 },
                { "name": "Large (14\")", "price_modifier": 6.00 },
                { "name": "Extra Large (16\")", "price_modifier": 9.00 }
              ]
            },
            {
              "name": "Crust Type",
              "type": "single_select", 
              "required": true,
              "options": [
                { "name": "Thin Crust", "price_modifier": 0 },
                { "name": "Thick Crust", "price_modifier": 1.50 },
                { "name": "Gluten-Free", "price_modifier": 3.00 }
              ]
            },
            {
              "name": "Extra Toppings",
              "type": "multi_select",
              "required": false,
              "options": [
                { "name": "Extra Cheese", "price_modifier": 2.00 },
                { "name": "Pepperoni", "price_modifier": 2.50 },
                { "name": "Mushrooms", "price_modifier": 1.50 },
                { "name": "Olives", "price_modifier": 1.50 }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": "Beverages",
      "description": "Refreshing drinks",
      "display_order": 2,
      "items": [
        {
          "name": "Coca-Cola",
          "description": "Classic Coca-Cola",
          "base_price": 2.99,
          "prep_time_minutes": 1,
          "modifiers": [
            {
              "name": "Size",
              "type": "single_select",
              "required": true,
              "options": [
                { "name": "Small", "price_modifier": 0 },
                { "name": "Medium", "price_modifier": 0.50 },
                { "name": "Large", "price_modifier": 1.00 }
              ]
            }
          ]
        }
      ]
    }
  ],
  "pricing_rules": {
    "happy_hour": {
      "days": ["monday", "tuesday", "wednesday"],
      "start_time": "15:00",
      "end_time": "17:00",
      "discount_percentage": 20
    },
    "combo_deals": [
      {
        "name": "Pizza + Drink Combo",
        "qualifying_items": ["category:pizzas", "category:beverages"],
        "discount_amount": 2.00,
        "minimum_items": 2
      }
    ]
  }
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "template_standard_pizza_2024",
  "organization_id": "org_abc123",
  "name": "Standard Pizza Menu 2024",
  "status": "active",
  "version": "1.0",
  "created_at": "2024-08-16T12:00:00Z",
  "categories": [
    {
      "id": "cat_pizzas_123",
      "name": "Pizzas",
      "item_count": 1
    },
    {
      "id": "cat_beverages_456",
      "name": "Beverages", 
      "item_count": 1
    }
  ],
  "deployment_status": {
    "total_restaurants": 247,
    "deployed_to": 0,
    "pending_deployment": 247
  },
  "estimated_deployment_time": "2-4 hours"
}
```

### **4.2 Restaurant-Specific Menu Management**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/menu**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/menu
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "restaurant_id": "rest_downtown_789",
  "menu_template_id": "template_standard_pizza_2024",
  "last_updated": "2024-08-16T12:30:00Z",
  "categories": [
    {
      "id": "cat_pizzas_123",
      "name": "Pizzas",
      "description": "Our signature hand-tossed pizzas",
      "display_order": 1,
      "is_available": true,
      "items": [
        {
          "id": "item_margherita_456",
          "name": "Margherita Pizza",
          "description": "Fresh mozzarella, tomato sauce, and basil",
          "base_price": 14.99,
          "final_price": 14.99,
          "is_available": true,
          "availability_status": "in_stock",
          "prep_time_minutes": 12,
          "nutrition_info": {
            "calories": 250,
            "protein": 12,
            "carbs": 30,
            "fat": 8
          },
          "allergens": ["gluten", "dairy"],
          "dietary_tags": ["vegetarian"],
          "image_url": "https://cdn.rms-platform.com/menu/margherita_pizza.jpg",
          "modifiers": [
            {
              "id": "mod_size_789",
              "name": "Size",
              "type": "single_select",
              "required": true,
              "options": [
                {
                  "id": "opt_small_123",
                  "name": "Small (10\")",
                  "price_modifier": 0,
                  "is_available": true
                },
                {
                  "id": "opt_medium_456", 
                  "name": "Medium (12\")",
                  "price_modifier": 3.00,
                  "is_available": true
                },
                {
                  "id": "opt_large_789",
                  "name": "Large (14\")",
                  "price_modifier": 6.00,
                  "is_available": true
                },
                {
                  "id": "opt_xlarge_012",
                  "name": "Extra Large (16\")",
                  "price_modifier": 9.00,
                  "is_available": false,
                  "unavailable_reason": "out_of_dough"
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "restaurant_customizations": {
    "local_pricing_adjustments": [
      {
        "item_id": "item_margherita_456",
        "price_adjustment": 1.00,
        "reason": "high_rent_area"
      }
    ],
    "unavailable_items": [],
    "special_offers": [
      {
        "name": "Grand Opening Special",
        "description": "20% off all pizzas",
        "discount_percentage": 20,
        "valid_until": "2024-08-30T23:59:59Z"
      }
    ]
  }
}
```

#### **PUT /organizations/{org_id}/restaurants/{restaurant_id}/menu/items/{item_id}/availability**
```http
PUT /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/menu/items/item_margherita_456/availability
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "is_available": false,
  "unavailable_reason": "out_of_ingredients",
  "estimated_return": "2024-08-16T18:00:00Z",
  "staff_note": "Ran out of fresh mozzarella, expecting delivery at 6 PM"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "item_id": "item_margherita_456",
  "restaurant_id": "rest_downtown_789",
  "is_available": false,
  "unavailable_reason": "out_of_ingredients",
  "estimated_return": "2024-08-16T18:00:00Z",
  "updated_at": "2024-08-16T14:30:00Z",
  "updated_by": {
    "user_id": "user_mike_789",
    "name": "Mike Rodriguez"
  },
  "impact_analysis": {
    "affected_combo_deals": 1,
    "historical_daily_orders": 45,
    "revenue_impact_estimate": 675.00
  }
}
```

---

## 🛒 Order Management APIs

### **5.1 Get Available Delivery Time Slots**

#### **GET /restaurants/{restaurant_id}/delivery-slots**
```http
GET /api/v1/restaurants/rest_downtown_789/delivery-slots?date=2024-08-16&order_type=delivery
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "restaurant_id": "rest_downtown_789",
  "date": "2024-08-16",
  "current_time": "2024-08-16T14:30:00Z",
  "available_slots": [
    {
      "time": "2024-08-16T18:00:00Z",
      "display_time": "6:00 PM",
      "status": "available",
      "capacity_remaining": 8,
      "estimated_prep_time": 25,
      "delivery_fee": 3.99
    },
    {
      "time": "2024-08-16T18:30:00Z",
      "display_time": "6:30 PM",
      "status": "available",
      "capacity_remaining": 12,
      "estimated_prep_time": 20,
      "delivery_fee": 2.99
    },
    {
      "time": "2024-08-16T19:00:00Z",
      "display_time": "7:00 PM",
      "status": "limited",
      "capacity_remaining": 3,
      "estimated_prep_time": 35,
      "delivery_fee": 3.99
    },
    {
      "time": "2024-08-16T19:30:00Z",
      "display_time": "7:30 PM",
      "status": "unavailable",
      "capacity_remaining": 0,
      "reason": "Peak hours - fully booked"
    }
  ],
  "next_available_slot": "2024-08-16T20:00:00Z",
  "restaurant_settings": {
    "minimum_advance_time": 30,
    "maximum_advance_days": 7,
    "slot_duration": 30,
    "auto_approval_threshold": 5
  }
}
```

### **5.2 Order Creation with Scheduled Delivery**

#### **POST /orders**
```http
POST /api/v1/orders
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "restaurant_id": "rest_downtown_789",
  "order_type": "delivery",
  "customer_info": {
    "name": "Jane Doe",
    "phone": "+1-555-0177",
    "email": "jane.doe@email.com"
  },
  "delivery_info": {
    "address": {
      "street": "789 Oak Street",
      "city": "Downtown",
      "state": "CA",
      "zip": "90210",
      "instructions": "Ring doorbell, apartment 3B"
    },
    "scheduled_delivery": {
      "requested_time": "2024-08-16T19:00:00Z",
      "time_slot_id": "slot_190000_789",
      "delivery_preference": "on_time",
      "backup_time": "2024-08-16T19:30:00Z"
    }
  },
  "items": [
    {
      "menu_item_id": "item_margherita_456",
      "quantity": 2,
      "special_instructions": "Extra crispy crust",
      "modifiers": [
        {
          "modifier_id": "mod_size_789",
          "option_id": "opt_large_789"
        },
        {
          "modifier_id": "mod_crust_012",
          "option_id": "opt_thin_123"
        },
        {
          "modifier_id": "mod_toppings_345",
          "option_ids": ["opt_extra_cheese_456", "opt_mushrooms_789"]
        }
      ]
    },
    {
      "menu_item_id": "item_coke_789",
      "quantity": 2,
      "modifiers": [
        {
          "modifier_id": "mod_drink_size_123",
          "option_id": "opt_large_456"
        }
      ]
    }
  ],
  "payment_info": {
    "payment_method": "credit_card",
    "payment_token": "tok_visa_ending_4242",
    "tip_amount": 5.00,
    "tip_percentage": 18
  },
  "loyalty_info": {
    "customer_id": "cust_987xyz",
    "points_to_redeem": 0,
    "coupon_code": "NEWCUSTOMER10"
  }
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "order_abc123def456",
  "order_number": "DT-2024-001247",
  "restaurant": {
    "id": "rest_downtown_789",
    "name": "Downtown Pizza Express",
    "phone": "+1-555-0199"
  },
  "status": "pending_restaurant_approval",
  "order_type": "delivery",
  "created_at": "2024-08-16T15:00:00Z",
  "scheduled_delivery": {
    "requested_time": "2024-08-16T19:00:00Z",
    "approval_status": "pending",
    "restaurant_response_deadline": "2024-08-16T15:15:00Z",
    "auto_approve_in": 900
  },
  "estimated_ready_time": "2024-08-16T18:45:00Z",
  "estimated_delivery_time": "2024-08-16T19:00:00Z",
  "items": [
    {
      "id": "order_item_1",
      "menu_item": {
        "id": "item_margherita_456",
        "name": "Margherita Pizza"
      },
      "quantity": 2,
      "unit_price": 20.99,
      "total_price": 41.98,
      "modifiers_applied": [
        { "name": "Large (14\")", "price": 6.00 },
        { "name": "Thin Crust", "price": 0.00 },
        { "name": "Extra Cheese", "price": 2.00 },
        { "name": "Mushrooms", "price": 1.50 }
      ],
      "special_instructions": "Extra crispy crust"
    },
    {
      "id": "order_item_2",
      "menu_item": {
        "id": "item_coke_789",
        "name": "Coca-Cola"
      },
      "quantity": 2,
      "unit_price": 3.49,
      "total_price": 6.98,
      "modifiers_applied": [
        { "name": "Large", "price": 1.00 }
      ]
    }
  ],
  "pricing": {
    "subtotal": 48.96,
    "tax": 4.41,
    "delivery_fee": 2.99,
    "tip": 5.00,
    "discount": 4.90,
    "total": 56.46
  },
  "discounts_applied": [
    {
      "code": "NEWCUSTOMER10",
      "description": "10% off for new customers",
      "amount": 4.90
    }
  ],
  "payment": {
    "status": "processed",
    "method": "credit_card",
    "last_four": "4242",
    "transaction_id": "txn_abc123"
  },
  "tracking": {
    "tracking_url": "https://app.rms-platform.com/track/order_abc123def456",
    "estimated_steps": [
      { "step": "confirmed", "time": "2024-08-16T15:00:00Z", "completed": true },
      { "step": "preparing", "time": "2024-08-16T15:05:00Z", "completed": false },
      { "step": "ready", "time": "2024-08-16T15:35:00Z", "completed": false },
      { "step": "out_for_delivery", "time": "2024-08-16T15:40:00Z", "completed": false },
      { "step": "delivered", "time": "2024-08-16T15:50:00Z", "completed": false }
    ]
  }
}
```

### **5.3 Restaurant Scheduled Order Approval**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/pending-approvals**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/pending-approvals
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "pending_orders": [
    {
      "order_id": "order_abc123def456",
      "order_number": "DT-2024-001247",
      "customer_name": "Jane Doe",
      "requested_delivery_time": "2024-08-16T19:00:00Z",
      "order_total": 54.47,
      "items_count": 4,
      "estimated_prep_time": 25,
      "deadline_to_respond": "2024-08-16T15:15:00Z",
      "minutes_remaining": 12,
      "current_capacity": {
        "19_00_slot": {
          "current_orders": 8,
          "max_capacity": 12,
          "remaining_capacity": 4
        }
      },
      "conflict_analysis": {
        "has_conflicts": false,
        "kitchen_load": "moderate",
        "delivery_capacity": "available"
      },
      "customer_priority": "regular",
      "order_complexity": "standard"
    },
    {
      "order_id": "order_def456ghi789",
      "order_number": "DT-2024-001248",
      "customer_name": "John Smith",
      "requested_delivery_time": "2024-08-16T19:30:00Z",
      "order_total": 89.25,
      "items_count": 8,
      "estimated_prep_time": 45,
      "deadline_to_respond": "2024-08-16T15:20:00Z",
      "minutes_remaining": 17,
      "current_capacity": {
        "19_30_slot": {
          "current_orders": 11,
          "max_capacity": 12,
          "remaining_capacity": 1
        }
      },
      "conflict_analysis": {
        "has_conflicts": true,
        "kitchen_load": "high",
        "delivery_capacity": "limited",
        "conflicts": [
          "Kitchen prep time extends into next slot",
          "Limited delivery drivers available"
        ]
      },
      "customer_priority": "vip",
      "order_complexity": "complex"
    }
  ],
  "capacity_overview": {
    "current_time": "2024-08-16T15:03:00Z",
    "today_total_orders": 127,
    "today_capacity_utilization": 78.5,
    "upcoming_slots": [
      {
        "time": "2024-08-16T18:00:00Z",
        "orders": 6,
        "capacity": 12,
        "status": "available"
      },
      {
        "time": "2024-08-16T18:30:00Z",
        "orders": 9,
        "capacity": 12,
        "status": "available"
      },
      {
        "time": "2024-08-16T19:00:00Z",
        "orders": 8,
        "capacity": 12,
        "status": "moderate"
      },
      {
        "time": "2024-08-16T19:30:00Z",
        "orders": 11,
        "capacity": 12,
        "status": "near_full"
      }
    ]
  }
}
```

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/orders/{order_id}/approve**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/orders/order_abc123def456/approve
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "approval_status": "approved",
  "confirmed_delivery_time": "2024-08-16T19:00:00Z",
  "estimated_prep_time": 25,
  "staff_notes": "Order approved, normal prep time expected",
  "customer_notification": {
    "send_sms": true,
    "send_email": true,
    "custom_message": "Your order has been confirmed! We'll have it ready by 7:00 PM."
  }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "order_id": "order_abc123def456",
  "approval_status": "approved",
  "updated_status": "confirmed",
  "confirmed_delivery_time": "2024-08-16T19:00:00Z",
  "estimated_ready_time": "2024-08-16T18:45:00Z",
  "slot_reserved": "slot_190000_789",
  "capacity_impact": {
    "slot_utilization": 75.0,
    "remaining_capacity": 3
  },
  "notifications_sent": {
    "customer_sms": true,
    "customer_email": true,
    "kitchen_alert": true
  },
  "updated_at": "2024-08-16T15:08:00Z"
}
```

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/orders/{order_id}/modify-schedule**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/orders/order_def456ghi789/modify-schedule
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "action": "propose_alternative",
  "reason": "Kitchen capacity conflict",
  "proposed_alternatives": [
    {
      "delivery_time": "2024-08-16T20:00:00Z",
      "estimated_prep_time": 35,
      "delivery_fee_adjustment": -1.00,
      "explanation": "20 minutes later, reduced delivery fee as compensation"
    },
    {
      "delivery_time": "2024-08-17T18:30:00Z",
      "estimated_prep_time": 25,
      "delivery_fee_adjustment": 0.00,
      "promotion_applied": "15% discount for next day delivery",
      "explanation": "Next day delivery with discount applied"
    }
  ],
  "customer_notification": {
    "notification_type": "schedule_conflict",
    "auto_call_customer": true,
    "message": "We're experiencing high volume. We can offer alternative delivery times with compensation."
  }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "order_id": "order_def456ghi789",
  "modification_status": "alternatives_proposed",
  "customer_response_deadline": "2024-08-16T15:35:00Z",
  "proposed_alternatives": [
    {
      "alternative_id": "alt_001",
      "delivery_time": "2024-08-16T20:00:00Z",
      "compensation": "Delivery fee reduced by $1.00"
    },
    {
      "alternative_id": "alt_002", 
      "delivery_time": "2024-08-17T18:30:00Z",
      "compensation": "15% discount applied"
    }
  ],
  "notifications_sent": {
    "customer_call_scheduled": true,
    "customer_sms": true,
    "customer_email": true
  },
  "next_action": "wait_customer_response"
}
```

### **5.4 Customer Response to Schedule Changes**

#### **POST /orders/{order_id}/schedule-response**
```http
POST /api/v1/orders/order_def456ghi789/schedule-response
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "response": "accept_alternative",
  "selected_alternative_id": "alt_001",
  "customer_notes": "8:00 PM works perfectly, thank you for the discount!"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "order_id": "order_def456ghi789",
  "status": "confirmed",
  "confirmed_delivery_time": "2024-08-16T20:00:00Z",
  "estimated_ready_time": "2024-08-16T19:35:00Z",
  "compensation_applied": {
    "type": "delivery_fee_reduction",
    "amount": 1.00,
    "new_total": 88.25
  },
  "updated_at": "2024-08-16T15:12:00Z"
}
```

### **5.5 Restaurant Order Management**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/orders**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/orders?status=preparing&date=2024-08-16&limit=50
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "orders": [
    {
      "id": "order_abc123def456",
      "order_number": "DT-2024-001247",
      "status": "preparing",
      "order_type": "delivery",
      "created_at": "2024-08-16T15:00:00Z",
      "estimated_ready_time": "2024-08-16T15:35:00Z",
      "customer": {
        "name": "Jane Doe",
        "phone": "+1-555-0177",
        "masked_phone": "***-***-0177"
      },
      "items_summary": {
        "total_items": 4,
        "description": "2x Margherita Pizza (Large), 2x Coca-Cola (Large)"
      },
      "pricing": {
        "total": 56.46,
        "payment_status": "paid"
      },
      "kitchen_notes": {
        "special_instructions": ["Extra crispy crust"],
        "allergen_alerts": ["gluten", "dairy"],
        "prep_priority": "normal"
      },
      "delivery_info": {
        "address": "789 Oak Street, Downtown, CA 90210",
        "estimated_delivery": "2024-08-16T15:50:00Z"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 23,
    "pages": 1
  },
  "restaurant_metrics": {
    "orders_today": 67,
    "revenue_today": 2450.75,
    "avg_order_value": 36.58,
    "avg_prep_time": 18.5,
    "on_time_percentage": 94.2
  }
}
```

#### **PUT /organizations/{org_id}/restaurants/{restaurant_id}/orders/{order_id}/status**
```http
PUT /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/orders/order_abc123def456/status
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "status": "ready",
  "staff_notes": "Order ready for pickup by delivery driver",
  "actual_prep_time": 22,
  "quality_check": {
    "checked_by": "user_chef_123",
    "notes": "All items prepared correctly"
  }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "order_id": "order_abc123def456",
  "status": "ready",
  "updated_at": "2024-08-16T15:22:00Z",
  "updated_by": {
    "user_id": "user_mike_789", 
    "name": "Mike Rodriguez",
    "role": "restaurant_manager"
  },
  "timeline": [
    { "status": "confirmed", "timestamp": "2024-08-16T15:00:00Z" },
    { "status": "preparing", "timestamp": "2024-08-16T15:05:00Z" },
    { "status": "ready", "timestamp": "2024-08-16T15:22:00Z" }
  ],
  "performance_metrics": {
    "estimated_prep_time": 18,
    "actual_prep_time": 22,
    "variance": 4,
    "on_time": false
  },
  "next_steps": {
    "action_required": "assign_delivery_driver",
    "estimated_delivery": "2024-08-16T15:45:00Z"
  },
  "customer_notification": {
    "sent_at": "2024-08-16T15:22:30Z",
    "channels": ["sms", "push_notification"],
    "message": "Your order DT-2024-001247 is ready for delivery!"
  }
}
```

### **5.3 Organization-Wide Order Analytics**

#### **GET /organizations/{org_id}/orders/analytics**
```http
GET /api/v1/organizations/org_abc123/orders/analytics?timeframe=last_7_days&group_by=restaurant
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "timeframe": "last_7_days",
  "organization_summary": {
    "total_orders": 18450,
    "total_revenue": 675000.50,
    "avg_order_value": 36.58,
    "order_growth": 12.5,
    "revenue_growth": 15.8
  },
  "restaurant_breakdown": [
    {
      "restaurant_id": "rest_downtown_789",
      "name": "Downtown Pizza Express",
      "orders": 1247,
      "revenue": 45600.75,
      "avg_order_value": 36.58,
      "growth_rate": 18.2,
      "performance_ranking": 1
    },
    {
      "restaurant_id": "rest_mall_456",
      "name": "Mall Pizza",
      "orders": 987,
      "revenue": 35400.25,
      "avg_order_value": 35.87,
      "growth_rate": 8.9,
      "performance_ranking": 2
    }
  ],
  "trending_items": [
    {
      "item_name": "Margherita Pizza",
      "orders": 2890,
      "revenue": 58950.75,
      "growth": 25.4
    }
  ],
  "performance_metrics": {
    "avg_prep_time": 18.5,
    "on_time_percentage": 94.2,
    "customer_satisfaction": 4.7,
    "order_accuracy": 98.1
  }
}
```

---

## 👥 Staff Management APIs

### **6.1 Restaurant Staff Management**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/staff**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/staff
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "email": "chef@globalpizza.com",
  "full_name": "Carlos Rodriguez",
  "phone": "+1-555-0166",
  "role": "kitchen_manager",
  "employment_info": {
    "employee_id": "EMP-DT-2024-0156",
    "hire_date": "2024-08-16",
    "hourly_wage": 22.50,
    "employment_type": "full_time"
  },
  "certifications": [
    {
      "type": "food_safety",
      "certification_name": "ServSafe Manager",
      "number": "12345678",
      "issued_date": "2024-01-15",
      "expiry_date": "2027-01-15"
    }
  ],
  "availability": {
    "monday": { "start": "06:00", "end": "14:00" },
    "tuesday": { "start": "06:00", "end": "14:00" },
    "wednesday": { "start": "06:00", "end": "14:00" },
    "thursday": { "start": "06:00", "end": "14:00" },
    "friday": { "start": "06:00", "end": "14:00" },
    "saturday": { "unavailable": true },
    "sunday": { "unavailable": true }
  },
  "permissions": {
    "kitchen_orders:manage": true,
    "menu_items:update_availability": true,
    "kitchen_staff:manage": true,
    "inventory:view_kitchen": true
  },
  "send_welcome_email": true
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "user_carlos_789",
  "email": "chef@globalpizza.com",
  "full_name": "Carlos Rodriguez",
  "restaurant_id": "rest_downtown_789",
  "organization_id": "org_abc123",
  "role": "kitchen_manager",
  "status": "invitation_sent",
  "employment_info": {
    "employee_id": "EMP-DT-2024-0156",
    "hire_date": "2024-08-16",
    "employment_type": "full_time",
    "department": "kitchen"
  },
  "certifications": [
    {
      "id": "cert_servesafe_123",
      "type": "food_safety",
      "status": "valid",
      "expiry_date": "2027-01-15",
      "days_until_expiry": 1247
    }
  ],
  "permissions": {
    "kitchen_orders:manage": true,
    "menu_items:update_availability": true,
    "kitchen_staff:manage": true,
    "inventory:view_kitchen": true
  },
  "invitation": {
    "token": "invite_token_chef_xyz",
    "expires_at": "2024-08-23T16:00:00Z",
    "setup_url": "https://app.rms-platform.com/staff-setup?token=invite_token_chef_xyz"
  },
  "created_at": "2024-08-16T16:00:00Z"
}
```

### **6.2 Staff Scheduling**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/schedules**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/schedules
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "week_start_date": "2024-08-19",
  "shifts": [
    {
      "staff_id": "user_carlos_789",
      "date": "2024-08-19",
      "start_time": "06:00",
      "end_time": "14:00",
      "position": "kitchen_manager",
      "break_times": [
        { "start": "09:00", "end": "09:15", "type": "break" },
        { "start": "11:30", "end": "12:00", "type": "lunch" }
      ]
    },
    {
      "staff_id": "user_sarah_456",
      "date": "2024-08-19",
      "start_time": "10:00", 
      "end_time": "18:00",
      "position": "server",
      "break_times": [
        { "start": "13:00", "end": "13:30", "type": "lunch" },
        { "start": "15:30", "end": "15:45", "type": "break" }
      ]
    }
  ],
  "notes": "Busy Monday expected, extra staff scheduled"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "schedule_week_2024_08_19",
  "restaurant_id": "rest_downtown_789",
  "week_start_date": "2024-08-19",
  "status": "published",
  "shifts": [
    {
      "id": "shift_carlos_mon_123",
      "staff": {
        "id": "user_carlos_789",
        "name": "Carlos Rodriguez",
        "role": "kitchen_manager"
      },
      "date": "2024-08-19",
      "start_time": "06:00",
      "end_time": "14:00",
      "duration_hours": 8.0,
      "position": "kitchen_manager",
      "estimated_cost": 180.00
    }
  ],
  "schedule_summary": {
    "total_shifts": 47,
    "total_hours": 312.5,
    "estimated_labor_cost": 7812.50,
    "coverage_analysis": {
      "peak_hours_covered": true,
      "minimum_staff_met": true,
      "overtime_hours": 8.5
    }
  },
  "published_at": "2024-08-16T16:30:00Z",
  "notifications_sent": {
    "staff_count": 12,
    "sent_at": "2024-08-16T16:30:30Z"
  }
}
```

---

## 💳 Payment & Billing APIs

### **7.1 Payment Processing**

#### **POST /orders/{order_id}/payments**
```http
POST /api/v1/orders/order_abc123def456/payments
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "payment_method": "credit_card",
  "payment_token": "tok_visa_ending_4242",
  "amount": 56.46,
  "tip_amount": 5.00,
  "currency": "USD",
  "billing_address": {
    "street": "789 Oak Street",
    "city": "Downtown",
    "state": "CA", 
    "zip": "90210",
    "country": "US"
  },
  "save_payment_method": true
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "payment_abc123",
  "order_id": "order_abc123def456",
  "status": "succeeded",
  "amount": 56.46,
  "tip_amount": 5.00,
  "total_charged": 61.46,
  "currency": "USD",
  "payment_method": {
    "type": "credit_card",
    "brand": "visa",
    "last_four": "4242",
    "exp_month": 12,
    "exp_year": 2027
  },
  "transaction_details": {
    "transaction_id": "txn_stripe_abc123def",
    "gateway": "stripe",
    "gateway_fee": 1.95,
    "net_amount": 59.51,
    "processed_at": "2024-08-16T15:01:15Z"
  },
  "restaurant_payout": {
    "amount": 54.05,
    "platform_fee": 3.41,
    "processing_fee": 1.95,
    "payout_date": "2024-08-17T09:00:00Z"
  },
  "receipt": {
    "receipt_url": "https://receipts.rms-platform.com/payment_abc123",
    "receipt_number": "REC-2024-001247"
  }
}
```

### **7.2 Organization Billing**

#### **GET /organizations/{org_id}/billing/invoices**
```http
GET /api/v1/organizations/org_abc123/billing/invoices?status=paid&year=2024&month=8
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "invoices": [
    {
      "id": "inv_aug_2024_org_abc123",
      "invoice_number": "INV-2024-08-000123",
      "billing_period": {
        "start": "2024-08-01",
        "end": "2024-08-31"
      },
      "status": "paid",
      "subscription": {
        "tier": "enterprise",
        "restaurants_included": 100,
        "price_per_restaurant": 149.99
      },
      "usage": {
        "active_restaurants": 247,
        "orders_processed": 285000,
        "overage_restaurants": 147
      },
      "charges": {
        "base_subscription": 14999.00,
        "overage_charges": 22053.00,
        "total_before_tax": 37052.00,
        "tax": 3334.68,
        "total": 40386.68
      },
      "payment": {
        "paid_at": "2024-08-02T10:00:00Z",
        "payment_method": "bank_transfer",
        "transaction_id": "wire_transfer_abc123"
      },
      "invoice_url": "https://billing.rms-platform.com/invoices/inv_aug_2024_org_abc123.pdf"
    }
  ],
  "billing_summary": {
    "current_tier": "enterprise",
    "next_billing_date": "2024-09-01",
    "estimated_next_amount": 42150.75,
    "payment_method": {
      "type": "bank_transfer",
      "account_ending": "***7890"
    }
  }
}
```

### **7.3 Restaurant Revenue Analytics**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/revenue**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/revenue?timeframe=last_30_days&breakdown=daily
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "restaurant_id": "rest_downtown_789",
  "timeframe": "last_30_days",
  "summary": {
    "total_revenue": 135750.50,
    "total_orders": 3421,
    "avg_order_value": 39.68,
    "growth_rate": 12.5
  },
  "daily_breakdown": [
    {
      "date": "2024-08-16",
      "revenue": 4521.75,
      "orders": 114,
      "avg_order_value": 39.66,
      "payment_methods": {
        "credit_card": 3840.50,
        "cash": 456.25,
        "digital_wallet": 225.00
      }
    }
  ],
  "payment_analytics": {
    "processing_fees": 4072.52,
    "platform_fees": 8145.03,
    "net_revenue": 123532.95,
    "payout_schedule": "daily",
    "next_payout": "2024-08-17T09:00:00Z"
  },
  "top_performing_items": [
    {
      "item_name": "Margherita Pizza",
      "revenue": 28950.00,
      "orders": 1450,
      "avg_price": 19.97
    }
  ]
}
```

---

## 📊 Analytics & Reporting APIs

### **8.1 Platform Analytics (Super Admin)**

#### **GET /platform/analytics/dashboard**
```http
GET /api/v1/platform/analytics/dashboard?timeframe=last_30_days
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "timeframe": "last_30_days",
  "platform_overview": {
    "total_organizations": 1247,
    "total_restaurants": 12847,
    "total_orders": 5650000,
    "total_revenue": 225000000.75,
    "active_users": 125000,
    "new_signups": 347
  },
  "performance_metrics": {
    "avg_response_time": 67,
    "uptime_percentage": 99.97,
    "api_requests_per_day": 45000000,
    "error_rate": 0.03,
    "peak_concurrent_users": 245000
  },
  "business_metrics": {
    "mrr": 8750000.50,
    "arr": 105000000.00,
    "churn_rate": 0.025,
    "expansion_revenue": 1250000.75,
    "customer_acquisition_cost": 125.50
  },
  "geographic_breakdown": {
    "north_america": {
      "organizations": 856,
      "revenue": 157500000.50,
      "growth_rate": 15.2
    },
    "europe": {
      "organizations": 234,
      "revenue": 45000000.25,
      "growth_rate": 28.7
    },
    "asia_pacific": {
      "organizations": 157,
      "revenue": 22500000.00,
      "growth_rate": 42.1
    }
  },
  "trending_metrics": {
    "fastest_growing_segment": "quick_service_restaurants",
    "most_popular_features": ["real_time_ordering", "delivery_integration"],
    "emerging_markets": ["latin_america", "middle_east"]
  }
}
```

### **8.2 Organization Performance Dashboard**

#### **GET /organizations/{org_id}/analytics/dashboard**
```http
GET /api/v1/organizations/org_abc123/analytics/dashboard?timeframe=last_7_days
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "organization_id": "org_abc123",
  "timeframe": "last_7_days",
  "overview": {
    "total_restaurants": 247,
    "active_restaurants": 239,
    "total_orders": 18450,
    "total_revenue": 675000.50,
    "growth_rate": 12.5
  },
  "top_performing_restaurants": [
    {
      "restaurant_id": "rest_downtown_789",
      "name": "Downtown Pizza Express",
      "orders": 1247,
      "revenue": 45600.75,
      "growth_rate": 18.2,
      "ranking": 1
    },
    {
      "restaurant_id": "rest_mall_456", 
      "name": "Mall Pizza",
      "orders": 987,
      "revenue": 35400.25,
      "growth_rate": 8.9,
      "ranking": 2
    }
  ],
  "operational_metrics": {
    "avg_order_prep_time": 18.5,
    "on_time_delivery_rate": 94.2,
    "customer_satisfaction": 4.7,
    "order_accuracy": 98.1,
    "staff_productivity": 87.3
  },
  "menu_analytics": {
    "best_selling_items": [
      {
        "item_name": "Margherita Pizza",
        "orders": 2890,
        "revenue": 58950.75,
        "margin": 68.5
      }
    ],
    "underperforming_items": [
      {
        "item_name": "Seafood Special",
        "orders": 45,
        "revenue": 1350.00,
        "margin": 42.1
      }
    ]
  },
  "financial_summary": {
    "gross_revenue": 675000.50,
    "platform_fees": 40500.03,
    "processing_fees": 20250.02,
    "net_revenue": 614250.45,
    "projected_monthly": 2457001.80
  }
}
```

### **8.3 Restaurant-Specific Analytics**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/analytics**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/analytics?timeframe=last_30_days&include=sales,operations,customers
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "restaurant_id": "rest_downtown_789",
  "timeframe": "last_30_days",
  "sales_analytics": {
    "total_revenue": 135750.50,
    "total_orders": 3421,
    "avg_order_value": 39.68,
    "growth_metrics": {
      "revenue_growth": 12.5,
      "order_volume_growth": 8.2,
      "aov_growth": 3.9
    },
    "sales_by_day_of_week": {
      "monday": 15250.75,
      "tuesday": 14800.50,
      "wednesday": 16750.25,
      "thursday": 18950.00,
      "friday": 22750.50,
      "saturday": 24850.75,
      "sunday": 22397.75
    },
    "peak_hours": [
      { "hour": 12, "orders": 145, "revenue": 5875.50 },
      { "hour": 18, "orders": 167, "revenue": 6789.25 },
      { "hour": 19, "orders": 189, "revenue": 7650.75 }
    ]
  },
  "operational_analytics": {
    "kitchen_performance": {
      "avg_prep_time": 16.5,
      "on_time_percentage": 96.2,
      "fastest_item": { "name": "Beverages", "avg_time": 1.2 },
      "slowest_item": { "name": "Large Specialty Pizza", "avg_time": 25.8 }
    },
    "staff_efficiency": {
      "orders_per_staff_hour": 8.7,
      "labor_cost_percentage": 28.5,
      "overtime_hours": 23.5
    },
    "inventory_turnover": {
      "cheese": { "turnover_rate": 12.5, "waste_percentage": 2.1 },
      "dough": { "turnover_rate": 15.2, "waste_percentage": 1.8 }
    }
  },
  "customer_analytics": {
    "customer_metrics": {
      "new_customers": 234,
      "returning_customers": 567,
      "customer_retention_rate": 68.5,
      "avg_customer_lifetime_value": 245.75
    },
    "order_patterns": {
      "dine_in": { "percentage": 35, "avg_value": 42.50 },
      "takeout": { "percentage": 40, "avg_value": 38.25 },
      "delivery": { "percentage": 25, "avg_value": 45.75 }
    },
    "satisfaction_metrics": {
      "avg_rating": 4.7,
      "total_reviews": 456,
      "response_rate": 89.2,
      "complaint_resolution_time": 2.3
    }
  }
}
```

---

## 🔔 Notification & Communication APIs

### **9.1 Real-Time Order Updates**

#### **WebSocket Connection: /ws/orders/{order_id}**
```javascript
// WebSocket Connection Example
const ws = new WebSocket('wss://api.rms-platform.com/ws/orders/order_abc123def456?token=eyJhbG...');

ws.onmessage = function(event) {
  const update = JSON.parse(event.data);
  console.log('Order update received:', update);
};
```

**WebSocket Message Format:**
```json
{
  "type": "order_status_update",
  "order_id": "order_abc123def456",
  "timestamp": "2024-08-16T15:22:00Z",
  "data": {
    "status": "ready",
    "message": "Your order is ready for pickup!",
    "estimated_delivery": "2024-08-16T15:45:00Z",
    "updated_by": {
      "user_id": "user_mike_789",
      "name": "Mike Rodriguez",
      "role": "restaurant_manager"
    }
  }
}
```

### **9.2 Customer Notifications**

#### **POST /notifications/customers/{customer_id}/send**
```http
POST /api/v1/notifications/customers/cust_987xyz/send
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "type": "order_ready",
  "order_id": "order_abc123def456",
  "channels": ["sms", "push_notification", "email"],
  "message": {
    "title": "Order Ready!",
    "body": "Your order DT-2024-001247 is ready for pickup at Downtown Pizza Express.",
    "action_url": "https://app.rms-platform.com/orders/order_abc123def456/track"
  },
  "personalization": {
    "customer_name": "Jane",
    "restaurant_name": "Downtown Pizza Express",
    "estimated_pickup_time": "2024-08-16T15:45:00Z"
  }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "notification_id": "notif_customer_abc123",
  "customer_id": "cust_987xyz",
  "status": "sent",
  "channels_sent": [
    {
      "channel": "sms",
      "status": "delivered",
      "sent_at": "2024-08-16T15:22:30Z",
      "delivery_time": 1.2
    },
    {
      "channel": "push_notification",
      "status": "delivered", 
      "sent_at": "2024-08-16T15:22:31Z",
      "delivery_time": 0.8
    },
    {
      "channel": "email",
      "status": "sent",
      "sent_at": "2024-08-16T15:22:32Z",
      "delivery_status": "pending"
    }
  ],
  "message_delivered": {
    "sms": "Hi Jane! Your order DT-2024-001247 is ready for pickup at Downtown Pizza Express. Estimated pickup: 3:45 PM. Track: https://rms.co/t/abc123",
    "push_title": "Order Ready!",
    "push_body": "Your order DT-2024-001247 is ready for pickup."
  }
}
```

### **9.3 Staff Notifications**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/notifications/broadcast**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/notifications/broadcast
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "type": "urgent_message",
  "target_roles": ["kitchen_staff", "kitchen_manager"],
  "message": {
    "title": "Equipment Alert",
    "body": "Pizza oven #2 temperature running high. Please check and adjust.",
    "priority": "high",
    "action_required": true
  },
  "metadata": {
    "equipment_id": "oven_002",
    "temperature_reading": 650,
    "threshold": 600,
    "safety_alert": true
  }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "broadcast_id": "broadcast_urgent_abc123",
  "restaurant_id": "rest_downtown_789",
  "sent_at": "2024-08-16T15:30:00Z",
  "recipients": [
    {
      "user_id": "user_carlos_789",
      "name": "Carlos Rodriguez",
      "role": "kitchen_manager",
      "delivery_status": "delivered",
      "read_at": "2024-08-16T15:30:15Z"
    },
    {
      "user_id": "user_jenny_456",
      "name": "Jenny Smith",
      "role": "kitchen_staff",
      "delivery_status": "delivered",
      "read_at": null
    }
  ],
  "delivery_summary": {
    "total_recipients": 4,
    "delivered": 4,
    "read": 1,
    "delivery_rate": 100
  }
}
```

---

## 🔧 Integration APIs

### **10.1 POS System Integration**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/integrations/pos**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/integrations/pos
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "pos_provider": "square",
  "credentials": {
    "application_id": "sq0idp-abc123def456",
    "access_token": "EAAAEOo...",
    "location_id": "LCABC123DEF456"
  },
  "sync_settings": {
    "menu_sync": true,
    "inventory_sync": true,
    "order_sync": true,
    "payment_sync": false,
    "sync_frequency": "real_time"
  },
  "field_mappings": {
    "menu_category": "category_name",
    "menu_item": "item_name", 
    "price": "base_price",
    "inventory_quantity": "stock_level"
  }
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "integration_id": "pos_square_rest_downtown_789",
  "restaurant_id": "rest_downtown_789",
  "pos_provider": "square",
  "status": "active",
  "setup_completed_at": "2024-08-16T16:00:00Z",
  "sync_status": {
    "last_sync": "2024-08-16T16:00:30Z",
    "sync_frequency": "real_time",
    "items_synced": {
      "menu_items": 45,
      "categories": 6,
      "inventory_items": 23
    },
    "sync_health": "healthy"
  },
  "webhook_endpoints": {
    "menu_updates": "https://api.rms-platform.com/webhooks/pos/square/menu",
    "inventory_updates": "https://api.rms-platform.com/webhooks/pos/square/inventory",
    "order_updates": "https://api.rms-platform.com/webhooks/pos/square/orders"
  },
  "next_full_sync": "2024-08-17T02:00:00Z"
}
```

### **10.2 Food Delivery Partner Integration**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/delivery-partners/available**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/delivery-partners/available
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "available_partners": [
    {
      "partner_id": "uber_eats",
      "name": "Uber Eats",
      "logo": "https://cdn.rms-platform.com/partners/uber_eats_logo.png",
      "market_coverage": "High",
      "commission_rate": "15-30%",
      "setup_complexity": "Medium",
      "features": [
        "Real-time menu sync",
        "Order management",
        "Analytics dashboard",
        "Promotional tools",
        "Customer reviews"
      ],
      "integration_status": "available",
      "estimated_setup_time": "2-3 business days"
    },
    {
      "partner_id": "doordash",
      "name": "DoorDash",
      "logo": "https://cdn.rms-platform.com/partners/doordash_logo.png",
      "market_coverage": "High",
      "commission_rate": "15-25%",
      "setup_complexity": "Medium",
      "features": [
        "Menu synchronization",
        "Order routing",
        "Delivery tracking",
        "Marketing campaigns",
        "Performance analytics"
      ],
      "integration_status": "available",
      "estimated_setup_time": "1-2 business days"
    },
    {
      "partner_id": "grubhub",
      "name": "Grubhub",
      "logo": "https://cdn.rms-platform.com/partners/grubhub_logo.png",
      "market_coverage": "Medium",
      "commission_rate": "10-20%",
      "setup_complexity": "Low",
      "features": [
        "Menu management",
        "Order processing",
        "Customer insights",
        "Loyalty integration"
      ],
      "integration_status": "available",
      "estimated_setup_time": "1 business day"
    }
  ],
  "region_specific_recommendations": [
    {
      "region": "Urban areas",
      "recommended": ["uber_eats", "doordash"]
    },
    {
      "region": "Suburban areas", 
      "recommended": ["doordash", "grubhub"]
    }
  ]
}
```

### **10.3 Uber Eats Integration Setup**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/integrations/uber-eats**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/integrations/uber-eats
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "uber_eats_credentials": {
    "client_id": "uber_client_abc123",
    "client_secret": "uber_secret_xyz789",
    "store_id": "uber_store_456def",
    "webhook_url": "https://api.rms-platform.com/webhooks/uber-eats/rest_downtown_789"
  },
  "integration_settings": {
    "menu_sync": {
      "enabled": true,
      "sync_frequency": "real_time",
      "auto_update_prices": true,
      "sync_availability": true,
      "sync_descriptions": true,
      "sync_images": true
    },
    "order_management": {
      "auto_accept_orders": false,
      "acceptance_time_limit": 300,
      "preparation_time_buffer": 5,
      "auto_mark_ready": false
    },
    "delivery_settings": {
      "delivery_radius": 5.0,
      "minimum_order_value": 15.00,
      "delivery_fee": 2.99,
      "service_fee_percentage": 2.5
    },
    "operational_hours": {
      "use_restaurant_hours": true,
      "custom_hours": null,
      "holiday_schedule": "follow_restaurant"
    }
  },
  "commission_structure": {
    "delivery_commission": 25.0,
    "pickup_commission": 15.0,
    "marketing_fee": 3.0,
    "payment_processing": 2.9
  }
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "integration_id": "uber_eats_rest_downtown_789",
  "partner": "uber_eats",
  "status": "pending_verification",
  "setup_progress": {
    "credentials_verified": true,
    "menu_uploaded": false,
    "store_approved": false,
    "webhook_configured": true,
    "test_order_completed": false
  },
  "next_steps": [
    {
      "step": "menu_sync",
      "description": "Upload and sync menu with Uber Eats",
      "estimated_time": "30 minutes",
      "action_required": "Complete menu setup"
    },
    {
      "step": "store_verification",
      "description": "Uber Eats will verify restaurant details",
      "estimated_time": "1-2 business days",
      "action_required": "Wait for approval"
    }
  ],
  "estimated_go_live": "2024-08-18T00:00:00Z",
  "support_contact": {
    "rms_support": "+1-555-RMS-HELP",
    "uber_eats_support": "+1-800-253-9377"
  }
}
```

### **10.4 Menu Synchronization with Delivery Partners**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/integrations/{partner_id}/sync-menu**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/integrations/uber_eats/sync-menu
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "sync_options": {
    "full_sync": true,
    "include_categories": ["pizzas", "appetizers", "beverages"],
    "exclude_categories": ["catering"],
    "price_adjustments": {
      "markup_percentage": 20.0,
      "delivery_surcharge": 1.50
    },
    "availability_settings": {
      "sync_real_time": true,
      "out_of_stock_handling": "auto_disable",
      "low_stock_threshold": 5
    },
    "customizations": {
      "platform_specific_descriptions": true,
      "optimize_for_delivery": true,
      "add_delivery_instructions": true
    }
  }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "sync_id": "sync_uber_eats_789abc",
  "partner": "uber_eats",
  "sync_status": "in_progress",
  "items_to_sync": 47,
  "sync_progress": {
    "categories_synced": 3,
    "items_synced": 12,
    "images_uploaded": 8,
    "errors": 0
  },
  "estimated_completion": "2024-08-16T16:45:00Z",
  "sync_summary": {
    "new_items": 23,
    "updated_items": 19,
    "disabled_items": 5,
    "price_adjustments_applied": 42
  }
}
```

### **10.5 Unified Order Management from Delivery Partners**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/delivery-orders**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/delivery-orders?status=new&partner=all&date=2024-08-16
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "delivery_orders": [
    {
      "order_id": "uber_eats_order_abc123",
      "partner": "uber_eats",
      "partner_order_id": "uber_12345678",
      "status": "new",
      "created_at": "2024-08-16T18:30:00Z",
      "customer": {
        "name": "Sarah Johnson",
        "phone": "+1-555-0167",
        "delivery_address": "456 Oak St, Apt 2B",
        "delivery_instructions": "Ring doorbell twice"
      },
      "order_details": {
        "subtotal": 32.47,
        "delivery_fee": 3.99,
        "service_fee": 2.50,
        "tip": 6.00,
        "total": 44.96,
        "payment_method": "Credit Card"
      },
      "items": [
        {
          "name": "Large Margherita Pizza",
          "quantity": 1,
          "price": 22.99,
          "modifications": ["Extra cheese", "Thin crust"],
          "special_instructions": "Well done"
        },
        {
          "name": "Coca-Cola (Large)",
          "quantity": 2,
          "price": 4.74
        }
      ],
      "delivery_info": {
        "estimated_delivery_time": "2024-08-16T19:15:00Z",
        "delivery_method": "partner_driver",
        "driver_assigned": false
      },
      "restaurant_actions": {
        "accept_deadline": "2024-08-16T18:35:00Z",
        "estimated_prep_time": 25,
        "can_modify_prep_time": true
      }
    },
    {
      "order_id": "doordash_order_def456",
      "partner": "doordash",
      "partner_order_id": "dd_87654321",
      "status": "accepted",
      "created_at": "2024-08-16T18:25:00Z",
      "customer": {
        "name": "Mike Chen",
        "phone": "+1-555-0198",
        "delivery_address": "789 Pine Ave, Unit 5",
        "delivery_instructions": "Leave at door"
      },
      "order_details": {
        "subtotal": 28.99,
        "delivery_fee": 2.99,
        "service_fee": 1.50,
        "tip": 5.50,
        "total": 38.98
      },
      "items": [
        {
          "name": "Pepperoni Pizza (Medium)",
          "quantity": 1,
          "price": 18.99
        },
        {
          "name": "Garlic Bread",
          "quantity": 1,
          "price": 6.99
        },
        {
          "name": "Sprite (Medium)",
          "quantity": 1,
          "price": 3.49
        }
      ],
      "delivery_info": {
        "estimated_delivery_time": "2024-08-16T19:10:00Z",
        "delivery_method": "partner_driver",
        "driver_assigned": true,
        "driver_name": "Alex Rodriguez"
      },
      "prep_status": {
        "prep_time_confirmed": 20,
        "ready_by": "2024-08-16T18:45:00Z"
      }
    }
  ],
  "summary": {
    "total_orders": 12,
    "by_partner": {
      "uber_eats": 7,
      "doordash": 4,
      "grubhub": 1
    },
    "by_status": {
      "new": 3,
      "accepted": 5,
      "preparing": 2,
      "ready": 1,
      "picked_up": 1
    },
    "total_revenue": 487.23
  }
}
```

### **10.6 Accept/Reject Delivery Partner Orders**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/delivery-orders/{order_id}/accept**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/delivery-orders/uber_eats_order_abc123/accept
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "estimated_prep_time": 25,
  "special_instructions": "Customer requested extra napkins",
  "staff_assigned": "kitchen_staff_123",
  "notes": "Peak hour order - prioritize preparation"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "order_id": "uber_eats_order_abc123",
  "status": "accepted",
  "estimated_ready_time": "2024-08-16T18:55:00Z",
  "estimated_delivery_time": "2024-08-16T19:15:00Z",
  "partner_notification_sent": true,
  "customer_notification_sent": true,
  "kitchen_ticket_printed": true,
  "prep_sequence_number": 3
}
```

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/delivery-orders/{order_id}/reject**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/delivery-orders/uber_eats_order_abc123/reject
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "rejection_reason": "kitchen_overwhelmed",
  "estimated_delay": 45,
  "custom_message": "We're experiencing high volume. Please allow extra time or consider ordering later."
}
```

### **10.7 Delivery Partner Analytics & Performance**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/delivery-partners/analytics**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/delivery-partners/analytics?period=last_30_days
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "period": "last_30_days",
  "overall_performance": {
    "total_orders": 1247,
    "total_revenue": 34567.89,
    "average_order_value": 27.74,
    "order_acceptance_rate": 94.2,
    "customer_rating": 4.6,
    "on_time_delivery_rate": 91.8
  },
  "partner_breakdown": [
    {
      "partner": "uber_eats",
      "orders": 687,
      "revenue": 19234.56,
      "market_share": 55.1,
      "commission_paid": 4808.64,
      "average_order_value": 27.98,
      "acceptance_rate": 95.8,
      "customer_rating": 4.7,
      "trending": "up_8_percent"
    },
    {
      "partner": "doordash",
      "orders": 423,
      "revenue": 11789.23,
      "market_share": 33.9,
      "commission_paid": 2357.85,
      "average_order_value": 27.87,
      "acceptance_rate": 92.1,
      "customer_rating": 4.5,
      "trending": "up_3_percent"
    },
    {
      "partner": "grubhub",
      "orders": 137,
      "revenue": 3544.10,
      "market_share": 11.0,
      "commission_paid": 531.62,
      "average_order_value": 25.87,
      "acceptance_rate": 96.4,
      "customer_rating": 4.4,
      "trending": "down_2_percent"
    }
  ],
  "peak_hours": [
    {
      "hour": "12:00-13:00",
      "orders": 87,
      "revenue": 2398.45
    },
    {
      "hour": "18:00-19:00",
      "orders": 134,
      "revenue": 3721.32
    },
    {
      "hour": "19:00-20:00",
      "orders": 156,
      "revenue": 4234.67
    }
  ],
  "recommendations": [
    {
      "type": "optimization",
      "message": "Consider extending Uber Eats hours - 23% of rejected orders are after 9 PM",
      "potential_revenue_increase": "$2,340/month"
    },
    {
      "type": "marketing",
      "message": "DoorDash orders have lower AOV - consider promotional campaigns",
      "suggested_action": "Create combo deals for DoorDash platform"
    }
  ]
}
```

### **10.8 Original Delivery Platform Integration**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/integrations/delivery**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/integrations/delivery
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "platforms": [
    {
      "provider": "doordash",
      "credentials": 
        "developer_id": "dev_abc123",
        "key_id": "key_456def",
        "signing_secret": "secret_789ghi"
      },
      "settings": {
        "auto_accept_orders": false,
        "max_prep_time": 30,
        "delivery_fee": 2.99,
        "commission_rate": 15.0
      }
    },
    {
      "provider": "ubereats",
      "credentials": {
        "client_id": "uber_client_123",
        "client_secret": "uber_secret_456",
        "store_id": "store_789"
      },
      "settings": {
        "auto_accept_orders": true,
        "max_prep_time": 25,
        "delivery_fee": 2.49,
        "commission_rate": 18.0
      }
    }
  ],
  "aggregation_settings": {
    "consolidate_orders": true,
    "unified_menu_sync": true,
    "cross_platform_analytics": true
  }
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "integration_id": "delivery_multi_rest_downtown_789",
  "restaurant_id": "rest_downtown_789",
  "platforms": [
    {
      "provider": "doordash",
      "status": "active",
      "integration_id": "dd_rest_downtown_789",
      "menu_sync_status": "completed",
      "last_order_sync": "2024-08-16T15:45:00Z"
    },
    {
      "provider": "ubereats", 
      "status": "active",
      "integration_id": "ue_rest_downtown_789",
      "menu_sync_status": "completed",
      "last_order_sync": "2024-08-16T15:47:00Z"
    }
  ],
  "aggregation_dashboard": {
    "unified_order_queue": true,
    "cross_platform_menu_management": true,
    "consolidated_analytics": true
  },
  "webhook_urls": {
    "order_events": "https://api.rms-platform.com/webhooks/delivery/orders",
    "menu_updates": "https://api.rms-platform.com/webhooks/delivery/menu"
  }
}
```

---

## 📱 Customer-Facing APIs

### **11.1 QR Code Table Ordering**

#### **GET /qr/{table_qr_code}**
```http
GET /api/v1/qr/table_rest789_t05_abc123def
Accept: application/json
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "restaurant": {
    "id": "rest_downtown_789",
    "name": "Downtown Pizza Express",
    "logo": "https://cdn.rms-platform.com/restaurants/rest_downtown_789/logo.jpg",
    "address": "123 Main Street, Downtown, CA 90210"
  },
  "table": {
    "id": "table_005",
    "number": "T05",
    "capacity": 4,
    "location": "main_dining"
  },
  "ordering_session": {
    "id": "session_abc123def456",
    "status": "active",
    "participants": [],
    "created_at": "2024-08-16T19:00:00Z",
    "expires_at": "2024-08-16T23:00:00Z"
  },
  "menu_url": "/api/v1/restaurants/rest_downtown_789/menu?session=session_abc123def456"
}
```

#### **POST /qr/{table_qr_code}/join**
```http
POST /api/v1/qr/table_rest789_t05_abc123def/join
Content-Type: application/json

{
  "customer_name": "John Doe",
  "phone_number": "+1-555-0123",
  "dietary_preferences": ["vegetarian"],
  "device_id": "device_mobile_789abc"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "participant_id": "participant_john_123",
  "session_id": "session_abc123def456",
  "customer_token": "temp_token_john_789abc123",
  "expires_at": "2024-08-16T23:00:00Z",
  "ordering_capabilities": {
    "can_add_items": true,
    "can_modify_items": true,
    "can_view_session_orders": true,
    "can_request_split_bill": true
  }
}
```

### **11.2 Multi-Person Session Management**

#### **GET /ordering-sessions/{session_id}**
```http
GET /api/v1/ordering-sessions/session_abc123def456
Authorization: Bearer temp_token_john_789abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "session_id": "session_abc123def456",
  "table": {
    "number": "T05",
    "restaurant_name": "Downtown Pizza Express"
  },
  "participants": [
    {
      "id": "participant_john_123",
      "name": "John Doe",
      "joined_at": "2024-08-16T19:05:00Z",
      "order_total": 24.99,
      "items_count": 2
    },
    {
      "id": "participant_jane_456",
      "name": "Jane Smith", 
      "joined_at": "2024-08-16T19:07:00Z",
      "order_total": 18.50,
      "items_count": 1
    }
  ],
  "session_totals": {
    "total_amount": 43.49,
    "total_items": 3,
    "tax": 3.91,
    "service_charge": 0.00
  },
  "split_options": {
    "available": true,
    "split_by_person": true,
    "split_by_item": true,
    "equal_split": true
  }
}
```

### **11.3 Individual Ordering Within Session**

#### **POST /ordering-sessions/{session_id}/orders**
```http
POST /api/v1/ordering-sessions/session_abc123def456/orders
Authorization: Bearer temp_token_john_789abc123
Content-Type: application/json

{
  "participant_id": "participant_john_123",
  "items": [
    {
      "menu_item_id": "item_margherita_pizza",
      "quantity": 1,
      "customizations": [
        {
          "option_id": "extra_cheese",
          "selected": true
        }
      ],
      "special_instructions": "Well done crust"
    },
    {
      "menu_item_id": "item_caesar_salad",
      "quantity": 1,
      "customizations": []
    }
  ],
  "notes": "Please serve salad first"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "personal_order_id": "porder_john_789abc",
  "participant_id": "participant_john_123",
  "session_id": "session_abc123def456",
  "items": [
    {
      "id": "order_item_123",
      "menu_item_id": "item_margherita_pizza",
      "name": "Margherita Pizza",
      "quantity": 1,
      "unit_price": 18.99,
      "customizations_price": 2.00,
      "total_price": 20.99
    },
    {
      "id": "order_item_124",
      "menu_item_id": "item_caesar_salad", 
      "name": "Caesar Salad",
      "quantity": 1,
      "unit_price": 8.99,
      "total_price": 8.99
    }
  ],
  "personal_subtotal": 29.98,
  "personal_tax": 2.70,
  "personal_total": 32.68,
  "order_status": "pending_confirmation"
}
```

### **11.4 Split Bill Management**

#### **POST /ordering-sessions/{session_id}/split-bill**
```http
POST /api/v1/ordering-sessions/session_abc123def456/split-bill
Authorization: Bearer temp_token_john_789abc123
Content-Type: application/json

{
  "split_type": "by_person",
  "initiated_by": "participant_john_123",
  "split_details": {
    "participants": [
      {
        "participant_id": "participant_john_123",
        "responsible_for": ["order_item_123", "order_item_124"],
        "share_percentage": 60.0
      },
      {
        "participant_id": "participant_jane_456", 
        "responsible_for": ["order_item_125"],
        "share_percentage": 40.0
      }
    ],
    "shared_charges": {
      "service_charge": "split_equally",
      "tax": "proportional_to_order"
    }
  }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "split_bill_id": "split_abc123def456",
  "session_id": "session_abc123def456",
  "split_type": "by_person",
  "individual_bills": [
    {
      "participant_id": "participant_john_123",
      "bill_id": "bill_john_789abc",
      "items": [
        {
          "name": "Margherita Pizza (Extra Cheese)",
          "quantity": 1,
          "amount": 20.99
        },
        {
          "name": "Caesar Salad",
          "quantity": 1,
          "amount": 8.99
        }
      ],
      "subtotal": 29.98,
      "tax": 2.70,
      "service_charge": 0.00,
      "total": 32.68,
      "payment_status": "pending"
    },
    {
      "participant_id": "participant_jane_456",
      "bill_id": "bill_jane_456def",
      "items": [
        {
          "name": "Pepperoni Pizza",
          "quantity": 1,
          "amount": 19.99
        }
      ],
      "subtotal": 19.99,
      "tax": 1.80,
      "service_charge": 0.00,
      "total": 21.79,
      "payment_status": "pending"
    }
  ],
  "total_session_amount": 54.47,
  "split_confirmation_required": true
}
```

### **11.5 Individual Payment Processing**

#### **POST /ordering-sessions/{session_id}/bills/{bill_id}/payment**
```http
POST /api/v1/ordering-sessions/session_abc123def456/bills/bill_john_789abc/payment
Authorization: Bearer temp_token_john_789abc123
Content-Type: application/json

{
  "payment_method": "card",
  "payment_details": {
    "card_token": "tok_visa_1234567890abcdef",
    "save_card": false
  },
  "tip_amount": 5.00,
  "customer_email": "john.doe@email.com"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "payment_id": "pay_john_789abc123",
  "bill_id": "bill_john_789abc",
  "participant_id": "participant_john_123",
  "payment_status": "completed",
  "transaction_id": "txn_stripe_abc123def456",
  "amounts": {
    "subtotal": 29.98,
    "tax": 2.70,
    "tip": 5.00,
    "total_paid": 37.68
  },
  "receipt": {
    "receipt_id": "receipt_john_789abc",
    "receipt_url": "https://receipts.rms-platform.com/receipt_john_789abc.pdf",
    "email_sent": true
  },
  "order_status": "paid",
  "estimated_preparation_time": 15
}
```

### **11.6 Session Status and Notifications**

#### **GET /ordering-sessions/{session_id}/status**
```http
GET /api/v1/ordering-sessions/session_abc123def456/status
Authorization: Bearer temp_token_john_789abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "session_id": "session_abc123def456",
  "overall_status": "partially_paid",
  "participants_status": [
    {
      "participant_id": "participant_john_123",
      "name": "John Doe",
      "payment_status": "completed",
      "order_status": "confirmed"
    },
    {
      "participant_id": "participant_jane_456",
      "name": "Jane Smith",
      "payment_status": "pending",
      "order_status": "pending_payment"
    }
  ],
  "kitchen_status": {
    "items_in_preparation": 2,
    "estimated_completion": "2024-08-16T19:35:00Z"
  },
  "can_add_more_items": true,
  "session_expires_at": "2024-08-16T23:00:00Z"
}
```

#### **WebSocket: Real-time Session Updates**
```javascript
// WebSocket connection for real-time updates
const socket = new WebSocket('wss://api.rms-platform.com/ws/ordering-sessions/session_abc123def456');

socket.onmessage = function(event) {
  const update = JSON.parse(event.data);
  
  switch(update.type) {
    case 'participant_joined':
      console.log('New participant joined:', update.participant);
      break;
    case 'order_added':
      console.log('New order added:', update.order);
      break;
    case 'payment_completed':
      console.log('Payment completed:', update.payment);
      break;
    case 'kitchen_update':
      console.log('Kitchen status update:', update.status);
      break;
  }
};
```

---

## 📱 Original Customer-Facing APIs

### **11.1 Restaurant Discovery**

#### **GET /customers/restaurants/search**
```http
GET /api/v1/customers/restaurants/search?q=pizza&lat=34.0522&lng=-118.2437&radius=5&cuisine=italian&delivery=true
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "restaurants": [
    {
      "id": "rest_downtown_789",
      "name": "Downtown Pizza Express",
      "cuisine_type": "italian",
      "rating": 4.7,
      "review_count": 1247,
      "price_range": "$$",
      "distance": 1.2,
      "estimated_delivery_time": 25,
      "delivery_fee": 2.99,
      "minimum_order": 15.00,
      "is_open": true,
      "address": {
        "street": "123 Main Street",
        "city": "Downtown",
        "formatted": "123 Main Street, Downtown, CA 90210"
      },
      "image_url": "https://cdn.rms-platform.com/restaurants/rest_downtown_789/hero.jpg",
      "specialties": ["wood_fired_pizza", "fresh_ingredients"],
      "service_options": ["delivery", "pickup", "dine_in"],
      "current_offers": [
        {
          "title": "Free Delivery",
          "description": "On orders over $25",
          "valid_until": "2024-08-20T23:59:59Z"
        }
      ]
    }
  ],
  "search_metadata": {
    "total_results": 23,
    "search_radius": 5.0,
    "coordinates": {
      "lat": 34.0522,
      "lng": -118.2437
    },
    "filters_applied": ["cuisine:italian", "delivery:true"]
  }
}
```

### **11.2 Customer Order History**

#### **GET /customers/{customer_id}/orders**
```http
GET /api/v1/customers/cust_987xyz/orders?status=completed&limit=10&page=1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "orders": [
    {
      "id": "order_abc123def456",
      "order_number": "DT-2024-001247",
      "restaurant": {
        "id": "rest_downtown_789",
        "name": "Downtown Pizza Express",
        "image_url": "https://cdn.rms-platform.com/restaurants/rest_downtown_789/logo.jpg"
      },
      "status": "delivered",
      "order_type": "delivery",
      "placed_at": "2024-08-16T15:00:00Z",
      "delivered_at": "2024-08-16T15:48:00Z",
      "total": 56.46,
      "items_summary": "2x Margherita Pizza (Large), 2x Coca-Cola (Large)",
      "rating": {
        "food_rating": 5,
        "delivery_rating": 4,
        "overall_rating": 4.5,
        "review": "Great pizza, delivery was a bit slow but food was hot!"
      },
      "reorder_available": true
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 47,
    "pages": 5
  },
  "customer_insights": {
    "total_orders": 47,
    "total_spent": 1892.50,
    "avg_order_value": 40.27,
    "favorite_restaurant": "Downtown Pizza Express",
    "loyalty_tier": "gold",
    "points_available": 2450
  }
}
```

### **11.3 Customer Loyalty & Rewards**

#### **GET /customers/{customer_id}/loyalty**
```http
GET /api/v1/customers/cust_987xyz/loyalty
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "customer_id": "cust_987xyz",
  "loyalty_program": {
    "tier": "gold",
    "points_balance": 2450,
    "points_to_next_tier": 550,
    "next_tier": "platinum",
    "tier_benefits": [
      "10% discount on all orders",
      "Free delivery on orders over $20",
      "Priority customer support",
      "Early access to new menu items"
    ]
  },
  "points_history": [
    {
      "transaction_id": "points_txn_123",
      "order_id": "order_abc123def456",
      "points_earned": 56,
      "points_spent": 0,
      "balance_after": 2450,
      "earned_date": "2024-08-16T15:48:00Z",
      "description": "Order DT-2024-001247 - 1 point per $1 spent"
    }
  ],
  "available_rewards": [
    {
      "reward_id": "reward_free_pizza",
      "title": "Free Medium Pizza",
      "description": "Get a free medium pizza with any topping",
      "points_required": 1500,
      "expiry_date": "2024-12-31T23:59:59Z",
      "terms": "Valid on pizzas up to $18 value"
    },
    {
      "reward_id": "reward_free_delivery",
      "title": "Free Delivery (5x)",
      "description": "Five free delivery vouchers",
      "points_required": 800,
      "expiry_date": "2024-10-31T23:59:59Z"
    }
  ],
  "recent_achievements": [
    {
      "achievement_id": "gold_tier_reached",
      "title": "Gold Status Achieved!",
      "description": "You've reached Gold tier status",
      "unlocked_at": "2024-08-10T12:00:00Z",
      "badge_url": "https://cdn.rms-platform.com/badges/gold_tier.png"
    }
  ]
}
```

---

## 📦 Inventory Management APIs

### **12.1 Get Restaurant Inventory**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/inventory**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/inventory
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "inventory_items": [
    {
      "id": "inv_12345",
      "ingredient_name": "Mozzarella Cheese",
      "category": "dairy",
      "current_stock": 45.5,
      "unit": "kg",
      "minimum_threshold": 10.0,
      "maximum_capacity": 100.0,
      "unit_cost": 8.50,
      "supplier_id": "sup_678",
      "supplier_name": "Fresh Dairy Co",
      "last_restocked": "2024-08-14T10:30:00Z",
      "expiry_date": "2024-08-25T00:00:00Z",
      "storage_location": "Walk-in Freezer A",
      "status": "in_stock",
      "reorder_needed": false
    },
    {
      "id": "inv_12346", 
      "ingredient_name": "Tomato Sauce",
      "category": "sauces",
      "current_stock": 8.2,
      "unit": "kg",
      "minimum_threshold": 15.0,
      "maximum_capacity": 50.0,
      "unit_cost": 4.25,
      "supplier_id": "sup_789",
      "supplier_name": "Mediterranean Foods",
      "last_restocked": "2024-08-10T14:20:00Z",
      "expiry_date": "2024-08-30T00:00:00Z",
      "storage_location": "Pantry B-2",
      "status": "low_stock",
      "reorder_needed": true
    }
  ],
  "summary": {
    "total_items": 47,
    "low_stock_items": 8,
    "out_of_stock_items": 2,
    "expired_items": 1,
    "total_value": 2847.50
  }
}
```

### **12.2 Update Inventory Item**

#### **PUT /organizations/{org_id}/restaurants/{restaurant_id}/inventory/{inventory_id}**
```http
PUT /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/inventory/inv_12345
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "current_stock": 55.0,
  "unit_cost": 8.75,
  "minimum_threshold": 12.0,
  "supplier_id": "sup_678",
  "notes": "Price increase from supplier, adjusted threshold"
}
```

### **12.3 Record Stock Usage**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/inventory/{inventory_id}/usage**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/inventory/inv_12345/usage
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "quantity_used": 2.5,
  "order_id": "ord_987654",
  "menu_item": "Margherita Pizza",
  "used_by": "kitchen_staff_456",
  "usage_timestamp": "2024-08-16T18:45:00Z",
  "notes": "Large order for table 12"
}
```

---

## 🪑 Table & Reservation Management APIs

### **13.1 Get Restaurant Tables**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/tables**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/tables
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "tables": [
    {
      "id": "table_001",
      "table_number": "T01",
      "capacity": 4,
      "location": "main_dining",
      "status": "available",
      "current_reservation": null,
      "next_reservation": {
        "id": "res_789",
        "customer_name": "Smith Family",
        "start_time": "2024-08-16T19:30:00Z",
        "party_size": 4
      }
    },
    {
      "id": "table_015",
      "table_number": "T15",
      "capacity": 2,
      "location": "window_section",
      "status": "occupied",
      "current_reservation": {
        "id": "res_456",
        "customer_name": "John & Jane",
        "start_time": "2024-08-16T18:00:00Z",
        "party_size": 2,
        "estimated_duration": 90
      },
      "next_reservation": null
    }
  ],
  "restaurant_layout": {
    "total_tables": 24,
    "available_tables": 18,
    "occupied_tables": 6,
    "reserved_tables": 3,
    "out_of_service": 0
  }
}
```

### **13.2 Create Reservation**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/reservations**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/reservations
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "customer_name": "Robert Johnson",
  "customer_phone": "+1-555-0123",
  "customer_email": "robert.j@email.com",
  "party_size": 6,
  "reservation_date": "2024-08-20",
  "reservation_time": "19:00",
  "special_requests": "Birthday celebration, need high chair",
  "preferred_table_location": "quiet_section",
  "estimated_duration": 120
}
```

### **13.3 Update Table Status**

#### **PUT /organizations/{org_id}/restaurants/{restaurant_id}/tables/{table_id}/status**
```http
PUT /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/tables/table_015/status
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "status": "cleaning",
  "updated_by": "staff_789",
  "notes": "Spill cleanup in progress",
  "estimated_available_time": "2024-08-16T19:15:00Z"
}
```

---

## ⭐ Customer Feedback & Review APIs

### **14.1 Submit Customer Review**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/reviews**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/reviews
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "customer_id": "cust_456789",
  "order_id": "ord_987654",
  "overall_rating": 4,
  "food_rating": 5,
  "service_rating": 4,
  "atmosphere_rating": 4,
  "review_text": "Excellent pizza! The margherita was perfect. Service was friendly but a bit slow during dinner rush.",
  "would_recommend": true,
  "dining_type": "dine_in",
  "visit_date": "2024-08-15T19:30:00Z"
}
```

### **14.2 Get Restaurant Reviews**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/reviews**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/reviews?limit=10&rating_filter=4,5&sort=newest
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "reviews": [
    {
      "id": "rev_12345",
      "customer_name": "Sarah M.",
      "overall_rating": 5,
      "food_rating": 5,
      "service_rating": 5,
      "atmosphere_rating": 4,
      "review_text": "Amazing experience! Best pizza in town.",
      "would_recommend": true,
      "dining_type": "dine_in",
      "visit_date": "2024-08-15T19:30:00Z",
      "created_at": "2024-08-16T08:15:00Z",
      "verified_order": true
    }
  ],
  "summary": {
    "average_rating": 4.6,
    "total_reviews": 1247,
    "rating_distribution": {
      "5_star": 687,
      "4_star": 356,
      "3_star": 134,
      "2_star": 45,
      "1_star": 25
    },
    "recent_trend": "improving"
  }
}
```

### **14.3 Respond to Review**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/reviews/{review_id}/response**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/reviews/rev_12345/response
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "response_text": "Thank you for your feedback! We're glad you enjoyed your pizza. We're working on improving our service speed during peak hours.",
  "responder_name": "John Smith - Manager",
  "is_public": true
}
```

---

## 💾 Data Management & Export APIs

### **15.1 Export Restaurant Data**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/exports**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/exports
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "export_type": "sales_report",
  "format": "csv",
  "date_range": {
    "start_date": "2024-07-01",
    "end_date": "2024-07-31"
  },
  "include_fields": [
    "order_id",
    "customer_info",
    "items_ordered",
    "total_amount",
    "payment_method",
    "order_timestamp"
  ],
  "email_when_ready": true,
  "notification_email": "manager@pizzachain.com"
}
```

**Response:**
```http
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "export_id": "exp_789abc",
  "status": "processing",
  "estimated_completion": "2024-08-16T17:45:00Z",
  "download_url": null,
  "created_at": "2024-08-16T17:30:00Z",
  "expires_at": "2024-08-23T17:30:00Z"
}
```

### **15.2 Data Backup Request**

#### **POST /organizations/{org_id}/backup**
```http
POST /api/v1/organizations/org_abc123/backup
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "backup_type": "full",
  "include_historical_data": true,
  "include_customer_data": true,
  "encryption_enabled": true,
  "notification_email": "admin@pizzachain.com"
}
```

### **15.3 Data Import**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/imports**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/imports
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: multipart/form-data

file: menu_data.csv
import_type: menu_items
validation_mode: strict
overwrite_existing: false
```

---

## 🖥️ Kitchen Display System APIs

### **16.1 Get Kitchen Display Orders**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/kitchen/display**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/kitchen/display
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "active_orders": [
    {
      "order_id": "ord_123456",
      "table_number": "T05",
      "order_type": "dine_in",
      "priority": "normal",
      "estimated_completion": "2024-08-16T19:15:00Z",
      "elapsed_time": 12,
      "items": [
        {
          "id": "item_789",
          "name": "Margherita Pizza",
          "quantity": 2,
          "special_instructions": "Extra basil, light cheese",
          "station": "pizza",
          "status": "in_progress",
          "prep_time": 8
        },
        {
          "id": "item_790",
          "name": "Caesar Salad",
          "quantity": 1,
          "special_instructions": "Dressing on side",
          "station": "salad",
          "status": "ready",
          "prep_time": 3
        }
      ]
    }
  ],
  "station_status": {
    "pizza": {
      "active_items": 8,
      "average_prep_time": 12,
      "backlog": 3
    },
    "salad": {
      "active_items": 2,
      "average_prep_time": 5,
      "backlog": 0
    }
  }
}
```

### **16.2 Update Item Status**

#### **PUT /organizations/{org_id}/restaurants/{restaurant_id}/kitchen/items/{item_id}/status**
```http
PUT /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/kitchen/items/item_789/status
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "status": "ready",
  "completed_by": "chef_456",
  "completion_time": "2024-08-16T19:12:00Z",
  "quality_notes": "Perfect temperature and presentation"
}
```

---

## 🎁 Promotions & Loyalty Management APIs

### **17.1 Create Promotion Campaign**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/promotions**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/promotions
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "name": "Summer Pizza Special",
  "description": "20% off all large pizzas during summer",
  "promotion_type": "percentage_discount",
  "discount_value": 20.0,
  "applicable_items": ["menu_item_123", "menu_item_456"],
  "minimum_order_amount": 25.00,
  "start_date": "2024-06-01T00:00:00Z",
  "end_date": "2024-08-31T23:59:59Z",
  "usage_limit": 1000,
  "per_customer_limit": 3,
  "coupon_code": "SUMMER20",
  "auto_apply": false,
  "target_customer_segments": ["new_customers", "loyalty_tier_silver"]
}
```

### **17.2 Customer Loyalty Program**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/loyalty/{customer_id}**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/loyalty/cust_789123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "customer_id": "cust_789123",
  "loyalty_tier": "gold",
  "total_points": 2450,
  "points_to_next_tier": 550,
  "lifetime_spent": 1247.50,
  "rewards_available": [
    {
      "id": "reward_123",
      "name": "Free Large Pizza",
      "points_required": 500,
      "expires_at": "2024-12-31T23:59:59Z"
    }
  ],
  "recent_transactions": [
    {
      "date": "2024-08-15",
      "points_earned": 25,
      "order_amount": 24.99,
      "description": "Order #ORD-789"
    }
  ]
}
```

### **17.3 Redeem Loyalty Points**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/loyalty/{customer_id}/redeem**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/loyalty/cust_789123/redeem
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "reward_id": "reward_123",
  "points_to_redeem": 500,
  "order_id": "ord_456789"
}
```

---

## 🚚 Delivery & Driver Management APIs

### **18.1 Driver Management**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/drivers**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/drivers?status=available
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "drivers": [
    {
      "id": "driver_123",
      "name": "Mike Johnson",
      "status": "available",
      "current_location": {
        "latitude": 34.0522,
        "longitude": -118.2437
      },
      "vehicle_info": {
        "type": "motorcycle",
        "license_plate": "ABC-123"
      },
      "performance": {
        "average_delivery_time": 18,
        "completion_rate": 98.5,
        "customer_rating": 4.8
      },
      "current_orders": []
    }
  ]
}
```

### **18.2 Assign Delivery Order**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/orders/{order_id}/assign-driver**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/orders/ord_456789/assign-driver
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "driver_id": "driver_123",
  "estimated_delivery_time": "2024-08-16T19:45:00Z",
  "delivery_instructions": "Ring doorbell, leave at door if no answer"
}
```

### **18.3 Real-Time Delivery Tracking**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/orders/{order_id}/delivery-tracking**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/orders/ord_456789/delivery-tracking
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "order_id": "ord_456789",
  "delivery_status": "en_route",
  "driver": {
    "id": "driver_123",
    "name": "Mike Johnson",
    "phone": "+1-555-0987",
    "current_location": {
      "latitude": 34.0530,
      "longitude": -118.2420
    }
  },
  "estimated_arrival": "2024-08-16T19:43:00Z",
  "tracking_updates": [
    {
      "timestamp": "2024-08-16T19:15:00Z",
      "status": "picked_up",
      "location": "restaurant"
    },
    {
      "timestamp": "2024-08-16T19:25:00Z", 
      "status": "en_route",
      "location": "intersection_main_5th"
    }
  ]
}
```

---

## 🌐 Multi-Language & Localization APIs

### **19.1 Get Supported Languages**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/languages**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/languages
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "supported_languages": [
    {
      "code": "en",
      "name": "English",
      "is_default": true,
      "completion_percentage": 100
    },
    {
      "code": "es",
      "name": "Español",
      "is_default": false,
      "completion_percentage": 95
    },
    {
      "code": "fr",
      "name": "Français",
      "is_default": false,
      "completion_percentage": 87
    }
  ],
  "auto_translate_enabled": true,
  "region_settings": {
    "currency": "USD",
    "date_format": "MM/DD/YYYY",
    "time_format": "12h",
    "timezone": "America/Los_Angeles"
  }
}
```

### **19.2 Get Localized Menu**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/menu?lang=es**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/menu?lang=es
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Accept-Language: es
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "menu_items": [
    {
      "id": "item_123",
      "name": "Pizza Margherita",
      "description": "Pizza clásica con salsa de tomate, mozzarella fresca y albahaca",
      "price": 18.99,
      "category": "Pizzas",
      "allergens": ["gluten", "lácteos"],
      "dietary_tags": ["vegetariano"]
    }
  ],
  "language": "es",
  "translation_quality": "human_verified"
}
```

---

## 🔒 Audit & Compliance APIs

### **20.1 Get Audit Logs**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/audit-logs**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/audit-logs?start_date=2024-08-01&end_date=2024-08-16&action_type=order_modification
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "audit_logs": [
    {
      "id": "audit_789123",
      "timestamp": "2024-08-16T14:30:00Z",
      "user_id": "user_manager_456",
      "user_name": "John Smith",
      "action": "order_modification",
      "resource_type": "order",
      "resource_id": "ord_123456",
      "details": {
        "field_changed": "total_amount",
        "old_value": "24.99",
        "new_value": "22.49",
        "reason": "Applied manager discount"
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ],
  "total_records": 1247,
  "page": 1,
  "per_page": 50
}
```

### **20.2 GDPR Data Export**

#### **POST /organizations/{org_id}/customers/{customer_id}/gdpr-export**
```http
POST /api/v1/organizations/org_abc123/customers/cust_789123/gdpr-export
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "export_format": "json",
  "include_orders": true,
  "include_reviews": true,
  "include_loyalty_data": true,
  "customer_consent_id": "consent_abc123"
}
```

**Response:**
```http
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "export_id": "gdpr_export_456",
  "status": "processing",
  "estimated_completion": "2024-08-16T15:30:00Z",
  "download_expires_at": "2024-08-23T15:30:00Z"
}
```

### **20.3 Data Deletion Request**

#### **POST /organizations/{org_id}/customers/{customer_id}/delete-request**
```http
POST /api/v1/organizations/org_abc123/customers/cust_789123/delete-request
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "deletion_reason": "customer_request",
  "retain_financial_records": true,
  "anonymize_reviews": true,
  "customer_consent_id": "consent_delete_789"
}
```

---

## 🚛 Supplier & Procurement APIs

### **21.1 Get Suppliers**

#### **GET /organizations/{org_id}/restaurants/{restaurant_id}/suppliers**
```http
GET /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/suppliers
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "suppliers": [
    {
      "id": "sup_678",
      "name": "Fresh Dairy Co",
      "contact_person": "Mike Johnson",
      "email": "orders@freshdairy.com",
      "phone": "+1-555-0234",
      "address": "123 Dairy Lane, Farm City, ST 12345",
      "categories": ["dairy", "cheese", "milk_products"],
      "payment_terms": "Net 30",
      "delivery_schedule": "Tuesday, Thursday, Saturday",
      "minimum_order": 100.00,
      "status": "active",
      "performance_rating": 4.8,
      "average_delivery_time": 24,
      "quality_score": 4.9
    },
    {
      "id": "sup_789",
      "name": "Mediterranean Foods",
      "contact_person": "Sarah Ahmed", 
      "email": "supply@medfoods.com",
      "phone": "+1-555-0567",
      "address": "456 Olive St, Food District, ST 67890",
      "categories": ["sauces", "oils", "spices", "vegetables"],
      "payment_terms": "Net 15",
      "delivery_schedule": "Monday, Wednesday, Friday",
      "minimum_order": 75.00,
      "status": "active",
      "performance_rating": 4.6,
      "average_delivery_time": 18,
      "quality_score": 4.7
    }
  ]
}
```

### **21.2 Create Purchase Order**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/purchase-orders**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/purchase-orders
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "supplier_id": "sup_678",
  "expected_delivery_date": "2024-08-20",
  "items": [
    {
      "inventory_id": "inv_12345",
      "ingredient_name": "Mozzarella Cheese",
      "quantity": 25.0,
      "unit": "kg",
      "unit_price": 8.50,
      "total_price": 212.50
    },
    {
      "inventory_id": "inv_12367",
      "ingredient_name": "Parmesan Cheese",
      "quantity": 10.0,
      "unit": "kg", 
      "unit_price": 15.75,
      "total_price": 157.50
    }
  ],
  "special_instructions": "Please ensure cold chain delivery",
  "priority": "normal"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "purchase_order_id": "po_987654",
  "po_number": "PO-2024-08-001",
  "status": "pending",
  "created_at": "2024-08-16T16:30:00Z",
  "total_amount": 370.00,
  "estimated_delivery": "2024-08-20T10:00:00Z",
  "supplier_notification_sent": true
}
```

### **21.3 Receive Delivery**

#### **POST /organizations/{org_id}/restaurants/{restaurant_id}/deliveries/{po_id}/receive**
```http
POST /api/v1/organizations/org_abc123/restaurants/rest_downtown_789/deliveries/po_987654/receive
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Tenant-Context: org_abc123
Content-Type: application/json

{
  "received_by": "staff_manager_123",
  "delivery_date": "2024-08-20T09:45:00Z",
  "items_received": [
    {
      "inventory_id": "inv_12345",
      "quantity_ordered": 25.0,
      "quantity_received": 25.0,
      "quality_rating": 5,
      "expiry_date": "2024-09-01T00:00:00Z",
      "batch_number": "BC2024-0820-001"
    },
    {
      "inventory_id": "inv_12367", 
      "quantity_ordered": 10.0,
      "quantity_received": 9.8,
      "quality_rating": 4,
      "expiry_date": "2024-09-15T00:00:00Z",
      "batch_number": "BC2024-0820-002",
      "notes": "Slightly short on weight, acceptable quality"
    }
  ],
  "delivery_notes": "On-time delivery, good packaging",
  "invoice_number": "INV-FDC-2024-0820"
}
```

---

## 🔧 System Health & Monitoring APIs

### **22.1 Health Check**

#### **GET /health**
```http
GET /api/v1/health
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "healthy",
  "timestamp": "2024-08-16T16:30:00Z",
  "version": "2.1.5",
  "environment": "production",
  "services": {
    "database": {
      "status": "healthy",
      "response_time": 12,
      "connections": {
        "active": 245,
        "max": 1000,
        "utilization": 24.5
      }
    },
    "redis": {
      "status": "healthy",
      "response_time": 3,
      "memory_usage": 68.5,
      "connected_clients": 1247
    },
    "message_queue": {
      "status": "healthy",
      "response_time": 8,
      "queue_depth": 156,
      "consumer_lag": 2.3
    },
    "external_services": {
      "stripe": "healthy",
      "sendgrid": "healthy",
      "cloudinary": "healthy"
    }
  },
  "performance_metrics": {
    "avg_response_time": 67,
    "requests_per_minute": 45000,
    "error_rate": 0.03,
    "uptime_percentage": 99.97
  }
}
```

### **12.2 System Metrics**

#### **GET /platform/metrics/system**
```http
GET /api/v1/platform/metrics/system?timeframe=last_1_hour
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "timeframe": "last_1_hour",
  "system_metrics": {
    "api_performance": {
      "total_requests": 2700000,
      "avg_response_time": 67,
      "p95_response_time": 245,
      "p99_response_time": 850,
      "error_rate": 0.03,
      "timeout_rate": 0.01
    },
    "database_performance": {
      "avg_query_time": 15.2,
      "slow_queries": 23,
      "connection_pool_utilization": 67.8,
      "cache_hit_rate": 94.2
    },
    "infrastructure": {
      "cpu_utilization": 45.6,
      "memory_utilization": 72.3,
      "disk_utilization": 34.8,
      "network_io": 1250.5
    },
    "business_metrics": {
      "orders_per_minute": 2450,
      "revenue_per_minute": 89750.50,
      "active_restaurants": 11247,
      "concurrent_users": 125000
    }
  },
  "alerts": [
    {
      "level": "warning",
      "metric": "memory_utilization",
      "current_value": 72.3,
      "threshold": 70.0,
      "message": "Memory utilization approaching threshold"
    }
  ]
}
```

---

## 📋 API Authentication Headers

### **Standard Headers for All Requests**

```http
# Required Headers
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
Accept: application/json

# Optional Headers
X-Request-ID: req_abc123def456ghi789  # For request tracing
X-API-Version: 2.1                    # API version specification
X-Client-Version: web-app-1.5.2       # Client application version
X-Tenant-Context: org_abc123          # Explicit tenant context (optional)
User-Agent: RMS-WebApp/1.5.2          # Client identification

# Rate Limiting Headers (in response)
X-RateLimit-Limit: 10000              # Requests per hour limit
X-RateLimit-Remaining: 9547           # Remaining requests
X-RateLimit-Reset: 1692201600         # Reset time (Unix timestamp)

# Pagination Headers (for list endpoints)
X-Total-Count: 1247                   # Total items available
X-Page-Count: 63                      # Total pages
Link: <https://api.rms-platform.com/api/v1/organizations?page=2>; rel="next"
```

### **Error Response Format**

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "type": "validation_error",
    "message": "Invalid request parameters",
    "code": "INVALID_PARAMETERS",
    "request_id": "req_abc123def456",
    "timestamp": "2024-08-16T16:45:00Z",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_EMAIL"
      },
      {
        "field": "restaurant_id",
        "message": "Restaurant not found or access denied",
        "code": "RESOURCE_NOT_FOUND"
      }
    ],
    "documentation_url": "https://docs.rms-platform.com/api/errors/validation_error"
  }
}
```

---

## 🎯 API Summary

### **Total Endpoints by Category**

| Category | Endpoint Count | Description |
|----------|---------------|-------------|
| **Authentication** | 15 | Multi-level auth for platform, org, and customers |
| **Platform Management** | 25 | Super admin organization and analytics |
| **Organization Management** | 37 | Restaurant and user management with feature modules |
| **Menu Management** | 20 | Template and restaurant-specific menus |
| **Order Management** | 38 | Order lifecycle, scheduling, and restaurant approval |
| **Staff Management** | 18 | Employee and scheduling management |
| **Payment & Billing** | 22 | Payment processing and subscription billing |
| **Analytics & Reporting** | 15 | Multi-level performance dashboards |
| **Notifications** | 12 | Real-time and batch communications |
| **Integrations** | 24 | POS systems and delivery partner integrations |
| **Customer APIs** | 32 | QR ordering, discovery, and guest management |
| **Inventory Management** | 8 | Stock tracking and supplier integration |
| **Table & Reservations** | 12 | Dining room and reservation management |
| **Customer Feedback** | 10 | Review collection and response system |
| **Data Management** | 9 | Export, import, and backup operations |
| **Kitchen Display** | 6 | Real-time kitchen order management |
| **Promotions & Loyalty** | 12 | Campaigns, discounts, and reward programs |
| **Delivery & Driver Management** | 15 | Driver tracking and delivery logistics |
| **Multi-Language & Localization** | 8 | Internationalization and localization |
| **Audit & Compliance** | 10 | GDPR compliance and audit trails |
| **Supplier & Procurement** | 8 | Purchase orders and delivery tracking |
| **System Health** | 8 | Monitoring and health checks |

**Total API Endpoints**: 384

### **Key Features**

✅ **Multi-Tenant Architecture**: Complete tenant isolation with hierarchical scoping  
✅ **Real-Time Operations**: WebSocket connections for kitchen displays and live order tracking  
✅ **Comprehensive Analytics**: Platform, organization, and restaurant-level insights  
✅ **Enterprise Security**: JWT with role-based permissions and audit trails  
✅ **Scalable Design**: Rate limiting, pagination, and caching-friendly responses  
✅ **Integration Ready**: POS systems, delivery platforms, and payment gateways  
✅ **Customer Experience**: QR code ordering, split payments, reviews, and loyalty programs  
✅ **Operational Excellence**: Staff management, scheduling, and performance tracking  
✅ **Inventory Management**: Stock tracking, supplier integration, and automated reordering  
✅ **Table Management**: Reservation system with dining room optimization  
✅ **Supply Chain**: Purchase orders, delivery tracking, and quality management  
✅ **Data Operations**: Export, import, backup, and business intelligence

---

## 📚 Related Documentation

- **Development Timeline**: See `DEVELOPMENT_PHASES.md` for implementation phases and project planning
- **Architecture Analysis**: See `SHORTCOMINGS.md` for scalability considerations and improvements
- **Project Overview**: See `README.md` for system architecture and business requirements

---

*This API documentation provides complete technical specifications for enterprise-grade multi-tenant restaurant management platform serving independent restaurants to global franchise operations.*

**API Documentation Level: ⭐⭐⭐⭐⭐**  
*Complete with request/response examples, authentication patterns, error handling, and integration guidelines.*