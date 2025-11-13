import api from '../config/api';

export interface PlaceCategory {
  id: number;
  name: string;
  category_type: string;
  icon: string;
  color: string;
}

export interface Place {
  id: number;
  name: string;
  short_description: string;
  description?: string;
  category: PlaceCategory;
  address: string;
  district: string;
  latitude?: string;
  longitude?: string;
  phone?: string;
  email?: string;
  website?: string;
  instagram?: string;
  price_range: string;
  price_display: string;
  opening_hours?: string;
  features?: string;
  main_image_url?: string;
  images?: Array<{ image_url: string }>;
  rating: string;
  review_count: number;
  is_featured: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface PlaceFilters {
  search?: string;
  category?: string;
  district?: string;
  price?: string;
  min_rating?: number;
  verified?: boolean;
  sort?: 'featured' | 'rating' | 'name' | 'newest' | 'reviews';
}

export const placeService = {
  // Get places list
  getPlaces: async (filters?: PlaceFilters) => {
    const params = new URLSearchParams();
    if (filters?.search) params.append('search', filters.search);
    if (filters?.category) params.append('category', filters.category);
    if (filters?.district) params.append('district', filters.district);
    if (filters?.price) params.append('price', filters.price);
    if (filters?.min_rating) params.append('min_rating', filters.min_rating.toString());
    if (filters?.verified) params.append('verified', 'true');
    if (filters?.sort) params.append('sort', filters.sort);

    const response = await api.get(`/places/places/?${params.toString()}`);
    return response.data.results || response.data;
  },

  // Get place detail
  getPlace: async (id: number) => {
    const response = await api.get(`/places/places/${id}/`);
    return response.data;
  },

  // Get categories
  getCategories: async () => {
    const response = await api.get('/places/categories/');
    return response.data.results || response.data;
  },

  // Toggle favorite
  toggleFavorite: async (id: number, isFavorite: boolean) => {
    if (isFavorite) {
      const response = await api.post(`/places/places/${id}/favorite/`);
      return response.data;
    } else {
      const response = await api.delete(`/places/places/${id}/favorite/`);
      return response.data;
    }
  },

  // Check if favorited
  isFavorited: async (id: number) => {
    const response = await api.get(`/places/places/${id}/is_favorited/`);
    return response.data;
  },

  // Get favorites
  getFavorites: async () => {
    const response = await api.get('/places/favorites/');
    return response.data.results || response.data;
  },
};

