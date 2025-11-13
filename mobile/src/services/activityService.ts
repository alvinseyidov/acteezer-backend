import api from '../config/api';

export interface ActivityCategory {
  id: number;
  name: string;
  category_type: string;
  icon: string;
  color: string;
}

export interface Activity {
  id: number;
  title: string;
  short_description: string;
  description?: string;
  category: ActivityCategory;
  organizer: {
    id: number;
    full_name: string;
    images?: Array<{ image_url: string }>;
  };
  start_date: string;
  end_date: string;
  duration_hours: number;
  location_name: string;
  address: string;
  district: string;
  latitude?: string;
  longitude?: string;
  max_participants: number;
  min_participants: number;
  price: string;
  is_free: boolean;
  difficulty_level: string;
  main_image_url?: string;
  images?: Array<{ image_url: string }>;
  status: string;
  is_featured: boolean;
  participants_count: number;
  available_spots: number;
  is_upcoming: boolean;
  is_ongoing: boolean;
  is_past: boolean;
  created_at: string;
}

export interface ActivityFilters {
  search?: string;
  category?: string;
  district?: string;
  date?: 'today' | 'upcoming';
  price?: 'free' | 'paid';
  difficulty?: string;
  sort?: 'featured' | 'date' | 'price_low' | 'price_high' | 'newest';
}

export const activityService = {
  // Get activities list
  getActivities: async (filters?: ActivityFilters) => {
    const params = new URLSearchParams();
    if (filters?.search) params.append('search', filters.search);
    if (filters?.category) params.append('category', filters.category);
    if (filters?.district) params.append('district', filters.district);
    if (filters?.date) params.append('date', filters.date);
    if (filters?.price) params.append('price', filters.price);
    if (filters?.difficulty) params.append('difficulty', filters.difficulty);
    if (filters?.sort) params.append('sort', filters.sort);

    const response = await api.get(`/activities/activities/?${params.toString()}`);
    return response.data.results || response.data;
  },

  // Get activity detail
  getActivity: async (id: number) => {
    const response = await api.get(`/activities/activities/${id}/`);
    return response.data;
  },

  // Get categories
  getCategories: async () => {
    const response = await api.get('/activities/categories/');
    return response.data.results || response.data;
  },

  // Join activity
  joinActivity: async (id: number, message?: string) => {
    const response = await api.post(`/activities/activities/${id}/join/`, {
      message: message || '',
    });
    return response.data;
  },

  // Cancel join request
  cancelJoin: async (id: number) => {
    const response = await api.post(`/activities/activities/${id}/cancel_join/`);
    return response.data;
  },

  // Check if can join
  canJoin: async (id: number) => {
    const response = await api.get(`/activities/activities/${id}/can_join/`);
    return response.data;
  },

  // Get participants
  getParticipants: async (id: number) => {
    const response = await api.get(`/activities/activities/${id}/participants/`);
    return response.data;
  },
};

