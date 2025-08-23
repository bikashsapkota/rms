#!/usr/bin/env python3
"""
Focused Security Test for Phase 1
Test specific security fixes that were implemented.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def setup_auth():
    """Setup authentication for testing."""
    print("Setting up authentication...")
    
    # First setup a restaurant
    setup_data = {
        "restaurant_name": f"Security Test {int(time.time())}",
        "admin_user": {
            "email": f"security.test.{int(time.time())}@example.com",
            "password": "SecurePassword123!",
            "full_name": "Security Test Admin"
        }
    }
    
    response = requests.post(f"{BASE_URL}/setup", json=setup_data)
    if response.status_code != 200:
        print(f"❌ Setup failed: {response.status_code}")
        return None, None
    
    setup_result = response.json()
    restaurant_id = setup_result["restaurant"]["id"]
    
    # Authenticate
    auth_data = {
        "email": setup_data["admin_user"]["email"],
        "password": setup_data["admin_user"]["password"]
    }
    response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
    if response.status_code != 200:
        print(f"❌ Auth failed: {response.status_code}")
        return None, None
    
    auth_result = response.json()
    token = auth_result["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Authentication setup complete")
    return auth_headers, restaurant_id

def test_xss_protection(auth_headers):
    """Test XSS protection in menu items."""
    print("\n🛡️ Testing XSS Protection...")
    
    # Test script tag
    xss_data = {
        "name": "<script>alert('xss')</script>",
        "description": "<img src=x onerror=alert('xss')>",
        "price": 10.99,
        "is_available": True
    }
    
    response = requests.post(f"{API_BASE}/menu/items/", json=xss_data, headers=auth_headers)
    
    if response.status_code == 422:
        print("✅ XSS Protection Working - Script tags rejected")
        return True
    elif response.status_code in [200, 201]:
        print("❌ XSS Protection Failed - Script tags accepted")
        return False
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")
        return False

def test_negative_price_validation(auth_headers):
    """Test negative price validation."""
    print("\n💰 Testing Negative Price Validation...")
    
    negative_price_data = {
        "name": "Negative Price Item",
        "price": -10.99,
        "is_available": True
    }
    
    response = requests.post(f"{API_BASE}/menu/items/", json=negative_price_data, headers=auth_headers)
    
    if response.status_code == 422:
        print("✅ Negative Price Protection Working")
        return True
    elif response.status_code in [200, 201]:
        print("❌ Negative Price Protection Failed")
        return False
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")
        return False

def test_uuid_validation(auth_headers):
    """Test UUID validation."""
    print("\n🔢 Testing UUID Validation...")
    
    invalid_uuids = ["invalid", "123", "not-a-uuid"]
    results = []
    
    for invalid_uuid in invalid_uuids:
        response = requests.get(f"{API_BASE}/menu/items/{invalid_uuid}", headers=auth_headers)
        
        if response.status_code == 400:
            print(f"✅ UUID Validation Working for '{invalid_uuid}'")
            results.append(True)
        elif response.status_code == 500:
            print(f"❌ UUID Validation Failed for '{invalid_uuid}' - 500 error")
            results.append(False)
        else:
            print(f"⚠️ Unexpected response for '{invalid_uuid}': {response.status_code}")
            results.append(False)
    
    return all(results)

def test_auth_header_handling():
    """Test authentication header handling."""
    print("\n🔐 Testing Auth Header Handling...")
    
    # Missing auth header
    response = requests.get(f"{API_BASE}/menu/categories/")
    
    if response.status_code == 403:
        print("✅ Missing Auth Header Correctly Rejected (403)")
        return True
    elif response.status_code == 401:
        print("✅ Missing Auth Header Correctly Rejected (401)")
        return True
    else:
        print(f"❌ Unexpected response for missing auth: {response.status_code}")
        return False

def main():
    """Run focused security tests."""
    print("🔒 FOCUSED SECURITY TESTING")
    print("=" * 50)
    
    auth_headers, restaurant_id = setup_auth()
    if not auth_headers:
        print("❌ Failed to setup authentication")
        return False
    
    tests = [
        ("XSS Protection", lambda: test_xss_protection(auth_headers)),
        ("Negative Price Validation", lambda: test_negative_price_validation(auth_headers)),
        ("UUID Validation", lambda: test_uuid_validation(auth_headers)),
        ("Auth Header Handling", test_auth_header_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 SECURITY TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All security tests PASSED!")
        return True
    else:
        print("⚠️ Some security tests FAILED!")
        return False

if __name__ == "__main__":
    main()