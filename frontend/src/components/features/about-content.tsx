'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Award, Heart, Leaf, Users, Star, ChefHat, Clock, Globe } from 'lucide-react';
import Link from 'next/link';

export function AboutContent() {
  const restaurantName = process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Demo Restaurant';

  const teamMembers = [
    {
      name: 'Marco Rossi',
      role: 'Owner & Head Chef',
      experience: '20+ Years',
      specialty: 'Italian Cuisine',
      description: 'Passionate about authentic Italian flavors and family traditions.',
      achievements: ['James Beard Nominated', 'Michelin Featured']
    },
    {
      name: 'Sarah Chen',
      role: 'Executive Sous Chef',
      experience: '12 Years',
      specialty: 'Modern Fusion',
      description: 'Expert in blending traditional techniques with modern innovation.',
      achievements: ['Culinary Institute Graduate', 'Rising Chef Award']
    },
    {
      name: 'David Martinez',
      role: 'Pastry Chef',
      experience: '8 Years',
      specialty: 'Artisan Desserts',
      description: 'Creating sweet masterpieces that complement every meal.',
      achievements: ['Best Dessert Award', 'Certified Chocolatier']
    }
  ];

  const values = [
    {
      icon: Leaf,
      title: 'Fresh & Local',
      description: 'We source ingredients from local farms and markets, supporting our community while ensuring the freshest flavors.'
    },
    {
      icon: Heart,
      title: 'Made with Love',
      description: 'Every dish is prepared with passion and care, following time-honored recipes passed down through generations.'
    },
    {
      icon: Users,
      title: 'Community First',
      description: 'We believe in bringing people together, creating a warm and welcoming space for families and friends.'
    },
    {
      icon: Award,
      title: 'Excellence',
      description: 'We strive for perfection in every aspect, from ingredient selection to service and presentation.'
    }
  ];

  const milestones = [
    { year: '2003', event: 'Restaurant opens its doors' },
    { year: '2008', event: 'First culinary award received' },
    { year: '2012', event: 'Expanded to current location' },
    { year: '2018', event: 'James Beard nomination' },
    { year: '2020', event: 'Adapted to community needs during pandemic' },
    { year: '2023', event: 'Celebrated 20 years of service' }
  ];

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-orange-50 via-white to-orange-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              About {restaurantName}
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              For over 20 years, we've been more than just a restaurant. We're a gathering place 
              where families create memories, friends celebrate life, and every meal tells a story.
            </p>
          </div>
        </div>
      </section>

      {/* Our Story */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Story</h2>
              <div className="prose prose-lg text-gray-600 space-y-6">
                <p>
                  What started as a dream in 2003 has blossomed into a beloved cornerstone of our community. 
                  Chef Marco Rossi, inspired by his grandmother's recipes from Tuscany, opened {restaurantName} 
                  with a simple mission: to bring authentic, heartfelt dining to our neighborhood.
                </p>
                <p>
                  From humble beginnings with just six tables, we've grown while never losing sight of what 
                  matters most – the personal touch, the warmth of genuine hospitality, and the joy that 
                  comes from sharing exceptional food with people you care about.
                </p>
                <p>
                  Today, we're proud to be a place where proposals happen, birthdays are celebrated, 
                  business deals are made, and families gather for Sunday dinner. Every plate we serve 
                  carries the love and tradition that started it all.
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              {/* Photo placeholders */}
              <div className="aspect-square bg-gradient-to-br from-orange-100 to-orange-200 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <ChefHat className="h-12 w-12 mx-auto mb-2 text-orange-600" />
                  <p className="text-sm text-gray-600">Kitchen Photo</p>
                </div>
              </div>
              <div className="aspect-square bg-gradient-to-br from-orange-100 to-orange-200 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Users className="h-12 w-12 mx-auto mb-2 text-orange-600" />
                  <p className="text-sm text-gray-600">Team Photo</p>
                </div>
              </div>
              <div className="aspect-square bg-gradient-to-br from-orange-100 to-orange-200 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Globe className="h-12 w-12 mx-auto mb-2 text-orange-600" />
                  <p className="text-sm text-gray-600">Restaurant Photo</p>
                </div>
              </div>
              <div className="aspect-square bg-gradient-to-br from-orange-100 to-orange-200 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Award className="h-12 w-12 mx-auto mb-2 text-orange-600" />
                  <p className="text-sm text-gray-600">Awards Photo</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Values */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">What We Stand For</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our values guide everything we do, from selecting ingredients to welcoming guests.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => {
              const Icon = value.icon;
              return (
                <Card key={index} className="text-center hover:shadow-lg transition-shadow duration-300">
                  <CardContent className="p-6">
                    <div className="h-16 w-16 mx-auto mb-4 rounded-full bg-orange-100 flex items-center justify-center">
                      <Icon className="h-8 w-8 text-orange-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">{value.title}</h3>
                    <p className="text-gray-600 text-sm leading-relaxed">{value.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Meet Our Team */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Meet Our Team</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Behind every great meal is a passionate team dedicated to culinary excellence.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {teamMembers.map((member, index) => (
              <Card key={index} className="overflow-hidden hover:shadow-lg transition-shadow duration-300">
                {/* Member Photo Placeholder */}
                <div className="aspect-square bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center">
                  <div className="text-center">
                    <div className="h-24 w-24 mx-auto mb-4 rounded-full bg-orange-500 flex items-center justify-center">
                      <span className="text-white text-2xl font-bold">
                        {member.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm">Photo coming soon</p>
                  </div>
                </div>
                
                <CardContent className="p-6">
                  <div className="text-center">
                    <h3 className="text-xl font-bold text-gray-900 mb-1">{member.name}</h3>
                    <p className="text-orange-600 font-medium mb-3">{member.role}</p>
                    
                    <div className="flex justify-center gap-2 mb-4">
                      <Badge variant="secondary">{member.experience}</Badge>
                      <Badge variant="secondary">{member.specialty}</Badge>
                    </div>
                    
                    <p className="text-gray-600 text-sm mb-4 leading-relaxed">
                      {member.description}
                    </p>
                    
                    <div className="space-y-1">
                      {member.achievements.map((achievement, i) => (
                        <div key={i} className="flex items-center justify-center text-sm text-gray-500">
                          <Star className="h-3 w-3 text-yellow-400 mr-1" />
                          {achievement}
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Journey</h2>
            <p className="text-lg text-gray-600">
              Key milestones that have shaped our story over the years.
            </p>
          </div>
          
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-orange-200"></div>
            
            <div className="space-y-8">
              {milestones.map((milestone, index) => (
                <div key={index} className="relative flex items-center">
                  <div className="absolute left-0 h-8 w-8 rounded-full bg-orange-500 flex items-center justify-center">
                    <Clock className="h-4 w-4 text-white" />
                  </div>
                  <div className="ml-12 bg-white p-4 rounded-lg shadow-sm border">
                    <div className="flex items-center space-x-4">
                      <Badge className="bg-orange-100 text-orange-800">{milestone.year}</Badge>
                      <p className="text-gray-900 font-medium">{milestone.event}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-orange-600 mb-2">20+</div>
              <div className="text-gray-600">Years of Service</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-orange-600 mb-2">50K+</div>
              <div className="text-gray-600">Happy Customers</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-orange-600 mb-2">15</div>
              <div className="text-gray-600">Awards Won</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-orange-600 mb-2">4.8★</div>
              <div className="text-gray-600">Average Rating</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-orange-50">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Join Our Story
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            We'd love to welcome you to our table and make you part of our extended family. 
            Come experience what makes {restaurantName} special.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/book">
              <Button size="lg" className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3">
                Make a Reservation
              </Button>
            </Link>
            <Link href="/menu">
              <Button size="lg" variant="outline" className="border-orange-500 text-orange-600 hover:bg-orange-50 px-8 py-3">
                View Our Menu
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}