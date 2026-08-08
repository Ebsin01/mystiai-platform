import api from './api';

/**
 * Authentication service handling interaction with FastAPI backend auth APIs.
 */
const authService = {
  /**
   * Registers a new user.
   * Sends JSON body matching backend UserRegister schema.
   */
  register: async (fullName, email, password) => {
    const response = await api.post('/register', {
      full_name: fullName,
      email: email,
      password: password,
    });
    return response.data;
  },

  /**
   * Logins an existing user.
   * Note: OAuth2PasswordRequestForm expects application/x-www-form-urlencoded.
   */
  login: async (email, password) => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);

    const response = await api.post('/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    // Save JWT access token upon successful login
    if (response.data && response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('token', response.data.access_token);
    }
    
    return response.data;
  },

  /**
   * Retrieves the authenticated user's profile.
   * Uses JWT token attached via interceptor.
   */
  getProfile: async () => {
    const response = await api.get('/profile');
    return response.data;
  },

  /**
   * Updates the user's profile.
   * Sends UserUpdate schema body containing updated full_name.
   */
  updateProfile: async (fullName) => {
    const response = await api.put('/profile', {
      full_name: fullName,
    });
    return response.data;
  },

  /**
   * Helper to check if a token exists in local storage.
   */
  isAuthenticated: () => {
    return !!(localStorage.getItem('access_token') || localStorage.getItem('token'));
  },

  /**
   * Logs out the user by removing local storage tokens.
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token');
  }
};

export default authService;
