/**
 * Authentication Context
 *
 * Provides authentication state and methods to the entire app.
 * Handles login, logout, and user session management.
 */

import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is authenticated on mount
  useEffect(() => {
    const initAuth = async () => {
      if (authAPI.isAuthenticated()) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
        } catch (err) {
          console.error('Failed to fetch user:', err);
          // Token might be invalid, let interceptor handle it
          authAPI.logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username, password) => {
    try {
      setError(null);
      const data = await authAPI.login(username, password);

      // Fetch user data after successful login
      const userData = await authAPI.getCurrentUser();
      setUser(userData);

      return { success: true, data };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    setUser(null);
    authAPI.logout();
  };

  const register = async (username, password, email) => {
    try {
      setError(null);
      const data = await authAPI.register(username, password, email);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Registration failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    register,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
