# 🍽️ Restaurant Management System - Integrated API Test Workflows

## 📋 Overview

This document outlines comprehensive end-to-end workflow tests for all **Phase 1** features of the Restaurant Management System. These workflows simulate real-world user scenarios and verify complete integration between frontend and backend systems.

## 🎯 Test Environment Setup

### **Prerequisites**
- Backend API running on `http://localhost:8000`
- Frontend application running on `http://localhost:3000`
- PostgreSQL database with seeded demo data
- Demo user credentials available

### **Test Data**
- **Manager**: `manager@demorestaurant.com` / `password123`
- **Staff**: `staff@demorestaurant.com` / `password123`
- **Restaurant ID**: `a499f8ac-6307-4a84-ab2c-41ab36361b4c`
- **Organization ID**: `2da4af12-63af-432a-ad0d-51dc68568028`

---

## 🔄 Core Workflow Tests

### **WF-001: Customer Discovery & Menu Viewing**
**Scenario**: Customer discovers restaurant and views menu without creating account

#### **Steps**:
1. **Navigate to Homepage**
   ```
   URL: http://localhost:3000/
   Expected: Restaurant homepage loads with branding
   Verify: Hero section, navigation menu, restaurant info
   ```

2. **View Public Menu**
   ```
   Action: Click "View Menu" or navigate to /menu
   URL: http://localhost:3000/menu
   Expected: Full menu display with categories and items
   API Call: GET /api/v1/menu/public?restaurant_id=...
   Verify: 
   - Categories load from backend
   - Menu items display with prices
   - Availability status shown
   - No authentication required
   ```

3. **Browse Menu Categories**
   ```
   Action: Filter by different categories
   Expected: Menu filters work correctly
   Verify: Items update based on category selection
   ```

#### **Expected Results**:
- ✅ Public menu loads without authentication
- ✅ Real menu data from backend API
- ✅ Responsive design on mobile/desktop
- ✅ Fast loading times (< 2 seconds)

---

### **WF-002: Customer Reservation Creation**
**Scenario**: Customer makes a table reservation through public interface

#### **Steps**:
1. **Navigate to Reservations**
   ```
   URL: http://localhost:3000/book
   Expected: Reservation booking form loads
   Verify: Date picker, time slots, party size selector
   ```

2. **Check Availability**
   ```
   Action: Select date, time, and party size
   API Call: GET /api/v1/public/reservations/{restaurant_id}/availability
   Expected: Available time slots displayed
   Verify: Real-time availability from backend
   ```

3. **Submit Reservation**
   ```
   Action: Fill form and submit reservation
   API Call: POST /api/v1/public/reservations/{restaurant_id}/book
   Form Data:
   - Customer name
   - Phone number
   - Email address
   - Special requests
   Expected: Confirmation message with reservation details
   ```

4. **Verify Reservation Status**
   ```
   Action: Check reservation status (if confirmation link provided)
   API Call: GET /api/v1/public/reservations/{restaurant_id}/status
   Expected: Reservation details displayed
   ```

#### **Expected Results**:
- ✅ Availability check returns real data
- ✅ Reservation creation successful
- ✅ Confirmation details provided
- ✅ Data persisted in backend database

---

### **WF-003: Staff Authentication & Dashboard Access**
**Scenario**: Staff member logs in and accesses management dashboard

#### **Steps**:
1. **Navigate to Login**
   ```
   URL: http://localhost:3000/auth/login
   Expected: Login form displayed
   Verify: Email and password fields
   ```

2. **Staff Login**
   ```
   Action: Login with staff credentials
   Credentials: staff@demorestaurant.com / password123
   API Call: POST /api/v1/auth/login
   Expected: Successful authentication and redirect to dashboard
   Verify: JWT token received and stored
   ```

3. **Access Dashboard**
   ```
   URL: http://localhost:3000/dashboard
   Expected: Dashboard overview with real data
   API Calls: Multiple dashboard data endpoints
   Verify: 
   - Today's statistics
   - Recent reservations
   - Menu status
   - Navigation sidebar
   ```

