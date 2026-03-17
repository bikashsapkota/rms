'use client';

import { useState, useEffect } from 'react';
import { useApiClient } from '@/hooks/useApiClient';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Calendar, 
  DollarSign, 
  Users, 
  TrendingUp, 
  Clock, 
  CheckCircle,
  AlertTriangle,
  Eye
} from 'lucide-react';
import Link from 'next/link';

export function DashboardOverview() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({
    todayReservations: 0,
    todayRevenue: 0,
    todayGuests: 0,
    weeklyGrowth: 0,
  });
  const [recentReservations, setRecentReservations] = useState<any[]>([]);
  const [todayMenu, setTodayMenu] = useState<any[]>([]);

  const restaurantName = process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Demo Restaurant';
  const apiClient = useApiClient();

  // Fetch dashboard data from backend
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all dashboard data in parallel
        const [statsResponse, reservationsResponse, menuResponse] = await Promise.all([
          apiClient.getDashboardStats(),
          apiClient.getTodaysReservations(),
          apiClient.getMenuItemsWithOrderCount()
        ]);

        setStats(statsResponse);
        setRecentReservations(reservationsResponse);
        setTodayMenu(menuResponse);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError(`Failed to load dashboard data from database. Error: ${error instanceof Error ? error.message : 'Unknown error'}. Please check your backend connection and database.`);
        
        // No fallback data - show empty states and errors
        setStats({
          todayReservations: 0,
          todayRevenue: 0,
          todayGuests: 0,
          weeklyGrowth: 0,
        });
        setRecentReservations([]);
        setTodayMenu([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [apiClient]);

  // Auto-refresh data every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('Auto-refreshing dashboard data...');
      const fetchData = async () => {
        try {
          const [statsResponse, reservationsResponse, menuResponse] = await Promise.all([
            apiClient.getDashboardStats(),
            apiClient.getTodaysReservations(),
            apiClient.getMenuItemsWithOrderCount()
          ]);
          setStats(statsResponse);
          setRecentReservations(reservationsResponse);
          setTodayMenu(menuResponse);
        } catch (error) {
          console.error('Error auto-refreshing dashboard data:', error);
        }
      };
      fetchData();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [apiClient]);

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
            <p className="mt-2 text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Error Display */}
      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div className="flex">
            <AlertTriangle className="h-5 w-5 text-yellow-400" />
            <div className="ml-3">
              <p className="text-sm text-yellow-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome to {restaurantName}
          </h1>
          <p className="text-gray-600 mt-1">
            Here's what's happening at your restaurant today.
          </p>
        </div>
        <Link href="/" target="_blank">
          <Button variant="outline" className="flex items-center space-x-2">
            <Eye className="h-4 w-4" />
            <span>View Public Site</span>
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Today's Reservations
            </CardTitle>
            <Calendar className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{stats.todayReservations}</div>
            <p className="text-xs text-green-600 mt-1">
              +3 from yesterday
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Today's Revenue
            </CardTitle>
            <DollarSign className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              ${stats.todayRevenue.toLocaleString()}
            </div>
            <p className="text-xs text-green-600 mt-1">
              +{stats.weeklyGrowth}% from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Guests Served
            </CardTitle>
            <Users className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{stats.todayGuests}</div>
            <p className="text-xs text-green-600 mt-1">
              +8 from yesterday
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Weekly Growth
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              +{stats.weeklyGrowth}%
            </div>
            <p className="text-xs text-green-600 mt-1">
              Revenue increase
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Reservations */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold">
                Today's Reservations
              </CardTitle>
              <Link href="/dashboard/reservations">
                <Button variant="outline" size="sm">
                  View All
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentReservations.length > 0 ? (
                recentReservations.map((reservation) => (
                  <div
                    key={reservation.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center">
                        <span className="text-orange-600 font-medium text-sm">
                          {reservation.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{reservation.name}</p>
                        <p className="text-sm text-gray-500">
                          {reservation.time} • {reservation.guests} guests
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {reservation.status === 'confirmed' ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : (
                        <Clock className="h-5 w-5 text-yellow-500" />
                      )}
                      <span className={`text-xs font-medium ${
                        reservation.status === 'confirmed' 
                          ? 'text-green-600' 
                          : 'text-yellow-600'
                      }`}>
                        {reservation.status}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Calendar className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 text-sm">No reservations found for today</p>
                  <p className="text-gray-400 text-xs mt-1">
                    Reservations will appear here once customers book tables
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Menu Status */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold">
                Menu Status
              </CardTitle>
              <Link href="/dashboard/menu">
                <Button variant="outline" size="sm">
                  Manage Menu
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {todayMenu.length > 0 ? (
                todayMenu.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{item.name}</p>
                      <p className="text-sm text-gray-500">{item.orders} orders today</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      {item.status === 'available' ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : (
                        <AlertTriangle className="h-5 w-5 text-yellow-500" />
                      )}
                      <span className={`text-xs font-medium ${
                        item.status === 'available' 
                          ? 'text-green-600' 
                          : 'text-yellow-600'
                      }`}>
                        {item.status === 'low-stock' ? 'Low Stock' : 'Available'}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Users className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 text-sm">No menu data available</p>
                  <p className="text-gray-400 text-xs mt-1">
                    Menu items and order statistics will appear here
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link href="/dashboard/reservations">
              <Button variant="outline" className="w-full justify-start h-auto p-4">
                <div className="flex flex-col items-start space-y-1">
                  <Calendar className="h-5 w-5 text-orange-600" />
                  <span className="font-medium">Manage Reservations</span>
                  <span className="text-xs text-gray-500">View and update bookings</span>
                </div>
              </Button>
            </Link>

            <Link href="/dashboard/menu">
              <Button variant="outline" className="w-full justify-start h-auto p-4">
                <div className="flex flex-col items-start space-y-1">
                  <Users className="h-5 w-5 text-orange-600" />
                  <span className="font-medium">Update Menu</span>
                  <span className="text-xs text-gray-500">Edit dishes and prices</span>
                </div>
              </Button>
            </Link>

            <Link href="/dashboard/staff">
              <Button variant="outline" className="w-full justify-start h-auto p-4">
                <div className="flex flex-col items-start space-y-1">
                  <Users className="h-5 w-5 text-orange-600" />
                  <span className="font-medium">Staff Management</span>
                  <span className="text-xs text-gray-500">Manage team members</span>
                </div>
              </Button>
            </Link>

            <Link href="/dashboard/settings">
              <Button variant="outline" className="w-full justify-start h-auto p-4">
                <div className="flex flex-col items-start space-y-1">
                  <TrendingUp className="h-5 w-5 text-orange-600" />
                  <span className="font-medium">Restaurant Settings</span>
                  <span className="text-xs text-gray-500">Configure restaurant</span>
                </div>
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}