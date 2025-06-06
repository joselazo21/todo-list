import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/api';

/**
 * Custom hook that provides authentication methods with automatic state management
 */
export const useAuthService = () => {
  const auth = useAuth();

  const login = async (email: string, password: string) => {
    const result = await authService.login(email, password);
    return result;
  };

  const register = async (name: string, email: string, password: string) => {
    const result = await authService.register(name, email, password);
    return result;
  };

  const logout = () => {
    authService.logout();
  };

  return {
    // Auth state
    isAuthenticated: auth.isAuthenticated,
    user: auth.user,
    accessToken: auth.accessToken,
    
    // Auth methods
    login,
    register,
    logout,
    
    // Direct access to auth service methods
    isAuthenticatedCheck: authService.isAuthenticated,
    getCurrentUser: authService.getCurrentUser,
  };
};