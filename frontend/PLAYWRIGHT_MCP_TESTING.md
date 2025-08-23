# Playwright MCP Testing Strategy for Restaurant Frontend

## 🎯 Overview

This document outlines the comprehensive testing strategy using **Playwright MCP via Claude Code** for the single restaurant frontend that connects to the multi-tenant backend.

## 🧪 Testing Architecture

```
┌─────────────────────────────────────┐
│           Claude Code               │
│        Playwright MCP               │
│  ┌─────────────────────────────────┐ │
│  │     Browser Automation          │ │
│  │  ┌─────────────┐ ┌─────────────┐ │ │
│  │  │  Customer   │ │   Staff     │ │ │
│  │  │  Journey    │ │ Dashboard   │ │ │
│  │  └─────────────┘ └─────────────┘ │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              │ API Testing
              ▼
┌─────────────────────────────────────┐
│      Multi-Tenant Backend           │
│     (Restaurant Context)            │
└─────────────────────────────────────┘
```

## 🎭 Test Scenarios

### **1. Customer Journey Tests**

#### **A. Restaurant Landing Page**
```typescript
// Test: Customer discovers restaurant
async function testRestaurantDiscovery() {
  await page.goto('/')
  
  // Verify restaurant branding
  await expect(page.locator('[data-testid="restaurant-name"]')).toContainText(process.env.NEXT_PUBLIC_RESTAURANT_NAME)
  
  // Check hero section
  await expect(page.locator('[data-testid="hero-section"]')).toBeVisible()
  
  // Verify operating hours display
  await expect(page.locator('[data-testid="operating-hours"]')).toBeVisible()
  
  // Check call-to-action buttons
  await expect(page.locator('[data-testid="view-menu-cta"]')).toBeVisible()
  await expect(page.locator('[data-testid="book-table-cta"]')).toBeVisible()
  
  // Test photo gallery
  await page.click('[data-testid="photo-gallery"]')
  await expect(page.locator('[data-testid="gallery-modal"]')).toBeVisible()
}
```

#### **B. Public Menu Browsing**
```typescript
async function testMenuBrowsing() {
  await page.goto('/menu')
  
  // Verify menu categories load
  await page.waitForSelector('[data-testid="menu-categories"]')
  
  // Test category filtering
  await page.click('[data-testid="category-appetizers"]')
  await expect(page.locator('[data-testid="menu-items"]')).toContainText('Appetizer')
  
  // Test menu item details
  await page.click('[data-testid="menu-item-first"]')
  await expect(page.locator('[data-testid="item-modal"]')).toBeVisible()
  await expect(page.locator('[data-testid="item-price"]')).toBeVisible()
  await expect(page.locator('[data-testid="item-description"]')).toBeVisible()
  
  // Test dietary restrictions display
  await expect(page.locator('[data-testid="dietary-info"]')).toBeVisible()
  
  // Test search functionality
  await page.fill('[data-testid="menu-search"]', 'pizza')
  await page.waitForTimeout(500) // debounce
  await expect(page.locator('[data-testid="search-results"]')).toContainText('pizza')
}
```

#### **C. Reservation Booking Flow**
```typescript
async function testReservationBooking() {
  await page.goto('/book')
  
  // Test date selection
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  await page.fill('[data-testid="reservation-date"]', tomorrow.toISOString().split('T')[0])
  
  // Test party size selection
  await page.selectOption('[data-testid="party-size"]', '4')
  
  // Wait for available time slots to load
  await page.waitForSelector('[data-testid="time-slots"]')
  
  // Select time slot
  await page.click('[data-testid="time-slot-1900"]')
  
  // Fill customer information
  await page.fill('[data-testid="customer-name"]', 'John Doe')
  await page.fill('[data-testid="customer-email"]', 'john@example.com')
  await page.fill('[data-testid="customer-phone"]', '555-0123')
  await page.fill('[data-testid="special-requests"]', 'Window seat preferred')
  
  // Verify API call includes restaurant context
  const reservationRequest = page.waitForRequest(request => 
    request.url().includes('/api/v1/public/reservations') &&
    request.headers()['x-restaurant-id'] === process.env.NEXT_PUBLIC_RESTAURANT_ID
  )
  
  await page.click('[data-testid="confirm-reservation"]')
  await reservationRequest
  
  // Verify confirmation page
  await expect(page.locator('[data-testid="reservation-confirmation"]')).toBeVisible()
  await expect(page.locator('[data-testid="confirmation-details"]')).toContainText('John Doe')
  await expect(page.locator('[data-testid="confirmation-details"]')).toContainText('4 guests')
}
```

