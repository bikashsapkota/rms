# Multi-Tenant Backend Integration Guide

## 🎯 Overview

This document outlines how the **single restaurant frontend** integrates with the **multi-tenant backend** architecture.

## 🏗️ Architecture Pattern

```
┌─────────────────────────────────────┐
│         Multi-Tenant Backend        │
│  ┌─────────────────────────────────┐ │
│  │     Organization Layer          │ │
│  │  ┌─────────────┐ ┌─────────────┐ │ │
│  │  │Restaurant A │ │Restaurant B │ │ │
│  │  └─────────────┘ └─────────────┘ │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              │ API Calls
              ▼
┌─────────────────────────────────────┐
│    Single Restaurant Frontend       │
│         (Restaurant A)              │
│  ┌─────────────────────────────────┐ │
│  │     Auto-inject Tenant Context │ │
│  │     restaurant_id: uuid-a      │ │
│  │     organization_id: uuid-org  │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 🔧 Integration Strategy

### **1. Environment-Based Configuration**

Each restaurant deployment has its own configuration:

```bash
# Restaurant A (.env.local)
NEXT_PUBLIC_RESTAURANT_ID=550e8400-e29b-41d4-a716-446655440001
NEXT_PUBLIC_ORGANIZATION_ID=660e8400-e29b-41d4-a716-446655440002
NEXT_PUBLIC_RESTAURANT_NAME="Pizza Palace"
NEXT_PUBLIC_API_URL=https://api.pizzapalace.com

# Restaurant B (.env.local)  
NEXT_PUBLIC_RESTAURANT_ID=770e8400-e29b-41d4-a716-446655440003
NEXT_PUBLIC_ORGANIZATION_ID=880e8400-e29b-41d4-a716-446655440004
NEXT_PUBLIC_RESTAURANT_NAME="Burger Barn"
NEXT_PUBLIC_API_URL=https://api.burgerbarn.com
```

### **2. API Client with Automatic Tenant Context**

```typescript
// lib/api.ts
class MultiTenantApiClient {
  private config = {
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    restaurantId: process.env.NEXT_PUBLIC_RESTAURANT_ID,
    organizationId: process.env.NEXT_PUBLIC_ORGANIZATION_ID,
  }

  // Automatically inject tenant headers
  private createRequest(config: RequestConfig) {
    return {
      ...config,
      headers: {
        ...config.headers,
        'Content-Type': 'application/json',
        'X-Restaurant-ID': this.config.restaurantId,
        'X-Organization-ID': this.config.organizationId,
        ...(this.getAuthToken() && {
          'Authorization': `Bearer ${this.getAuthToken()}`
        })
      }
    }
  }

  // Menu endpoints - automatically scoped to restaurant
  async getCategories() {
    // Backend receives restaurant_id context automatically
    return this.get('/api/v1/menu/categories/')
  }

  async createMenuItem(item: MenuItemCreate) {
    // Backend automatically associates with correct restaurant
    return this.post('/api/v1/menu/items/', item)
  }

  // Reservation endpoints - automatically scoped
  async getReservations() {
    return this.get('/api/v1/reservations/')
  }

  async createReservation(reservation: ReservationCreate) {
    return this.post('/api/v1/reservations/', reservation)
  }

  // Public endpoints for customers
  async getPublicMenu() {
    // No auth required, but includes restaurant context
    return this.get('/api/v1/menu/public')
  }
}
```

### **3. Authentication Integration**

```typescript
// lib/auth.ts
export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        // Login to multi-tenant backend
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Restaurant-ID': process.env.NEXT_PUBLIC_RESTAURANT_ID,
          },
          body: JSON.stringify({
            email: credentials?.email,
            password: credentials?.password,
          }),
        })

        const data = await response.json()
        
        if (response.ok && data.access_token) {
          // Verify user belongs to this restaurant
          if (data.user.restaurant_id === process.env.NEXT_PUBLIC_RESTAURANT_ID) {
            return {
              id: data.user.id,
              email: data.user.email,
              name: data.user.full_name,
              role: data.user.role,
              restaurantId: data.user.restaurant_id,
              organizationId: data.user.organization_id,
              accessToken: data.access_token,
            }
          }
        }
        
        return null
      }
    })
  ],
  
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.accessToken
        token.restaurantId = user.restaurantId
        token.organizationId = user.organizationId
        token.role = user.role
      }
      return token
    },
    
    async session({ session, token }) {
      session.accessToken = token.accessToken
      session.user.restaurantId = token.restaurantId
      session.user.organizationId = token.organizationId
      session.user.role = token.role
      return session
    }
  }
}
```

## 📋 Key Implementation Details

### **1. Tenant Context Injection**

Every API call automatically includes:
- `X-Restaurant-ID`: The specific restaurant UUID
- `X-Organization-ID`: The organization UUID (for multi-restaurant chains)
- `Authorization`: JWT token with user context

### **2. Data Isolation**

- **Frontend**: Only sees data for its configured restaurant
- **Backend**: Uses Row Level Security (RLS) to enforce tenant isolation
- **APIs**: All responses automatically filtered by tenant context

### **3. Public vs Private APIs**

```typescript
// Public APIs (no authentication, restaurant context only)
const publicMenu = await api.getPublicMenu()           // /api/v1/menu/public
const availability = await api.getPublicAvailability() // /api/v1/public/reservations/availability

