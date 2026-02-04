'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/lib/api';

interface User {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on component mount
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      setToken(storedToken);
      // Try to fetch user info to verify token
      fetchUserInfo(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserInfo = async (authToken: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (!apiUrl) {
        console.error('NEXT_PUBLIC_API_URL is not defined');
        localStorage.removeItem('auth_token');
        setToken(null);
        setUser(null);
        setLoading(false);
        return;
      }

      // Temporarily set the token in the API client for this request
      const response = await fetch(`${apiUrl}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Token is invalid, clear it
        localStorage.removeItem('auth_token');
        setToken(null);
        setUser(null);
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      // Validate environment variable is set
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (!apiUrl) {
        console.error('NEXT_PUBLIC_API_URL is not defined');
        return false;
      }

      console.log('Attempting to connect to API at:', `${apiUrl}/auth/login`);

      const response = await fetch(`${apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      console.log('Response received:', response.status);

      if (response.ok) {
        const data = await response.json();
        const authToken = data.access_token;

        // Store the token
        localStorage.setItem('auth_token', authToken);
        setToken(authToken);

        // Fetch user info
        await fetchUserInfo(authToken);

        return true;
      } else {
        const errorData = await response.json();
        console.error('Login error:', errorData.detail || 'Login failed');
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      // More specific error handling for network issues
      if (error instanceof TypeError && (error.message.includes('fetch') || error.message.includes('network'))) {
        console.error('Network error: Could not reach the authentication server. Please ensure the backend server is running.');
        console.error('Check that your backend server is running on the configured API URL:', process.env.NEXT_PUBLIC_API_URL);
      } else if (error instanceof Error) {
        console.error('Connection error:', error.message);
        if (error.message.includes('ECONNREFUSED') || error.message.includes('WinError 1225')) {
          console.error('The connection was refused. Please check if:');
          console.error('- The backend server is running');
          console.error('- The API URL is correctly configured in your environment variables');
          console.error('- The port is correct and accessible');
        }
      }
      return false;
    }
  };

  const register = async (email: string, password: string): Promise<boolean> => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (!apiUrl) {
        console.error('NEXT_PUBLIC_API_URL is not defined');
        return false;
      }

      const response = await fetch(`${apiUrl}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const userData = await response.json();

        // After registration, user needs to log in
        return await login(email, password);
      } else {
        const errorData = await response.json();
        console.error('Registration error:', errorData.detail || 'Registration failed');
        return false;
      }
    } catch (error) {
      console.error('Registration error:', error);
      // Additional error handling for network issues
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.error('Network error: Could not reach the authentication server. Please ensure the backend server is running.');
      }
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!token && !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};