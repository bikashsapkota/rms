'use client';

import { SessionProvider } from 'next-auth/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { Header } from './header';
import { Footer } from './footer';

interface LayoutProps {
  children: React.ReactNode;
  variant?: 'public' | 'dashboard';
  session?: any;
}

export function Layout({ children, variant = 'public', session }: LayoutProps) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        retry: 1,
      },
    },
  }));

  return (
    <SessionProvider session={session}>
      <QueryClientProvider client={queryClient}>
        <div className="min-h-screen bg-gray-50 flex flex-col">
          <Header variant={variant} />
          <main className="flex-1">
            {children}
          </main>
          {variant === 'public' && <Footer />}
        </div>
      </QueryClientProvider>
    </SessionProvider>
  );
}

export function PublicLayout({ children, session }: { children: React.ReactNode; session?: any }) {
  return (
    <Layout variant="public" session={session}>
      {children}
    </Layout>
  );
}

export function DashboardLayout({ children, session }: { children: React.ReactNode; session?: any }) {
  return (
    <Layout variant="dashboard" session={session}>
      <div className="bg-white">
        {children}
      </div>
    </Layout>
  );
}