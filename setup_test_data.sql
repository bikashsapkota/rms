-- Setup minimal test data for restaurant management system
-- This script creates the necessary tables and inserts test data

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(255) NOT NULL,
    organization_type VARCHAR(50) NOT NULL DEFAULT 'single_location',
    subscription_tier VARCHAR(50) NOT NULL DEFAULT 'basic',
    billing_email VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- Restaurants table
CREATE TABLE IF NOT EXISTS restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    address JSONB,
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    cuisine_type VARCHAR(100),
    price_range VARCHAR(50),
    operating_hours JSONB,
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID REFERENCES restaurants(id),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- Menu categories table
CREATE TABLE IF NOT EXISTS menu_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    cover_image_url VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- Menu items table
CREATE TABLE IF NOT EXISTS menu_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id),
    category_id UUID REFERENCES menu_categories(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    image_url VARCHAR(500),
    is_available BOOLEAN NOT NULL DEFAULT true
);

-- Insert test data
-- Organization
INSERT INTO organizations (id, name, organization_type, subscription_tier, billing_email, is_active)
VALUES ('6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'Demo Restaurant Organization', 'single_location', 'basic', 'admin@demorestaurant.com', true)
ON CONFLICT (id) DO NOTHING;

-- Restaurant
INSERT INTO restaurants (id, organization_id, name, slug, description, phone, email, cuisine_type, price_range, is_active)
VALUES ('d6fbbb71-b57e-4dba-9bf6-73125e493e82', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'Demo Restaurant', 'demo-restaurant', 'A fine dining experience with exceptional cuisine', '(555) 123-4567', 'info@demorestaurant.com', 'Modern American', '$$$', true)
ON CONFLICT (id) DO NOTHING;

-- Users
INSERT INTO users (id, organization_id, restaurant_id, email, password_hash, full_name, role, is_active)
VALUES 
('e9870419-4b32-40ad-9e22-f6116ddd4725', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'manager@demorestaurant.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj98.8/C/bDS', 'Demo Manager', 'admin', true),
('a1234567-4b32-40ad-9e22-f6116ddd4725', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'staff@demorestaurant.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj98.8/C/bDS', 'Demo Staff', 'staff', true)
ON CONFLICT (email) DO NOTHING;

-- Menu categories
INSERT INTO menu_categories (id, organization_id, restaurant_id, name, description, sort_order, is_active)
VALUES 
('c1111111-1111-1111-1111-111111111111', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'Appetizers', 'Start your meal with these delicious options', 1, true),
('c2222222-2222-2222-2222-222222222222', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'Main Courses', 'Our signature entrees and hearty dishes', 2, true),
('c3333333-3333-3333-3333-333333333333', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'Desserts', 'Sweet endings to your dining experience', 3, true)
ON CONFLICT (id) DO NOTHING;

-- Menu items
INSERT INTO menu_items (organization_id, restaurant_id, category_id, name, description, price, is_available)
VALUES 
('6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c1111111-1111-1111-1111-111111111111', 'Truffle Arancini', 'Crispy risotto balls with black truffle and parmesan', 16.99, true),
('6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c1111111-1111-1111-1111-111111111111', 'Burrata Salad', 'Fresh burrata with heirloom tomatoes and basil', 18.99, true),
('6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c2222222-2222-2222-2222-222222222222', 'Grilled Salmon', 'Fresh Atlantic salmon with lemon herb butter and seasonal vegetables', 28.99, true),
('6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c2222222-2222-2222-2222-222222222222', 'Ribeye Steak', '12oz prime ribeye with garlic mashed potatoes', 42.99, true),
('6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c3333333-3333-3333-3333-333333333333', 'Chocolate Soufflé', 'Warm chocolate soufflé with vanilla ice cream', 12.99, true),
('6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c3333333-3333-3333-3333-333333333333', 'Tiramisu', 'Classic Italian dessert with espresso and mascarpone', 9.99, true);

-- Print success message
SELECT 'Database setup completed successfully!' AS message;