"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { useSession } from "next-auth/react"
import { restaurantApi, menuApi, reviewApi } from "@/lib/api"
import { Star, MapPin, Phone, Mail, Clock } from "lucide-react"
import ReviewForm from "@/components/review-form"
import ReviewsList from "@/components/reviews-list"

interface Restaurant {
  id: string
  name: string
  description?: string
  address: string
  phone?: string
  email?: string
  cuisine?: string
  averageRating?: number
  totalReviews?: number
}

interface MenuItem {
  id: string
  name: string
  description?: string
  price: number
  category: string
  available: boolean
  averageRating?: number
  totalReviews?: number
}

interface Review {
  id: string
  rating: number
  comment?: string
  user: {
    name?: string
    email: string
  }
  createdAt: string
}

export default function RestaurantDetail() {
  const { data: session } = useSession()
  const params = useParams()
  const restaurantId = params.id as string

  const [restaurant, setRestaurant] = useState<Restaurant | null>(null)
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [reviews, setReviews] = useState<Review[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")
  const [activeTab, setActiveTab] = useState<'menu' | 'reviews'>('menu')
  const [showReviewForm, setShowReviewForm] = useState(false)

  useEffect(() => {
    if (restaurantId) {
      fetchRestaurantData()
    }
  }, [restaurantId])

  const fetchRestaurantData = async () => {
    try {
      const [restaurantData, menuData, reviewsData] = await Promise.all([
        restaurantApi.getById(restaurantId),
        menuApi.getItems(restaurantId),
        reviewApi.getRestaurantReviews(restaurantId)
      ])
      
      setRestaurant(restaurantData)
      setMenuItems(menuData)
      setReviews(reviewsData)
    } catch (err: any) {
      setError(err.message || "Failed to fetch restaurant data")
    } finally {
      setIsLoading(false)
    }
  }

  const handleReviewSubmitted = () => {
    setShowReviewForm(false)
    fetchRestaurantData() // Refresh data to show new review
  }

  const groupedMenuItems = menuItems.reduce((acc, item) => {
    if (!acc[item.category]) {
      acc[item.category] = []
    }
    acc[item.category].push(item)
    return acc
  }, {} as Record<string, MenuItem[]>)

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">Loading restaurant details...</div>
      </div>
    )
  }

  if (!restaurant) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Restaurant not found</h2>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Restaurant Header */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{restaurant.name}</h1>
                {restaurant.cuisine && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800 mt-2">
                    {restaurant.cuisine}
                  </span>
                )}
              </div>
              {restaurant.averageRating && (
                <div className="flex items-center">
                  <Star className="w-5 h-5 text-yellow-400 fill-current" />
                  <span className="ml-1 text-lg font-semibold text-gray-900">
                    {restaurant.averageRating.toFixed(1)}
                  </span>
                  {restaurant.totalReviews && (
                    <span className="ml-1 text-gray-600">
                      ({restaurant.totalReviews} reviews)
                    </span>
                  )}
                </div>
              )}
            </div>

            {restaurant.description && (
              <p className="text-gray-600 mb-4">{restaurant.description}</p>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
              <div className="flex items-center">
                <MapPin className="w-4 h-4 mr-2" />
                <span>{restaurant.address}</span>
              </div>
              {restaurant.phone && (
                <div className="flex items-center">
                  <Phone className="w-4 h-4 mr-2" />
                  <span>{restaurant.phone}</span>
                </div>
              )}
              {restaurant.email && (
                <div className="flex items-center">
                  <Mail className="w-4 h-4 mr-2" />
                  <span>{restaurant.email}</span>
                </div>
              )}
            </div>
          </div>

          {/* Tabs */}
          <div className="bg-white rounded-lg shadow-md">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex">
                <button
                  onClick={() => setActiveTab('menu')}
                  className={`py-2 px-4 border-b-2 font-medium text-sm ${
                    activeTab === 'menu'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Menu
                </button>
                <button
                  onClick={() => setActiveTab('reviews')}
                  className={`py-2 px-4 border-b-2 font-medium text-sm ${
                    activeTab === 'reviews'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Reviews ({reviews.length})
                </button>
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'menu' && (
                <div>
                  {Object.keys(groupedMenuItems).length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      No menu items available yet.
                    </div>
                  ) : (
                    <div className="space-y-8">
                      {Object.entries(groupedMenuItems).map(([category, items]) => (
                        <div key={category}>
                          <h3 className="text-xl font-semibold text-gray-900 mb-4">{category}</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {items.filter(item => item.available).map((item) => (
                              <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                                <div className="flex justify-between items-start mb-2">
                                  <h4 className="text-lg font-medium text-gray-900">{item.name}</h4>
                                  <span className="text-lg font-bold text-indigo-600">
                                    ${item.price.toFixed(2)}
                                  </span>
                                </div>
                                {item.description && (
                                  <p className="text-gray-600 text-sm mb-2">{item.description}</p>
                                )}
                                {item.averageRating && (
                                  <div className="flex items-center">
                                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                                    <span className="ml-1 text-sm text-gray-600">
                                      {item.averageRating.toFixed(1)}
                                      {item.totalReviews && (
                                        <span className="text-gray-400">
                                          {" "}({item.totalReviews})
                                        </span>
                                      )}
                                    </span>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'reviews' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-semibold text-gray-900">Customer Reviews</h3>
                    {session && session.user.role === "USER" && (
                      <button
                        onClick={() => setShowReviewForm(true)}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      >
                        Write a Review
                      </button>
                    )}
                  </div>

                  {showReviewForm && (
                    <div className="mb-6">
                      <ReviewForm
                        restaurantId={restaurantId}
                        onSuccess={handleReviewSubmitted}
                        onCancel={() => setShowReviewForm(false)}
                      />
                    </div>
                  )}

                  <ReviewsList reviews={reviews} />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}