'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Calendar, Menu as MenuIcon, MapPin, Phone, Clock } from 'lucide-react';

export function HeroSection() {
  const restaurantName = process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Demo Restaurant';

  return (
    <section className="relative bg-gradient-to-br from-orange-50 via-white to-orange-50 py-16 lg:py-24">
      <div className="absolute inset-0 bg-[url('/hero-pattern.svg')] opacity-5"></div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div className="text-center lg:text-left">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Welcome to <br />
              <span className="text-orange-500">{restaurantName}</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl">
              Experience exceptional dining with authentic flavors, fresh ingredients, 
              and warm hospitality in the heart of downtown.
            </p>
            
            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start mb-8">
              <Link href="/book">
                <Button size="lg" className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 text-lg">
                  <Calendar className="mr-2 h-5 w-5" />
                  Make Reservation
                </Button>
              </Link>
              <Link href="/menu">
                <Button variant="outline" size="lg" className="border-orange-500 text-orange-600 hover:bg-orange-50 px-8 py-3 text-lg">
                  <MenuIcon className="mr-2 h-5 w-5" />
                  View Menu
                </Button>
              </Link>
            </div>

            {/* Quick Info */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm text-gray-600">
              <div className="flex items-center justify-center lg:justify-start">
                <MapPin className="h-4 w-4 mr-2 text-orange-500" />
                <span>123 Main Street, Downtown</span>
              </div>
              <div className="flex items-center justify-center lg:justify-start">
                <Phone className="h-4 w-4 mr-2 text-orange-500" />
                <span>(555) 123-4567</span>
              </div>
              <div className="flex items-center justify-center lg:justify-start">
                <Clock className="h-4 w-4 mr-2 text-orange-500" />
                <span className="text-green-600 font-medium">Open Now</span>
              </div>
            </div>
          </div>

          {/* Hero Image */}
          <div className="lg:order-first">
            <div className="relative">
              <div className="aspect-square rounded-2xl bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center shadow-2xl">
                <div className="text-center">
                  <div className="h-32 w-32 mx-auto mb-4 rounded-full bg-orange-500 flex items-center justify-center">
                    <span className="text-white text-4xl font-bold">
                      {restaurantName.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <p className="text-gray-600 text-lg">
                    Beautiful restaurant interior<br />
                    photo coming soon
                  </p>
                </div>
              </div>
              
              {/* Decorative elements */}
              <div className="absolute -top-4 -right-4 h-24 w-24 rounded-full bg-orange-300 opacity-20"></div>
              <div className="absolute -bottom-4 -left-4 h-16 w-16 rounded-full bg-orange-400 opacity-30"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Info Bar */}
      <div className="mt-16 bg-orange-500 text-white py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-center md:justify-between gap-4 text-center md:text-left">
            <div className="flex items-center">
              <Clock className="h-5 w-5 mr-2" />
              <span className="font-medium">Today: 11:00 AM - 10:00 PM</span>
            </div>
            <div className="flex items-center">
              <span className="px-3 py-1 bg-orange-600 rounded-full text-sm font-medium">
                🎉 Happy Hour 4-6 PM - 20% off appetizers
              </span>
            </div>
            <div className="flex items-center">
              <Phone className="h-5 w-5 mr-2" />
              <span>Call (555) 123-4567 for takeout</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}