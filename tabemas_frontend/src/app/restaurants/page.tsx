"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { menuApi } from "@/lib/api"
import Link from "next/link"
import { Star, MapPin } from "lucide-react"

interface MenuItem {
  id: string
  name: string
  description?: string
  price: number
  category: string
  available: boolean
}

export default function MenuItems() {
  const { data: session } = useSession()
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [categories, setCategories] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (session?.accessToken) {
      fetchMenuData()
    }
  }, [session])

  const fetchMenuData = async () => {
    try {
      const [itemsData, categoriesData] = await Promise.all([
        menuApi.getItems(session?.accessToken),
        menuApi.getCategories(session?.accessToken)
      ])
      setMenuItems(itemsData)
      setCategories(categoriesData)
    } catch (err: any) {
      setError(err.message || "Failed to fetch menu data")
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">Loading menu...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Menu Items</h1>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {menuItems.length === 0 ? (
            <div className="text-center py-12">
              <h3 className="mt-2 text-sm font-medium text-gray-900">No menu items found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Check back later for new menu items.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {menuItems.filter(item => item.available).map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden"
                >
                  <div className="p-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {item.name}
                    </h3>
                    
                    {item.description && (
                      <p className="text-gray-600 text-sm mb-3 line-clamp-3">
                        {item.description}
                      </p>
                    )}

                    <div className="flex items-center justify-between">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                        {item.category}
                      </span>
                      <span className="text-lg font-bold text-green-600">
                        ${item.price.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {categories.length > 0 && (
            <div className="mt-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Categories</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {categories.map((category) => (
                  <div key={category.id} className="bg-white rounded-lg shadow p-4 text-center">
                    <h3 className="font-medium text-gray-900">{category.name}</h3>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}