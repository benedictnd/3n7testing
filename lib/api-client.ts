import { Notification } from '@/components/ui/notification-bell';

// API base URL from environment or default
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types for API responses
export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export interface FeedbackSubmitData {
  training_session_id: string;
  training_quality: number;
  expectations: number;
  body_condition: number;
  intensity: number;
  notes?: string;
}

export interface FeedbackResponse {
  id: string;
  message: string;
}

export interface NotificationsResponse {
  notifications: Notification[];
  unread_count: number;
}

// Main API client class
class ApiClient {
  private token: string | null = null;

  constructor() {
    // Get token from localStorage if we're in a browser environment
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  // Set authentication token
  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  // Clear authentication token
  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Get request headers
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Generic request method
  private async request<T>(
    endpoint: string,
    method: string = 'GET',
    body?: any
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      const options: RequestInit = {
        method,
        headers: this.getHeaders(),
        credentials: 'include',
      };

      if (body) {
        options.body = JSON.stringify(body);
      }

      const response = await fetch(url, options);
      const data = await response.json();

      if (!response.ok) {
        return { error: data.detail || 'An error occurred' };
      }

      return { data };
    } catch (error) {
      console.error('API request error:', error);
      return { error: 'Network error, please try again' };
    }
  }

  // Authentication methods
  async login(email: string, password: string): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('username', email); // OAuth2 uses username field
    formData.append('password', password);

    try {
      const url = `${API_BASE_URL}/auth/token`;
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        return { error: data.detail || 'Login failed' };
      }

      // Save the token
      this.setToken(data.access_token);

      return { data };
    } catch (error) {
      console.error('Login error:', error);
      return { error: 'Network error, please try again' };
    }
  }

  async logout(): Promise<void> {
    this.clearToken();
  }

  // Training feedback methods
  async submitFeedback(feedback: FeedbackSubmitData): Promise<ApiResponse<FeedbackResponse>> {
    return this.request<FeedbackResponse>('/training/feedback', 'POST', feedback);
  }

  // Notifications methods
  async getNotifications(): Promise<ApiResponse<NotificationsResponse>> {
    return this.request<NotificationsResponse>('/training/notifications');
  }

  async markNotificationAsRead(id: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/training/notifications/${id}/read`, 'POST');
  }

  async markAllNotificationsAsRead(): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>('/training/notifications/read-all', 'POST');
  }
}

// Create and export an instance
const apiClient = new ApiClient();
export default apiClient; 