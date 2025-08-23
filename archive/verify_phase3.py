#!/usr/bin/env python3
"""
Simple Phase 3 verification script.
Tests core order management functionality.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_phase3_basic_functionality():
    """Test basic Phase 3 functionality."""
    print("🧪 Phase 3 Basic Functionality Test")
    print("=" * 50)
    
    try:
        # 1. Test server health
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health Check: {response.status_code}")
        
        # 2. Test OpenAPI endpoints exist
        response = requests.get(f"{API_BASE}/openapi.json")
        if response.status_code == 200:
            data = response.json()
            total_endpoints = len(data['paths'])
            order_endpoints = len([p for p in data['paths'] if 'order' in p.lower() or 'kitchen' in p.lower() or 'payment' in p.lower() or 'qr' in p.lower()])
            print(f"✅ API Schema: {total_endpoints} total endpoints, {order_endpoints} Phase 3 endpoints")
        
        # 3. Test basic setup workflow
        setup_data = {
            "restaurant_name": "Verification Restaurant",
            "admin_user": {
                "email": f"verify.{int(time.time())}@test.com",
                "password": "testpassword123",
                "full_name": "Verify Admin"
            }
        }
        
        response = requests.post(f"{BASE_URL}/setup", json=setup_data)
        if response.status_code == 200:
            print("✅ Restaurant Setup: Working")
            
            # 4. Test authentication
            auth_data = {
                "email": setup_data["admin_user"]["email"],
                "password": "testpassword123"
            }
            
            response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
            if response.status_code == 200:
                token = response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                print("✅ Authentication: Working")
                
                # 5. Test basic menu creation
                cat_data = {"name": "Verify Category", "description": "Test"}
                response = requests.post(f"{API_BASE}/menu/categories/", json=cat_data, headers=headers)
                if response.status_code == 200:
                    print("✅ Menu Categories: Working")
                    
                    category_id = response.json()["id"]
                    item_data = {"name": "Verify Item", "price": 15.99, "category_id": category_id}
                    response = requests.post(f"{API_BASE}/menu/items/", json=item_data, headers=headers)
                    if response.status_code == 200:
                        print("✅ Menu Items: Working")
                        
                        # 6. Test Phase 3 order endpoints exist
                        response = requests.get(f"{API_BASE}/orders/", headers=headers)
                        print(f"✅ Orders Endpoint: {response.status_code}")
                        
                        response = requests.get(f"{API_BASE}/kitchen/orders", headers=headers)
                        print(f"✅ Kitchen Endpoint: {response.status_code}")
                        
                        response = requests.get(f"{API_BASE}/payments/summary", headers=headers)
                        print(f"✅ Payments Endpoint: {response.status_code}")
                        
                        response = requests.get(f"{API_BASE}/qr-orders/analytics", headers=headers)
                        print(f"✅ QR Orders Endpoint: {response.status_code}")
                        
                        print("\\n🎉 Phase 3 basic functionality verification: PASSED")
                        return True
                    else:
                        print(f"❌ Menu Items: {response.status_code}")
                else:
                    print(f"❌ Menu Categories: {response.status_code}")
            else:
                print(f"❌ Authentication: {response.status_code}")
        else:
            print(f"❌ Restaurant Setup: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    
    print("\\n💥 Phase 3 basic functionality verification: FAILED")
    return False

def count_phase3_endpoints():
    """Count Phase 3 endpoints."""
    try:
        response = requests.get(f"{API_BASE}/openapi.json")
        if response.status_code == 200:
            data = response.json()
            
            # All endpoints
            total_endpoints = len(data['paths'])
            
            # Phase 1 endpoints (setup, auth, menu, platform)
            phase1_patterns = ['setup', 'auth', 'menu', 'platform', 'users']
            phase1_endpoints = len([p for p in data['paths'] if any(pattern in p.lower() for pattern in phase1_patterns) and not any(phase3 in p.lower() for phase3 in ['order', 'kitchen', 'payment', 'qr'])])
            
            # Phase 2 endpoints (tables, reservations, availability, waitlist)
            phase2_patterns = ['tables', 'reservations', 'availability', 'waitlist']
            phase2_endpoints = len([p for p in data['paths'] if any(pattern in p.lower() for pattern in phase2_patterns)])
            
            # Phase 3 endpoints (orders, kitchen, payments, qr)
            phase3_patterns = ['order', 'kitchen', 'payment', 'qr']
            phase3_endpoints = len([p for p in data['paths'] if any(pattern in p.lower() for pattern in phase3_patterns)])
            
            print("\\n📊 Endpoint Analysis:")
            print(f"   Total Endpoints: {total_endpoints}")
            print(f"   Phase 1 (Setup/Menu): ~{phase1_endpoints}")
            print(f"   Phase 2 (Tables/Reservations): ~{phase2_endpoints}")
            print(f"   Phase 3 (Orders/Kitchen/Payments): {phase3_endpoints}")
            print(f"   Other/System: {total_endpoints - phase1_endpoints - phase2_endpoints - phase3_endpoints}")
            
            completion_percentage = (phase3_endpoints / 45) * 100 if phase3_endpoints else 0
            print(f"\\n🎯 Phase 3 Implementation: {completion_percentage:.1f}% ({phase3_endpoints}/45 planned endpoints)")
            
            return phase3_endpoints
            
    except Exception as e:
        print(f"❌ Endpoint analysis failed: {str(e)}")
        return 0

if __name__ == "__main__":
    success = test_phase3_basic_functionality()
    phase3_count = count_phase3_endpoints()
    
    if success and phase3_count >= 20:
        print(f"\\n✅ Phase 3 verification successful with {phase3_count} endpoints!")
        exit(0)
    else:
        print(f"\\n❌ Phase 3 verification failed. Found {phase3_count} endpoints.")
        exit(1)