'use client';

import { useState, useEffect } from 'react';
import { useApiClient } from '@/hooks/useApiClient';
import { signOut } from 'next-auth/react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Calendar, 
  Search, 
  Filter,
  CheckCircle,
  Clock,
  X,
  Users,
  Phone,
  Mail,
  MessageSquare
} from 'lucide-react';

interface Reservation {
  id: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  reservation_date: string;
  reservation_time: string;
  party_size: number;
  status: 'confirmed' | 'pending' | 'completed' | 'cancelled';
  special_requests?: string;
  created_at: string;
}

export function ReservationsManagement() {
  const apiClient = useApiClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('today');
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Demo data for fallback
  const demoReservations: Reservation[] = [
    {
      id: 'RES-001',
      customer_name: 'John Smith',
      customer_email: 'john.smith@email.com',
      customer_phone: '(555) 123-4567',
      reservation_date: '2025-08-21',
      reservation_time: '7:00 PM',
      party_size: 4,
      status: 'confirmed',
      special_requests: 'Window table preferred, celebrating anniversary',
      created_at: '2025-08-20T10:30:00Z'
    },
    {
      id: 'RES-002',
      customer_name: 'Sarah Johnson',
      customer_email: 'sarah.j@email.com',
      customer_phone: '(555) 234-5678',
      reservation_date: '2025-08-21',
      reservation_time: '7:30 PM',
      party_size: 2,
      status: 'confirmed',
      created_at: '2025-08-20T11:15:00Z'
    },
    {
      id: 'RES-003',
      customer_name: 'Mike Davis',
      customer_email: 'mike.davis@email.com',
      customer_phone: '(555) 345-6789',
      reservation_date: '2025-08-21',
      reservation_time: '8:00 PM',
      party_size: 6,
      status: 'pending',
      special_requests: 'High chair needed for baby',
      created_at: '2025-08-20T14:22:00Z'
    },
    {
      id: 'RES-004',
      customer_name: 'Emily Brown',
      customer_email: 'emily.brown@email.com',
      customer_phone: '(555) 456-7890',
      reservation_date: '2025-08-20',
      reservation_time: '6:30 PM',
      party_size: 3,
      status: 'completed',
      created_at: '2025-08-19T16:45:00Z'
    },
    {
      id: 'RES-005',
      customer_name: 'David Wilson',
      customer_email: 'david.w@email.com',
      customer_phone: '(555) 567-8901',
      reservation_date: '2025-08-20',
      reservation_time: '8:00 PM',
      party_size: 2,
      status: 'cancelled',
      created_at: '2025-08-19T09:12:00Z'
    }
  ];

  // Load reservations from API
  useEffect(() => {
    const loadReservations = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiClient.getReservations();
        setReservations(data);
      } catch (error) {
        console.error('Failed to load reservations:', error);
        
        // Check if error is due to authentication failure
        if (error instanceof Error && ((error as any).status === 401 || error.message.includes('401'))) {
          console.warn('Authentication failed, redirecting to login');
          await signOut({ callbackUrl: '/auth/login' });
          return;
        }
        
        setError('Failed to load reservations. Using demo data.');
        setReservations(demoReservations);
      } finally {
        setLoading(false);
      }
    };

    loadReservations();
  }, [apiClient]);

  // Filter reservations
  const filteredReservations = reservations.filter((reservation) => {
    const matchesSearch = 
      reservation.customer_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      reservation.customer_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      reservation.customer_phone.includes(searchQuery) ||
      reservation.id.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || reservation.status === statusFilter;
    
    let matchesDate = true;
    const today = new Date().toISOString().split('T')[0];
    const tomorrow = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    if (dateFilter === 'today') {
      matchesDate = reservation.reservation_date === today;
    } else if (dateFilter === 'tomorrow') {
      matchesDate = reservation.reservation_date === tomorrow;
    } else if (dateFilter === 'upcoming') {
      matchesDate = reservation.reservation_date >= today;
    }
    
    return matchesSearch && matchesStatus && matchesDate;
  });

  const updateReservationStatus = async (id: string, status: Reservation['status']) => {
    try {
      // Update via API
      await apiClient.updateReservation(id, { status });
      
      // Update local state
      setReservations(prev => 
        prev.map(reservation => 
          reservation.id === id 
            ? { ...reservation, status }
            : reservation
        )
      );
    } catch (error) {
      console.error('Error updating reservation status:', error);
      setError('Failed to update reservation status.');
    }
  };

  const getStatusColor = (status: Reservation['status']) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: Reservation['status']) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="h-4 w-4" />;
      case 'pending':
        return <Clock className="h-4 w-4" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      case 'cancelled':
        return <X className="h-4 w-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reservations</h1>
          <p className="text-gray-600 mt-1">
            Manage restaurant reservations and bookings.
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="text-sm">
            {filteredReservations.length} reservations
          </Badge>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-gray-900">
                  {reservations.filter(r => r.status === 'pending').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Confirmed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {reservations.filter(r => r.status === 'confirmed').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">Today's Guests</p>
                <p className="text-2xl font-bold text-gray-900">
                  {reservations
                    .filter(r => r.reservation_date === new Date().toISOString().split('T')[0] && r.status !== 'cancelled')
                    .reduce((sum, r) => sum + r.party_size, 0)
                  }
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Calendar className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm font-medium text-gray-600">This Week</p>
                <p className="text-2xl font-bold text-gray-900">
                  {reservations.filter(r => r.status !== 'cancelled').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filters & Search</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search by name, email, phone, or reservation ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={dateFilter} onValueChange={setDateFilter}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="today">Today</SelectItem>
                <SelectItem value="tomorrow">Tomorrow</SelectItem>
                <SelectItem value="upcoming">Upcoming</SelectItem>
                <SelectItem value="all">All Dates</SelectItem>
              </SelectContent>
            </Select>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="confirmed">Confirmed</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {loading && (
        <Card>
          <CardContent className="p-6 text-center">
            <p>Loading reservations...</p>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400">
              <MessageSquare className="h-4 w-4" />
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Reservations List */}
      {!loading && (
        <div className="space-y-4">
          {filteredReservations.length === 0 ? (
            <Card>
              <CardContent className="p-6 text-center">
                <p>No reservations found.</p>
              </CardContent>
            </Card>
          ) : (
            filteredReservations.map((reservation) => (
          <Card key={reservation.id} className="overflow-hidden">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {reservation.customer_name}
                    </h3>
                    <Badge className={getStatusColor(reservation.status)}>
                      <div className="flex items-center space-x-1">
                        {getStatusIcon(reservation.status)}
                        <span className="capitalize">{reservation.status}</span>
                      </div>
                    </Badge>
                    <Badge variant="outline">
                      {reservation.id}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Calendar className="h-4 w-4" />
                      <span>{formatDate(reservation.reservation_date)}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Clock className="h-4 w-4" />
                      <span>{reservation.reservation_time}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Users className="h-4 w-4" />
                      <span>{reservation.party_size} guests</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Phone className="h-4 w-4" />
                      <span>{reservation.customer_phone}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 text-sm text-gray-600 mb-3">
                    <Mail className="h-4 w-4" />
                    <span>{reservation.customer_email}</span>
                  </div>

                  {reservation.special_requests && (
                    <div className="flex items-start space-x-2 text-sm text-gray-600 mb-4">
                      <MessageSquare className="h-4 w-4 mt-0.5" />
                      <span>{reservation.special_requests}</span>
                    </div>
                  )}
                </div>

                <div className="flex flex-col space-y-2 ml-4">
                  {reservation.status === 'pending' && (
                    <>
                      <Button
                        size="sm"
                        onClick={() => updateReservationStatus(reservation.id, 'confirmed')}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Confirm
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateReservationStatus(reservation.id, 'cancelled')}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <X className="h-4 w-4 mr-1" />
                        Cancel
                      </Button>
                    </>
                  )}
                  
                  {reservation.status === 'confirmed' && (
                    <>
                      <Button
                        size="sm"
                        onClick={() => updateReservationStatus(reservation.id, 'completed')}
                        className="bg-blue-600 hover:bg-blue-700"
                      >
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Complete
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateReservationStatus(reservation.id, 'cancelled')}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <X className="h-4 w-4 mr-1" />
                        Cancel
                      </Button>
                    </>
                  )}
                  
                  {(reservation.status === 'completed' || reservation.status === 'cancelled') && (
                    <div className="text-xs text-gray-500 text-center">
                      {reservation.status === 'completed' ? 'Service completed' : 'Reservation cancelled'}
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
            ))
          )}
        </div>
      )}
    </div>
  );
}