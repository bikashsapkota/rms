import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { PublicLayout } from '@/components/layout/layout';
import { MenuDisplay } from '@/components/features/menu-display';
import { apiClient } from '@/lib/api';

async function getMenuData() {
  try {
    // Only fetch public menu data, derive categories from items
    const menuItems = await apiClient.getPublicMenu();
    
    // Extract unique categories from menu items
    const categorySet = new Set();
    const categories: any[] = [];
    
    if (Array.isArray(menuItems)) {
      menuItems.forEach((item: any) => {
        if (item.category_name && !categorySet.has(item.category_name)) {
          categorySet.add(item.category_name);
          categories.push({
            id: item.category_name.toLowerCase().replace(/\s+/g, '-'),
            name: item.category_name,
            description: `Delicious ${item.category_name.toLowerCase()}`
          });
        }
      });

      // Add category_id to menu items for proper filtering and convert price to number
      menuItems.forEach((item: any) => {
        if (item.category_name) {
          item.category_id = item.category_name.toLowerCase().replace(/\s+/g, '-');
        }
        // Convert price string to number
        if (item.price && typeof item.price === 'string') {
          item.price = parseFloat(item.price);
        }
        // Ensure is_available is boolean
        if (item.is_available === undefined) {
          item.is_available = true;
        }
      });
    }

    return {
      categories,
      menuItems: menuItems || []
    };
  } catch (error) {
    console.error('Failed to fetch menu data:', error);
    // Return fallback demo data
    return {
      categories: [
        { id: '1', name: 'Appetizers', description: 'Start your meal with these delicious options' },
        { id: '2', name: 'Main Courses', description: 'Our signature entrees and hearty dishes' },
        { id: '3', name: 'Desserts', description: 'Sweet endings to your dining experience' },
        { id: '4', name: 'Beverages', description: 'Refreshing drinks and specialty cocktails' }
      ],
      menuItems: [
        {
          id: '1',
          category_id: '1',
          name: 'Truffle Arancini',
          description: 'Crispy risotto balls with black truffle and parmesan',
          price: 16.99,
          is_available: true
        },
        {
          id: '2', 
          category_id: '1',
          name: 'Burrata Salad',
          description: 'Fresh burrata with heirloom tomatoes and basil',
          price: 18.99,
          is_available: true
        },
        {
          id: '3',
          category_id: '2', 
          name: 'Truffle Pasta',
          description: 'Homemade pasta with black truffle and parmesan cheese',
          price: 24.99,
          is_available: true
        },
        {
          id: '4',
          category_id: '2',
          name: 'Grilled Salmon',
          description: 'Fresh Atlantic salmon with lemon herb butter and seasonal vegetables',
          price: 28.99,
          is_available: true
        },
        {
          id: '5',
          category_id: '2',
          name: 'Ribeye Steak',
          description: '12oz prime ribeye with garlic mashed potatoes',
          price: 42.99,
          is_available: true
        },
        {
          id: '6',
          category_id: '3',
          name: 'Chocolate Soufflé',
          description: 'Warm chocolate soufflé with vanilla ice cream',
          price: 12.99,
          is_available: true
        },
        {
          id: '7',
          category_id: '3',
          name: 'Tiramisu',
          description: 'Classic Italian dessert with espresso and mascarpone',
          price: 9.99,
          is_available: true
        }
      ]
    };
  }
}

export default async function MenuPage() {
  const session = await getServerSession(authOptions);
  const { categories, menuItems } = await getMenuData();

  return (
    <PublicLayout session={session}>
      <div className="bg-white min-h-screen">
        <MenuDisplay categories={categories} menuItems={menuItems} />
      </div>
    </PublicLayout>
  );
}

export const metadata = {
  title: `Menu - ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Restaurant'}`,
  description: `Discover our delicious menu featuring fresh ingredients and authentic flavors. Browse appetizers, main courses, desserts and beverages at ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'our restaurant'}.`,
};