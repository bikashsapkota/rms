#!/bin/bash

# Start development server script

echo "🚀 Starting Restaurant Management System - Development Server"
echo "============================================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: This script must be run from the project root directory"
    echo "   Please run: cd /path/to/rms && ./scripts/start.sh"
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env"
    export $(cat .env | grep -v '#' | xargs)
else
    echo "⚠️  Warning: .env file not found. Using defaults."
    echo "   Copy .env.example to .env and configure as needed."
fi

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv sync

# Run migrations
echo "🔄 Running database migrations..."
uv run alembic upgrade head

# Create demo users (skip only if --no-seed is passed)
if [ "$1" != "--no-seed" ]; then
    echo "🌱 Creating demo users..."
    echo "   (Use --no-seed to skip demo user creation)"
    uv run python -c "
import asyncio
from uuid import uuid4
from sqlmodel import text
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

DATABASE_URL = 'postgresql+asyncpg://rms_user:rms_pass@localhost:5432/rms_dev'
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def ensure_demo_data():
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    org_id = '2da4af12-63af-432a-ad0d-51dc68568028'
    restaurant_id = 'a499f8ac-6307-4a84-ab2c-41ab36361b4c'
    
    try:
        async with AsyncSessionLocal() as session:
            # Create organization if not exists
            result = await session.exec(text('SELECT id FROM organizations WHERE id = :id'), {'id': org_id})
            if not result.first():
                await session.exec(text('''
                    INSERT INTO organizations (id, name, organization_type, subscription_tier, billing_email, is_active, created_at, updated_at)
                    VALUES (:id, :name, :org_type, :tier, :email, :active, NOW(), NOW())
                '''), {
                    'id': org_id,
                    'name': 'Demo Restaurant Organization',
                    'org_type': 'independent',
                    'tier': 'basic',
                    'email': 'billing@demorestaurant.com',
                    'active': True
                })
            
            # Create restaurant if not exists
            result = await session.exec(text('SELECT id FROM restaurants WHERE id = :id'), {'id': restaurant_id})
            if not result.first():
                await session.exec(text('''
                    INSERT INTO restaurants (id, name, organization_id, phone, email, is_active, created_at, updated_at)
                    VALUES (:id, :name, :org_id, :phone, :email, :active, NOW(), NOW())
                '''), {
                    'id': restaurant_id,
                    'name': 'Demo Restaurant',
                    'org_id': org_id,
                    'phone': '+1-555-DEMO',
                    'email': 'info@demorestaurant.com',
                    'active': True
                })
            
            # Create demo users if they don't exist
            users = [
                {'email': 'manager@demorestaurant.com', 'name': 'Demo Manager', 'role': 'manager'},
                {'email': 'staff@demorestaurant.com', 'name': 'Demo Staff', 'role': 'staff'}
            ]
            
            for user_data in users:
                result = await session.exec(text('SELECT id FROM users WHERE email = :email'), {'email': user_data['email']})
                if not result.first():
                    password_hash = pwd_context.hash('password123')
                    await session.exec(text('''
                        INSERT INTO users (id, email, full_name, role, password_hash, organization_id, restaurant_id, is_active, created_at, updated_at)
                        VALUES (:id, :email, :full_name, :role, :password_hash, :org_id, :restaurant_id, :active, NOW(), NOW())
                    '''), {
                        'id': str(uuid4()),
                        'email': user_data['email'],
                        'full_name': user_data['name'],
                        'role': user_data['role'],
                        'password_hash': password_hash,
                        'org_id': org_id,
                        'restaurant_id': restaurant_id,
                        'active': True
                    })
            
            await session.commit()
            print('✅ Demo users ensured')
            
    except Exception as e:
        print(f'⚠️  Error creating demo users: {e}')
    finally:
        await engine.dispose()

asyncio.run(ensure_demo_data())
"
    echo ""
    echo "Demo users available:"
    echo "  • manager@demorestaurant.com (password: password123)"
    echo "  • staff@demorestaurant.com (password: password123)"
    echo ""
fi

# Start the server
echo "🌐 Starting FastAPI development server..."
echo "   API will be available at: http://localhost:8000"
echo "   API docs will be available at: http://localhost:8000/docs"
echo "   Press Ctrl+C to stop the server"
echo ""

uv run uvicorn app.core.app:app --host 0.0.0.0 --port 8000 --reload