### **2. Staff Dashboard Tests**

#### **A. Staff Authentication**
```typescript
async function testStaffLogin() {
  await page.goto('/auth/login')
  
  // Test invalid credentials
  await page.fill('[data-testid="email"]', 'wrong@email.com')
  await page.fill('[data-testid="password"]', 'wrongpassword')
  await page.click('[data-testid="login-button"]')
  await expect(page.locator('[data-testid="error-message"]')).toBeVisible()
  
  // Test valid staff credentials
  await page.fill('[data-testid="email"]', 'staff@restaurant.com')
  await page.fill('[data-testid="password"]', 'correctpassword')
  
  // Verify API call includes restaurant context
  const loginRequest = page.waitForRequest(request =>
    request.url().includes('/api/v1/auth/login') &&
    request.headers()['x-restaurant-id'] === process.env.NEXT_PUBLIC_RESTAURANT_ID
  )
  
  await page.click('[data-testid="login-button"]')
  await loginRequest
  
  // Verify redirect to dashboard
  await expect(page).toHaveURL('/dashboard')
  await expect(page.locator('[data-testid="staff-name"]')).toBeVisible()
}
```

#### **B. Menu Management**
```typescript
async function testMenuManagement() {
  // Assume already logged in
  await page.goto('/dashboard/menu')
  
  // Test category creation
  await page.click('[data-testid="add-category"]')
  await page.fill('[data-testid="category-name"]', 'Test Category')
  await page.fill('[data-testid="category-description"]', 'Test description')
  await page.click('[data-testid="save-category"]')
  
  // Verify category appears
  await expect(page.locator('[data-testid="category-Test Category"]')).toBeVisible()
  
  // Test menu item creation
  await page.click('[data-testid="add-menu-item"]')
  await page.fill('[data-testid="item-name"]', 'Test Dish')
  await page.fill('[data-testid="item-description"]', 'Delicious test dish')
  await page.fill('[data-testid="item-price"]', '15.99')
  await page.selectOption('[data-testid="item-category"]', 'Test Category')
  
  // Test image upload
  const fileInput = page.locator('[data-testid="item-image-upload"]')
  await fileInput.setInputFiles('test-assets/food-image.jpg')
  
  // Verify API call includes tenant context
  const createItemRequest = page.waitForRequest(request =>
    request.url().includes('/api/v1/menu/items/') &&
    request.method() === 'POST' &&
    request.headers()['x-restaurant-id'] === process.env.NEXT_PUBLIC_RESTAURANT_ID
  )
  
  await page.click('[data-testid="save-item"]')
  await createItemRequest
  
  // Verify item appears in list
  await expect(page.locator('[data-testid="menu-item-Test Dish"]')).toBeVisible()
  
  // Test availability toggle
  await page.click('[data-testid="toggle-availability-Test Dish"]')
  await expect(page.locator('[data-testid="item-status-Test Dish"]')).toContainText('Unavailable')
}
```

#### **C. Reservations Management**
```typescript
async function testReservationsManagement() {
  await page.goto('/dashboard/reservations')
  
  // Verify today's reservations load
  await expect(page.locator('[data-testid="todays-reservations"]')).toBeVisible()
  
  // Test reservation search/filter
  await page.fill('[data-testid="search-reservations"]', 'John')
  await expect(page.locator('[data-testid="reservation-John"]')).toBeVisible()
  
  // Test check-in process
  await page.click('[data-testid="checkin-John"]')
  await expect(page.locator('[data-testid="checkin-confirmation"]')).toBeVisible()
  
  // Test table assignment
  await page.click('[data-testid="assign-table-John"]')
  await page.selectOption('[data-testid="table-selector"]', 'Table 5')
  await page.click('[data-testid="confirm-table-assignment"]')
  await expect(page.locator('[data-testid="assigned-table-John"]')).toContainText('Table 5')
  
  // Test waitlist management
  await page.click('[data-testid="waitlist-tab"]')
  await expect(page.locator('[data-testid="waitlist-entries"]')).toBeVisible()
}
```

### **3. Multi-Tenant API Context Tests**

