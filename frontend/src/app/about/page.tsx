import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { PublicLayout } from '@/components/layout/layout';
import { AboutContent } from '@/components/features/about-content';

export default async function AboutPage() {
  const session = await getServerSession(authOptions);

  return (
    <PublicLayout session={session}>
      <div className="bg-white min-h-screen">
        <AboutContent />
      </div>
    </PublicLayout>
  );
}

export const metadata = {
  title: `About Us - ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Restaurant'}`,
  description: `Learn about ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'our restaurant'}'s story, our passionate team, and our commitment to exceptional dining experiences.`,
};