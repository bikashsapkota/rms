"""
RMS API Testing Utilities

Core utilities for comprehensive API testing, adapted from ABC API Modular project.
Provides HTTP client, result tracking, and testing helpers for the Restaurant Management System.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import aiohttp
from urllib.parse import urljoin


@dataclass
class TestResult:
    """Represents a single test result"""
    category: str
    test_name: str
    success: bool
    response_time: float = 0.0
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None
    request_data: Optional[Dict] = None
    endpoint: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "category": self.category,
            "test_name": self.test_name,
            "success": self.success,
            "response_time": self.response_time,
            "status_code": self.status_code,
            "error_message": self.error_message,
            "response_data": self.response_data,
            "request_data": self.request_data,
            "endpoint": self.endpoint,
            "timestamp": self.timestamp.isoformat()
        }


class TestResults:
    """Manages and tracks test results throughout testing session"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.execution_time = 0.0
        
    @property
    def total_tests(self) -> int:
        return len(self.results)
        
    @property
    def passed_tests(self) -> int:
        return len([r for r in self.results if r.success])
        
    @property
    def failed_tests(self) -> int:
        return len([r for r in self.results if not r.success])
        
    @property
    def skipped_tests(self) -> int:
        # For now, we don't have explicit skipped tests
        return 0
        
    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 100.0
        return (self.passed_tests / self.total_tests) * 100
        
    @property
    def successes(self) -> List[Dict]:
        """Get successful tests in legacy format for compatibility"""
        return [
            {
                "category": r.category,
                "test": r.test_name,
                "details": r.response_data
            }
            for r in self.results if r.success
        ]
        
    @property
    def failures(self) -> List[Dict]:
        """Get failed tests in legacy format for compatibility"""
        return [
            {
                "category": r.category,
                "test": r.test_name,
                "error": r.error_message or f"Status: {r.status_code}"
            }
            for r in self.results if not r.success
        ]
        
    def add_result(self, result: TestResult):
        """Add a test result"""
        self.results.append(result)
        
    def add_success(self, category: str, test_name: str, details: Optional[Dict] = None):
        """Add a successful test result"""
        result = TestResult(
            category=category,
            test_name=test_name,
            success=True,
            response_data=details
        )
        self.add_result(result)
        
    def add_failure(self, category: str, test_name: str, error: str, 
                   status_code: Optional[int] = None, details: Optional[Dict] = None):
        """Add a failed test result"""
        result = TestResult(
            category=category,
            test_name=test_name,
            success=False,
            error_message=error,
            status_code=status_code,
            response_data=details
        )
        self.add_result(result)
        
    def get_results_by_category(self, category: str) -> List[TestResult]:
        """Get all results for a specific category"""
        return [r for r in self.results if r.category == category]
        
    def get_average_response_time(self, category: Optional[str] = None) -> float:
        """Get average response time for all tests or specific category"""
        relevant_results = self.results
        if category:
            relevant_results = self.get_results_by_category(category)
            
        times = [r.response_time for r in relevant_results if r.response_time > 0]
        return sum(times) / len(times) if times else 0.0
        
    def export_to_json(self, filename: str):
        """Export results to JSON file"""
        data = {
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": self.success_rate,
                "execution_time": self.execution_time,
                "average_response_time": self.get_average_response_time()
            },
            "results": [r.to_dict() for r in self.results]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)


