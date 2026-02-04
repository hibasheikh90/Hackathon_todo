'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import CreateTaskForm from '@/components/tasks/CreateTaskForm';
import TaskList from '@/components/tasks/TaskList';

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { isAuthenticated, loading: authLoading, logout } = useAuth();

  useEffect(() => {
    if (!authLoading) {
      // Allow both authenticated and unauthenticated users to access the dashboard
      // Unauthenticated users will see a limited version
      setLoading(false);
    }
  }, [isAuthenticated, authLoading, router]);

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-black to-gray-900">
        <div className="text-lg text-white">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      <nav className="bg-gray-800/50 backdrop-blur-md border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">TaskFlow</span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  href="/dashboard"
                  className="border-indigo-500 text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Dashboard
                </Link>
              </div>
            </div>
            <div className="flex items-center">
              <div className="ml-3 relative">
                <div className="flex items-center space-x-4">
                  {!isAuthenticated ? (
                    <>
                      <Link
                        href="/login"
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      >
                        Sign In
                      </Link>
                      <Link
                        href="/home"
                        className="text-sm text-gray-300 hover:text-white"
                      >
                        Back to Home
                      </Link>
                    </>
                  ) : (
                    <button
                      onClick={() => {
                        logout();
                        router.push('/home');
                      }}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      Logout
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:flex lg:items-center lg:justify-between mb-8">
            <div className="min-w-0 flex-1">
              <h1 className="text-3xl font-bold leading-7 bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-300 sm:text-4xl sm:truncate">
                {isAuthenticated ? 'My Tasks' : 'TaskFlow Demo'}
              </h1>
            </div>
          </div>

          {!isAuthenticated ? (
            <div className="bg-gray-800/30 backdrop-blur-sm p-8 rounded-2xl border border-gray-700/50 text-center">
              <h2 className="text-xl font-semibold mb-4">Welcome to TaskFlow!</h2>
              <p className="text-gray-300 mb-6">
                This is a demo of the TaskFlow application. Sign in to experience the full functionality.
              </p>
              <div className="space-y-4">
                <Link
                  href="/login"
                  className="inline-block px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full text-white font-medium hover:from-indigo-700 hover:to-purple-700 transition-all duration-300"
                >
                  Sign In to Continue
                </Link>
                <p className="text-gray-400 text-sm mt-4">
                  Or explore the features below (limited functionality without login)
                </p>
              </div>
            </div>
          ) : (
            <>
              <div className="bg-gray-800/30 backdrop-blur-sm p-6 rounded-2xl border border-gray-700/50 mb-8">
                <CreateTaskForm onTaskCreated={() => {}} />
              </div>

              <div className="bg-gray-800/30 backdrop-blur-sm p-6 rounded-2xl border border-gray-700/50">
                <TaskList />
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}