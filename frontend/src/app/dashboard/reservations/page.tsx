import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { redirect } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { ReservationsManagement } from '@/components/features/reservations-management';

export default async function ReservationsManagementPage() {
  const session = await getServerSession(authOptions);

  // Redirect to login if not authenticated
  if (!session) {
    redirect('/auth/login');
  }

  return (
    <DashboardLayout session={session}>
      <ReservationsManagement />
    </DashboardLayout>
  );
}

export const metadata = {
  title: `Reservations - ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Restaurant'}`,
  description: 'Manage restaurant reservations and bookings.',
};