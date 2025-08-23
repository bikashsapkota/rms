'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Award, Heart, Leaf, Users } from 'lucide-react';
import Link from 'next/link';

export function RestaurantStory() {
  const restaurantName = process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Demo Restaurant';

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Story Content */}
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Story</h2>
            <div className="prose prose-lg text-gray-600">
              <p className="mb-6">
                For over 20 years, we've been serving exceptional cuisine made with love and the 
                freshest ingredients. Our family recipes have been passed down through generations, 
                creating an authentic dining experience that brings people together.
              </p>
              <p className="mb-6">
                Located in the heart of downtown, {restaurantName} combines traditional cooking 
                methods with modern culinary techniques to create dishes that honor our heritage 
                while exciting contemporary palates.
              </p>
              <p className="mb-8">
                Every dish tells a story, every meal creates memories, and every guest becomes 
                part of our extended family.
              </p>
            </div>

            {/* Values */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center">
                  <Leaf className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Farm to Table</h4>
                  <p className="text-sm text-gray-600">Fresh local ingredients</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center">
                  <Heart className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Made with Love</h4>
                  <p className="text-sm text-gray-600">Family recipes</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center">
                  <Users className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Community First</h4>
                  <p className="text-sm text-gray-600">Supporting local</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center">
                  <Award className="h-5 w-5 text-orange-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Award Winning</h4>
                  <p className="text-sm text-gray-600">Recognized excellence</p>
                </div>
              </div>
            </div>

            <Link href="/about">
              <Button variant="outline" className="border-orange-500 text-orange-600 hover:bg-orange-50">
                Learn More About Us
              </Button>
            </Link>
          </div>

          {/* Chef Profile */}
          <div>
            <Card className="overflow-hidden shadow-lg">
              <div className="aspect-square bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center">
                <div className="text-center">
                  <div className="h-32 w-32 mx-auto mb-4 rounded-full bg-orange-500 flex items-center justify-center">
                    <span className="text-white text-4xl font-bold">MR</span>
                  </div>
                  <p className="text-gray-600">Chef Marco Rossi</p>
                  <p className="text-sm text-gray-500">Photo coming soon</p>
                </div>
              </div>
              <CardContent className="p-6">
                <div className="text-center">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">Chef Marco Rossi</h3>
                  <p className="text-orange-600 font-medium mb-4">Owner & Head Chef</p>
                  
                  <div className="flex justify-center gap-2 mb-4">
                    <Badge variant="secondary">20+ Years Experience</Badge>
                    <Badge variant="secondary">James Beard Nominated</Badge>
                  </div>
                  
                  <p className="text-gray-600 text-sm leading-relaxed">
                    "Cooking is not just my profession, it's my passion. Every dish I create 
                    is a reflection of my Italian heritage and my commitment to bringing 
                    families together around the dinner table."
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Awards & Recognition */}
            <div className="mt-6 grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">4.8★</div>
                <div className="text-sm text-gray-600">Google Rating</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">500+</div>
                <div className="text-sm text-gray-600">5-Star Reviews</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">#1</div>
                <div className="text-sm text-gray-600">Local Favorite</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}