4. **Check Permissions**
   ```
   Expected: Staff-level access only
   Verify: No admin-only features visible
   ```

#### **Expected Results**:
- ✅ Successful authentication flow
- ✅ Role-based access control
- ✅ Dashboard loads with real backend data
- ✅ Navigation works correctly

---

### **WF-004: Manager Reservation Management**
**Scenario**: Manager reviews and manages customer reservations

#### **Steps**:
1. **Manager Login**
   ```
   Action: Login with manager credentials
   Credentials: manager@demorestaurant.com / password123
   Expected: Full manager access to dashboard
   ```

2. **View Reservations Dashboard**
   ```
   URL: http://localhost:3000/dashboard/reservations
   API Call: GET /api/v1/reservations/
   Expected: List of all reservations with filters
   Verify:
   - Today's reservations highlighted
   - Filter by date, status, party size
   - Search functionality
   ```

3. **Review Individual Reservation**
   ```
   Action: Click on a reservation
   API Call: GET /api/v1/reservations/{reservation_id}
   Expected: Detailed reservation view
   Verify:
   - Customer information
   - Reservation details
   - Special requests
   - Status management options
   ```

4. **Update Reservation Status**
   ```
   Action: Change reservation status (approve/confirm)
   API Call: PUT /api/v1/reservations/{reservation_id}
   Expected: Status updated successfully
   Verify: Real-time status change in UI
   ```

5. **Check Table Assignment**
   ```
   Action: Assign table to reservation
   API Call: POST /api/v1/reservations/{reservation_id}/seat
   Expected: Table assigned successfully
   Verify: Table status updated
   ```

#### **Expected Results**:
- ✅ Manager can view all reservations
- ✅ Reservation status updates work
- ✅ Table assignment functionality
- ✅ Real-time data synchronization

---

### **WF-005: Menu Management & Updates**
**Scenario**: Manager updates menu items and prices

#### **Steps**:
1. **Access Menu Management**
   ```
   URL: http://localhost:3000/dashboard/menu
   API Call: GET /api/v1/menu/items/
   Expected: Menu management interface
   Verify: 
   - List of all menu items
   - Categories organization
   - Availability toggles
   ```

2. **Create New Menu Item**
   ```
   Action: Click "Add New Item"
   API Call: POST /api/v1/menu/items/
   Form Data:
   - Item name
   - Description
   - Price
   - Category
   - Availability status
   Expected: New item created successfully
   ```

3. **Edit Existing Item**
   ```
   Action: Edit an existing menu item
   API Call: PUT /api/v1/menu/items/{item_id}
   Expected: Item updated successfully
   Verify: Changes reflected immediately
   ```

4. **Toggle Item Availability**
   ```
   Action: Enable/disable menu item
   API Call: PUT /api/v1/menu/items/{item_id}/availability
   Expected: Availability status changes
   Verify: Public menu reflects changes
   ```

5. **Delete Menu Item**
   ```
   Action: Delete menu item
   API Call: DELETE /api/v1/menu/items/{item_id}
   Expected: Item removed successfully
   Verify: Item no longer appears in lists
   ```

#### **Expected Results**:
- ✅ Full CRUD operations on menu items
- ✅ Real-time updates to public menu
- ✅ Category management works
- ✅ Availability controls function properly

---

### **WF-006: Availability Checking & Management**
**Scenario**: Check and manage restaurant table availability

#### **Steps**:
1. **View Availability Calendar**
   ```
   URL: http://localhost:3000/dashboard/reservations
   API Call: GET /api/v1/availability/calendar
   Expected: Calendar view with availability
   Verify: 
   - Monthly view with available slots
   - Capacity indicators
   - Booking density visualization
   ```

2. **Check Specific Date Availability**
   ```
   Action: Select specific date and time
   API Call: GET /api/v1/availability/slots
   Expected: Available time slots for selected date
   Verify: Real-time availability calculation
   ```

