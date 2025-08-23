#!/usr/bin/env python3
"""
Direct Phase 3 endpoint testing to identify specific issues.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_phase3_endpoints():
    """Test Phase 3 endpoints with proper authentication."""
    
    # 1. Setup restaurant and get auth token
    print("Setting up restaurant and authentication...")
    
    unique_id = int(time.time())
    setup_data = {
        "restaurant_name": "Test Restaurant",
        "admin_user": {
            "email": f"test{unique_id}@example.com",
            "password": "testpass123",
            "full_name": "Test Admin"
        }
    }
    
    response = requests.post(f"{BASE_URL}/setup", json=setup_data)
    if response.status_code != 200:
        print(f"Setup failed: {response.status_code} - {response.text}")
        return False
    
    # 2. Authenticate
    auth_data = {
        "email": f"test{unique_id}@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
    if response.status_code != 200:
        print(f"Auth failed: {response.status_code} - {response.text}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Test individual Phase 3 endpoints
    print("\nTesting Phase 3 endpoints individually:")
    
    endpoints_to_test = [
        ("GET", "/orders/", "List orders"),
        ("GET", "/kitchen/orders", "Kitchen orders"),
        ("GET", "/payments/summary", "Payment summary"),
        ("GET", "/qr-orders/analytics", "QR analytics"),
    ]
    
    for method, endpoint, description in endpoints_to_test:
        print(f"\nTesting {description}: {method} {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error: {response.text}")
            else:
                print("Success!")
                
        except Exception as e:
            print(f"Exception: {e}")
    
    return True

if __name__ == "__main__":
    test_phase3_endpoints()