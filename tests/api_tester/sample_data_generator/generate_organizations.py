#!/usr/bin/env python3
"""
Generate Organizations Test Data

Creates realistic organization data for RMS API testing.
Supports independent restaurants, chains, and franchise operations.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.api_tester.shared.utils import APITestClient, APITestHelper
from tests.api_tester.shared.auth import get_auth_headers
from tests.api_tester.shared.fixtures import RMSTestFixtures


class OrganizationDataGenerator:
    """Generates organization test data via API calls"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.created_organizations = []
        
    async def generate_organization(self, org_type: str = "independent") -> dict:
        """Generate a single organization"""
        
        try:
            # Get authentication headers
            headers = await get_auth_headers(self.client)
            if not headers:
                print("❌ Failed to authenticate - cannot create organizations")
                return None
                
            # Generate organization data
            org_data = RMSTestFixtures.generate_organization_data(org_type)
            
            print(f"🏢 Creating {org_type} organization: {org_data['name']}")
            
            # Create organization via API
            response = await self.client.post("/api/v1/organizations", json=org_data, headers=headers)
            
            if response.status_code == 201:
                org_response = response.json()
                self.created_organizations.append(org_response)
                
                print(f"✅ Organization created successfully:")
                print(f"   ID: {org_response['id']}")
                print(f"   Name: {org_response['name']}")
                print(f"   Type: {org_response['organization_type']}")
                print(f"   Tier: {org_response['subscription_tier']}")
                
                return org_response
                
            elif response.status_code == 404:
                print("⚠️  Organization creation endpoint not found - this is expected in Phase 1")
                print("    Organizations will be auto-created with restaurants")
                return None
                
            else:
                print(f"❌ Failed to create organization: HTTP {response.status_code}")
                if response.json_data:
                    print(f"   Error: {response.json_data}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating organization: {e}")
            return None
            
    async def generate_multiple_organizations(self, scenarios: list = None) -> list:
        """Generate multiple organizations for different scenarios"""
        
        if scenarios is None:
            scenarios = [
                {"type": "independent", "count": 2},
                {"type": "chain", "count": 1}, 
                {"type": "franchise", "count": 1}
            ]
            
        all_organizations = []
        
        for scenario in scenarios:
            org_type = scenario["type"]
            count = scenario["count"]
            
            print(f"\n🏗️  Generating {count} {org_type} organization(s)")
            
            for i in range(count):
                org = await self.generate_organization(org_type)
                if org:
                    all_organizations.append(org)
                    
        return all_organizations
        
    async def cleanup_organizations(self):
        """Clean up created organizations (if deletion is supported)"""
        
        if not self.created_organizations:
            print("🧹 No organizations to clean up")
            return
            
        print(f"\n🧹 Cleaning up {len(self.created_organizations)} created organizations")
        
        try:
            headers = await get_auth_headers(self.client)
            if not headers:
                print("❌ Cannot authenticate for cleanup")
                return
                
            for org in self.created_organizations:
                org_id = org["id"]
                response = await self.client.delete(f"/api/v1/organizations/{org_id}", headers=headers)
                
                if response.status_code == 204:
                    print(f"✅ Deleted organization: {org['name']}")
                elif response.status_code == 404:
                    print(f"⚠️  Organization deletion not supported in current phase")
                    break  # Don't try others
                else:
                    print(f"❌ Failed to delete organization {org['name']}: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            
    def print_summary(self):
        """Print generation summary"""
        
        print(f"\n📊 Organization Generation Summary")
        print(f"{'='*50}")
        print(f"Total Organizations Created: {len(self.created_organizations)}")
        
        if self.created_organizations:
            by_type = {}
            by_tier = {}
            
            for org in self.created_organizations:
                org_type = org["organization_type"]
                tier = org["subscription_tier"]
                
                by_type[org_type] = by_type.get(org_type, 0) + 1
                by_tier[tier] = by_tier.get(tier, 0) + 1
                
            print(f"\nBy Organization Type:")
            for org_type, count in by_type.items():
                print(f"  {org_type.title()}: {count}")
                
            print(f"\nBy Subscription Tier:")
            for tier, count in by_tier.items():
                print(f"  {tier.title()}: {count}")
                
            print(f"\nCreated Organizations:")
            for org in self.created_organizations:
                print(f"  • {org['name']} ({org['organization_type']}, {org['subscription_tier']})")
                print(f"    ID: {org['id']}")
        else:
            print("❌ No organizations were created successfully")
            
    async def run_generation(self):
        """Run the complete organization generation process"""
        
        print("🏢 RMS Organization Data Generator")
        print("="*50)
        
        try:
            # Generate organizations
            organizations = await self.generate_multiple_organizations()
            
            # Print summary
            self.print_summary()
            
            return organizations
            
        except KeyboardInterrupt:
            print("\n⚠️  Generation interrupted by user")
            return []
        except Exception as e:
            print(f"\n❌ Generation failed: {e}")
            return []
        finally:
            # Close the client
            await self.client.close()


async def main():
    """Main entry point for organization data generation"""
    
    generator = OrganizationDataGenerator()
    
    try:
        organizations = await generator.run_generation()
        
        if organizations:
            print(f"\n✅ Successfully generated {len(organizations)} organizations")
            
            # Optionally save to file for other generators
            import json
            output_file = Path(__file__).parent / "generated_organizations.json"
            with open(output_file, 'w') as f:
                json.dump(organizations, f, indent=2, default=str)
            print(f"📁 Organization data saved to: {output_file}")
            
        else:
            print("\n⚠️  No organizations created - this may be expected in Phase 1")
            print("    Organizations are typically auto-created with restaurants")
            
    except Exception as e:
        print(f"❌ Generation process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())