3. **View Table Layout**
   ```
   Action: Check table management
   API Call: GET /api/v1/tables/
   Expected: Restaurant floor plan or table list
   Verify:
   - Table capacities
   - Current status
   - Location information
   ```

4. **Update Table Status**
   ```
   Action: Change table status (available/occupied/maintenance)
   API Call: PUT /api/v1/tables/{table_id}/status
   Expected: Table status updated
   Verify: Affects availability calculations
   ```

#### **Expected Results**:
- ✅ Accurate availability calculations
- ✅ Real-time table status updates
- ✅ Calendar view functionality
- ✅ Capacity management works

---

### **WF-007: Admin Platform Management**
**Scenario**: Platform admin manages restaurant applications and users

#### **Steps**:
1. **Admin Login**
   ```
   Action: Login with platform admin credentials
   Expected: Platform admin dashboard access
   Verify: Admin-level permissions
   ```

2. **View Restaurant Applications**
   ```
   API Call: GET /api/v1/platform/applications
   Expected: List of pending applications
   Verify:
   - Application details
   - Status tracking
   - Review workflow
   ```

3. **Review Application Details**
   ```
   Action: View specific application
   API Call: GET /api/v1/platform/applications/{application_id}
   Expected: Detailed application information
   Verify: Complete restaurant setup data
   ```

4. **Approve/Reject Application**
   ```
   Action: Make approval decision
   API Call: POST /api/v1/platform/applications/{application_id}/approve
   Expected: Application status updated
   Verify: Restaurant account created (if approved)
   ```

5. **User Management**
   ```
   API Call: GET /api/v1/users/
   Expected: User management interface
   Verify: Role assignments and permissions
   ```

#### **Expected Results**:
- ✅ Platform admin functions work
- ✅ Application approval workflow
- ✅ User management capabilities
- ✅ Proper permission isolation

---

## 🧪 Integration Test Scenarios

### **TS-001: Complete Customer Journey**
**End-to-End Flow**: Customer discovers → views menu → makes reservation → staff manages

#### **Test Steps**:
1. Customer views homepage and menu (no auth required)
2. Customer makes reservation through public interface
3. Staff member logs in and sees new reservation
4. Manager reviews and approves reservation
5. Staff assigns table to reservation
6. Verify all data flows correctly between components

#### **Validation Points**:
- ✅ Data consistency across all interfaces
- ✅ Real-time updates between customer and staff views
- ✅ Proper authentication boundaries
- ✅ Role-based access control enforcement

---

### **TS-002: Menu Update Propagation**
**Real-time Updates**: Menu changes immediately reflect across all interfaces

#### **Test Steps**:
1. Manager updates menu item availability
2. Verify public menu reflects changes immediately
3. Update menu item price
4. Verify customer sees updated pricing
5. Add new menu item
6. Verify item appears in public menu

#### **Validation Points**:
- ✅ Immediate propagation of changes
- ✅ No caching issues
- ✅ Consistent data across interfaces
- ✅ Public menu accuracy

---

### **TS-003: Availability Synchronization**
**Real-time Availability**: Table availability updates across reservation system

#### **Test Steps**:
1. Customer checks availability for specific time
2. Second customer attempts same time slot
3. Staff updates table status
4. Verify availability calculations update
5. Make reservation and verify slot becomes unavailable

#### **Validation Points**:
- ✅ Accurate availability calculations
- ✅ Prevention of double-bookings
- ✅ Real-time status synchronization
- ✅ Capacity management accuracy

---

## 📊 Performance & Load Testing

### **PT-001: API Response Times**
**Target**: All API calls under 500ms, 95th percentile under 1 second

#### **Test Endpoints**:
- GET /api/v1/menu/public (most frequent)
- GET /api/v1/availability/slots (most complex)
- POST /api/v1/reservations/ (most critical)
- GET /api/v1/reservations/ (most data)

#### **Load Conditions**:
- 10 concurrent users (normal operation)
- 50 concurrent users (peak hours)
- 100 concurrent users (stress test)

