'use client';

import { useState, useEffect } from 'react';
import { useApiClient } from '@/hooks/useApiClient';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Eye, 
  EyeOff,
  Filter,
  ChefHat,
  RefreshCw
} from 'lucide-react';

interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  category_id: string;
  category_name: string;
  is_available: boolean;
  image_url?: string;
  created_at: string;
  updated_at: string;
  organization_id: string;
  restaurant_id: string;
}

interface Category {
  id: string;
  name: string;
  description?: string;
}

export function MenuManagement() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showUnavailable, setShowUnavailable] = useState(true);
  const [isAddItemOpen, setIsAddItemOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<MenuItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const apiClient = useApiClient();

  // State for dynamic data from backend
  const [categories, setCategories] = useState<Category[]>([]);
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);

  // Fetch data from backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch categories and items in parallel
        const [categoriesResponse, itemsResponse] = await Promise.all([
          apiClient.getCategories(),
          apiClient.getMenuItems(undefined, showUnavailable) // Use showUnavailable state
        ]);

        // Transform backend data to match frontend interface
        const transformedCategories = categoriesResponse.map((cat: any) => ({
          id: cat.id,
          name: cat.name,
          description: cat.description || ''
        }));

        const transformedItems = itemsResponse.map((item: any) => ({
          ...item,
          price: parseFloat(item.price) // Ensure price is a number
        }));

        setCategories(transformedCategories);
        setMenuItems(transformedItems);
      } catch (error) {
        console.error('Error fetching menu data:', error);
        setError('Failed to load menu data. Using demo data.');
        
        // Fallback to demo data if API fails
        setCategories([
          { id: '1', name: 'Appetizers', description: 'Start your meal with these delicious options' },
          { id: '2', name: 'Main Courses', description: 'Our signature entrees and hearty dishes' },
          { id: '3', name: 'Desserts', description: 'Sweet endings to your dining experience' }
        ]);
        setMenuItems([
          {
            id: '1',
            name: 'Demo Item',
            description: 'This is demo data - backend connection failed',
            price: 16.99,
            category: 'Appetizers',
            isAvailable: true
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [apiClient, showUnavailable]); // Add showUnavailable to dependencies

  // Refresh data function for manual refresh
  const refreshData = async () => {
    try {
      setLoading(true);
      const [categoriesResponse, itemsResponse] = await Promise.all([
        apiClient.getCategories(),
        apiClient.getMenuItems(undefined, showUnavailable) // Use current showUnavailable state
      ]);

      const transformedCategories = categoriesResponse.map((cat: any) => ({
        id: cat.id,
        name: cat.name,
        description: cat.description || ''
      }));

      const transformedItems = itemsResponse.map((item: any) => ({
        ...item,
        price: parseFloat(item.price) // Ensure price is a number
      }));

      setCategories(transformedCategories);
      setMenuItems(transformedItems);
      setError(null);
    } catch (error) {
      console.error('Error refreshing menu data:', error);
      setError('Failed to refresh menu data.');
    } finally {
      setLoading(false);
    }
  };

  // Filter menu items
  const filteredItems = menuItems.filter((item) => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || item.category_name === selectedCategory;
    const matchesAvailability = showUnavailable || item.is_available;
    
    return matchesSearch && matchesCategory && matchesAvailability;
  });

  const toggleAvailability = async (itemId: string) => {
    try {
      const item = menuItems.find(i => i.id === itemId);
      if (!item) return;

      // Update via API
      const updatedData = {
        name: item.name,
        description: item.description,
        price: item.price,
        category_id: item.category_id,
        is_available: !item.is_available
      };
      
      await apiClient.updateMenuItem(itemId, updatedData);
      
      // Update local state
      setMenuItems(items => 
        items.map(i => 
          i.id === itemId 
            ? { ...i, is_available: !i.is_available }
            : i
        )
      );
    } catch (error) {
      console.error('Error toggling availability:', error);
      setError('Failed to update item availability.');
    }
  };

  const deleteItem = (itemId: string) => {
    setMenuItems(items => items.filter(item => item.id !== itemId));
  };

  const ItemForm = ({ item, onSave, onCancel }: {
    item?: MenuItem;
    onSave: (item: Partial<MenuItem>) => void;
    onCancel: () => void;
  }) => {
    const [formData, setFormData] = useState({
      name: item?.name || '',
      description: item?.description || '',
      price: item?.price || 0,
      category: item?.category_name || '',
      is_available: item?.is_available ?? true
    });

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      onSave(formData);
    };

    return (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Item Name *
            </label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Enter item name"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Price *
            </label>
            <Input
              type="number"
              step="0.01"
              value={formData.price}
              onChange={(e) => setFormData(prev => ({ ...prev, price: parseFloat(e.target.value) }))}
              placeholder="0.00"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category *
          </label>
          <Select value={formData.category} onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}>
            <SelectTrigger>
              <SelectValue placeholder="Select a category" />
            </SelectTrigger>
            <SelectContent>
              {categories.map((category) => (
                <SelectItem key={category.id} value={category.name}>
                  {category.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description *
          </label>
          <Textarea
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            placeholder="Describe the dish..."
            rows={3}
            required
          />
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="available"
            checked={formData.is_available}
            onChange={(e) => setFormData(prev => ({ ...prev, is_available: e.target.checked }))}
            className="rounded border-gray-300"
          />
          <label htmlFor="available" className="text-sm font-medium text-gray-700">
            Available for ordering
          </label>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" className="bg-orange-500 hover:bg-orange-600">
            {item ? 'Update Item' : 'Add Item'}
          </Button>
        </DialogFooter>
      </form>
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Menu Management</h1>
          <p className="text-gray-600 mt-1">
            Manage your restaurant's menu items and categories.
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button 
            variant="outline" 
            onClick={refreshData}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Dialog open={isAddItemOpen} onOpenChange={setIsAddItemOpen}>
          <DialogTrigger asChild>
            <Button className="bg-orange-500 hover:bg-orange-600">
              <Plus className="h-4 w-4 mr-2" />
              Add New Item
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add New Menu Item</DialogTitle>
              <DialogDescription>
                Create a new dish for your restaurant menu.
              </DialogDescription>
            </DialogHeader>
            <ItemForm 
              onSave={async (data) => {
                try {
                  setLoading(true);
                  
                  // Find the category ID by name
                  const category = categories.find(cat => cat.name === data.category);
                  if (!category) {
                    throw new Error('Category not found');
                  }

                  // Create item via API
                  const newItemData = {
                    name: data.name!,
                    description: data.description!,
                    price: data.price!,
                    category_id: category.id, // Use the actual category ID
                    is_available: data.is_available!
                  };

                  const createdItem = await apiClient.createMenuItem(newItemData);
                  
                  // Add the new item to local state with correct format
                  const newItem: MenuItem = {
                    id: createdItem.id,
                    name: createdItem.name,
                    description: createdItem.description,
                    price: parseFloat(createdItem.price),
                    category_id: createdItem.category_id,
                    category_name: data.category!,
                    is_available: createdItem.is_available,
                    image_url: createdItem.image_url,
                    created_at: createdItem.created_at,
                    updated_at: createdItem.updated_at,
                    organization_id: createdItem.organization_id,
                    restaurant_id: createdItem.restaurant_id
                  };
                  
                  setMenuItems(prev => [...prev, newItem]);
                  setIsAddItemOpen(false);
                  setError(null);
                } catch (error) {
                  console.error('Error creating menu item:', error);
                  setError(`Failed to create menu item: ${error instanceof Error ? error.message : 'Unknown error'}`);
                } finally {
                  setLoading(false);
                }
              }}
              onCancel={() => setIsAddItemOpen(false)}
            />
          </DialogContent>
        </Dialog>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center space-x-2">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <button 
                onClick={() => setError(null)}
                className="flex-shrink-0 ml-auto text-red-400 hover:text-red-600"
              >
                <span className="sr-only">Close</span>
                <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filters & Search</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search menu items..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((category) => (
                  <SelectItem key={category.id} value={category.name}>
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              onClick={() => setShowUnavailable(!showUnavailable)}
              className={showUnavailable ? 'bg-orange-50 border-orange-200' : ''}
            >
              <Filter className="h-4 w-4 mr-2" />
              {showUnavailable ? 'Hide' : 'Show'} Unavailable
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Menu Items */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredItems.map((item) => (
          <Card key={item.id} className="overflow-hidden">
            <div className="aspect-video bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center">
              <div className="text-center">
                <ChefHat className="h-12 w-12 mx-auto mb-2 text-orange-600" />
                <p className="text-sm text-gray-600">Photo coming soon</p>
              </div>
            </div>
            
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-900 text-lg">{item.name}</h3>
                <Badge 
                  variant={item.is_available ? "default" : "secondary"}
                  className={item.is_available ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}
                >
                  {item.is_available ? 'Available' : 'Unavailable'}
                </Badge>
              </div>
              
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                {item.description}
              </p>
              
              <div className="flex items-center justify-between mb-4">
                <span className="text-2xl font-bold text-orange-600">
                  ${item.price.toFixed(2)}
                </span>
                <Badge variant="outline">
                  {item.category_name}
                </Badge>
              </div>
              
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => toggleAvailability(item.id)}
                  className="flex-1"
                >
                  {item.is_available ? (
                    <>
                      <EyeOff className="h-4 w-4 mr-1" />
                      Disable
                    </>
                  ) : (
                    <>
                      <Eye className="h-4 w-4 mr-1" />
                      Enable
                    </>
                  )}
                </Button>
                
                <Dialog open={editingItem?.id === item.id} onOpenChange={(open) => !open && setEditingItem(null)}>
                  <DialogTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setEditingItem(item)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Edit Menu Item</DialogTitle>
                      <DialogDescription>
                        Update the details for {item.name}.
                      </DialogDescription>
                    </DialogHeader>
                    <ItemForm 
                      item={editingItem!}
                      onSave={async (data) => {
                        try {
                          setLoading(true);
                          
                          // Find the category ID by name
                          const category = categories.find(cat => cat.name === data.category);
                          if (!category) {
                            throw new Error('Category not found');
                          }

                          // Update item via API
                          const updateData = {
                            name: data.name!,
                            description: data.description!,
                            price: data.price!,
                            category_id: category.id,
                            is_available: data.is_available!
                          };

                          await apiClient.updateMenuItem(item.id, updateData);
                          
                          // Update local state with correct format
                          setMenuItems(prev => prev.map(i => 
                            i.id === item.id 
                              ? { 
                                  ...i, 
                                  name: data.name!,
                                  description: data.description!,
                                  price: data.price!,
                                  category_name: data.category!,
                                  category_id: category.id,
                                  is_available: data.is_available!
                                }
                              : i
                          ));
                          setEditingItem(null);
                        } catch (error) {
                          console.error('Error updating item:', error);
                          setError('Failed to update menu item.');
                        } finally {
                          setLoading(false);
                        }
                      }}
                      onCancel={() => setEditingItem(null)}
                    />
                  </DialogContent>
                </Dialog>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => deleteItem(item.id)}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredItems.length === 0 && (
        <div className="text-center py-12">
          <ChefHat className="h-16 w-16 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No menu items found</h3>
          <p className="text-gray-600 mb-4">
            {searchQuery || selectedCategory !== 'all' 
              ? 'Try adjusting your search or filters.'
              : 'Start by adding your first menu item.'
            }
          </p>
          {!searchQuery && selectedCategory === 'all' && (
            <Button 
              onClick={() => setIsAddItemOpen(true)}
              className="bg-orange-500 hover:bg-orange-600"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Item
            </Button>
          )}
        </div>
      )}
    </div>
  );
}