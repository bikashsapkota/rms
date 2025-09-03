"use client"

import { useSession } from "next-auth/react"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { restaurantApi } from "@/lib/api"
import { Plus, Edit, Trash2, Eye } from "lucide-react"

interface Restaurant {
  id: string
  name: string
  description?: string
  address: string
  phone?: string
  email?: string
  cuisine?: string
  createdAt: string
}

export default function Dashboard() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (status === "loading") return
    
    if (!session) {
      router.push("/auth/signin")
      return
    }
    
    if (session.user.role !== "OWNER") {
      router.push("/restaurants")
      return
    }

    fetchRestaurants()
  }, [session, status, router])

  const fetchRestaurants = async () => {
    try {
      const data = await restaurantApi.getAll(session?.accessToken)
      setRestaurants(data)
    } catch (err: any) {
      setError(err.message || "Failed to fetch restaurants")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this restaurant?")) return

    try {
      await restaurantApi.delete(id, session?.accessToken)
      setRestaurants(restaurants.filter(r => r.id !== id))
    } catch (err: any) {
      setError(err.message || "Failed to delete restaurant")
    }
  }

  if (status === "loading" || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Restaurant Dashboard</h1>
            <Link
              href="/dashboard/restaurants/new"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Restaurant
            </Link>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {restaurants.length === 0 ? (
            <div className="text-center py-12">
              <h3 className="mt-2 text-sm font-medium text-gray-900">No restaurants</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating your first restaurant.
              </p>
              <div className="mt-6">
                <Link
                  href="/dashboard/restaurants/new"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Restaurant
                </Link>
              </div>
            </div>
          ) : (
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {restaurants.map((restaurant) => (
                  <li key={restaurant.id}>
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-medium text-indigo-600">
                            {restaurant.name}
                          </h3>
                          <p className="mt-1 text-sm text-gray-600">
                            {restaurant.description}
                          </p>
                          <div className="mt-2 text-sm text-gray-500">
                            <p>{restaurant.address}</p>
                            {restaurant.cuisine && (
                              <p className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 mt-1">
                                {restaurant.cuisine}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Link
                            href={`/restaurants/${restaurant.id}`}
                            className="text-gray-400 hover:text-gray-600"
                            title="View Restaurant"
                          >
                            <Eye className="w-5 h-5" />
                          </Link>
                          <Link
                            href={`/dashboard/restaurants/${restaurant.id}/edit`}
                            className="text-indigo-400 hover:text-indigo-600"
                            title="Edit Restaurant"
                          >
                            <Edit className="w-5 h-5" />
                          </Link>
                          <Link
                            href={`/dashboard/restaurants/${restaurant.id}/menu`}
                            className="text-green-400 hover:text-green-600 text-sm font-medium"
                            title="Manage Menu"
                          >
                            Menu
                          </Link>
                          <button
                            onClick={() => handleDelete(restaurant.id)}
                            className="text-red-400 hover:text-red-600"
                            title="Delete Restaurant"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}