---

### **PT-002: Frontend Performance**
**Target**: Page load times under 2 seconds

#### **Test Pages**:
- Homepage (/)
- Public menu (/menu)
- Reservation form (/book)
- Dashboard (/dashboard)
- Menu management (/dashboard/menu)

---

## 🔍 Error Handling & Edge Cases

### **EH-001: Network Failure Scenarios**
#### **Test Cases**:
1. **Backend API Down**
   - Expected: Graceful fallback to demo data
   - Verify: User-friendly error messages

2. **Database Connection Lost**
   - Expected: Appropriate error handling
   - Verify: No system crashes

3. **Partial API Failures**
   - Expected: Page components fail gracefully
   - Verify: Other features continue working

### **EH-002: Authentication Edge Cases**
#### **Test Cases**:
1. **Expired JWT Token**
   - Expected: Automatic redirect to login
   - Verify: Session restoration after re-auth

2. **Invalid Permissions**
   - Expected: Access denied with clear messaging
   - Verify: No unauthorized data exposure

3. **Concurrent Login Sessions**
   - Expected: Multiple sessions handled correctly
   - Verify: No session conflicts

---

## 📝 Test Execution Checklist

### **Pre-Test Setup**
- [ ] Backend server running (`http://localhost:8000`)
- [ ] Frontend server running (`http://localhost:3000`)
- [ ] Database seeded with demo data
- [ ] Test user accounts available
- [ ] Network connectivity verified

### **Test Execution**
- [ ] **WF-001**: Customer Discovery & Menu Viewing
- [ ] **WF-002**: Customer Reservation Creation  
- [ ] **WF-003**: Staff Authentication & Dashboard Access
- [ ] **WF-004**: Manager Reservation Management
- [ ] **WF-005**: Menu Management & Updates
- [ ] **WF-006**: Availability Checking & Management
- [ ] **WF-007**: Admin Platform Management

### **Integration Tests**
- [ ] **TS-001**: Complete Customer Journey
- [ ] **TS-002**: Menu Update Propagation
- [ ] **TS-003**: Availability Synchronization

### **Performance Tests**
- [ ] **PT-001**: API Response Times
- [ ] **PT-002**: Frontend Performance

### **Error Handling Tests**
- [ ] **EH-001**: Network Failure Scenarios
- [ ] **EH-002**: Authentication Edge Cases

---

## 🎯 Success Criteria

### **Functional Requirements**
- ✅ All user workflows complete successfully
- ✅ Real-time data synchronization works
- ✅ Authentication and authorization enforced
- ✅ CRUD operations function correctly
- ✅ Public APIs work without authentication

### **Performance Requirements**
- ✅ API response times < 500ms average
- ✅ Page load times < 2 seconds
- ✅ Supports 50+ concurrent users
- ✅ No memory leaks or performance degradation

### **Quality Requirements**
- ✅ Graceful error handling
- ✅ User-friendly error messages
- ✅ Data consistency across interfaces
- ✅ Responsive design on all devices
- ✅ Accessibility compliance

---

## 🚀 Automated Test Suite

### **Test Automation Script**
```bash
# Frontend automated test execution
cd frontend
npm run test:integration

# Backend API testing
cd ../
python -m pytest tests/integration/

# End-to-end testing
npm run test:e2e
```

### **Continuous Integration**
- Automated test execution on every commit
- Performance monitoring on staging environment
- Regression testing for all critical workflows
- Weekly load testing with performance reports

---

## 📈 Reporting & Metrics

### **Test Results Dashboard**
- Pass/fail rates for each workflow
- Performance metrics trending
- Error frequency and types
- User experience metrics

### **Weekly Test Reports**
- Workflow completion rates
- Performance benchmarks
- Bug discovery and resolution
- User feedback integration

This comprehensive testing strategy ensures the Restaurant Management System delivers a reliable, performant, and user-friendly experience across all Phase 1 features.