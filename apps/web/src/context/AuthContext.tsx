import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signin: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, firstName?: string, lastName?: string) => Promise<void>;
  signout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    if (apiClient.isAuthenticated()) {
      // In a real app, you'd fetch the user profile here
      setUser({ id: 'current-user', email: 'user@example.com' });
    }
    setLoading(false);
  }, []);

  const signin = async (email: string, password: string) => {
    const response = await apiClient.signin(email, password);
    setUser(response.user);
  };

  const signup = async (email: string, password: string, firstName?: string, lastName?: string) => {
    const response = await apiClient.signup(email, password, firstName, lastName);
    setUser(response.user);
  };

  const signout = async () => {
    await apiClient.signout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        signin,
        signup,
        signout,
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