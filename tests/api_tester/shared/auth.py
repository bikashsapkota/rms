"""
RMS API Authentication Utilities

Handles JWT authentication for comprehensive API testing.
Adapted from ABC API Modular project's authentication patterns.
"""

import json
from typing import Dict, Optional
from tests.api_tester.shared.utils import APITestClient


# Default test credentials
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_TEST_ADMIN_EMAIL = "admin@testrestaurant.com"
DEFAULT_TEST_ADMIN_PASSWORD = "secure_test_password"

# Alternative credentials for testing
FALLBACK_CREDENTIALS = [
    {"email": "admin@example.com", "password": "iampassword"},
    {"email": "test@restaurant.com", "password": "testpassword"},
    {"email": "manager@pizzapalace.com", "password": "managerpass"},
]


class RMSAuthManager:
    """Manages authentication for RMS API testing"""
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.current_user: Optional[Dict] = None
        self.organization_id: Optional[str] = None
        self.restaurant_id: Optional[str] = None
        
    async def authenticate(self, client: APITestClient, 
                          email: str = DEFAULT_TEST_ADMIN_EMAIL, 
                          password: str = DEFAULT_TEST_ADMIN_PASSWORD) -> bool:
        """Authenticate with the RMS API and store tokens"""
        
        try:
            # Try OAuth2 password flow (FastAPI default)
            auth_data = {
                "username": email,  # FastAPI OAuth2 uses 'username' field
                "password": password
            }
            
            # Try form data first (OAuth2 standard)
            response = await client.post("/auth/login", data=auth_data)
            
            if response.status_code != 200:
                # Try JSON format as fallback
                auth_data = {
                    "email": email,
                    "password": password
                }
                response = await client.post("/auth/login", json=auth_data)
                
            if response.status_code == 200:
                auth_response = response.json()
                
                # Extract tokens (different possible response formats)
                self.access_token = (
                    auth_response.get("access_token") or 
                    auth_response.get("token") or
                    auth_response.get("access")
                )
                
                self.refresh_token = (
                    auth_response.get("refresh_token") or
                    auth_response.get("refresh")
                )
                
                # Extract user info if provided
                self.current_user = (
                    auth_response.get("user") or
                    auth_response.get("profile")
                )
                
                if self.current_user:
                    self.organization_id = self.current_user.get("organization_id")
                    self.restaurant_id = self.current_user.get("restaurant_id")
                    
                return self.access_token is not None
                
            return False
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
            
    async def try_multiple_credentials(self, client: APITestClient) -> bool:
        """Try multiple credential combinations for authentication"""
        
        credentials_to_try = [
            {"email": DEFAULT_TEST_ADMIN_EMAIL, "password": DEFAULT_TEST_ADMIN_PASSWORD}
        ] + FALLBACK_CREDENTIALS
        
        for creds in credentials_to_try:
            if await self.authenticate(client, creds["email"], creds["password"]):
                print(f"✅ Authentication successful with {creds['email']}")
                return True
            else:
                print(f"❌ Authentication failed with {creds['email']}")
                
        return False
        
    async def get_current_user_info(self, client: APITestClient) -> Optional[Dict]:
        """Get current user information"""
        
        if not self.access_token:
            return None
            
        headers = self.get_auth_headers()
        response = await client.get("/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            self.current_user = user_info
            self.organization_id = user_info.get("organization_id")
            self.restaurant_id = user_info.get("restaurant_id")
            return user_info
            
        return None
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        
        if not self.access_token:
            return {}
            
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
    def get_tenant_context(self) -> Dict[str, str]:
        """Get tenant context headers for multi-tenant requests"""
        
        headers = {}
        
        if self.organization_id:
            headers["X-Organization-ID"] = self.organization_id
            
        if self.restaurant_id:
            headers["X-Restaurant-ID"] = self.restaurant_id
            
        return headers
        
    def get_full_headers(self) -> Dict[str, str]:
        """Get complete headers including auth and tenant context"""
        
        headers = self.get_auth_headers()
        headers.update(self.get_tenant_context())
        
        return headers
        
    async def refresh_access_token(self, client: APITestClient) -> bool:
        """Refresh the access token using refresh token"""
        
        if not self.refresh_token:
            return False
            
        try:
            refresh_data = {"refresh_token": self.refresh_token}
            response = await client.post("/auth/refresh", json=refresh_data)
            
            if response.status_code == 200:
                auth_response = response.json()
                self.access_token = (
                    auth_response.get("access_token") or 
                    auth_response.get("token") or
                    auth_response.get("access")
                )
                return self.access_token is not None
                
            return False
            
        except Exception as e:
            print(f"Token refresh error: {e}")
            return False
            
    async def logout(self, client: APITestClient) -> bool:
        """Logout and clear authentication state"""
        
        try:
            if self.access_token:
                headers = self.get_auth_headers()
                await client.post("/auth/logout", headers=headers)
                
        except Exception:
            pass  # Logout errors are not critical
            
        finally:
            # Clear all auth state
            self.access_token = None
            self.refresh_token = None
            self.current_user = None
            self.organization_id = None
            self.restaurant_id = None
            
        return True
        
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        return self.access_token is not None
        
    def print_auth_status(self):
        """Print current authentication status"""
        
        if self.is_authenticated():
            print("🔐 Authentication Status: AUTHENTICATED")
            if self.current_user:
                print(f"   👤 User: {self.current_user.get('email', 'Unknown')}")
                print(f"   🏢 Organization: {self.organization_id or 'None'}")
                print(f"   🍽️  Restaurant: {self.restaurant_id or 'None'}")
                print(f"   👥 Role: {self.current_user.get('role', 'Unknown')}")
        else:
            print("🔐 Authentication Status: NOT AUTHENTICATED")


# Global auth manager instance
_auth_manager = RMSAuthManager()


async def get_auth_headers(client: APITestClient, 
                          email: str = DEFAULT_TEST_ADMIN_EMAIL,
                          password: str = DEFAULT_TEST_ADMIN_PASSWORD) -> Optional[Dict[str, str]]:
    """
    Convenience function to get authentication headers for API testing
    
    Args:
        client: APITestClient instance
        email: Email for authentication
        password: Password for authentication
        
    Returns:
        Dictionary of authentication headers or None if authentication fails
    """
    
    global _auth_manager
    
    # Try to authenticate if not already authenticated
    if not _auth_manager.is_authenticated():
        if not await _auth_manager.try_multiple_credentials(client):
            return None
            
    # Get current user info to ensure we have tenant context
    await _auth_manager.get_current_user_info(client)
    
    return _auth_manager.get_full_headers()


async def authenticate_as_role(client: APITestClient, role: str) -> Optional[Dict[str, str]]:
    """
    Authenticate as a specific role for testing
    
    Args:
        client: APITestClient instance
        role: Role to authenticate as (admin, manager, staff)
        
    Returns:
        Dictionary of authentication headers or None if authentication fails
    """
    
    role_credentials = {
        "admin": {"email": "admin@testrestaurant.com", "password": "secure_test_password"},
        "manager": {"email": "manager@testrestaurant.com", "password": "manager_password"},
        "staff": {"email": "staff@testrestaurant.com", "password": "staff_password"}
    }
    
    if role not in role_credentials:
        print(f"❌ Unknown role: {role}")
        return None
        
    creds = role_credentials[role]
    auth_manager = RMSAuthManager()
    
    if await auth_manager.authenticate(client, creds["email"], creds["password"]):
        await auth_manager.get_current_user_info(client)
        return auth_manager.get_full_headers()
        
    return None


async def test_authentication_flow(client: APITestClient) -> bool:
    """
    Test the complete authentication flow
    
    Args:
        client: APITestClient instance
        
    Returns:
        True if authentication flow works correctly
    """
    
    print("🔐 Testing RMS Authentication Flow")
    print("=" * 50)
    
    auth_manager = RMSAuthManager()
    
    # Test authentication
    print("1. Testing authentication...")
    if await auth_manager.try_multiple_credentials(client):
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
        return False
        
    # Test getting user info
    print("2. Testing user info retrieval...")
    user_info = await auth_manager.get_current_user_info(client)
    if user_info:
        print("✅ User info retrieved successfully")
        auth_manager.print_auth_status()
    else:
        print("❌ Failed to retrieve user info")
        
    # Test authenticated request
    print("3. Testing authenticated API request...")
    headers = auth_manager.get_full_headers()
    response = await client.get("/api/v1/restaurants", headers=headers)
    if response.status_code in [200, 404]:  # 404 is OK if no restaurants exist
        print("✅ Authenticated request successful")
    else:
        print(f"❌ Authenticated request failed: {response.status_code}")
        
    # Test logout
    print("4. Testing logout...")
    if await auth_manager.logout(client):
        print("✅ Logout successful")
    else:
        print("❌ Logout failed")
        
    print("=" * 50)
    print("🔐 Authentication flow test completed")
    
    return True


# Standalone authentication function for Phase 2 tests
async def authenticate_user(session, api_base: str, 
                           email: str = DEFAULT_TEST_ADMIN_EMAIL,
                           password: str = DEFAULT_TEST_ADMIN_PASSWORD) -> Optional[str]:
    """
    Authenticate user and return access token for Phase 2 tests
    
    Args:
        session: aiohttp ClientSession
        api_base: Base API URL (e.g., "http://localhost:8000/api/v1")
        email: Email for authentication
        password: Password for authentication
        
    Returns:
        Access token string or None if authentication fails
    """
    
    try:
        # Try main credentials first
        auth_data = {"email": email, "password": password}
        
        async with session.post(f"{api_base}/auth/login", json=auth_data) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("access_token") or result.get("token")
            
        # Try fallback credentials
        for creds in FALLBACK_CREDENTIALS:
            try:
                async with session.post(f"{api_base}/auth/login", json=creds) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("access_token") or result.get("token")
            except Exception:
                continue
                
        return None
        
    except Exception as e:
        print(f"Authentication error: {e}")
        return None