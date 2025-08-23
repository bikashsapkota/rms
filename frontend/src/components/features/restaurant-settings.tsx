'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { 
  Save,
  Clock,
  MapPin,
  Phone,
  Mail,
  Globe,
  Users,
  Settings
} from 'lucide-react';

export function RestaurantSettings() {
  const [isLoading, setIsLoading] = useState(false);
  
  // Basic Information
  const [basicInfo, setBasicInfo] = useState({
    name: process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Demo Restaurant',
    description: 'Experience exceptional dining with authentic flavors, fresh ingredients, and warm hospitality in the heart of the city.',
    cuisine: 'Italian',
    priceRange: '$$',
    capacity: 80,
    phone: '(555) 123-4567',
    email: 'info@demorestaurant.com',
    website: 'https://demorestaurant.com'
  });

  // Location Information
  const [locationInfo, setLocationInfo] = useState({
    address: '123 Main Street',
    city: 'Downtown',
    state: 'City',
    zipCode: '12345',
    country: 'United States'
  });

  // Operating Hours
  const [hours, setHours] = useState({
    monday: { open: '11:00', close: '22:00', closed: false },
    tuesday: { open: '11:00', close: '22:00', closed: false },
    wednesday: { open: '11:00', close: '22:00', closed: false },
    thursday: { open: '11:00', close: '22:00', closed: false },
    friday: { open: '11:00', close: '23:00', closed: false },
    saturday: { open: '11:00', close: '23:00', closed: false },
    sunday: { open: '12:00', close: '21:00', closed: false }
  });

  // Reservation Settings
  const [reservationSettings, setReservationSettings] = useState({
    maxPartySize: 12,
    advanceBookingDays: 30,
    minAdvanceHours: 2,
    defaultReservationDuration: 120,
    autoConfirm: true,
    requirePhone: true,
    requireEmail: true
  });

  const handleSave = async (section: string) => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
    // Show success message (in real app)
    console.log(`${section} settings saved`);
  };

  const dayNames = {
    monday: 'Monday',
    tuesday: 'Tuesday', 
    wednesday: 'Wednesday',
    thursday: 'Thursday',
    friday: 'Friday',
    saturday: 'Saturday',
    sunday: 'Sunday'
  };

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Restaurant Settings</h1>
          <p className="text-gray-600 mt-1">
            Configure your restaurant's information and preferences.
          </p>
        </div>

        <Tabs defaultValue="basic" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="basic">Basic Info</TabsTrigger>
            <TabsTrigger value="location">Location</TabsTrigger>
            <TabsTrigger value="hours">Hours</TabsTrigger>
            <TabsTrigger value="reservations">Reservations</TabsTrigger>
          </TabsList>

          {/* Basic Information */}
          <TabsContent value="basic">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="h-5 w-5" />
                  <span>Basic Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Restaurant Name *
                    </label>
                    <Input
                      value={basicInfo.name}
                      onChange={(e) => setBasicInfo(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Enter restaurant name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cuisine Type
                    </label>
                    <Select value={basicInfo.cuisine} onValueChange={(value) => setBasicInfo(prev => ({ ...prev, cuisine: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select cuisine type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Italian">Italian</SelectItem>
                        <SelectItem value="French">French</SelectItem>
                        <SelectItem value="American">American</SelectItem>
                        <SelectItem value="Asian">Asian</SelectItem>
                        <SelectItem value="Mediterranean">Mediterranean</SelectItem>
                        <SelectItem value="Mexican">Mexican</SelectItem>
                        <SelectItem value="Other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <Textarea
                    value={basicInfo.description}
                    onChange={(e) => setBasicInfo(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe your restaurant..."
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Price Range
                    </label>
                    <Select value={basicInfo.priceRange} onValueChange={(value) => setBasicInfo(prev => ({ ...prev, priceRange: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="$">$ - Budget Friendly</SelectItem>
                        <SelectItem value="$$">$$ - Moderate</SelectItem>
                        <SelectItem value="$$$">$$$ - Upscale</SelectItem>
                        <SelectItem value="$$$$">$$$$ - Fine Dining</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Capacity (seats)
                    </label>
                    <Input
                      type="number"
                      value={basicInfo.capacity}
                      onChange={(e) => setBasicInfo(prev => ({ ...prev, capacity: parseInt(e.target.value) }))}
                      placeholder="Total seating capacity"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number
                    </label>
                    <Input
                      value={basicInfo.phone}
                      onChange={(e) => setBasicInfo(prev => ({ ...prev, phone: e.target.value }))}
                      placeholder="(555) 123-4567"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <Input
                      type="email"
                      value={basicInfo.email}
                      onChange={(e) => setBasicInfo(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="info@restaurant.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Website
                    </label>
                    <Input
                      value={basicInfo.website}
                      onChange={(e) => setBasicInfo(prev => ({ ...prev, website: e.target.value }))}
                      placeholder="https://restaurant.com"
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button 
                    onClick={() => handleSave('basic')}
                    disabled={isLoading}
                    className="bg-orange-500 hover:bg-orange-600"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Location Information */}
          <TabsContent value="location">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <MapPin className="h-5 w-5" />
                  <span>Location Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Street Address *
                  </label>
                  <Input
                    value={locationInfo.address}
                    onChange={(e) => setLocationInfo(prev => ({ ...prev, address: e.target.value }))}
                    placeholder="123 Main Street"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      City *
                    </label>
                    <Input
                      value={locationInfo.city}
                      onChange={(e) => setLocationInfo(prev => ({ ...prev, city: e.target.value }))}
                      placeholder="City"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      State/Province *
                    </label>
                    <Input
                      value={locationInfo.state}
                      onChange={(e) => setLocationInfo(prev => ({ ...prev, state: e.target.value }))}
                      placeholder="State"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Zip/Postal Code *
                    </label>
                    <Input
                      value={locationInfo.zipCode}
                      onChange={(e) => setLocationInfo(prev => ({ ...prev, zipCode: e.target.value }))}
                      placeholder="12345"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Country *
                    </label>
                    <Input
                      value={locationInfo.country}
                      onChange={(e) => setLocationInfo(prev => ({ ...prev, country: e.target.value }))}
                      placeholder="United States"
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button 
                    onClick={() => handleSave('location')}
                    disabled={isLoading}
                    className="bg-orange-500 hover:bg-orange-600"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Operating Hours */}
          <TabsContent value="hours">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="h-5 w-5" />
                  <span>Operating Hours</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {Object.entries(dayNames).map(([key, dayName]) => (
                  <div key={key} className="flex items-center space-x-4 p-4 border rounded-lg">
                    <div className="w-24">
                      <span className="font-medium text-gray-900">{dayName}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={hours[key as keyof typeof hours].closed}
                        onChange={(e) => setHours(prev => ({
                          ...prev,
                          [key]: { ...prev[key as keyof typeof prev], closed: e.target.checked }
                        }))}
                        className="rounded border-gray-300"
                      />
                      <label className="text-sm text-gray-600">Closed</label>
                    </div>

                    {!hours[key as keyof typeof hours].closed && (
                      <div className="flex items-center space-x-2">
                        <Input
                          type="time"
                          value={hours[key as keyof typeof hours].open}
                          onChange={(e) => setHours(prev => ({
                            ...prev,
                            [key]: { ...prev[key as keyof typeof prev], open: e.target.value }
                          }))}
                          className="w-32"
                        />
                        <span className="text-gray-500">to</span>
                        <Input
                          type="time"
                          value={hours[key as keyof typeof hours].close}
                          onChange={(e) => setHours(prev => ({
                            ...prev,
                            [key]: { ...prev[key as keyof typeof prev], close: e.target.value }
                          }))}
                          className="w-32"
                        />
                      </div>
                    )}
                  </div>
                ))}

                <div className="flex justify-end">
                  <Button 
                    onClick={() => handleSave('hours')}
                    disabled={isLoading}
                    className="bg-orange-500 hover:bg-orange-600"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Reservation Settings */}
          <TabsContent value="reservations">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5" />
                  <span>Reservation Settings</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Maximum Party Size
                    </label>
                    <Input
                      type="number"
                      value={reservationSettings.maxPartySize}
                      onChange={(e) => setReservationSettings(prev => ({ 
                        ...prev, 
                        maxPartySize: parseInt(e.target.value) 
                      }))}
                      min="1"
                      max="50"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Advance Booking (days)
                    </label>
                    <Input
                      type="number"
                      value={reservationSettings.advanceBookingDays}
                      onChange={(e) => setReservationSettings(prev => ({ 
                        ...prev, 
                        advanceBookingDays: parseInt(e.target.value) 
                      }))}
                      min="1"
                      max="365"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Minimum Advance Hours
                    </label>
                    <Input
                      type="number"
                      value={reservationSettings.minAdvanceHours}
                      onChange={(e) => setReservationSettings(prev => ({ 
                        ...prev, 
                        minAdvanceHours: parseInt(e.target.value) 
                      }))}
                      min="0"
                      max="48"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Default Duration (minutes)
                    </label>
                    <Input
                      type="number"
                      value={reservationSettings.defaultReservationDuration}
                      onChange={(e) => setReservationSettings(prev => ({ 
                        ...prev, 
                        defaultReservationDuration: parseInt(e.target.value) 
                      }))}
                      min="30"
                      max="240"
                      step="15"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={reservationSettings.autoConfirm}
                      onChange={(e) => setReservationSettings(prev => ({ 
                        ...prev, 
                        autoConfirm: e.target.checked 
                      }))}
                      className="rounded border-gray-300"
                    />
                    <label className="text-sm font-medium text-gray-700">
                      Auto-confirm reservations
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={reservationSettings.requirePhone}
                      onChange={(e) => setReservationSettings(prev => ({ 
                        ...prev, 
                        requirePhone: e.target.checked 
                      }))}
                      className="rounded border-gray-300"
                    />
                    <label className="text-sm font-medium text-gray-700">
                      Require phone number
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={reservationSettings.requireEmail}
                      onChange={(e) => setReservationSettings(prev => ({ 
                        ...prev, 
                        requireEmail: e.target.checked 
                      }))}
                      className="rounded border-gray-300"
                    />
                    <label className="text-sm font-medium text-gray-700">
                      Require email address
                    </label>
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button 
                    onClick={() => handleSave('reservations')}
                    disabled={isLoading}
                    className="bg-orange-500 hover:bg-orange-600"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}