import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
}

interface AuthContextType {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: User) => void;
  clearAuth: () => void;
  getAccessToken: () => string | null;
  getRefreshToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [user, setUserState] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from sessionStorage and localStorage on app start
  useEffect(() => {
    const initializeAuth = () => {
      try {
        // First try sessionStorage (more secure, persists during session)
        let storedAccessToken = sessionStorage.getItem('accessToken');
        let storedRefreshToken = sessionStorage.getItem('refreshToken');
        let storedUserData = sessionStorage.getItem('userData');

        // Fallback to localStorage for migration
        if (!storedAccessToken) {
          storedAccessToken = localStorage.getItem('accessToken');
          storedRefreshToken = localStorage.getItem('refreshToken');
          storedUserData = localStorage.getItem('userData');

          // If found in localStorage, migrate to sessionStorage and clear localStorage
          if (storedAccessToken && storedRefreshToken) {
            sessionStorage.setItem('accessToken', storedAccessToken);
            sessionStorage.setItem('refreshToken', storedRefreshToken);
            if (storedUserData) {
              sessionStorage.setItem('userData', storedUserData);
            }

            // Clear localStorage after migration
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('userData');
          }
        }

        if (storedAccessToken && storedRefreshToken) {
          setAccessToken(storedAccessToken);
          setRefreshToken(storedRefreshToken);
          
          if (storedUserData) {
            try {
              setUserState(JSON.parse(storedUserData));
            } catch (error) {
              console.error('Error parsing stored user data:', error);
              // Clear corrupted data
              sessionStorage.removeItem('userData');
            }
          }
        }
      } catch (error) {
        console.error('Error initializing auth state:', error);
        // Clear potentially corrupted data
        sessionStorage.clear();
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userData');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Persist auth state to sessionStorage when it changes
  useEffect(() => {
    if (!isLoading) {
      if (accessToken && refreshToken) {
        sessionStorage.setItem('accessToken', accessToken);
        sessionStorage.setItem('refreshToken', refreshToken);
      } else {
        sessionStorage.removeItem('accessToken');
        sessionStorage.removeItem('refreshToken');
      }
    }
  }, [accessToken, refreshToken, isLoading]);

  useEffect(() => {
    if (!isLoading) {
      if (user) {
        sessionStorage.setItem('userData', JSON.stringify(user));
      } else {
        sessionStorage.removeItem('userData');
      }
    }
  }, [user, isLoading]);

  const setTokens = (newAccessToken: string, newRefreshToken: string) => {
    setAccessToken(newAccessToken);
    setRefreshToken(newRefreshToken);
  };

  const setUser = (userData: User) => {
    setUserState(userData);
  };

  const clearAuth = () => {
    setAccessToken(null);
    setRefreshToken(null);
    setUserState(null);
    // Clear all storage
    sessionStorage.removeItem('accessToken');
    sessionStorage.removeItem('refreshToken');
    sessionStorage.removeItem('userData');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userData');
  };

  const getAccessToken = () => accessToken;
  const getRefreshToken = () => refreshToken;

  const isAuthenticated = !!accessToken;

  const value: AuthContextType = {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    isLoading,
    setTokens,
    setUser,
    clearAuth,
    getAccessToken,
    getRefreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};