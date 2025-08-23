import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { redirect } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { RestaurantSettings } from '@/components/features/restaurant-settings';

export default async function SettingsPage() {
  const session = await getServerSession(authOptions);

  // Redirect to login if not authenticated
  if (!session) {
    redirect('/auth/login');
  }

  return (
    <DashboardLayout session={session}>
      <RestaurantSettings />
    </DashboardLayout>
  );
}

export const metadata = {
  title: `Settings - ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Restaurant'}`,
  description: 'Configure restaurant settings and preferences.',
};