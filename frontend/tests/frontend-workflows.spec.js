// @ts-check
const { test, expect } = require('@playwright/test');

// Configuration
const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://localhost:8000';

// Test credentials
const CREDENTIALS = {
  manager: {
    email: 'manager@demorestaurant.com',
    password: 'password123'
  },
  staff: {
    email: 'staff@demorestaurant.com',
    password: 'password123'
  }
};

test.describe('Restaurant Management System - Frontend Workflows', () => {
  test.beforeEach(async ({ page }) => {
    // Set up any global test conditions
    await page.goto(FRONTEND_URL);
  });

  test.describe('WF-001: Customer Discovery & Menu Viewing', () => {
    test('customer can visit homepage and view restaurant information', async ({ page }) => {
      await page.goto(FRONTEND_URL);
      
      // Check homepage loads
      await expect(page).toHaveTitle(/Restaurant|Demo/);
      
      // Check for navigation menu
      await expect(page.locator('nav')).toBeVisible();
      
      // Check for hero section or main content
      const mainContent = page.locator('main, .hero, h1');
      await expect(mainContent).toBeVisible();
    });

    test('customer can navigate to menu page and view menu items', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/menu`);
      
      // Wait for menu page to load
      await page.waitForLoadState('networkidle');
      
      // Check page title
      await expect(page).toHaveTitle(/Menu/);
      
      // Look for menu items (they should be loaded from backend)
      const menuItems = page.locator('[data-testid="menu-item"], .menu-item, .card').first();
      await expect(menuItems).toBeVisible({ timeout: 10000 });
      
      // Check if menu categories are visible
      const categories = page.locator('[data-testid="category"], .category, .menu-category');
      await expect(categories.first()).toBeVisible({ timeout: 5000 });
    });

    test('public menu loads without authentication required', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/menu`);
      
      // Should not be redirected to login
      expect(page.url()).toBe(`${FRONTEND_URL}/menu`);
      
      // Should not show login form
      const loginForm = page.locator('form[action*="login"], input[name="email"]');
      await expect(loginForm).not.toBeVisible();
      
      // Should show menu content
      const menuContent = page.locator('text=/menu|appetizer|main|dessert/i').first();
      await expect(menuContent).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('WF-002: Customer Reservation Creation', () => {
    test('customer can access reservation page', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/book`);
      
      // Check page loads
      await expect(page).toHaveTitle(/Book|Reservation/);
      
      // Look for reservation form elements
      const reservationForm = page.locator('form, [data-testid="reservation-form"]');
      await expect(reservationForm).toBeVisible({ timeout: 10000 });
      
      // Check for date picker or date input
      const dateInput = page.locator('input[type="date"], [data-testid="date-picker"]');
      await expect(dateInput).toBeVisible();
      
      // Check for party size selector
      const partySizeInput = page.locator('input[name*="party"], select[name*="party"], [data-testid="party-size"]');
      await expect(partySizeInput).toBeVisible();
    });

    test('customer can fill out reservation form', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/book`);
      await page.waitForLoadState('networkidle');
      
      // Fill out reservation form
      const nameInput = page.locator('input[name*="name"], input[placeholder*="name" i]').first();
      if (await nameInput.isVisible()) {
        await nameInput.fill('Test Customer');
      }
      
      const emailInput = page.locator('input[name*="email"], input[type="email"]').first();
      if (await emailInput.isVisible()) {
        await emailInput.fill('test@example.com');
      }
      
      const phoneInput = page.locator('input[name*="phone"], input[type="tel"]').first();
      if (await phoneInput.isVisible()) {
        await phoneInput.fill('+1234567890');
      }
      
      // Check that form accepts input
      await expect(nameInput).toHaveValue('Test Customer');
      await expect(emailInput).toHaveValue('test@example.com');
    });
  });

  test.describe('WF-003: Staff Authentication & Dashboard Access', () => {
    test('staff can navigate to login page', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/auth/login`);
      
      // Check login page loads
      await expect(page).toHaveTitle(/Login|Sign/);
      
      // Check for login form
      const loginForm = page.locator('form');
      await expect(loginForm).toBeVisible();
      
      // Check for email and password fields
      const emailField = page.locator('input[name="email"], input[type="email"]');
      const passwordField = page.locator('input[name="password"], input[type="password"]');
      
      await expect(emailField).toBeVisible();
      await expect(passwordField).toBeVisible();
      
      // Check for submit button
      const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")');
      await expect(submitButton).toBeVisible();
    });

    test('staff can login with valid credentials', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/auth/login`);
      await page.waitForLoadState('networkidle');
      
      // Fill login form
      await page.fill('input[name="email"], input[type="email"]', CREDENTIALS.staff.email);
      await page.fill('input[name="password"], input[type="password"]', CREDENTIALS.staff.password);
      
      // Submit form
      await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")');
      
      // Wait for navigation to dashboard
      await page.waitForURL('**/dashboard**', { timeout: 15000 });
      
      // Verify we're on dashboard
      expect(page.url()).toContain('/dashboard');
      
      // Check for dashboard content
      const dashboardContent = page.locator('h1, [data-testid="dashboard"], text=/dashboard|welcome/i').first();
      await expect(dashboardContent).toBeVisible({ timeout: 10000 });
    });

    test('staff can access dashboard after login', async ({ page }) => {
      // Login first
      await page.goto(`${FRONTEND_URL}/auth/login`);
      await page.fill('input[type="email"]', CREDENTIALS.staff.email);
      await page.fill('input[type="password"]', CREDENTIALS.staff.password);
      await page.click('button[type="submit"]');
      
      // Wait for dashboard
      await page.waitForURL('**/dashboard**', { timeout: 15000 });
      
      // Check dashboard elements
      const navigation = page.locator('nav, [role="navigation"], .sidebar');
      await expect(navigation).toBeVisible({ timeout: 10000 });
      
      // Check for dashboard statistics or cards
      const statsCards = page.locator('.card, [data-testid="stat-card"]');
      if (await statsCards.count() > 0) {
        await expect(statsCards.first()).toBeVisible();
      }
    });
  });

  test.describe('WF-004: Manager Reservation Management', () => {
    test.beforeEach(async ({ page }) => {
      // Login as manager before each test
      await page.goto(`${FRONTEND_URL}/auth/login`);
      await page.fill('input[type="email"]', CREDENTIALS.manager.email);
      await page.fill('input[type="password"]', CREDENTIALS.manager.password);
      await page.click('button[type="submit"]');
      await page.waitForURL('**/dashboard**', { timeout: 15000 });
    });

    test('manager can access reservations management', async ({ page }) => {
      // Navigate to reservations
      await page.goto(`${FRONTEND_URL}/dashboard/reservations`);
      
      // Check reservations page loads
      await expect(page).toHaveTitle(/Reservation/);
      
      // Look for reservations list or table
      const reservationsList = page.locator('table, .reservation-item, [data-testid="reservations-list"]');
      await expect(reservationsList).toBeVisible({ timeout: 10000 });
    });

    test('manager can view reservation filters and controls', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/dashboard/reservations`);
      await page.waitForLoadState('networkidle');
      
      // Look for filter controls
      const filters = page.locator('input[placeholder*="search"], select, [data-testid="filter"]');
      if (await filters.count() > 0) {
        await expect(filters.first()).toBeVisible();
      }
      
      // Look for action buttons
      const actionButtons = page.locator('button:has-text("Add"), button:has-text("New"), button[data-testid*="add"]');
      if (await actionButtons.count() > 0) {
        await expect(actionButtons.first()).toBeVisible();
      }
    });
  });

  test.describe('WF-005: Menu Management & Updates', () => {
    test.beforeEach(async ({ page }) => {
      // Login as manager
      await page.goto(`${FRONTEND_URL}/auth/login`);
      await page.fill('input[type="email"]', CREDENTIALS.manager.email);
      await page.fill('input[type="password"]', CREDENTIALS.manager.password);
      await page.click('button[type="submit"]');
      await page.waitForURL('**/dashboard**', { timeout: 15000 });
    });

    test('manager can access menu management page', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/dashboard/menu`);
      
      // Check menu management page loads
      await expect(page).toHaveTitle(/Menu Management|Menu/);
      
      // Look for menu items grid or list
      const menuGrid = page.locator('.grid, .menu-items, [data-testid="menu-items"]');
      await expect(menuGrid).toBeVisible({ timeout: 10000 });
    });

    test('manager can see menu items loaded from backend', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/dashboard/menu`);
      await page.waitForLoadState('networkidle');
      
      // Wait for menu items to load
      const menuItems = page.locator('.card, .menu-item, [data-testid="menu-item"]');
      await expect(menuItems.first()).toBeVisible({ timeout: 15000 });
      
      // Check for item details (name, price, etc.)
      const itemName = page.locator('h3, .item-name, [data-testid="item-name"]').first();
      const itemPrice = page.locator('.price, [data-testid="price"]').first();
      
      if (await itemName.isVisible()) {
        await expect(itemName).toContainText(/\w+/); // Should contain some text
      }
      
      if (await itemPrice.isVisible()) {
        await expect(itemPrice).toContainText(/\$|\d/); // Should contain $ or digits
      }
    });

    test('manager can interact with add new item button', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/dashboard/menu`);
      await page.waitForLoadState('networkidle');
      
      // Look for add new item button
      const addButton = page.locator('button:has-text("Add"), button:has-text("New"), button[data-testid*="add"]');
      
      if (await addButton.isVisible()) {
        await expect(addButton).toBeEnabled();
        
        // Click the button to open modal/form
        await addButton.click();
        
        // Check if modal or form appears
        const modal = page.locator('.modal, .dialog, [role="dialog"]');
        const form = page.locator('form');
        
        // Either a modal should appear or we should see a form
        const modalOrForm = await modal.isVisible() || await form.count() > 0;
        expect(modalOrForm).toBeTruthy();
      }
    });

    test('manager can see refresh functionality', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/dashboard/menu`);
      await page.waitForLoadState('networkidle');
      
      // Look for refresh button
      const refreshButton = page.locator('button:has-text("Refresh"), button[data-testid*="refresh"]');
      
      if (await refreshButton.isVisible()) {
        await expect(refreshButton).toBeEnabled();
        
        // Click refresh button
        await refreshButton.click();
        
        // Should not cause errors or navigation
        expect(page.url()).toContain('/dashboard/menu');
      }
    });
  });

  test.describe('WF-006: Navigation and User Experience', () => {
    test('main navigation is functional across pages', async ({ page }) => {
      const pages = [
        { url: '/', title: /Home|Restaurant/ },
        { url: '/menu', title: /Menu/ },
        { url: '/book', title: /Book|Reservation/ },
        { url: '/contact', title: /Contact/ }
      ];
      
      for (const testPage of pages) {
        await page.goto(`${FRONTEND_URL}${testPage.url}`);
        await expect(page).toHaveTitle(testPage.title);
        
        // Check navigation is present
        const nav = page.locator('nav, [role="navigation"]');
        await expect(nav).toBeVisible();
      }
    });

    test('responsive design works on different screen sizes', async ({ page }) => {
      await page.goto(FRONTEND_URL);
      
      // Test mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(1000);
      
      // Navigation should be visible or have mobile menu
      const nav = page.locator('nav, [role="navigation"], .mobile-menu, button[aria-label*="menu" i]');
      await expect(nav).toBeVisible();
      
      // Test desktop viewport
      await page.setViewportSize({ width: 1280, height: 720 });
      await page.waitForTimeout(1000);
      
      // Desktop navigation should be visible
      const desktopNav = page.locator('nav, [role="navigation"]');
      await expect(desktopNav).toBeVisible();
    });
  });

  test.describe('WF-007: Error Handling and Fallbacks', () => {
    test('pages handle loading states gracefully', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/menu`);
      
      // Look for loading indicators
      const loadingIndicator = page.locator('.loading, .spinner, [data-testid="loading"]');
      
      // Either we see a loading state briefly, or content loads quickly
      await page.waitForLoadState('networkidle');
      
      // After loading, content should be visible
      const content = page.locator('main, .content, h1').first();
      await expect(content).toBeVisible();
    });

    test('authentication redirects work properly', async ({ page }) => {
      // Try to access protected page without authentication
      await page.goto(`${FRONTEND_URL}/dashboard`);
      
      // Should redirect to login page
      await page.waitForURL('**/auth/login**', { timeout: 10000 });
      expect(page.url()).toContain('/auth/login');
      
      // Login page should be visible
      const loginForm = page.locator('form, input[type="email"]');
      await expect(loginForm).toBeVisible();
    });

    test('invalid routes show appropriate error pages', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/nonexistent-page`);
      
      // Should show 404 page or redirect appropriately
      const notFoundText = page.locator('text=/404|not found|page not found/i');
      const homeRedirect = page.url() === `${FRONTEND_URL}/`;
      
      // Either show 404 or redirect to home
      const handlesError = await notFoundText.isVisible() || homeRedirect;
      expect(handlesError).toBeTruthy();
    });
  });
});

// Performance Tests
test.describe('Performance and Accessibility', () => {
  test('pages load within acceptable time limits', async ({ page }) => {
    const startTime = Date.now();
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    // Should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('critical accessibility features are present', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    // Check for basic accessibility features
    const mainContent = page.locator('main, [role="main"]');
    if (await mainContent.count() > 0) {
      await expect(mainContent).toBeVisible();
    }
    
    // Check for navigation landmarks
    const navigation = page.locator('nav, [role="navigation"]');
    await expect(navigation).toBeVisible();
    
    // Check for proper headings
    const headings = page.locator('h1, h2, h3');
    await expect(headings.first()).toBeVisible();
  });
});