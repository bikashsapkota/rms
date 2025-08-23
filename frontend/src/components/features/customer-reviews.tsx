'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Star, Quote, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Review {
  id: string;
  name: string;
  rating: number;
  comment: string;
  date: string;
  platform: 'Google' | 'Yelp' | 'TripAdvisor';
  verified: boolean;
}

export function CustomerReviews() {
  const [currentReview, setCurrentReview] = useState(0);

  // Demo reviews (in real app, would come from review APIs)
  const reviews: Review[] = [
    {
      id: '1',
      name: 'Sarah Johnson',
      rating: 5,
      comment: 'Amazing food and exceptional service! The truffle pasta was absolutely incredible, and our server was so attentive. Will definitely be coming back!',
      date: '2 days ago',
      platform: 'Google',
      verified: true
    },
    {
      id: '2', 
      name: 'Mike Davis',
      rating: 5,
      comment: 'Perfect date night spot! The atmosphere is romantic, the wine selection is excellent, and every dish we tried was perfection. Highly recommend the salmon!',
      date: '1 week ago',
      platform: 'Yelp',
      verified: true
    },
    {
      id: '3',
      name: 'Emily Chen',
      rating: 5,
      comment: 'Had our anniversary dinner here and it exceeded all expectations. The chocolate soufflé was divine! The staff made our evening so special.',
      date: '2 weeks ago', 
      platform: 'Google',
      verified: true
    },
    {
      id: '4',
      name: 'James Wilson',
      rating: 4,
      comment: 'Great restaurant with authentic flavors. The service was prompt and friendly. The only minor issue was it got a bit noisy later in the evening, but the food made up for it.',
      date: '3 weeks ago',
      platform: 'TripAdvisor',
      verified: true
    },
    {
      id: '5',
      name: 'Lisa Martinez',
      rating: 5,
      comment: 'Outstanding culinary experience! Chef Marco\'s attention to detail is evident in every bite. This place truly captures the essence of fine dining.',
      date: '1 month ago',
      platform: 'Google',
      verified: true
    }
  ];

  // Auto-rotate reviews
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentReview((prev) => (prev + 1) % reviews.length);
    }, 5000);

    return () => clearInterval(timer);
  }, [reviews.length]);

  const nextReview = () => {
    setCurrentReview((prev) => (prev + 1) % reviews.length);
  };

  const prevReview = () => {
    setCurrentReview((prev) => (prev - 1 + reviews.length) % reviews.length);
  };

  const averageRating = reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length;
  const totalReviews = 247; // This would come from API
  const fiveStarCount = reviews.filter(r => r.rating === 5).length;
  const fiveStarPercentage = Math.round((fiveStarCount / reviews.length) * 100);

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            💬 What Our Guests Say
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Don't just take our word for it. Here's what our valued customers have to say 
            about their dining experience with us.
          </p>
        </div>

        {/* Review Statistics */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <Card className="text-center p-6">
            <div className="text-3xl font-bold text-orange-500 mb-2">
              {averageRating.toFixed(1)}
            </div>
            <div className="flex justify-center mb-2">
              {Array.from({ length: 5 }, (_, i) => (
                <Star 
                  key={i} 
                  className={`h-5 w-5 ${
                    i < Math.floor(averageRating) 
                      ? 'fill-yellow-400 text-yellow-400' 
                      : 'text-gray-300'
                  }`} 
                />
              ))}
            </div>
            <div className="text-sm text-gray-600">Average Rating</div>
          </Card>

          <Card className="text-center p-6">
            <div className="text-3xl font-bold text-orange-500 mb-2">{totalReviews}+</div>
            <div className="text-sm text-gray-600">Total Reviews</div>
          </Card>

          <Card className="text-center p-6">
            <div className="text-3xl font-bold text-orange-500 mb-2">{fiveStarPercentage}%</div>
            <div className="text-sm text-gray-600">5-Star Reviews</div>
          </Card>

          <Card className="text-center p-6">
            <div className="text-3xl font-bold text-orange-500 mb-2">#1</div>
            <div className="text-sm text-gray-600">Local Favorite</div>
          </Card>
        </div>

        {/* Featured Review Carousel */}
        <div className="relative max-w-4xl mx-auto">
          <Card className="shadow-lg overflow-hidden">
            <CardContent className="p-8">
              <div className="relative">
                <Quote className="h-12 w-12 text-orange-200 mb-4" />
                
                <div className="mb-6">
                  <div className="flex mb-2">
                    {Array.from({ length: 5 }, (_, i) => (
                      <Star 
                        key={i} 
                        className={`h-5 w-5 ${
                          i < reviews[currentReview].rating 
                            ? 'fill-yellow-400 text-yellow-400' 
                            : 'text-gray-300'
                        }`} 
                      />
                    ))}
                  </div>
                  <p className="text-lg text-gray-800 leading-relaxed mb-6">
                    "{reviews[currentReview].comment}"
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <Avatar className="h-12 w-12">
                      <AvatarFallback className="bg-orange-500 text-white">
                        {reviews[currentReview].name.split(' ').map(n => n.charAt(0)).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-gray-900">
                          {reviews[currentReview].name}
                        </span>
                        {reviews[currentReview].verified && (
                          <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                            Verified
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <span>{reviews[currentReview].date}</span>
                        <span>•</span>
                        <span>{reviews[currentReview].platform}</span>
                      </div>
                    </div>
                  </div>

                  {/* Navigation */}
                  <div className="flex space-x-2">
                    <Button variant="ghost" size="sm" onClick={prevReview}>
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={nextReview}>
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Review Indicators */}
          <div className="flex justify-center space-x-2 mt-6">
            {reviews.map((_, index) => (
              <button
                key={index}
                className={`h-2 w-2 rounded-full transition-all duration-300 ${
                  index === currentReview ? 'bg-orange-500' : 'bg-gray-300'
                }`}
                onClick={() => setCurrentReview(index)}
              />
            ))}
          </div>
        </div>

        {/* Platform Links */}
        <div className="text-center mt-12">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">
            See all our reviews on
          </h3>
          <div className="flex flex-col sm:flex-row justify-center items-center space-y-3 sm:space-y-0 sm:space-x-6">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded bg-blue-600 flex items-center justify-center">
                <span className="text-white text-xs font-bold">G</span>
              </div>
              <div>
                <div className="font-semibold text-gray-900">Google</div>
                <div className="text-sm text-gray-600">4.8 ★ (150+ reviews)</div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded bg-red-600 flex items-center justify-center">
                <span className="text-white text-xs font-bold">Y</span>
              </div>
              <div>
                <div className="font-semibold text-gray-900">Yelp</div>
                <div className="text-sm text-gray-600">4.7 ★ (80+ reviews)</div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded bg-green-600 flex items-center justify-center">
                <span className="text-white text-xs font-bold">T</span>
              </div>
              <div>
                <div className="font-semibold text-gray-900">TripAdvisor</div>
                <div className="text-sm text-gray-600">4.9 ★ (17+ reviews)</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}