import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { PublicLayout } from '@/components/layout/layout';
import { HeroSection } from '@/components/features/hero-section';
import { FeaturedMenu } from '@/components/features/featured-menu';
import { ReservationWidget } from '@/components/features/reservation-widget';
import { RestaurantStory } from '@/components/features/restaurant-story';
import { PhotoGallery } from '@/components/features/photo-gallery';
import { CustomerReviews } from '@/components/features/customer-reviews';
import { LocationContact } from '@/components/features/location-contact';

export default async function HomePage() {
  const session = await getServerSession(authOptions);

  return (
    <PublicLayout session={session}>
      <div className="bg-white">
        <HeroSection />
        <FeaturedMenu />
        <ReservationWidget />
        <RestaurantStory />
        <PhotoGallery />
        <CustomerReviews />
        <LocationContact />
      </div>
    </PublicLayout>
  );
}