// src/lib/axios.ts
import axios from 'axios';


const api = axios.create({
  baseURL: process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
});

// Use an interceptor to add the auth token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;