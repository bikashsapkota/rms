'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar, Clock, Users } from 'lucide-react';
import { format, addDays } from 'date-fns';

export function ReservationWidget() {
  const router = useRouter();
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [partySize, setPartySize] = useState<string>('');

  const today = new Date();
  const tomorrow = addDays(today, 1);
  const weekend = addDays(today, 6);

  const timeSlots = [
    '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
    '20:00', '20:30', '21:00', '21:30', '22:00'
  ];

  const handleQuickBook = (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    router.push(`/book?date=${dateStr}&party_size=2&time=19:00`);
  };

  const handleCheckAvailability = () => {
    if (!selectedDate || !selectedTime || !partySize) {
      alert('Please select date, time, and party size');
      return;
    }
    
    const params = new URLSearchParams({
      date: selectedDate,
      time: selectedTime,
      party_size: partySize
    });
    
    router.push(`/book?${params.toString()}`);
  };

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            📅 Reserve Your Table
          </h2>
          <p className="text-lg text-gray-600">
            Book your dining experience in just a few clicks
          </p>
        </div>

        <Card className="shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-xl text-gray-800">Find Available Times</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Reservation Form */}
            <div className="grid md:grid-cols-3 gap-4">
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
                  min={format(today, 'yyyy-MM-dd')}
                  className="w-full"
                />
              </div>

              <div>
                <Label htmlFor="time" className="flex items-center text-sm font-medium text-gray-700 mb-2">
                  <Clock className="h-4 w-4 mr-2" />
                  Time
                </Label>
                <Select value={selectedTime} onValueChange={setSelectedTime}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select time" />
                  </SelectTrigger>
                  <SelectContent>
                    {timeSlots.map((time) => (
                      <SelectItem key={time} value={time}>
                        {time}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="guests" className="flex items-center text-sm font-medium text-gray-700 mb-2">
                  <Users className="h-4 w-4 mr-2" />
                  Guests
                </Label>
                <Select value={partySize} onValueChange={setPartySize}>
                  <SelectTrigger>
                    <SelectValue placeholder="Party size" />
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
            </div>

            {/* Check Availability Button */}
            <div className="text-center">
              <Button 
                size="lg" 
                onClick={handleCheckAvailability}
                className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3"
              >
                Check Availability →
              </Button>
            </div>

            {/* Quick Book Options */}
            <div className="border-t pt-6">
              <h3 className="text-center font-medium text-gray-800 mb-4">Quick Book</h3>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button 
                  variant="outline" 
                  onClick={() => handleQuickBook(today)}
                  className="border-orange-500 text-orange-600 hover:bg-orange-50"
                >
                  Tonight (7:00 PM)
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => handleQuickBook(tomorrow)}
                  className="border-orange-500 text-orange-600 hover:bg-orange-50"
                >
                  Tomorrow (7:00 PM)
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => handleQuickBook(weekend)}
                  className="border-orange-500 text-orange-600 hover:bg-orange-50"
                >
                  This Weekend (7:00 PM)
                </Button>
              </div>
            </div>

            {/* Contact Info */}
            <div className="text-center text-sm text-gray-600 bg-gray-50 rounded-lg p-4">
              <p className="font-medium mb-2">Need assistance with your reservation?</p>
              <p>Call us at <span className="font-semibold text-orange-600">(555) 123-4567</span></p>
              <p>or email <span className="font-semibold text-orange-600">reservations@restaurant.com</span></p>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}