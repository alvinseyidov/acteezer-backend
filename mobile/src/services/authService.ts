import api from '../config/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface User {
  id: number;
  phone: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email?: string;
  birthday?: string;
  gender?: string;
  bio?: string;
  city?: string;
  images?: UserImage[];
  languages?: Language[];
  interests?: Interest[];
  is_phone_verified: boolean;
  is_registration_complete: boolean;
  registration_step: number;
}

export interface UserImage {
  id: number;
  image_url: string;
  is_primary: boolean;
}

export interface Language {
  id: number;
  name: string;
  code: string;
}

export interface Interest {
  id: number;
  name: string;
  icon?: string;
  category: string;
}

export interface AuthResponse {
  success: boolean;
  token: string;
  user: User;
  message?: string;
}

export const authService = {
  // Send OTP
  sendOTP: async (phone: string, purpose: 'registration' | 'login' | 'password_reset' = 'registration') => {
    const response = await api.post('/accounts/users/send_otp/', {
      phone,
      purpose,
    });
    return response.data;
  },

  // Verify OTP
  verifyOTP: async (phone: string, otp_code: string, purpose: 'registration' | 'login' | 'password_reset' = 'registration') => {
    const response = await api.post('/accounts/users/verify_otp/', {
      phone,
      otp_code,
      purpose,
    });
    return response.data;
  },

  // Register
  register: async (phone: string, first_name: string, last_name: string, password: string, password_confirm: string) => {
    const response = await api.post('/accounts/users/register/', {
      phone,
      first_name,
      last_name,
      password,
      password_confirm,
    });
    
    if (response.data.token) {
      await AsyncStorage.setItem('auth_token', response.data.token);
      await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data as AuthResponse;
  },

  // Login with phone and password
  login: async (phone: string, password: string) => {
    const response = await api.post('/accounts/users/login/', {
      phone,
      password,
    });
    
    if (response.data.token) {
      await AsyncStorage.setItem('auth_token', response.data.token);
      await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data as AuthResponse;
  },

  // Get current user
  getCurrentUser: async (): Promise<User | null> => {
    try {
      const response = await api.get('/accounts/users/me/');
      return response.data;
    } catch (error) {
      return null;
    }
  },

  // Update user profile
  updateProfile: async (data: Partial<User>) => {
    const response = await api.put('/accounts/users/me/', data);
    const updatedUser = response.data;
    await AsyncStorage.setItem('user', JSON.stringify(updatedUser));
    return updatedUser;
  },

  // Upload user image
  uploadImage: async (imageUri: string, isPrimary: boolean = false) => {
    const formData = new FormData();
    formData.append('image', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'photo.jpg',
    } as any);
    formData.append('is_primary', isPrimary.toString());

    const response = await api.post('/accounts/users/upload_image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Logout
  logout: async () => {
    await AsyncStorage.removeItem('auth_token');
    await AsyncStorage.removeItem('user');
  },

  // Get stored user
  getStoredUser: async (): Promise<User | null> => {
    try {
      const userJson = await AsyncStorage.getItem('user');
      return userJson ? JSON.parse(userJson) : null;
    } catch (error) {
      return null;
    }
  },

  // Get stored token
  getStoredToken: async (): Promise<string | null> => {
    return await AsyncStorage.getItem('auth_token');
  },
};

