'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';

interface GalleryImage {
  id: string;
  title: string;
  description: string;
  category: 'food' | 'interior' | 'events' | 'team';
}

export function PhotoGallery() {
  const [selectedImage, setSelectedImage] = useState<GalleryImage | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Demo gallery images (in real app, these would come from API/CMS)
  const galleryImages: GalleryImage[] = [
    { id: '1', title: 'Signature Truffle Pasta', description: 'Our most popular dish with black truffle', category: 'food' },
    { id: '2', title: 'Main Dining Room', description: 'Elegant dining atmosphere', category: 'interior' },
    { id: '3', title: 'Grilled Salmon', description: 'Fresh Atlantic salmon with seasonal vegetables', category: 'food' },
    { id: '4', title: 'Private Event Space', description: 'Perfect for celebrations and corporate events', category: 'events' },
    { id: '5', title: 'Chef at Work', description: 'Our talented culinary team in action', category: 'team' },
    { id: '6', title: 'Wine Selection', description: 'Curated collection of fine wines', category: 'interior' },
    { id: '7', title: 'Chocolate Soufflé', description: 'Decadent dessert to end your meal', category: 'food' },
    { id: '8', title: 'Wedding Reception', description: 'Making your special day memorable', category: 'events' },
  ];

  const categories = [
    { id: 'all', label: 'All Photos' },
    { id: 'food', label: 'Food' },
    { id: 'interior', label: 'Interior' },
    { id: 'events', label: 'Events' },
    { id: 'team', label: 'Our Team' },
  ];

  const filteredImages = selectedCategory === 'all' 
    ? galleryImages 
    : galleryImages.filter(img => img.category === selectedCategory);

  const openModal = (image: GalleryImage) => {
    setSelectedImage(image);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  const navigateImage = (direction: 'prev' | 'next') => {
    if (!selectedImage) return;
    
    const currentIndex = filteredImages.findIndex(img => img.id === selectedImage.id);
    let newIndex;
    
    if (direction === 'prev') {
      newIndex = currentIndex > 0 ? currentIndex - 1 : filteredImages.length - 1;
    } else {
      newIndex = currentIndex < filteredImages.length - 1 ? currentIndex + 1 : 0;
    }
    
    setSelectedImage(filteredImages[newIndex]);
  };

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            📸 Experience Our Restaurant
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Take a visual journey through our restaurant, from our beautifully crafted dishes 
            to our warm and inviting atmosphere.
          </p>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap justify-center gap-2 mb-8">
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
              {category.label}
            </Button>
          ))}
        </div>

        {/* Gallery Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
          {filteredImages.map((image) => (
            <div
              key={image.id}
              className="aspect-square cursor-pointer group overflow-hidden rounded-lg shadow-md hover:shadow-lg transition-all duration-300"
              onClick={() => openModal(image)}
            >
              <div className="w-full h-full bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center relative group-hover:scale-105 transition-transform duration-300">
                <div className="text-center p-4">
                  <div className="h-16 w-16 mx-auto mb-3 rounded-full bg-orange-500 flex items-center justify-center">
                    <span className="text-white text-xl font-bold">
                      {image.title.charAt(0)}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-gray-700">{image.title}</p>
                </div>
                
                {/* Overlay */}
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-300 flex items-center justify-center">
                  <span className="text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 font-medium">
                    View Photo
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Social Media Section */}
        <div className="text-center">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Follow us for more photos
          </h3>
          <p className="text-gray-600 mb-4">
            <span className="font-semibold text-orange-600">@{process.env.NEXT_PUBLIC_RESTAURANT_SLUG || 'restaurant'}</span> on Instagram
          </p>
          <div className="flex justify-center space-x-4">
            <Button variant="outline" className="border-orange-500 text-orange-600 hover:bg-orange-50">
              Follow on Instagram
            </Button>
            <Button variant="outline" className="border-orange-500 text-orange-600 hover:bg-orange-50">
              Like on Facebook
            </Button>
          </div>
        </div>
      </div>

      {/* Modal */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
          <div className="max-w-4xl max-h-full bg-white rounded-lg overflow-hidden">
            {/* Modal Header */}
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-xl font-semibold text-gray-900">{selectedImage.title}</h3>
              <Button variant="ghost" size="sm" onClick={closeModal}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Modal Content */}
            <div className="relative">
              <div className="aspect-video bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center">
                <div className="text-center p-8">
                  <div className="h-32 w-32 mx-auto mb-4 rounded-full bg-orange-500 flex items-center justify-center">
                    <span className="text-white text-4xl font-bold">
                      {selectedImage.title.charAt(0)}
                    </span>
                  </div>
                  <p className="text-gray-600 text-lg">{selectedImage.title}</p>
                  <p className="text-sm text-gray-500 mt-2">Photo coming soon</p>
                </div>
              </div>

              {/* Navigation Buttons */}
              <Button
                variant="ghost"
                size="sm"
                className="absolute left-2 top-1/2 -translate-y-1/2 bg-white hover:bg-gray-100"
                onClick={() => navigateImage('prev')}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-white hover:bg-gray-100"
                onClick={() => navigateImage('next')}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t">
              <p className="text-gray-600">{selectedImage.description}</p>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}