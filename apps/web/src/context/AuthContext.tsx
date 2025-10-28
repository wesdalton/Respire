import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signin: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, firstName?: string, lastName?: string, profilePictureUrl?: string) => Promise<void>;
  signout: () => Promise<void>;
  setAuthFromCallback: (accessToken: string, refreshToken: string) => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    const initAuth = async () => {
      // Check for demo mode first
      const isDemoMode = localStorage.getItem('demo_mode') === 'active';

      if (isDemoMode) {
        try {
          const userData = await apiClient.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Failed to fetch demo user:', error);
        }
        setLoading(false);
        return;
      }

      // Normal authentication flow
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const userData = await apiClient.getCurrentUser();
          setUser(userData);
        } catch (error: any) {
          console.error('Failed to fetch user:', error);
          // Only clear token if it's actually invalid (401), not network errors
          if (error.response?.status === 401) {
            apiClient.clearToken();
          }
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const signin = async (email: string, password: string) => {
    const response = await apiClient.signin(email, password);
    setUser(response.user);
  };

  const signup = async (email: string, password: string, firstName?: string, lastName?: string, profilePictureUrl?: string) => {
    const response = await apiClient.signup(email, password, firstName, lastName, profilePictureUrl);

    // Check if email confirmation is required
    if (response.requires_confirmation) {
      // Throw a special error that includes the confirmation message
      throw {
        response: {
          data: response
        }
      };
    }

    setUser(response.user);
  };

  const signout = async () => {
    await apiClient.signout();
    setUser(null);
  };

  const setAuthFromCallback = async (accessToken: string, refreshToken: string) => {
    // Store tokens
    apiClient.setToken(accessToken, refreshToken);
    // Fetch user data
    try {
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user after OAuth:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        signin,
        signup,
        signout,
        setAuthFromCallback,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}