#### **A. Tenant Isolation Verification**
```typescript
async function testTenantIsolation() {
  // Monitor all API requests
  const apiRequests: any[] = []
  
  page.on('request', request => {
    if (request.url().includes('/api/v1/')) {
      apiRequests.push({
        url: request.url(),
        headers: request.headers(),
        method: request.method()
      })
    }
  })
  
  // Perform various actions
  await page.goto('/menu')
  await page.goto('/dashboard/menu')
  await page.goto('/dashboard/reservations')
  
  // Verify all requests include correct tenant context
  apiRequests.forEach(request => {
    expect(request.headers['x-restaurant-id']).toBe(process.env.NEXT_PUBLIC_RESTAURANT_ID)
    expect(request.headers['x-organization-id']).toBeTruthy()
  })
  
  // Verify no cross-tenant data leakage
  await page.goto('/menu')
  const menuResponse = await page.waitForResponse('/api/v1/menu/public')
  const menuData = await menuResponse.json()
  
  // All menu items should belong to this restaurant
  menuData.items.forEach((item: any) => {
    expect(item.restaurant_id).toBe(process.env.NEXT_PUBLIC_RESTAURANT_ID)
  })
}
```

### **4. Performance & Accessibility Tests**

#### **A. Core Web Vitals**
```typescript
async function testPerformance() {
  // Test SSR pages (SEO-critical)
  const ssrPages = ['/', '/menu', '/book', '/contact']
  
  for (const path of ssrPages) {
    await page.goto(path)
    
    // Measure LCP (Largest Contentful Paint)
    const lcp = await page.evaluate(() => {
      return new Promise(resolve => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries()
          const lastEntry = entries[entries.length - 1]
          resolve(lastEntry.startTime)
        }).observe({ type: 'largest-contentful-paint', buffered: true })
      })
    })
    
    expect(lcp).toBeLessThan(2500) // < 2.5s target
    
    // Measure CLS (Cumulative Layout Shift)
    const cls = await page.evaluate(() => {
      return new Promise(resolve => {
        let clsValue = 0
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += entry.value
            }
          }
          resolve(clsValue)
        }).observe({ type: 'layout-shift', buffered: true })
        
        setTimeout(() => resolve(clsValue), 5000)
      })
    })
    
    expect(cls).toBeLessThan(0.1) // < 0.1 target
  }
}
```

#### **B. Accessibility Testing**
```typescript
async function testAccessibility() {
  const { injectAxe, checkA11y } = require('axe-playwright')
  
  const pagesToTest = ['/', '/menu', '/book', '/dashboard', '/auth/login']
  
  for (const path of pagesToTest) {
    await page.goto(path)
    await injectAxe(page)
    
    // Run axe-core accessibility checks
    const results = await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: { html: true }
    })
    
    // No violations should be found
    expect(results.violations).toHaveLength(0)
  }
  
  // Test keyboard navigation
  await page.goto('/')
  await page.keyboard.press('Tab') // Should focus on first interactive element
  await page.keyboard.press('Enter') // Should activate focused element
  
  // Test screen reader compatibility
  const ariaLabels = await page.locator('[aria-label]').count()
  expect(ariaLabels).toBeGreaterThan(0)
}
```

## 🚀 Test Execution Strategy

### **Development Workflow**
```bash
# 1. Start development server
npm run dev

# 2. Run unit tests first
npm run test

# 3. Use Claude Code Playwright MCP for E2E testing
# Execute test scenarios via Claude Code interface:
# - Customer journey tests
# - Staff dashboard tests  
# - Multi-tenant API validation
# - Performance testing
# - Accessibility audits

# 4. Generate test reports
# - Screenshots on failures
# - Performance metrics
# - Accessibility compliance reports
```

### **Continuous Integration**
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      
      # Unit tests
      - run: npm ci
      - run: npm run test
      
      # Build application
      - run: npm run build
      
      # Start application for E2E testing
      - run: npm run start &
      
      # Playwright MCP E2E tests would be triggered
      # via Claude Code in this environment
```

## 📊 Test Coverage Metrics

### **Target Coverage**
- **Unit Tests**: >80% component coverage
- **E2E Tests**: 100% critical user journeys
- **API Integration**: All tenant-aware endpoints
- **Performance**: All SSR pages < 2.5s LCP
- **Accessibility**: WCAG 2.1 AA compliance
- **Cross-browser**: Chrome, Firefox, Safari, Edge

### **Critical Test Scenarios**
1. ✅ Customer can browse menu and make reservations
2. ✅ Staff can manage menu items and view reservations  
3. ✅ All API calls include correct tenant context
4. ✅ No cross-tenant data leakage occurs
5. ✅ Performance targets are met on all pages
6. ✅ Accessibility standards are maintained
7. ✅ Authentication works with multi-tenant backend
8. ✅ Error handling works correctly

This comprehensive Playwright MCP testing strategy ensures the single restaurant frontend works seamlessly with the multi-tenant backend while providing excellent user experience for both customers and staff.