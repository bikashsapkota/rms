# Frontend Implementation Plan - Single Restaurant Management System

## 🎯 Project Overview

Building a modern React/Next.js frontend for a **single restaurant** that connects to a **multi-tenant backend**. The frontend provides a dedicated interface for one specific restaurant while the backend handles multi-tenant architecture.

### **Architecture Overview**
- **Backend**: Multi-tenant with `organization_id` and `restaurant_id` context
- **Frontend**: Single restaurant interface (configured for specific restaurant)
- **API Strategy**: Frontend automatically includes tenant context in all API calls
- **Authentication**: Staff login provides restaurant-specific access tokens

## 📋 Phase 1 Frontend Implementation Plan

### **Technology Stack**
- **Framework**: Next.js 14+ (App Router)
- **UI Library**: React 18+
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand (lightweight) + TanStack Query (server state)
- **Authentication**: NextAuth.js
- **Forms**: React Hook Form + Zod validation
- **Icons**: Lucide React
- **Deployment**: Docker

### **SEO vs Performance Strategy**
- **SSR Pages** (Customer-facing, SEO-critical):
  - Restaurant landing page (`/`)
  - Public menu (`/menu`)
  - Reservation booking (`/book`)
  - Contact & info pages (`/contact`, `/about`)
  
- **CSR Pages** (Staff/Owner dashboard):
  - Restaurant dashboard (`/dashboard/*`)
  - Menu management (`/dashboard/menu`)
  - Reservations management (`/dashboard/reservations`)
  - Kitchen display (`/kitchen`)
  - Staff interface (`/dashboard/staff`)

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (public)/          # Customer-facing routes (SSR)
│   │   │   ├── page.tsx       # Restaurant landing page
│   │   │   ├── menu/          # Public menu display
│   │   │   ├── book/          # Reservation booking
│   │   │   ├── contact/       # Contact information
│   │   │   └── about/         # About the restaurant
│   │   ├── (dashboard)/       # Staff/Owner routes (CSR)
│   │   │   ├── dashboard/     # Main dashboard
│   │   │   └── kitchen/       # Kitchen display
│   │   ├── auth/              # Login/logout pages
│   │   ├── api/               # API routes (proxy to backend)
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/               # shadcn/ui components
│   │   ├── layout/           # Layout components
│   │   ├── forms/            # Form components
│   │   └── features/         # Feature-specific components
│   ├── lib/
│   │   ├── api.ts            # API client configuration
│   │   ├── auth.ts           # Authentication config
│   │   ├── utils.ts          # Utility functions
│   │   └── validations.ts    # Zod schemas
│   ├── hooks/                # Custom React hooks
│   ├── stores/               # Zustand stores
│   ├── types/                # TypeScript type definitions
│   └── styles/               # Additional styles
├── public/                   # Static assets
├── package.json
├── tailwind.config.js
├── next.config.js
└── tsconfig.json
```

## 🎨 Phase 1 Features Implementation

### **1. Customer-Facing Pages (SSR for SEO)**

#### **Restaurant Landing Page (`/`) - Comprehensive Design**

**Primary Goal**: Convert visitors into customers through reservations

**Layout Sections:**

1. **Hero Section (Above the fold)**
   - Restaurant name, logo, and tagline
   - Hero image/video showcasing restaurant atmosphere
   - Primary CTAs: "Make Reservation" & "View Menu"
   - Key info: Address, phone, "Open Now" status
   - Today's operating hours

2. **Quick Info Bar**
   - Dynamic operating hours for today
   - Special offers, happy hour, events
   - Service highlights (takeout, parking, etc.)

3. **Featured Menu Section**
   - 3-4 chef's signature dishes with images and prices
   - Dynamic content from menu API
   - "View Full Menu" CTA

4. **Inline Reservation Widget**
   - Date picker, time slots, party size selector
   - Real-time availability from backend
   - Quick booking: "Tonight", "Tomorrow", "Weekend"
   - One-click reservation without page navigation

5. **Restaurant Story/About**
   - Chef/owner introduction with photo
   - Restaurant philosophy and history
   - Values (farm-to-table, family recipes)
   - Emotional connection building

6. **Photo Gallery Showcase**
   - Food, interior, staff, events photography
   - Instagram integration
   - Modal gallery on click

7. **Customer Reviews/Social Proof**
   - Live testimonials from Google/Yelp
   - Star ratings and review counts
   - Rotating customer feedback

8. **Location & Contact Section**
   - Interactive Google Maps embed
   - Complete address and contact info
   - Full weekly operating hours
   - "Get Directions" and "Call Now" CTAs

**Dynamic Features:**
- Real-time "Open/Closed" status
- Live table availability
- Featured menu items from backend API
- Weather-based messaging
- Special announcements

**Tech**: SSR for SEO, structured data (Local Business Schema), real-time API integration, mobile-optimized, Core Web Vitals optimization

#### **Public Menu (`/menu`)**
- Category-based menu display
- Item details with images and descriptions
- Price display with currency formatting
- Dietary restrictions and allergen indicators
- Search and filter functionality
- **Tech**: SSR, image optimization, structured data for rich snippets

#### **Reservation Booking (`/book`)**
- Available time slots for the restaurant
- Party size selection
- Customer information form
- Confirmation page with booking details
- Email/SMS confirmation system
- **Tech**: SSR for initial load, hydration for interactivity

#### **Contact & About Pages (`/contact`, `/about`)**
- Restaurant contact information
- Location with map integration
- Story and history of the restaurant
- Staff information and chef profiles
- **Tech**: SSR, local business schema markup

### **2. Authentication System**

#### **Login/Register Pages (`/auth/*`)**
- Restaurant owner/manager login
- Staff member authentication
- Password reset functionality
- Remember me functionality
- **Tech**: NextAuth.js, form validation, secure redirects

### **3. Restaurant Dashboard (CSR)**

#### **Dashboard Overview (`/dashboard`)**
- Today's statistics (reservations, revenue)
- Recent reservations overview
- Menu management shortcuts
- Quick actions panel
- Staff activity summary
- **Tech**: Real-time updates, charts/graphs

#### **Menu Management (`/dashboard/menu`)**
- Category management (create, edit, reorder)
- Menu item CRUD operations
- Image upload and management
- Availability toggle
- Pricing management
- **Tech**: Drag-and-drop, image processing, optimistic updates

#### **Reservations Management (`/dashboard/reservations`)**
- Today's reservations overview
- Table assignment and management
- Customer check-in/check-out
- Waitlist management
- Reservation calendar view
- **Tech**: Real-time updates, calendar integration

#### **Restaurant Settings (`/dashboard/settings`)**
- Restaurant profile and branding
- Operating hours configuration
- Table layout management
- Staff user management
- Notification preferences
- **Tech**: Form handling, real-time validation

### **4. Kitchen Display System (`/kitchen`)**

#### **Kitchen Display Interface**
- Live order queue display
- Order preparation status tracking
- Timer management for dishes
- Staff assignment to orders
- Order completion workflow
- **Tech**: Real-time WebSocket updates, touch-friendly interface

## 🔧 Implementation Phases

### **Phase 1A: Foundation Setup (1-2 weeks)**
```bash
# Setup tasks
1. Initialize Next.js project with TypeScript
2. Configure Tailwind CSS + shadcn/ui
3. Set up authentication with NextAuth.js (with tenant-aware tokens)
4. Configure multi-tenant aware API client
5. Create restaurant-specific environment configuration
6. Create basic layout components with restaurant branding
7. Set up development environment with tenant context
```

### **Phase 1B: Customer-Facing Pages (2-3 weeks)**
```bash
# Customer interface tasks
1. Build restaurant landing page with SSR
2. Create public menu display with categories
3. Build reservation booking system
4. Add contact and about pages
5. Add SEO optimization and meta tags
6. Implement local business structured data
```

### **Phase 1C: Authentication & Dashboard (2-3 weeks)**
```bash
# Restaurant management tasks
1. Implement staff login/authentication system
2. Create dashboard layout and navigation
3. Build menu management interface
4. Add reservations management page
5. Implement restaurant settings page
6. Add error handling and loading states
```

### **Phase 1D: Kitchen Display System (1-2 weeks)**
```bash
# Kitchen interface tasks (Future - Phase 3)
1. Create kitchen display layout
2. Build order queue interface
3. Add real-time order updates
4. Implement timer and status management
5. Add touch-friendly interactions
```

### **Phase 1E: Polish & Optimization (1 week)**
```bash
# Final optimization tasks
1. Performance optimization
2. Accessibility improvements
3. Mobile responsiveness testing
4. SEO audit and fixes
5. Error boundary implementation
6. Production deployment setup
```

## 🎨 Design System

### **Color Palette**
```css
/* Tailwind CSS custom colors */
:root {
  --primary: #f97316;      /* Orange-500 - Restaurant theme */
  --primary-dark: #ea580c; /* Orange-600 */
  --secondary: #64748b;    /* Slate-500 */
  --accent: #10b981;       /* Emerald-500 - Success states */
  --background: #ffffff;
  --surface: #f8fafc;      /* Slate-50 */
  --text: #1e293b;         /* Slate-800 */
  --text-muted: #64748b;   /* Slate-500 */
}
```

### **Typography**
- **Headings**: Inter font family
- **Body**: Inter font family
- **Code**: JetBrains Mono

### **Component Standards**
- shadcn/ui as base component library
- Consistent spacing using Tailwind spacing scale
- Responsive design mobile-first approach
- Accessibility compliance (WCAG 2.1 AA)

## 📱 Responsive Design Strategy

### **Breakpoints**
- **Mobile**: 320px - 640px (sm)
- **Tablet**: 640px - 1024px (md/lg)
- **Desktop**: 1024px+ (xl/2xl)

### **Mobile-First Features**
- Touch-optimized interface
- Simplified navigation
- Swipe gestures for galleries
- Optimized form inputs
- Fast loading with image optimization

## 🔐 Security Considerations

### **Authentication Security**
- JWT token handling
- Secure cookie configuration
- CSRF protection
- Session management
- Rate limiting for forms

### **Data Security**
- Input validation on all forms
- XSS prevention
- Secure API communication
- Environment variable protection
- Content Security Policy

## 📊 Performance Targets

### **Core Web Vitals**
- **LCP**: < 2.5s (Largest Contentful Paint)
- **FID**: < 100ms (First Input Delay)
- **CLS**: < 0.1 (Cumulative Layout Shift)

### **Optimization Strategies**
- Image optimization with Next.js Image
- Code splitting with dynamic imports
- Bundle size monitoring
- Caching strategies
- Database query optimization

## 🧪 Testing Strategy

### **Testing Framework**
- **Unit Tests**: Jest + React Testing Library
- **E2E Tests**: Playwright MCP (via Claude Code)
- **Performance Tests**: Lighthouse CI
- **Accessibility Tests**: axe-core integration with Playwright
- **API Integration Tests**: Playwright API testing

### **Playwright MCP Testing Approach**
```typescript
// Test scenarios using Playwright MCP
class RestaurantE2ETests {
  
