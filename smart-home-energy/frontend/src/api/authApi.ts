// src/api/authApi.ts
import axios from 'axios';

// Define the types for our function arguments and response

interface RegisterCredentials {
  email: string
  password: string
}
interface LoginCredentials {
  email: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Create an axios instance with a base URL if you want
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://smart-home-energy-production-5060.up.railway.app/api/v1',
});

export const loginUser = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  // FastAPI's OAuth2PasswordRequestForm expects form data, not JSON
  const formData = new URLSearchParams();
  formData.append('username', credentials.email);
  formData.append('password', credentials.password);

  try {
    const response = await api.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  } catch (error) {
    // You can add more robust error handling here
    console.error('Login failed:', error);
    throw error;
  }
};

export const registerUser = async (credentials: RegisterCredentials): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/auth/register', credentials);
  return response.data;
};