class APITestClient:
    """
    HTTP client specifically designed for RMS API testing
    Provides async HTTP methods with built-in error handling and response tracking
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def _ensure_session(self):
        """Ensure we have an active session"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if endpoint.startswith('http'):
            return endpoint
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
    async def _make_request(self, method: str, endpoint: str, 
                           headers: Optional[Dict] = None,
                           json_data: Optional[Dict] = None,
                           form_data: Optional[Dict] = None,
                           params: Optional[Dict] = None) -> 'APIResponse':
        """Make HTTP request with comprehensive error handling"""
        
        await self._ensure_session()
        url = self._build_url(endpoint)
        
        # Prepare headers
        request_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'RMS-API-Tester/1.0'
        }
        if headers:
            request_headers.update(headers)
            
        # Prepare request kwargs
        kwargs = {
            'headers': request_headers,
            'params': params
        }
        
        # Handle different data types
        if json_data is not None:
            kwargs['json'] = json_data
        elif form_data is not None:
            kwargs['data'] = form_data
            if 'Content-Type' in request_headers:
                # Let aiohttp set the content type for form data
                del request_headers['Content-Type']
                
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                # Read response text
                try:
                    response_text = await response.text()
                except Exception:
                    response_text = ""
                    
                # Try to parse JSON
                response_json = None
                if response_text:
                    try:
                        response_json = json.loads(response_text)
                    except json.JSONDecodeError:
                        pass
                        
                return APIResponse(
                    status_code=response.status,
                    headers=dict(response.headers),
                    text=response_text,
                    json_data=response_json,
                    response_time=response_time,
                    url=str(response.url),
                    method=method
                )
                
        except asyncio.TimeoutError:
            return APIResponse(
                status_code=0,
                headers={},
                text="",
                json_data=None,
                response_time=(time.time() - start_time) * 1000,
                url=url,
                method=method,
                error="Request timeout"
            )
        except Exception as e:
            return APIResponse(
                status_code=0,
                headers={},
                text="",
                json_data=None,
                response_time=(time.time() - start_time) * 1000,
                url=url,
                method=method,
                error=str(e)
            )
            
    async def get(self, endpoint: str, headers: Optional[Dict] = None, 
                  params: Optional[Dict] = None) -> 'APIResponse':
        """Make GET request"""
        return await self._make_request('GET', endpoint, headers=headers, params=params)
        
    async def post(self, endpoint: str, json: Optional[Dict] = None, 
                   data: Optional[Dict] = None, headers: Optional[Dict] = None,
                   params: Optional[Dict] = None) -> 'APIResponse':
        """Make POST request"""
        return await self._make_request('POST', endpoint, headers=headers, 
                                      json_data=json, form_data=data, params=params)
                                      
    async def put(self, endpoint: str, json: Optional[Dict] = None,
                  data: Optional[Dict] = None, headers: Optional[Dict] = None,
                  params: Optional[Dict] = None) -> 'APIResponse':
        """Make PUT request"""
        return await self._make_request('PUT', endpoint, headers=headers,
                                      json_data=json, form_data=data, params=params)
                                      
    async def patch(self, endpoint: str, json: Optional[Dict] = None,
                    data: Optional[Dict] = None, headers: Optional[Dict] = None,
                    params: Optional[Dict] = None) -> 'APIResponse':
        """Make PATCH request"""
        return await self._make_request('PATCH', endpoint, headers=headers,
                                      json_data=json, form_data=data, params=params)
                                      
    async def delete(self, endpoint: str, headers: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> 'APIResponse':
        """Make DELETE request"""
        return await self._make_request('DELETE', endpoint, headers=headers, params=params)
        
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None


@dataclass
class APIResponse:
    """Represents an HTTP response with additional testing utilities"""
    status_code: int
    headers: Dict[str, str]
    text: str
    json_data: Optional[Dict]
    response_time: float
    url: str
    method: str
    error: Optional[str] = None
    
    def json(self) -> Optional[Dict]:
        """Get JSON data (for compatibility with requests library)"""
        return self.json_data
        
    def is_success(self) -> bool:
        """Check if response indicates success"""
        return 200 <= self.status_code < 300
        
    def is_client_error(self) -> bool:
        """Check if response indicates client error"""
        return 400 <= self.status_code < 500
        
    def is_server_error(self) -> bool:
        """Check if response indicates server error"""
        return 500 <= self.status_code < 600
        
    def has_error(self) -> bool:
        """Check if response has any error"""
        return self.error is not None or not self.is_success()
        
    def print_details(self, include_response_body: bool = True):
        """Print detailed response information for debugging"""
        print(f"🌐 HTTP {self.method} {self.url}")
        print(f"📊 Status: {self.status_code}")
        print(f"⏱️  Response Time: {self.response_time:.0f}ms")
        
        if self.error:
            print(f"❌ Error: {self.error}")
            
        if self.headers:
            print(f"📋 Headers: {dict(self.headers)}")
            
        if include_response_body and self.text:
            if self.json_data:
                print(f"📄 Response (JSON):")
                print(json.dumps(self.json_data, indent=2))
            else:
                print(f"📄 Response (Text): {self.text[:500]}...")


class APITestHelper:
    """Helper class with common testing utilities for RMS API"""
    
    @staticmethod
    def validate_restaurant_response(response_data: Dict) -> bool:
        """Validate restaurant data structure"""
        required_fields = ['id', 'name', 'organization_id']
        return all(field in response_data for field in required_fields)
        
    @staticmethod
    def validate_menu_item_response(response_data: Dict) -> bool:
        """Validate menu item data structure"""
        required_fields = ['id', 'name', 'price', 'organization_id', 'restaurant_id']
        return all(field in response_data for field in required_fields)
        
    @staticmethod
    def validate_user_response(response_data: Dict) -> bool:
        """Validate user data structure"""
        required_fields = ['id', 'email', 'role', 'organization_id']
        return all(field in response_data for field in required_fields)
        
    @staticmethod
    def validate_pagination_response(response_data: Dict) -> bool:
        """Validate paginated response structure"""
        if isinstance(response_data, list):
            return True  # Simple list response
            
        required_fields = ['items', 'total', 'page', 'size']
        return all(field in response_data for field in required_fields)
        
    @staticmethod
    def generate_test_restaurant_data(suffix: str = "") -> Dict:
        """Generate test restaurant data"""
        return {
            "name": f"Test Restaurant {suffix}",
            "address": {
                "street": "123 Test Street",
                "city": "Test City",
                "state": "TS",
                "zip_code": "12345",
                "country": "US"
            },
            "phone": "+1-555-TEST",
            "email": f"test{suffix}@restaurant.com",
            "settings": {
                "cuisine_type": "american",
                "price_range": "medium",
                "accepts_reservations": True
            }
        }
        
    @staticmethod
    def generate_test_menu_category_data(suffix: str = "") -> Dict:
        """Generate test menu category data"""
        return {
            "name": f"Test Category {suffix}",
            "description": f"A test menu category {suffix}",
            "sort_order": 1
        }
        
    @staticmethod
    def generate_test_menu_item_data(category_id: str, suffix: str = "") -> Dict:
        """Generate test menu item data"""
        return {
            "name": f"Test Item {suffix}",
            "description": f"A delicious test item {suffix}",
            "price": 12.99,
            "category_id": category_id,
            "is_available": True
        }
        
    @staticmethod
    def generate_test_user_data(suffix: str = "", role: str = "staff") -> Dict:
        """Generate test user data"""
        return {
            "email": f"testuser{suffix}@restaurant.com",
            "full_name": f"Test User {suffix}",
            "role": role,
            "password": "secure_test_password"
        }
        
    @staticmethod
    def extract_id_from_response(response: APIResponse) -> Optional[str]:
        """Extract ID from response data"""
        if response.json_data and 'id' in response.json_data:
            return response.json_data['id']
        return None
        
    @staticmethod
    def print_test_header(title: str, emoji: str = "🧪"):
        """Print formatted test header"""
        print(f"\n{'=' * 60}")
        print(f"{emoji} {title}")
        print(f"{'=' * 60}")
        
    @staticmethod
    def print_test_step(step: str, status: str = "RUNNING"):
        """Print test step with status"""
        status_icons = {
            "RUNNING": "🔄",
            "SUCCESS": "✅",
            "FAILED": "❌",
            "SKIPPED": "⏭️"
        }
        icon = status_icons.get(status, "🔄")
        print(f"{icon} {step}")
        
    @staticmethod
    def assert_response_success(response: APIResponse, test_name: str):
        """Assert that response indicates success and print details"""
        if response.has_error():
            print(f"❌ {test_name} failed:")
            response.print_details()
            return False
        else:
            print(f"✅ {test_name} successful (HTTP {response.status_code}, {response.response_time:.0f}ms)")
            return True
            
    @staticmethod
    def compare_data_fields(expected: Dict, actual: Dict, fields: List[str]) -> bool:
        """Compare specific fields between expected and actual data"""
        for field in fields:
            if field in expected and field in actual:
                if expected[field] != actual[field]:
                    print(f"❌ Field mismatch - {field}: expected {expected[field]}, got {actual[field]}")
                    return False
            elif field in expected:
                print(f"❌ Missing field in response: {field}")
                return False
                
        return True


# Convenience functions for backward compatibility with ABC API tester
async def make_api_request(method: str, endpoint: str, base_url: str = "http://localhost:8000",
                          headers: Optional[Dict] = None, json_data: Optional[Dict] = None) -> APIResponse:
    """Make a single API request (convenience function)"""
    async with APITestClient(base_url) as client:
        if method.upper() == 'GET':
            return await client.get(endpoint, headers=headers)
        elif method.upper() == 'POST':
            return await client.post(endpoint, json=json_data, headers=headers)
        elif method.upper() == 'PUT':
            return await client.put(endpoint, json=json_data, headers=headers)
        elif method.upper() == 'DELETE':
            return await client.delete(endpoint, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")


def print_api_response(response: APIResponse, operation_description: str = "API Request"):
    """Print formatted API response (ABC API tester compatibility)"""
    print(f"\n{'=' * 50}")
    print(f"🍽️  RMS API Test: {operation_description}")
    print(f"Endpoint: {response.method} {response.url}")
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {response.response_time:.0f}ms")
    
    if response.error:
        print(f"Error: {response.error}")
    elif response.json_data:
        print("Response Data:")
        print(json.dumps(response.json_data, indent=2))
    elif response.text:
        print(f"Response Text: {response.text}")
        
    status_emoji = "✅" if response.is_success() else "❌"
    print(f"{status_emoji} {'SUCCESS' if response.is_success() else 'FAILED'}")
    print(f"{'=' * 50}")