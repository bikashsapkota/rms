'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, Star } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { MenuItem } from '@/types';

export function FeaturedMenu() {
  const [featuredItems, setFeaturedItems] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFeaturedItems = async () => {
      try {
        const response = await apiClient.getPublicMenu();
        // Take first 3 items as featured (in real app, would have a featured flag)
        const featured = response.items ? response.items.slice(0, 3) : [
          {
            id: '1',
            name: 'Truffle Pasta',
            description: 'Homemade pasta with black truffle and parmesan cheese',
            price: 24.99,
            image_url: null,
            is_available: true
          },
          {
            id: '2', 
            name: 'Grilled Salmon',
            description: 'Fresh Atlantic salmon with lemon herb butter',
            price: 28.99,
            image_url: null,
            is_available: true
          },
          {
            id: '3',
            name: 'Chocolate Soufflé',
            description: 'Warm chocolate soufflé with vanilla ice cream',
            price: 12.99,
            image_url: null,
            is_available: true
          }
        ];
        setFeaturedItems(featured);
      } catch (error) {
        console.error('Failed to fetch featured menu:', error);
        // Fallback to demo items
        setFeaturedItems([
          {
            id: '1',
            organization_id: '',
            restaurant_id: '',
            name: 'Truffle Pasta',
            description: 'Homemade pasta with black truffle and parmesan cheese',
            price: 24.99,
            is_available: true,
            created_at: '',
            updated_at: ''
          },
          {
            id: '2',
            organization_id: '',
            restaurant_id: '',
            name: 'Grilled Salmon', 
            description: 'Fresh Atlantic salmon with lemon herb butter',
            price: 28.99,
            is_available: true,
            created_at: '',
            updated_at: ''
          },
          {
            id: '3',
            organization_id: '',
            restaurant_id: '',
            name: 'Chocolate Soufflé',
            description: 'Warm chocolate soufflé with vanilla ice cream', 
            price: 12.99,
            is_available: true,
            created_at: '',
            updated_at: ''
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchFeaturedItems();
  }, []);

  if (loading) {
    return (
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Chef's Favorites</h2>
            <div className="animate-pulse space-y-8">
              <div className="grid md:grid-cols-3 gap-8">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="bg-gray-200 h-64 rounded-lg"></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            🍽️ Chef's Favorites
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Discover our most beloved dishes, crafted with the finest ingredients 
            and perfected by our talented chefs.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {featuredItems.map((item, index) => (
            <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-shadow duration-300">
              <div className="aspect-square bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center">
                {item.image_url ? (
                  <img 
                    src={item.image_url} 
                    alt={item.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="text-center p-8">
                    <div className="h-16 w-16 mx-auto mb-4 rounded-full bg-orange-500 flex items-center justify-center">
                      <span className="text-white text-2xl font-bold">
                        {item.name.charAt(0)}
                      </span>
                    </div>
                    <p className="text-gray-600">Photo coming soon</p>
                  </div>
                )}
              </div>
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-xl font-semibold text-gray-900">{item.name}</h3>
                  <div className="flex items-center">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm text-gray-500 ml-1">4.8</span>
                  </div>
                </div>
                <p className="text-gray-600 mb-4 text-sm leading-relaxed">
                  {item.description}
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold text-orange-500">
                    ${item.price.toFixed(2)}
                  </span>
                  {item.is_available ? (
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      Available
                    </Badge>
                  ) : (
                    <Badge variant="secondary" className="bg-red-100 text-red-800">
                      Sold Out
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="text-center">
          <Link href="/menu">
            <Button size="lg" variant="outline" className="border-orange-500 text-orange-600 hover:bg-orange-50">
              View Full Menu
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}