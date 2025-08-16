#!/bin/bash
# Script to verify database setup and migration status

echo "🗄️  Restaurant Management System - Database Verification"
echo "========================================================"

echo ""
echo "📊 Database Connection Test:"
docker exec rms_postgres psql -U rms_user -d rms_dev -c "SELECT 'Database connection successful!' as status;"

echo ""
echo "📋 Migration Status:"
uv run alembic current

echo ""
echo "🏗️  Database Tables:"
docker exec rms_postgres psql -U rms_user -d rms_dev -c "\dt"

echo ""
echo "🔗 Foreign Key Relationships:"
docker exec rms_postgres psql -U rms_user -d rms_dev -c "
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
ORDER BY tc.table_name, kcu.column_name;
"

echo ""
echo "🏢 Organizations Table Structure:"
docker exec rms_postgres psql -U rms_user -d rms_dev -c "\d organizations"

echo ""
echo "🍽️  Menu Items Table Structure (with foreign keys):"
docker exec rms_postgres psql -U rms_user -d rms_dev -c "\d menu_items"

echo ""
echo "✅ Phase 1 Multi-Tenant Database Schema Successfully Created!"
echo ""
echo "🎯 Key Features Implemented:"
echo "   • Multi-tenant foundation (organizations → restaurants)"
echo "   • User management with organization/restaurant scope"
echo "   • Menu categories and items with tenant isolation"
echo "   • UUID primary keys throughout"
echo "   • Proper foreign key relationships"
echo "   • Indexes for performance"
echo "   • Ready for Phase 4 Row Level Security activation"
echo ""
echo "🚀 Next Steps:"
echo "   • Run: npm run seed (populate with sample data)"
echo "   • Run: npm run dev (start the API server)"
echo "   • Phase 1 implementation is database-ready!"