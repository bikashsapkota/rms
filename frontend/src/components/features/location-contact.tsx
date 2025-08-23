'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { MapPin, Phone, Mail, Clock, Car, Navigation } from 'lucide-react';

export function LocationContact() {
  const restaurantName = process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Demo Restaurant';

  const openingHours = [
    { day: 'Monday - Thursday', hours: '11:00 AM - 10:00 PM' },
    { day: 'Friday - Saturday', hours: '11:00 AM - 11:00 PM' },
    { day: 'Sunday', hours: '12:00 PM - 9:00 PM' },
  ];

  const handleGetDirections = () => {
    // In a real app, this would open Google Maps with the restaurant address
    window.open('https://maps.google.com/?q=123+Main+Street+Downtown', '_blank');
  };

  const handleCallNow = () => {
    window.open('tel:+15551234567', '_self');
  };

  const handleEmailUs = () => {
    window.open(`mailto:info@${restaurantName.toLowerCase().replace(/\s+/g, '')}.com`, '_self');
  };

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            📍 Visit Us Today
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Located in the heart of downtown, we're easily accessible and ready to welcome you 
            for an unforgettable dining experience.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Map Section */}
          <div>
            <Card className="overflow-hidden shadow-lg h-full">
              <div className="aspect-square lg:aspect-auto lg:h-full bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center relative">
                <div className="text-center z-10">
                  <MapPin className="h-16 w-16 mx-auto mb-4 text-orange-600" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Interactive Map
                  </h3>
                  <p className="text-gray-600 mb-4">
                    123 Main Street<br />
                    Downtown, City 12345
                  </p>
                  <Button onClick={handleGetDirections} className="bg-orange-500 hover:bg-orange-600">
                    <Navigation className="mr-2 h-4 w-4" />
                    Get Directions
                  </Button>
                </div>
                
                {/* Placeholder for actual map integration */}
                <div className="absolute inset-0 bg-gradient-to-br from-orange-50 to-orange-100 opacity-50"></div>
              </div>
            </Card>
          </div>

          {/* Contact Information */}
          <div className="space-y-6">
            {/* Address & Contact */}
            <Card className="shadow-lg">
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Contact Information</h3>
                
                <div className="space-y-4">
                  <div className="flex items-start space-x-4">
                    <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center flex-shrink-0">
                      <MapPin className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">Address</h4>
                      <p className="text-gray-600">
                        123 Main Street<br />
                        Downtown, City 12345<br />
                        United States
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center flex-shrink-0">
                      <Phone className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">Phone</h4>
                      <p className="text-gray-600">(555) 123-4567</p>
                      <Button 
                        variant="link" 
                        className="p-0 h-auto text-orange-600 hover:text-orange-700"
                        onClick={handleCallNow}
                      >
                        Call Now
                      </Button>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center flex-shrink-0">
                      <Mail className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">Email</h4>
                      <p className="text-gray-600">info@{restaurantName.toLowerCase().replace(/\s+/g, '')}.com</p>
                      <Button 
                        variant="link" 
                        className="p-0 h-auto text-orange-600 hover:text-orange-700"
                        onClick={handleEmailUs}
                      >
                        Send Email
                      </Button>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center flex-shrink-0">
                      <Car className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">Parking</h4>
                      <p className="text-gray-600">
                        Free valet parking available<br />
                        Street parking also available
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Opening Hours */}
            <Card className="shadow-lg">
              <CardContent className="p-6">
                <div className="flex items-center mb-6">
                  <Clock className="h-5 w-5 text-orange-600 mr-2" />
                  <h3 className="text-xl font-semibold text-gray-900">Opening Hours</h3>
                </div>
                
                <div className="space-y-3">
                  {openingHours.map((schedule, index) => (
                    <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
                      <span className="font-medium text-gray-900">{schedule.day}</span>
                      <span className="text-gray-600">{schedule.hours}</span>
                    </div>
                  ))}
                </div>

                <div className="mt-6 p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center">
                    <div className="h-3 w-3 rounded-full bg-green-500 mr-3"></div>
                    <span className="font-semibold text-green-800">Open Now</span>
                  </div>
                  <p className="text-sm text-green-700 mt-1">Closes at 10:00 PM today</p>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 gap-4">
              <Button 
                size="lg" 
                onClick={handleGetDirections}
                className="bg-orange-500 hover:bg-orange-600 text-white"
              >
                <Navigation className="mr-2 h-4 w-4" />
                Get Directions
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                onClick={handleCallNow}
                className="border-orange-500 text-orange-600 hover:bg-orange-50"
              >
                <Phone className="mr-2 h-4 w-4" />
                Call Now
              </Button>
            </div>

            {/* Additional Info */}
            <Card className="bg-orange-50 border-orange-200">
              <CardContent className="p-6">
                <h3 className="font-semibold text-gray-900 mb-3">Good to Know</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li>• Reservations recommended for dinner</li>
                  <li>• Walk-ins welcome for lunch</li>
                  <li>• Private dining rooms available</li>
                  <li>• Wheelchair accessible</li>
                  <li>• Full bar with craft cocktails</li>
                  <li>• Vegetarian and gluten-free options available</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}