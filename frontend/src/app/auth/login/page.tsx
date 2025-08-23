import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { redirect } from 'next/navigation';
import { StaffLogin } from '@/components/features/staff-login';

export default async function LoginPage() {
  const session = await getServerSession(authOptions);

  // If user is already logged in, redirect to dashboard
  if (session) {
    redirect('/dashboard');
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <StaffLogin />
    </div>
  );
}

export const metadata = {
  title: `Staff Login - ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Restaurant'}`,
  description: 'Staff login portal for restaurant management system.',
};