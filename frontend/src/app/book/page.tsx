import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { PublicLayout } from '@/components/layout/layout';
import { ReservationBooking } from '@/components/features/reservation-booking';
import { apiClient } from '@/lib/api';

interface BookingPageProps {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

async function getAvailabilityData(searchParams: { [key: string]: string | string[] | undefined }) {
  // Extract search params for pre-filling the form
  const date = typeof searchParams.date === 'string' ? searchParams.date : '';
  const time = typeof searchParams.time === 'string' ? searchParams.time : '';
  const partySize = typeof searchParams.party_size === 'string' ? searchParams.party_size : '';

  // In a real app, we'd fetch actual availability from the API
  try {
    if (date && partySize) {
      const availability = await apiClient.getPublicAvailability(date, parseInt(partySize));
      return {
        availability,
        prefill: { date, time, partySize }
      };
    }
  } catch (error) {
    console.error('Failed to fetch availability:', error);
  }

  return {
    availability: null,
    prefill: { date, time, partySize }
  };
}

export default async function BookingPage({ searchParams }: BookingPageProps) {
  const session = await getServerSession(authOptions);
  const resolvedSearchParams = await searchParams;
  const { availability, prefill } = await getAvailabilityData(resolvedSearchParams);

  return (
    <PublicLayout session={session}>
      <div className="bg-white min-h-screen">
        <ReservationBooking 
          initialAvailability={availability}
          prefillData={prefill}
        />
      </div>
    </PublicLayout>
  );
}

export const metadata = {
  title: `Book a Table - ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'Restaurant'}`,
  description: `Reserve your table at ${process.env.NEXT_PUBLIC_RESTAURANT_NAME || 'our restaurant'}. Choose your preferred date, time, and party size for an exceptional dining experience.`,
};