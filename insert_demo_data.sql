-- Insert demo data with proper timestamps

-- Organization
INSERT INTO organizations (id, created_at, updated_at, name, organization_type, subscription_tier, billing_email, is_active)
VALUES ('6bd4089c-3b4c-40f8-98fb-60eaea1db072', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Demo Restaurant Organization', 'single_location', 'basic', 'admin@demorestaurant.com', true)
ON CONFLICT (id) DO NOTHING;

-- Restaurant
INSERT INTO restaurants (id, organization_id, created_at, updated_at, name, phone, email, is_active)
VALUES ('d6fbbb71-b57e-4dba-9bf6-73125e493e82', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Demo Restaurant', '(555) 123-4567', 'info@demorestaurant.com', true)
ON CONFLICT (id) DO NOTHING;

-- Users
INSERT INTO users (id, organization_id, restaurant_id, created_at, updated_at, email, password_hash, full_name, role, is_active)
VALUES 
('e9870419-4b32-40ad-9e22-f6116ddd4725', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'manager@demorestaurant.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj98.8/C/bDS', 'Demo Manager', 'admin', true),
('a1234567-4b32-40ad-9e22-f6116ddd4725', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'staff@demorestaurant.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj98.8/C/bDS', 'Demo Staff', 'staff', true)
ON CONFLICT (email) DO NOTHING;

-- Menu categories
INSERT INTO menu_categories (id, organization_id, restaurant_id, created_at, updated_at, name, description, sort_order, is_active)
VALUES 
('c1111111-1111-1111-1111-111111111111', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Appetizers', 'Start your meal with these delicious options', 1, true),
('c2222222-2222-2222-2222-222222222222', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Main Courses', 'Our signature entrees and hearty dishes', 2, true),
('c3333333-3333-3333-3333-333333333333', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Desserts', 'Sweet endings to your dining experience', 3, true)
ON CONFLICT (id) DO NOTHING;

-- Menu items
INSERT INTO menu_items (id, organization_id, restaurant_id, category_id, created_at, updated_at, name, description, price, is_available)
VALUES 
('11111111-1111-1111-1111-111111111111', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c1111111-1111-1111-1111-111111111111', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Truffle Arancini', 'Crispy risotto balls with black truffle and parmesan', 16.99, true),
('22222222-2222-2222-2222-222222222222', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c1111111-1111-1111-1111-111111111111', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Burrata Salad', 'Fresh burrata with heirloom tomatoes and basil', 18.99, true),
('33333333-3333-3333-3333-333333333333', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c2222222-2222-2222-2222-222222222222', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Grilled Salmon', 'Fresh Atlantic salmon with lemon herb butter and seasonal vegetables', 28.99, true),
('44444444-4444-4444-4444-444444444444', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c2222222-2222-2222-2222-222222222222', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Ribeye Steak', '12oz prime ribeye with garlic mashed potatoes', 42.99, true),
('55555555-5555-5555-5555-555555555555', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c3333333-3333-3333-3333-333333333333', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Chocolate Soufflé', 'Warm chocolate soufflé with vanilla ice cream', 12.99, true),
('66666666-6666-6666-6666-666666666666', '6bd4089c-3b4c-40f8-98fb-60eaea1db072', 'd6fbbb71-b57e-4dba-9bf6-73125e493e82', 'c3333333-3333-3333-3333-333333333333', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Tiramisu', 'Classic Italian dessert with espresso and mascarpone', 9.99, true);

SELECT 'Demo data inserted successfully!' AS message;