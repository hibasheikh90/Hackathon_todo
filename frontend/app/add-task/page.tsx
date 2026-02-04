'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import CreateTaskForm from '@/components/tasks/CreateTaskForm';
import Link from 'next/link';

export default function AddTaskPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Allow both authenticated and unauthenticated users to access the add task page
    if (!authLoading) {
      setIsLoading(false);
    }
  }, [isAuthenticated, authLoading]);

  if (isLoading || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-black to-gray-900">
        <div className="text-lg text-white">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-indigo-900/20 text-white relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-48 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-48 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <nav className="relative z-10 bg-gray-800/50 backdrop-blur-md border-b border-gray-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">TaskFlow</span>
            </div>
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <Link
                  href="/dashboard"
                  className="text-sm text-gray-300 hover:text-white transition-colors duration-200"
                >
                  My Dashboard
                </Link>
              ) : (
                <Link
                  href="/home"
                  className="text-sm text-gray-300 hover:text-white transition-colors duration-200"
                >
                  Back to Home
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="relative z-10 py-12">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-10 text-center">
            <h1 className="text-4xl md:text-5xl font-bold leading-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-indigo-200 mb-4">
              Create New Task
            </h1>
            <p className="text-lg text-gray-400 max-w-md mx-auto">
              Organize your work efficiently and boost your productivity
            </p>
          </div>

          <div className="bg-gray-800/40 backdrop-blur-xl p-8 rounded-3xl border border-gray-700/50 shadow-2xl shadow-indigo-900/10 transition-all duration-300 hover:shadow-2xl hover:shadow-indigo-900/20">
            <CreateTaskForm onTaskCreated={() => {
              // Optionally redirect to dashboard after successful task creation
              // router.push('/dashboard');
            }} />

            <div className="mt-6 text-center">
              <Link
                href={isAuthenticated ? '/dashboard' : '/home'}
                className="inline-flex items-center text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors duration-200 group"
              >
                <span>{isAuthenticated ? 'View all tasks' : 'Back to home'}</span>
                <svg
                  className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform duration-200"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}