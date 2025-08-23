import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { redirect } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { MenuManagement } from '@/components/features/menu-management';

export default async function MenuManagementPage() {
  const session = await getServerSession(authOptions);

  // Redirect to login if not authenticated
  if (!session) {
    redirect('/auth/login');
  }

  return (
    <DashboardLayout session={session}>
      <MenuManagement />
    </DashboardLayout>
  );
}

export const metadata = {
  title: `Menu Management - ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Restaurant'}`,
  description: 'Manage your restaurant menu items and categories.',
};