  // Customer Journey Tests
  async testCustomerReservationFlow() {
    // Navigate to restaurant homepage
    await page.goto('/')
    
    // Browse public menu
    await page.click('[data-testid="view-menu"]')
    await page.waitForSelector('[data-testid="menu-categories"]')
    
    // Make reservation
    await page.click('[data-testid="book-table"]')
    await page.fill('[data-testid="party-size"]', '4')
    await page.selectOption('[data-testid="time-slot"]', '19:00')
    await page.fill('[data-testid="customer-name"]', 'John Doe')
    await page.fill('[data-testid="customer-phone"]', '555-0123')
    await page.click('[data-testid="confirm-reservation"]')
    
    // Verify confirmation
    await expect(page.locator('[data-testid="reservation-confirmation"]')).toBeVisible()
  }
  
  // Staff Dashboard Tests
  async testStaffMenuManagement() {
    // Staff login
    await page.goto('/auth/login')
    await page.fill('[data-testid="email"]', 'staff@restaurant.com')
    await page.fill('[data-testid="password"]', 'password')
    await page.click('[data-testid="login-button"]')
    
    // Navigate to menu management
    await page.goto('/dashboard/menu')
    
    // Create new menu item
    await page.click('[data-testid="add-item"]')
    await page.fill('[data-testid="item-name"]', 'Test Dish')
    await page.fill('[data-testid="item-price"]', '15.99')
    await page.selectOption('[data-testid="category"]', 'mains')
    await page.click('[data-testid="save-item"]')
    
    // Verify item appears in list
    await expect(page.locator('[data-testid="menu-item-Test Dish"]')).toBeVisible()
  }
  
