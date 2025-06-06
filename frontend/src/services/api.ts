import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// We'll store the auth context reference here to access it in interceptors
let authContextRef: any = null;

export const setAuthContextRef = (authContext: any) => {
  authContextRef = authContext;
};

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = authContextRef?.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = authContextRef?.getRefreshToken();
        if (!refreshToken) {
          // No refresh token available, logout the user
          authContextRef?.clearAuth();
          return Promise.reject(error);
        }

        const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
          refresh: refreshToken
        });

        // Update tokens in state - use new refresh token if provided, otherwise keep the old one
        const newRefreshToken = response.data.refresh || refreshToken;
        authContextRef?.setTokens(response.data.access, newRefreshToken);

        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        authContextRef?.clearAuth();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const authService = {
  register: async (name: string, email: string, password: string) => {
    const response = await api.post('/auth/register/', { name, email, password });
    
    // Save user data in state if available
    if (response.data.name && response.data.email) {
      const userData = {
        id: response.data.user_id,
        name: response.data.name,
        email: response.data.email
      };
      authContextRef?.setUser(userData);
    }
    
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login/', { email, password });
    
    // Store tokens in state instead of localStorage
    authContextRef?.setTokens(response.data.access, response.data.refresh);
    
    // Save user data in state if available
    if (response.data.user) {
      authContextRef?.setUser(response.data.user);
    }
    
    return response.data;
  },

  logout: () => {
    authContextRef?.clearAuth();
  },

  isAuthenticated: () => {
    return authContextRef?.isAuthenticated || false;
  },

  getCurrentUser: () => {
    return authContextRef?.user || null;
  }
};

export default api;
