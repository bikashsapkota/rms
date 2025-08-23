#!/usr/bin/env python3
"""
Database seeder script for development and testing.
Populates the database with sample data.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.database.session import AsyncSessionLocal, create_db_and_tables
from app.shared.models.organization import Organization
from app.shared.models.restaurant import Restaurant
from app.shared.models.user import User
from app.modules.menu.models.category import MenuCategory
from app.modules.menu.models.item import MenuItem
from app.modules.platform.models.application import RestaurantApplication
from app.shared.auth.security import get_password_hash
from data.fixtures.organizations import SAMPLE_ORGANIZATIONS
from data.fixtures.restaurants import SAMPLE_RESTAURANTS
from data.fixtures.users import SAMPLE_USERS
from data.fixtures.categories import SAMPLE_CATEGORIES_BY_RESTAURANT
from data.fixtures.items import SAMPLE_ITEMS_BY_RESTAURANT


class DatabaseSeeder:
    """Database seeder for sample data."""
    
    def __init__(self):
        self.organizations: Dict[str, Organization] = {}
        self.restaurants: Dict[str, Restaurant] = {}
        self.categories: Dict[str, Dict[str, MenuCategory]] = {}
    
    async def seed_all(self):
        """Seed all sample data."""
        print("🌱 Starting database seeding...")
        
        async with AsyncSessionLocal() as session:
            try:
                await self.clear_existing_data(session)
                await self.seed_organizations(session)
                await self.seed_restaurants(session)
                await self.seed_users(session)
                await self.seed_menu_categories(session)
                await self.seed_menu_items(session)
                
                await session.commit()
                print("✅ Database seeding completed successfully!")
                
            except Exception as e:
                await session.rollback()
                print(f"❌ Error seeding database: {e}")
                raise
    
    async def clear_existing_data(self, session: AsyncSession):
        """Clear existing data (for development)."""
        print("🧹 Clearing existing data...")
        
        from sqlmodel import text
        
        # Delete in reverse order due to foreign key constraints
        await session.execute(text("DELETE FROM menu_items"))
        await session.execute(text("DELETE FROM menu_categories"))
        await session.execute(text("DELETE FROM users"))
        await session.execute(text("DELETE FROM restaurants"))
        await session.execute(text("DELETE FROM organizations"))
        
        print("   Cleared existing data")
    
    async def seed_organizations(self, session: AsyncSession):
        """Seed organizations."""
        print("🏢 Seeding organizations...")
        
        for org_data in SAMPLE_ORGANIZATIONS:
            org = Organization(**org_data)
            session.add(org)
            await session.flush()  # Get the ID
            
            self.organizations[org.name] = org
            print(f"   Created organization: {org.name}")
    
    async def seed_restaurants(self, session: AsyncSession):
        """Seed restaurants."""
        print("🏪 Seeding restaurants...")
        
        for rest_data in SAMPLE_RESTAURANTS:
            org_name = rest_data.pop("organization_name")
            organization = self.organizations[org_name]
            
            restaurant = Restaurant(
                **rest_data,
                organization_id=organization.id,
            )
            session.add(restaurant)
            await session.flush()
            
            self.restaurants[restaurant.name] = restaurant
            print(f"   Created restaurant: {restaurant.name}")
    
    async def seed_users(self, session: AsyncSession):
        """Seed users."""
        print("👥 Seeding users...")
        
        for user_data in SAMPLE_USERS:
            # Get organization
            org_name = user_data.pop("organization_name")
            organization = self.organizations[org_name]
            
            # Get restaurant (if specified)
            restaurant_name = user_data.pop("restaurant_name")
            restaurant = self.restaurants.get(restaurant_name) if restaurant_name else None
            
            # Hash password
            password = user_data.pop("password")
            password_hash = get_password_hash(password)
            
            user = User(
                **user_data,
                password_hash=password_hash,
                organization_id=organization.id,
                restaurant_id=restaurant.id if restaurant else None,
            )
            session.add(user)
            
            print(f"   Created user: {user.email} ({user.role})")
    
    async def seed_menu_categories(self, session: AsyncSession):
        """Seed menu categories."""
        print("📂 Seeding menu categories...")
        
        for restaurant_name, categories_data in SAMPLE_CATEGORIES_BY_RESTAURANT.items():
            restaurant = self.restaurants[restaurant_name]
            self.categories[restaurant_name] = {}
            
            for cat_data in categories_data:
                category = MenuCategory(
                    **cat_data,
                    organization_id=restaurant.organization_id,
                    restaurant_id=restaurant.id,
                )
                session.add(category)
                await session.flush()
                
                self.categories[restaurant_name][category.name] = category
                print(f"   Created category: {category.name} ({restaurant_name})")
    
    async def seed_menu_items(self, session: AsyncSession):
        """Seed menu items."""
        print("🍽️ Seeding menu items...")
        
        for restaurant_name, items_data in SAMPLE_ITEMS_BY_RESTAURANT.items():
            restaurant = self.restaurants[restaurant_name]
            restaurant_categories = self.categories[restaurant_name]
            
            for item_data in items_data:
                category_name = item_data.pop("category_name")
                category = restaurant_categories[category_name]
                
                item = MenuItem(
                    **item_data,
                    category_id=category.id,
                    organization_id=restaurant.organization_id,
                    restaurant_id=restaurant.id,
                )
                session.add(item)
                
                print(f"   Created item: {item.name} ({restaurant_name})")


async def main():
    """Main seeder function."""
    print("🚀 Restaurant Management System - Database Seeder")
    print("=" * 50)
    
    # Create tables first
    print("📋 Creating database tables...")
    await create_db_and_tables()
    print("   Database tables created")
    
    # Seed data
    seeder = DatabaseSeeder()
    await seeder.seed_all()
    
    print("\n🎉 Seeding completed! You can now:")
    print("   • Start the API server: uv run uvicorn app.main:app --reload")
    print("   • Run tests: uv run pytest")
    print("   • Login with sample users (password format: role123!):")
    print("     - admin@pizzapalace.com (admin)")
    print("     - manager.downtown@pizzapalace.com (manager)")
    print("     - staff.downtown@pizzapalace.com (staff)")


if __name__ == "__main__":
    asyncio.run(main())