  // Multi-tenant API Context Tests
  async testTenantContextIsolation() {
    // Verify API calls include correct restaurant context
    await page.route('/api/v1/menu/**', (route) => {
      const headers = route.request().headers()
      expect(headers['x-restaurant-id']).toBe(process.env.NEXT_PUBLIC_RESTAURANT_ID)
      route.continue()
    })
    
    await page.goto('/menu')
    await page.waitForResponse('/api/v1/menu/public')
  }
}
```

### **Test Coverage Goals**
- **Component Tests**: >80% coverage with Jest + RTL
- **E2E Tests**: 100% critical user journeys with Playwright MCP
- **API Integration**: All tenant-aware endpoints tested
- **Performance**: Lighthouse CI on all SSR pages
- **Accessibility**: axe-core validation on all pages

## 🚀 Deployment Strategy

### **Development Environment**
```bash
# Local development setup
npm run dev          # Development server with hot reload
npm run build        # Production build
npm run test         # Unit tests (Jest + RTL)
npm run test:e2e     # Playwright MCP E2E tests via Claude Code
npm run lint         # ESLint + Prettier
npm run test:a11y    # Accessibility tests with axe-core
```

### **Playwright MCP Test Execution**
```bash
# E2E testing workflow via Claude Code
# 1. Start development server
npm run dev

