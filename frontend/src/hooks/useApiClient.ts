'use client';

import { useSession } from 'next-auth/react';
import { useEffect } from 'react';
import { apiClient } from '@/lib/api';

export function useApiClient() {
  const { data: session } = useSession();

  useEffect(() => {
    if (session?.accessToken) {
      apiClient.setSessionToken(session.accessToken);
    }
  }, [session?.accessToken]);

  return apiClient;
}