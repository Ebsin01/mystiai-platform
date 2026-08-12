import axios from 'axios';

// FastAPI backend base URL - read from environment variables with fallback to live Render backend
const BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  process.env.REACT_APP_API_BASE_URL ||
  'https://mystial-platform-backend.onrender.com';

const api = axios.create({
  baseURL: BASE_URL,
});

// Axios request interceptor to automatically inject the Bearer token from localStorage 'access_token' or 'token'
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
