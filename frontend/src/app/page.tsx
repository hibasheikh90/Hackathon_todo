'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

const HomePage = () => {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Todo App</h1>
            </div>
            <div className="flex items-center space-x-4">
              {!isAuthenticated ? (
                <>
                  <Link href="/login" className="text-gray-600 hover:text-gray-900">
                    Login
                  </Link>
                  <Link
                    href="/signup"
                    className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
                  >
                    Sign Up
                  </Link>
                </>
              ) : (
                <Link
                  href="/dashboard"
                  className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700"
                >
                  Dashboard
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl">
            Manage Your Tasks
          </h1>
          <p className="mt-6 max-w-lg mx-auto text-xl text-gray-500">
            A simple and elegant todo application to help you stay organized and productive.
          </p>

          <div className="mt-10">
            {!isAuthenticated ? (
              <Link
                href="/signup"
                className="inline-block bg-blue-600 text-white px-8 py-3 rounded-md text-base font-medium hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
              >
                Get Started
              </Link>
            ) : (
              <Link
                href="/dashboard"
                className="inline-block bg-green-600 text-white px-8 py-3 rounded-md text-base font-medium hover:bg-green-700 md:py-4 md:text-lg md:px-10"
              >
                Go to Dashboard
              </Link>
            )}
          </div>
        </div>

        {/* Features */}
        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Task Management</h3>
            <p className="mt-2 text-gray-500">
              Create, update, and organize your tasks with ease.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Secure Authentication</h3>
            <p className="mt-2 text-gray-500">
              Protect your data with secure user authentication.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900">Real-time Updates</h3>
            <p className="mt-2 text-gray-500">
              See your tasks update instantly across all devices.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;