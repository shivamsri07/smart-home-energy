// src/services/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { loginUser } from '@/api/authApi';

// Define the shape of the context state
interface AuthContextType {
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Helper function to check if a JWT token is expired
const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    return payload.exp < currentTime;
  } catch (error) {
    // If we can't parse the token, consider it expired
    return true;
  }
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken && !isTokenExpired(storedToken)) {
      return storedToken;
    }
    // Clear expired token
    localStorage.removeItem('authToken');
    return null;
  });

  useEffect(() => {
    // This effect syncs the state with localStorage
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
  }, [token]);

  // Check token expiration on mount and set up periodic checks
  useEffect(() => {
    if (!token) return;

    // Check if token is expired
    if (isTokenExpired(token)) {
      setToken(null);
      return;
    }

    // Set up periodic token validation (check every 5 minutes)
    const interval = setInterval(() => {
      if (token && isTokenExpired(token)) {
        setToken(null);
      }
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [token]);

  const login = async (email: string, password: string) => {
    const response = await loginUser({ email, password });
    setToken(response.access_token);
  };

  const logout = () => {
    setToken(null);
  };

  const isAuthenticated = !!token && !isTokenExpired(token);

  return (
    <AuthContext.Provider value={{ token, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

// Create a custom hook for easy access to the context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};