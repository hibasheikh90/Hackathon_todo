'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function RootPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // If auth is loaded, redirect appropriately
    if (!authLoading) {
      if (isAuthenticated) {
        // If user is already logged in, redirect to dashboard
        router.push('/');
      } else {
        // If not authenticated, redirect to home page
        router.push('/home');
      }
      setIsLoading(false);
    }
  }, [isAuthenticated, authLoading, router]);

  if (isLoading || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-black to-gray-900">
        <div className="text-lg text-white">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-black to-gray-900">
      <div className="text-lg text-white">Redirecting...</div>
    </div>
  );
}