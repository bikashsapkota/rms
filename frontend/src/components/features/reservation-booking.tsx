'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Calendar, Clock, Users, CheckCircle, AlertCircle } from 'lucide-react';
import { format, addDays, isWeekend, isSunday } from 'date-fns';
import { apiClient } from '@/lib/api';

interface TimeSlot {
  time: string;
  available: boolean;
}

interface ReservationBookingProps {
  initialAvailability?: any;
  prefillData: {
    date: string;
    time: string;
    partySize: string;
  };
}

export function ReservationBooking({ initialAvailability, prefillData }: ReservationBookingProps) {
  const router = useRouter();
  const [step, setStep] = useState<'select' | 'form' | 'confirmation'>('select');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Booking selection state
  const [selectedDate, setSelectedDate] = useState(prefillData.date);
  const [selectedTime, setSelectedTime] = useState(prefillData.time);
  const [partySize, setPartySize] = useState(prefillData.partySize);
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);

  // Customer information state
  const [customerInfo, setCustomerInfo] = useState({
    name: '',
    email: '',
    phone: '',
    specialRequests: ''
  });

  // Confirmation state
  const [confirmation, setConfirmation] = useState<any>(null);

  const restaurantName = process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Demo Restaurant';

  // Generate time slots (demo data)
  const generateTimeSlots = (date: string): TimeSlot[] => {
    const slots: TimeSlot[] = [];
    const selectedDateObj = new Date(date);
    const isWeekendDay = isWeekend(selectedDateObj);
    const isSundayDay = isSunday(selectedDateObj);

    // Different hours for different days
    let startHour = isSundayDay ? 12 : 11; // Sunday starts at 12 PM
    let endHour = isWeekendDay && !isSundayDay ? 23 : isSundayDay ? 21 : 22; // Weekend until 11 PM, Sunday until 9 PM

    for (let hour = startHour; hour <= endHour; hour++) {
      for (let minute = 0; minute < 60; minute += 30) {
        const timeString = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
        
        // Simulate availability (some slots unavailable)
        const isAvailable = Math.random() > 0.3; // 70% availability
        
        slots.push({
          time: timeString,
          available: isAvailable
        });
      }
    }

    return slots;
  };

  // Load availability when date or party size changes
  useEffect(() => {
    if (selectedDate && partySize) {
      setLoading(true);
      setError(null);

      // Simulate API call delay
      setTimeout(() => {
        try {
          const slots = generateTimeSlots(selectedDate);
          setAvailableSlots(slots);
        } catch (err) {
          setError('Failed to load availability. Please try again.');
        } finally {
          setLoading(false);
        }
      }, 500);
    }
  }, [selectedDate, partySize]);

  const handleDateTimeSelection = () => {
    if (!selectedDate || !selectedTime || !partySize) {
      setError('Please select date, time, and party size');
      return;
    }
    setError(null);
    setStep('form');
  };

  const handleReservationSubmit = async () => {
    if (!customerInfo.name || !customerInfo.email || !customerInfo.phone) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create reservation
      const reservationData = {
        customer_name: customerInfo.name,
        customer_email: customerInfo.email,
        customer_phone: customerInfo.phone,
        party_size: parseInt(partySize),
        reservation_date: selectedDate,
        reservation_time: selectedTime,
        special_requests: customerInfo.specialRequests
      };

      // Call the real API to create reservation
      const response = await apiClient.createPublicReservation(reservationData);
      
      setConfirmation({
        id: response.reservation_id,
        ...reservationData,
        confirmation_number: `RES-${response.reservation_id.slice(-6)}`,
        status: response.status || 'confirmed'
      });
      setStep('confirmation');
      setLoading(false);

    } catch (err) {
      setError('Failed to create reservation. Please try again.');
      setLoading(false);
    }
  };

  const formatDisplayDate = (dateString: string) => {
    return format(new Date(dateString), 'EEEE, MMMM d, yyyy');
  };

  const formatDisplayTime = (timeString: string) => {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  if (step === 'confirmation' && confirmation) {
    return (
      <div className="bg-white">
        {/* Success Header */}
        <section className="bg-green-50 py-16">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-6" />
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Reservation Confirmed!
            </h1>
            <p className="text-xl text-gray-600">
              Thank you for choosing {restaurantName}. We look forward to serving you!
            </p>
          </div>
        </section>

        {/* Confirmation Details */}
        <section className="py-12">
          <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
            <Card className="shadow-lg">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl text-gray-900">Reservation Details</CardTitle>
                <p className="text-lg font-semibold text-green-600">
                  Confirmation #{confirmation.confirmation_number}
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <Label className="text-sm font-medium text-gray-700">Date</Label>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatDisplayDate(confirmation.reservation_date)}
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-700">Time</Label>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatDisplayTime(confirmation.reservation_time)}
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-700">Party Size</Label>
                    <p className="text-lg font-semibold text-gray-900">
                      {confirmation.party_size} {confirmation.party_size === 1 ? 'Guest' : 'Guests'}
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-700">Status</Label>
                    <p className="text-lg font-semibold text-green-600 capitalize">
                      {confirmation.status}
                    </p>
                  </div>
                </div>

                <div className="border-t pt-6">
                  <Label className="text-sm font-medium text-gray-700">Customer Information</Label>
                  <div className="mt-2 space-y-2">
                    <p><span className="font-medium">Name:</span> {confirmation.customer_name}</p>
                    <p><span className="font-medium">Email:</span> {confirmation.customer_email}</p>
                    <p><span className="font-medium">Phone:</span> {confirmation.customer_phone}</p>
                    {confirmation.special_requests && (
                      <p><span className="font-medium">Special Requests:</span> {confirmation.special_requests}</p>
                    )}
                  </div>
                </div>

                <div className="border-t pt-6 text-center">
                  <p className="text-sm text-gray-600 mb-4">
                    A confirmation email has been sent to {confirmation.customer_email}
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Button onClick={() => router.push('/')} variant="outline">
                      Back to Home
                    </Button>
                    <Button onClick={() => router.push('/menu')} className="bg-orange-500 hover:bg-orange-600">
                      View Menu
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="bg-white">
      {/* Header */}
      <section className="bg-gradient-to-br from-orange-50 via-white to-orange-50 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Book Your Table
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Reserve your spot for an exceptional dining experience at {restaurantName}. 
            Choose your preferred date and time below.
          </p>
        </div>
      </section>

      {/* Booking Steps */}
      <section className="py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Step Indicator */}
          <div className="flex items-center justify-center mb-8">
            <div className="flex items-center space-x-4">
              <div className={`flex items-center ${step === 'select' ? 'text-orange-600' : 'text-green-600'}`}>
                <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                  step === 'select' ? 'bg-orange-500 text-white' : 'bg-green-500 text-white'
                }`}>
                  {step === 'select' ? '1' : '✓'}
                </div>
                <span className="ml-2 font-medium">Select Date & Time</span>
              </div>
              <div className="h-0.5 w-8 bg-gray-300"></div>
              <div className={`flex items-center ${step === 'form' ? 'text-orange-600' : step === 'confirmation' ? 'text-green-600' : 'text-gray-400'}`}>
                <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                  step === 'form' ? 'bg-orange-500 text-white' : 
                  step === 'confirmation' ? 'bg-green-500 text-white' : 
                  'bg-gray-300 text-gray-600'
                }`}>
                  {step === 'confirmation' ? '✓' : '2'}
                </div>
                <span className="ml-2 font-medium">Your Information</span>
              </div>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
              <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
              <span className="text-red-700">{error}</span>
            </div>
          )}

          {step === 'select' && (
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="text-2xl text-center">When would you like to dine?</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Date, Time, Party Size Selection */}
                <div className="grid md:grid-cols-3 gap-6">
                  <div>
                    <Label htmlFor="date" className="flex items-center text-sm font-medium text-gray-700 mb-2">
                      <Calendar className="h-4 w-4 mr-2" />
                      Date
                    </Label>
                    <Input
                      id="date"
                      type="date"
                      value={selectedDate}
                      onChange={(e) => setSelectedDate(e.target.value)}
                      min={format(new Date(), 'yyyy-MM-dd')}
                      max={format(addDays(new Date(), 60), 'yyyy-MM-dd')}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <Label htmlFor="party-size" className="flex items-center text-sm font-medium text-gray-700 mb-2">
                      <Users className="h-4 w-4 mr-2" />
                      Party Size
                    </Label>
                    <Select value={partySize} onValueChange={setPartySize}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select party size" />
                      </SelectTrigger>
                      <SelectContent>
                        {Array.from({ length: 12 }, (_, i) => i + 1).map((size) => (
                          <SelectItem key={size} value={size.toString()}>
                            {size} {size === 1 ? 'Guest' : 'Guests'}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                      <Clock className="h-4 w-4 mr-2" />
                      Available Times
                    </Label>
                    <div className="text-sm text-gray-600">
                      {selectedDate && partySize ? 'Select a time below' : 'Choose date & party size first'}
                    </div>
                  </div>
                </div>

                {/* Time Slots */}
                {selectedDate && partySize && (
                  <div>
                    <Label className="text-lg font-semibold text-gray-900 mb-4 block">
                      Available Times for {formatDisplayDate(selectedDate)}
                    </Label>
                    
                    {loading ? (
                      <div className="text-center py-8">
                        <div className="animate-spin h-8 w-8 border-b-2 border-orange-500 rounded-full mx-auto"></div>
                        <p className="mt-2 text-gray-600">Loading available times...</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-3">
                        {availableSlots.map((slot) => (
                          <Button
                            key={slot.time}
                            variant={selectedTime === slot.time ? "default" : "outline"}
                            onClick={() => setSelectedTime(slot.time)}
                            disabled={!slot.available}
                            className={`${
                              selectedTime === slot.time 
                                ? 'bg-orange-500 hover:bg-orange-600 text-white' 
                                : slot.available 
                                  ? 'border-orange-500 text-orange-600 hover:bg-orange-50' 
                                  : 'opacity-50 cursor-not-allowed'
                            }`}
                          >
                            {formatDisplayTime(slot.time)}
                          </Button>
                        ))}
                      </div>
                    )}

                    {availableSlots.length > 0 && (
                      <div className="mt-6 text-center">
                        <Button 
                          size="lg" 
                          onClick={handleDateTimeSelection}
                          disabled={!selectedTime}
                          className="bg-orange-500 hover:bg-orange-600 text-white px-8"
                        >
                          Continue to Details
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {step === 'form' && (
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="text-2xl text-center">Your Information</CardTitle>
                <div className="text-center text-gray-600">
                  <p>{formatDisplayDate(selectedDate)} at {formatDisplayTime(selectedTime)}</p>
                  <p>{partySize} {parseInt(partySize) === 1 ? 'Guest' : 'Guests'}</p>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="name" className="text-sm font-medium text-gray-700">
                      Full Name *
                    </Label>
                    <Input
                      id="name"
                      type="text"
                      value={customerInfo.name}
                      onChange={(e) => setCustomerInfo(prev => ({ ...prev, name: e.target.value }))}
                      className="mt-1"
                      placeholder="John Doe"
                    />
                  </div>

                  <div>
                    <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                      Email Address *
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      value={customerInfo.email}
                      onChange={(e) => setCustomerInfo(prev => ({ ...prev, email: e.target.value }))}
                      className="mt-1"
                      placeholder="john@example.com"
                    />
                  </div>

                  <div>
                    <Label htmlFor="phone" className="text-sm font-medium text-gray-700">
                      Phone Number *
                    </Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={customerInfo.phone}
                      onChange={(e) => setCustomerInfo(prev => ({ ...prev, phone: e.target.value }))}
                      className="mt-1"
                      placeholder="(555) 123-4567"
                    />
                  </div>

                  <div>
                    <Label htmlFor="special-requests" className="text-sm font-medium text-gray-700">
                      Special Requests (Optional)
                    </Label>
                    <Textarea
                      id="special-requests"
                      value={customerInfo.specialRequests}
                      onChange={(e) => setCustomerInfo(prev => ({ ...prev, specialRequests: e.target.value }))}
                      className="mt-1"
                      placeholder="Allergies, special occasions, seating preferences..."
                      rows={3}
                    />
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button 
                    variant="outline" 
                    onClick={() => setStep('select')}
                    className="border-orange-500 text-orange-600 hover:bg-orange-50"
                  >
                    ← Back to Date & Time
                  </Button>
                  <Button 
                    size="lg" 
                    onClick={handleReservationSubmit}
                    disabled={loading}
                    className="bg-orange-500 hover:bg-orange-600 text-white px-8"
                  >
                    {loading ? 'Creating Reservation...' : 'Confirm Reservation'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </section>
    </div>
  );
}