// Private APIs (authentication + restaurant context required)
const orders = await api.getOrders()           // /api/v1/orders/
const reservations = await api.getReservations() // /api/v1/reservations/
```

### **4. Error Handling for Multi-Tenancy**

```typescript
class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message)
  }
}

// Handle tenant-specific errors
const handleApiError = (error: any) => {
  if (error.status === 403 && error.code === 'TENANT_ACCESS_DENIED') {
    // User trying to access wrong restaurant's data
    router.push('/auth/login?error=access_denied')
  }
  
  if (error.status === 404 && error.code === 'RESTAURANT_NOT_FOUND') {
    // Restaurant configuration issue
    console.error('Restaurant configuration error:', process.env.NEXT_PUBLIC_RESTAURANT_ID)
  }
}
```

## 🚀 Deployment Strategy

### **Per-Restaurant Deployments**

```bash
# Restaurant A Deployment
RESTAURANT_ID=uuid-a npm run build
RESTAURANT_NAME="Pizza Palace" npm run deploy:restaurant-a

# Restaurant B Deployment  
RESTAURANT_ID=uuid-b npm run build
RESTAURANT_NAME="Burger Barn" npm run deploy:restaurant-b
```

### **Docker Multi-Restaurant Setup**

```dockerfile
# Dockerfile.restaurant
FROM node:18-alpine

# Build-time restaurant configuration
ARG RESTAURANT_ID
ARG RESTAURANT_NAME
ARG API_URL

ENV NEXT_PUBLIC_RESTAURANT_ID=$RESTAURANT_ID
ENV NEXT_PUBLIC_RESTAURANT_NAME=$RESTAURANT_NAME
ENV NEXT_PUBLIC_API_URL=$API_URL

COPY . .
RUN npm ci && npm run build

CMD ["npm", "start"]
```

```bash
# Build restaurant-specific images
docker build --build-arg RESTAURANT_ID=uuid-a --build-arg RESTAURANT_NAME="Pizza Palace" -t frontend-pizza-palace .
docker build --build-arg RESTAURANT_ID=uuid-b --build-arg RESTAURANT_NAME="Burger Barn" -t frontend-burger-barn .
```

## 🔐 Security Considerations

### **1. Tenant Isolation**

- Frontend can only access its configured restaurant's data
- Backend enforces RLS policies based on organization_id
- JWT tokens include restaurant context for verification

### **2. Environment Security**

```bash
# Secure environment variables
NEXT_PUBLIC_RESTAURANT_ID=uuid              # Safe to expose (public)
NEXT_PUBLIC_API_URL=https://api.domain.com  # Safe to expose (public)
NEXTAUTH_SECRET=secure_secret               # Keep private
NEXTAUTH_URL=https://restaurant.domain.com  # Safe to expose
```

### **3. API Security**

- All private endpoints require valid JWT tokens
- Tokens include restaurant_id for server-side validation
- Public endpoints still respect restaurant context

## 📊 Benefits of This Approach

### **For Restaurant Owners**

- **Dedicated Experience**: Feels like a custom app for their restaurant
- **Custom Branding**: Each deployment can have unique styling/branding
- **Performance**: No multi-restaurant selection overhead
- **Simple URLs**: `pizzapalace.com` instead of `platform.com/pizza-palace`

### **For Development**

- **Single Codebase**: One frontend codebase serves multiple restaurants
- **Environment Configuration**: Easy per-restaurant customization
- **Scalability**: New restaurants = new deployment with different config
- **Maintenance**: Bug fixes and features deploy to all restaurants

### **For Backend**

- **Unified API**: One API serves all restaurants
- **Data Integrity**: Strong tenant isolation with RLS
- **Scalability**: Horizontal scaling with tenant partitioning
- **Analytics**: Cross-restaurant insights while maintaining isolation

This approach provides the best of both worlds: a unified backend architecture with dedicated, branded frontend experiences for each restaurant.