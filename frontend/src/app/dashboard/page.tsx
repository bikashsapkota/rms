import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { redirect } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { DashboardOverview } from '@/components/features/dashboard-overview';

export default async function DashboardPage() {
  const session = await getServerSession(authOptions);

  // Redirect to login if not authenticated
  if (!session) {
    redirect('/auth/login');
  }

  return (
    <DashboardLayout session={session}>
      <DashboardOverview />
    </DashboardLayout>
  );
}

export const metadata = {
  title: `Dashboard - ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Restaurant'}`,
  description: 'Restaurant management dashboard.',
};