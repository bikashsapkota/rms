// Restaurant Types
export interface Restaurant {
  id: string;
  organization_id: string;
  name: string;
  address?: {
    street?: string;
    city?: string;
    state?: string;
    zip?: string;
  };
  phone?: string;
  email?: string;
  settings?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Menu Types
export interface MenuCategory {
  id: string;
  organization_id: string;
  restaurant_id: string;
  name: string;
  description?: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MenuItem {
  id: string;
  organization_id: string;
  restaurant_id: string;
  category_id?: string;
  name: string;
  description?: string;
  price: number;
  is_available: boolean;
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Modifier {
  id: string;
  organization_id: string;
  restaurant_id: string;
  name: string;
  type: 'size' | 'addon' | 'substitution';
  price_adjustment: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Table Types
export interface Table {
  id: string;
  organization_id: string;
  restaurant_id: string;
  table_number: string;
  capacity: number;
  location?: string;
  status: 'available' | 'occupied' | 'reserved' | 'maintenance';
  coordinates?: { x: number; y: number };
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Reservation Types
export interface Reservation {
  id: string;
  organization_id: string;
  restaurant_id: string;
  table_id?: string;
  customer_name: string;
  customer_phone?: string;
  customer_email?: string;
  party_size: number;
  reservation_date: string; // ISO date string
  reservation_time: string; // Time string
  duration_minutes: number;
  status: 'pending' | 'confirmed' | 'seated' | 'completed' | 'cancelled' | 'no_show';
  special_requests?: string;
  customer_preferences?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface TimeSlot {
  time: string;
  available: boolean;
  table_id?: string;
}

export interface AvailabilityResponse {
  date: string;
  slots: TimeSlot[];
  total_available: number;
}

// User Types
export interface User {
  id: string;
  organization_id: string;
  restaurant_id?: string;
  email: string;
  full_name?: string;
  role: 'admin' | 'manager' | 'staff';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Authentication Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Form Types
export interface ReservationForm {
  customer_name: string;
  customer_email?: string;
  customer_phone?: string;
  party_size: number;
  reservation_date: string;
  reservation_time: string;
  special_requests?: string;
}

export interface MenuItemForm {
  name: string;
  description?: string;
  price: number;
  category_id?: string;
  is_available: boolean;
}

export interface CategoryForm {
  name: string;
  description?: string;
  sort_order?: number;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface ApiError {
  message: string;
  status: number;
  code?: string;
}

// Component Props Types
export interface PageProps {
  params?: Record<string, string>;
  searchParams?: Record<string, string>;
}

export interface LayoutProps {
  children: React.ReactNode;
}

// State Management Types
export interface AppState {
  user: User | null;
  restaurant: Restaurant | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Utility Types
export type Status = 'idle' | 'loading' | 'success' | 'error';

export interface LoadingState {
  status: Status;
  error?: string;
}