# 2. Use Claude Code Playwright MCP to run tests
# - Customer reservation flow testing
# - Staff dashboard functionality testing  
# - Multi-tenant API context validation
# - Performance and accessibility audits
# - Cross-browser compatibility testing

# 3. Automated test reporting
# - Screenshots on failures
# - Performance metrics collection
# - Accessibility violation reports
```

### **Production Deployment**
- **Vercel**: Recommended for easy deployment
- **Docker**: Alternative for custom hosting
- **Environment Management**: Separate configs for dev/staging/prod
- **CI/CD Pipeline**: GitHub Actions
- **Monitoring**: Error tracking and performance monitoring

## 📋 API Integration Plan

### **Backend API Endpoints**
- Authentication: `/api/v1/auth/*`
- Restaurant Setup: `/setup`  
- Menu Management: `/api/v1/menu/*`
- Reservations: `/api/v1/reservations/*`, `/api/v1/tables/*`
- Public APIs: `/api/v1/public/*`
- Health Check: `/health`

### **API Client Configuration**
```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const RESTAURANT_ID = process.env.NEXT_PUBLIC_RESTAURANT_ID // Configure per restaurant deployment

class ApiClient {
  private restaurantId: string = RESTAURANT_ID
  private organizationId: string // Set from auth token
  
  // Automatically inject tenant context in all API calls
  private addTenantContext(config: RequestConfig) {
    return {
      ...config,
      headers: {
        ...config.headers,
        'X-Restaurant-ID': this.restaurantId,
        'X-Organization-ID': this.organizationId,
      }
    }
  }
  
  // Multi-tenant aware endpoints
  async getMenu() {
    // Calls: GET /api/v1/menu/ with tenant context
    return this.get('/api/v1/menu/')
  }
  
  async getReservations() {
    // Calls: GET /api/v1/reservations/ with tenant context  
    return this.get('/api/v1/reservations/')
  }
  
  async getPublicMenu() {
    // Calls: GET /api/v1/menu/public (no auth, but includes restaurant context)
    return this.get('/api/v1/menu/public')
  }
}
```

### **Environment Configuration**
```bash
# .env.local (Per restaurant deployment)
NEXT_PUBLIC_API_URL=https://api.restaurantname.com
NEXT_PUBLIC_RESTAURANT_ID=550e8400-e29b-41d4-a716-446655440001
NEXT_PUBLIC_RESTAURANT_NAME="Your Restaurant Name"
NEXT_PUBLIC_RESTAURANT_SLUG="your-restaurant-name"

# Different restaurants would have different values:
# Restaurant A: RESTAURANT_ID=uuid-a, RESTAURANT_NAME="Pizza Palace"
# Restaurant B: RESTAURANT_ID=uuid-b, RESTAURANT_NAME="Burger Barn"
```

## 🎯 Success Metrics

### **User Experience**
- Page load time < 3 seconds
- Mobile responsiveness score > 95%
- Accessibility score > 95%
- User task completion rate > 90%

### **Technical Metrics**
- Build time < 2 minutes
- Bundle size < 500KB (initial load)
- Test coverage > 80%
- Zero TypeScript errors
- Lighthouse score > 90

## 🔄 Future Enhancements (Post-Phase 1)

### **Phase 2 Frontend Extensions**
- Real-time reservation updates
- Advanced table management UI
- Customer communication interface
- Waitlist management dashboard

### **Phase 3 Frontend Extensions**
- Kitchen display system
- Order management interface
- QR code ordering system
- Payment processing UI

### **Progressive Web App (PWA)**
- Offline functionality
- Push notifications
- Install prompts
- Background sync

---

## 📝 Implementation Notes

### **Development Workflow**
1. Feature branch development
2. Code review process
3. Testing before merge
4. Staging deployment
5. Production release

### **Code Standards**
- TypeScript strict mode
- ESLint + Prettier configuration
- Consistent naming conventions
- Component documentation
- Git commit message standards

### **Monitoring & Analytics**
- Error tracking (Sentry)
- Performance monitoring
- User analytics (privacy-compliant)
- A/B testing framework
- Feature flagging system

This plan provides a comprehensive roadmap for building a production-ready frontend that complements the existing backend infrastructure while setting the foundation for future phases.