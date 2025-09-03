import Link from "next/link"
import Navbar from "@/components/navbar"
import { Star, Users, Utensils } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      {/* Hero Section */}
      <div className="bg-white">
        <div className="max-w-7xl mx-auto py-16 px-4 sm:py-24 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
              Welcome to <span className="text-indigo-600">Tabemas</span>
            </h1>
            <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
              The ultimate platform for restaurant owners to manage their business and for food lovers to discover and review amazing restaurants.
            </p>
            <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
              <div className="rounded-md shadow">
                <Link
                  href="/restaurants"
                  className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10"
                >
                  Explore Restaurants
                </Link>
              </div>
              <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
                <Link
                  href="/auth/signup"
                  className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
                >
                  Get Started
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900">
              Everything you need to manage your restaurant
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Whether you're a restaurant owner or a food enthusiast, we've got you covered.
            </p>
          </div>

          <div className="mt-20">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {/* For Restaurant Owners */}
              <div className="text-center">
                <div className="flex mx-auto items-center justify-center h-20 w-20 rounded-md bg-indigo-500 text-white">
                  <Utensils className="h-10 w-10" />
                </div>
                <h3 className="mt-6 text-xl font-medium text-gray-900">Restaurant Management</h3>
                <p className="mt-2 text-base text-gray-500">
                  Easily manage your restaurant details, menu items, and track customer feedback all in one place.
                </p>
              </div>

              {/* For Customers */}
              <div className="text-center">
                <div className="flex mx-auto items-center justify-center h-20 w-20 rounded-md bg-indigo-500 text-white">
                  <Star className="h-10 w-10" />
                </div>
                <h3 className="mt-6 text-xl font-medium text-gray-900">Rate & Review</h3>
                <p className="mt-2 text-base text-gray-500">
                  Discover new restaurants, rate your dining experiences, and help others find great places to eat.
                </p>
              </div>

              {/* Community */}
              <div className="text-center">
                <div className="flex mx-auto items-center justify-center h-20 w-20 rounded-md bg-indigo-500 text-white">
                  <Users className="h-10 w-10" />
                </div>
                <h3 className="mt-6 text-xl font-medium text-gray-900">Community Driven</h3>
                <p className="mt-2 text-base text-gray-500">
                  Join a community of food lovers and restaurant owners working together to improve dining experiences.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-indigo-600">
        <div className="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            <span className="block">Ready to get started?</span>
          </h2>
          <p className="mt-4 text-lg leading-6 text-indigo-200">
            Join thousands of restaurant owners and food enthusiasts already using Tabemas.
          </p>
          <Link
            href="/auth/signup"
            className="mt-8 w-full inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50 sm:w-auto"
          >
            Sign up for free
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 md:flex md:items-center md:justify-between lg:px-8">
          <div className="flex justify-center space-x-6 md:order-2">
            <p className="text-base text-gray-400">
              &copy; 2024 Tabemas. All rights reserved.
            </p>
          </div>
          <div className="mt-8 md:mt-0 md:order-1">
            <p className="text-center text-base text-gray-400">
              Built with Next.js and Turbopack
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
