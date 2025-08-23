#!/usr/bin/env python3
"""Create demo users for testing."""

import asyncio
from app.shared.database.session import AsyncSessionLocal
from app.shared.models.organization import Organization
from app.shared.models.restaurant import Restaurant  
from app.shared.models.user import User
from app.shared.auth.security import get_password_hash

async def create_demo_users():
    """Create demo users for testing."""
    async with AsyncSessionLocal() as session:
        # Create organization
        org = Organization(
            name='Demo Restaurant Organization',
            description='Demo organization for testing'
        )
        session.add(org)
        await session.flush()
        
        # Create restaurant
        restaurant = Restaurant(
            name='Demo Restaurant',
            description='Demo restaurant for testing',
            organization_id=org.id,
            cuisine_type='International',
            address='123 Demo St',
            phone='555-0123',
            email='info@demorestaurant.com'
        )
        session.add(restaurant)
        await session.flush()
        
        # Create demo users
        users = [
            {
                'email': 'manager@demorestaurant.com',
                'password': 'password123',
                'role': 'manager',
                'first_name': 'Demo',
                'last_name': 'Manager'
            },
            {
                'email': 'staff@demorestaurant.com', 
                'password': 'password123',
                'role': 'staff',
                'first_name': 'Demo',
                'last_name': 'Staff'
            }
        ]
        
        for user_data in users:
            password = user_data.pop('password')
            user = User(
                **user_data,
                password_hash=get_password_hash(password),
                organization_id=org.id,
                restaurant_id=restaurant.id
            )
            session.add(user)
        
        await session.commit()
        print('✅ Demo users created successfully!')
        print(f'   Organization ID: {org.id}')
        print(f'   Restaurant ID: {restaurant.id}')
        print('   Users:')
        print('     - manager@demorestaurant.com (password: password123)')
        print('     - staff@demorestaurant.com (password: password123)')

if __name__ == "__main__":
    asyncio.run(create_demo_users())