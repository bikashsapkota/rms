import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { PublicLayout } from '@/components/layout/layout';
import { ContactInfo } from '@/components/features/contact-info';

export default async function ContactPage() {
  const session = await getServerSession(authOptions);

  return (
    <PublicLayout session={session}>
      <div className="bg-white min-h-screen">
        <ContactInfo />
      </div>
    </PublicLayout>
  );
}

export const metadata = {
  title: `Contact Us - ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Restaurant'}`,
  description: `Contact ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'our restaurant'} for reservations, inquiries, or feedback. Find our location, hours, and contact information.`,
};