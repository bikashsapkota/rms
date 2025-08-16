-- Initialize PostgreSQL for RMS Development
-- This script sets up the database with proper extensions and permissions

-- Enable required extensions
-- (Note: test database is in a separate container)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create user role for restaurant operations (Phase 1)
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'restaurant_user_role') THEN
        CREATE ROLE restaurant_user_role;
    END IF;
END $$;

-- Grant bypass RLS for Phase 1 simplicity (will be revoked in Phase 4)
ALTER ROLE restaurant_user_role BYPASSRLS;

-- Grant the role to the main user
GRANT restaurant_user_role TO rms_user;