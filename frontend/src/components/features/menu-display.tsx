'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Search, Star, Leaf, Wheat, Heart } from 'lucide-react';

interface MenuItem {
  id: string;
  category_id?: string;
  name: string;
  description: string;
  price: number;
  is_available: boolean;
  image_url?: string;
}

interface Category {
  id: string;
  name: string;
  description?: string;
}

interface MenuDisplayProps {
  categories: Category[];
  menuItems: MenuItem[];
}

export function MenuDisplay({ categories, menuItems }: MenuDisplayProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Filter menu items based on selected category and search query
  const filteredItems = menuItems.filter((item) => {
    const matchesCategory = selectedCategory === 'all' || item.category_id === selectedCategory;
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  // Group items by category for display
  const groupedItems = categories.reduce((acc, category) => {
    const categoryItems = filteredItems.filter(item => item.category_id === category.id);
    if (categoryItems.length > 0) {
      acc[category.id] = { category, items: categoryItems };
    }
    return acc;
  }, {} as Record<string, { category: Category; items: MenuItem[] }>);

  const restaurantName = process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Demo Restaurant';

  return (
    <div className="bg-white">
      {/* Header */}
      <section className="bg-gradient-to-br from-orange-50 via-white to-orange-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Our Menu
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Discover our carefully crafted dishes made with the finest ingredients. 
              Each dish tells a story of culinary excellence and tradition.
            </p>
          </div>
        </div>
      </section>

      {/* Search and Filters */}
      <section className="py-8 bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Search */}
          <div className="relative max-w-md mx-auto mb-8">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Input
              type="text"
              placeholder="Search menu items..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-3 w-full text-lg"
            />
          </div>

          {/* Category Filters */}
          <div className="flex flex-wrap justify-center gap-3">
            <Button
              variant={selectedCategory === 'all' ? 'default' : 'outline'}
              onClick={() => setSelectedCategory('all')}
              className={selectedCategory === 'all' 
                ? 'bg-orange-500 hover:bg-orange-600 text-white' 
                : 'border-orange-500 text-orange-600 hover:bg-orange-50'
              }
            >
              All Items
            </Button>
            {categories.map((category) => (
              <Button
                key={category.id}
                variant={selectedCategory === category.id ? 'default' : 'outline'}
                onClick={() => setSelectedCategory(category.id)}
                className={selectedCategory === category.id 
                  ? 'bg-orange-500 hover:bg-orange-600 text-white' 
                  : 'border-orange-500 text-orange-600 hover:bg-orange-50'
                }
              >
                {category.name}
              </Button>
            ))}
          </div>

          {/* Results count */}
          <div className="text-center mt-6">
            <p className="text-gray-600">
              Showing {filteredItems.length} {filteredItems.length === 1 ? 'item' : 'items'}
              {searchQuery && (
                <span> for &quot;{searchQuery}&quot;</span>
              )}
            </p>
          </div>
        </div>
      </section>

      {/* Menu Items */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {Object.keys(groupedItems).length === 0 ? (
            // No items found
            <div className="text-center py-16">
              <div className="h-32 w-32 mx-auto mb-6 rounded-full bg-gray-100 flex items-center justify-center">
                <Search className="h-16 w-16 text-gray-400" />
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">No items found</h3>
              <p className="text-gray-600 mb-6">
                Try adjusting your search or browse all menu items.
              </p>
              <Button 
                onClick={() => { setSearchQuery(''); setSelectedCategory('all'); }}
                className="bg-orange-500 hover:bg-orange-600 text-white"
              >
                View All Menu Items
              </Button>
            </div>
          ) : (
            // Display grouped menu items
            <div className="space-y-16">
              {Object.values(groupedItems).map(({ category, items }) => (
                <div key={category.id} id={category.id}>
                  {/* Category Header */}
                  <div className="text-center mb-10">
                    <h2 className="text-3xl font-bold text-gray-900 mb-3">{category.name}</h2>
                    {category.description && (
                      <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                        {category.description}
                      </p>
                    )}
                  </div>

                  {/* Category Items */}
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {items.map((item) => (
                      <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-shadow duration-300">
                        {/* Item Image */}
                        <div className="aspect-video bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center">
                          {item.image_url ? (
                            <img 
                              src={item.image_url} 
                              alt={item.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="text-center p-6">
                              <div className="h-16 w-16 mx-auto mb-4 rounded-full bg-orange-500 flex items-center justify-center">
                                <span className="text-white text-2xl font-bold">
                                  {item.name.charAt(0)}
                                </span>
                              </div>
                              <p className="text-gray-600 text-sm">Photo coming soon</p>
                            </div>
                          )}
                        </div>

                        <CardContent className="p-6">
                          {/* Item Header */}
                          <div className="flex justify-between items-start mb-3">
                            <h3 className="text-xl font-semibold text-gray-900 line-clamp-1">
                              {item.name}
                            </h3>
                            <div className="flex items-center ml-2">
                              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                              <span className="text-sm text-gray-500 ml-1">4.8</span>
                            </div>
                          </div>

                          {/* Item Description */}
                          <p className="text-gray-600 mb-4 text-sm leading-relaxed line-clamp-2">
                            {item.description}
                          </p>

                          {/* Dietary Info (Demo) */}
                          <div className="flex gap-2 mb-4">
                            <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                              <Leaf className="h-3 w-3 mr-1" />
                              Fresh
                            </Badge>
                            {item.name.toLowerCase().includes('pasta') && (
                              <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-800">
                                <Wheat className="h-3 w-3 mr-1" />
                                Contains Gluten
                              </Badge>
                            )}
                            {item.name.toLowerCase().includes('salmon') && (
                              <Badge variant="secondary" className="text-xs bg-purple-100 text-purple-800">
                                <Heart className="h-3 w-3 mr-1" />
                                Heart Healthy
                              </Badge>
                            )}
                          </div>

                          {/* Price and Availability */}
                          <div className="flex justify-between items-center">
                            <span className="text-2xl font-bold text-orange-500">
                              ${parseFloat(item.price).toFixed(2)}
                            </span>
                            {item.is_available ? (
                              <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
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
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-16 bg-orange-50">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Experience Our Cuisine?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Book your table now and enjoy an unforgettable dining experience at {restaurantName}.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3">
              Make a Reservation
            </Button>
            <Button size="lg" variant="outline" className="border-orange-500 text-orange-600 hover:bg-orange-50 px-8 py-3">
              Call (555) 123-4567
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}