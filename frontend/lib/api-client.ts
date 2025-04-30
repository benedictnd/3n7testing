import { useState, useEffect } from 'react';
import {
  ApiResponse,
  ReportFormat,
  User,
  TrainingSession,
  TrainingSessionDetail,
  TrainingSessionsResponse,
  FeedbackSubmitData,
  FeedbackResponse,
  NotificationsResponse,
  ReportResponse,
  ReportExportRequest,
  IndependentTrainingCreate,
  IndependentTraining,
  IndependentTrainingResponse,
  MonthlyReportData
} from './types/api';
import { 
  CheckEquipmentAvailabilityRequest, 
  EquipmentAvailabilityResponse, 
  Equipment, 
  ReserveEquipmentRequest, 
  ReserveEquipmentResponse 
} from "./types/equipment";
import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Define API response interface
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

// Define User registration data interface
export interface RegisterUserData {
  name: string;
  email: string;
  password: string;
  role: 'athlete' | 'coach';
  nationality: string;
  sports?: string[];
}

// Define User login data interface
export interface LoginUserData {
  email: string;
  password: string;
}

// Define Auth response interface
export interface AuthResponse {
  access_token: string;
  user: {
    id: string;
    name: string;
    email: string;
    role: 'athlete' | 'coach';
  };
}

// Define Email request data interface
export interface EmailRequestData {
  to_email: string;
  subject: string;
  html_content: string;
  cc?: string[];
  bcc?: string[];
}

// Define Test Email request data interface
export interface TestEmailRequestData {
  to_email?: string;
}

class ApiClient {
  private readonly baseURL: string;
  private readonly client: AxiosInstance;
  private authToken: string | null = null;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use((config: AxiosRequestConfig) => {
      if (this.authToken && config.headers) {
        config.headers.Authorization = `Bearer ${this.authToken}`;
      }
      return config;
    });

    // Initialize token from localStorage if available
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        this.authToken = token;
      }
    }
  }

  // Set authentication token
  public setToken(token: string): void {
    this.authToken = token;
  }

  // Clear authentication token
  public clearToken(): void {
    this.authToken = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Generic request handler
  private async request<T>(config: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<T> = await this.client(config);
      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        return {
          success: false,
          error: error.response.data?.message || 'An error occurred',
        };
      } else if (error.request) {
        // The request was made but no response was received
        return {
          success: false,
          error: 'No response from server. Please check your internet connection.',
        };
      } else {
        // Something happened in setting up the request that triggered an Error
        return {
          success: false,
          error: error.message || 'An unexpected error occurred',
        };
      }
    }
  }

  // User registration
  public async register(userData: RegisterUserData): Promise<ApiResponse<AuthResponse>> {
    return this.request<AuthResponse>({
      method: 'POST',
      url: '/auth/register',
      data: userData,
    });
  }

  // User login
  public async login(credentials: LoginUserData): Promise<ApiResponse<AuthResponse>> {
    return this.request<AuthResponse>({
      method: 'POST',
      url: '/auth/login',
      data: credentials,
    });
  }

  // Check authentication status
  public async checkAuth(): Promise<ApiResponse<{ user: any }>> {
    return this.request<{ user: any }>({
      method: 'GET',
      url: '/auth/me',
    });
  }

  // Logout
  public logout(): void {
    this.clearToken();
  }

  // Training session endpoints
  async getTrainingSessions(params: {
    startDate?: string;
    endDate?: string;
    limit?: number;
    offset?: number;
  } = {}): Promise<ApiResponse<TrainingSessionsResponse>> {
    const queryParams = new URLSearchParams();
    if (params.startDate) queryParams.append('start_date', params.startDate);
    if (params.endDate) queryParams.append('end_date', params.endDate);
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.offset) queryParams.append('offset', params.offset.toString());
    
    return this.request({
      method: 'GET',
      url: `/training-sessions?${queryParams.toString()}`,
    });
  }

  async getTrainingSession(id: string): Promise<ApiResponse<TrainingSessionDetail>> {
    return this.request({
      method: 'GET',
      url: `/training-sessions/${id}`,
    });
  }

  async createTrainingSession(sessionData: Partial<TrainingSession>): Promise<ApiResponse<TrainingSession>> {
    return this.request({
      method: 'POST',
      url: '/training-sessions',
      data: sessionData,
    });
  }

  async updateTrainingSession(id: string, sessionData: Partial<TrainingSession>): Promise<ApiResponse<TrainingSession>> {
    return this.request({
      method: 'PUT',
      url: `/training-sessions/${id}`,
      data: sessionData,
    });
  }

  async deleteTrainingSession(id: string): Promise<ApiResponse<{message: string}>> {
    return this.request({
      method: 'DELETE',
      url: `/training-sessions/${id}`,
    });
  }

  async markAttendance(sessionId: string, attendanceData: {athlete_ids: string[]}): Promise<ApiResponse<{message: string}>> {
    return this.request({
      method: 'POST',
      url: `/training-sessions/${sessionId}/attendance`,
      data: attendanceData,
    });
  }

  // User management endpoints
  async getUsers(params: { role?: string; limit?: number; offset?: number } = {}): Promise<ApiResponse<{users: User[], total: number, page: number, size: number}>> {
    const queryParams = new URLSearchParams();
    if (params.role) queryParams.append('role', params.role);
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.offset) queryParams.append('offset', params.offset.toString());
    
    return this.request({
      method: 'GET',
      url: `/users?${queryParams.toString()}`,
    });
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.request({
      method: 'GET',
      url: '/users/me',
    });
  }

  async getUser(id: string): Promise<ApiResponse<User>> {
    return this.request({
      method: 'GET',
      url: `/users/${id}`,
    });
  }

  async updateUser(id: string, userData: Partial<User>): Promise<ApiResponse<User>> {
    return this.request({
      method: 'PUT',
      url: `/users/${id}`,
      data: userData,
    });
  }

  async deleteUser(id: string): Promise<ApiResponse<{message: string}>> {
    return this.request({
      method: 'DELETE',
      url: `/users/${id}`,
    });
  }

  // Report generation endpoints
  async getTrainingReport(
    params: {
      startDate: string;
      endDate: string;
      format?: ReportFormat;
    }
  ): Promise<ApiResponse<ReportResponse>> {
    const queryParams = new URLSearchParams();
    queryParams.append('start_date', params.startDate);
    queryParams.append('end_date', params.endDate);
    if (params.format) queryParams.append('format', params.format);
    
    return this.request({
      method: 'GET',
      url: `/reports/training?${queryParams.toString()}`,
    });
  }

  async getAttendanceReport(
    params: {
      startDate: string;
      endDate: string;
      athleteId?: string;
      format?: ReportFormat;
    }
  ): Promise<ApiResponse<ReportResponse>> {
    const queryParams = new URLSearchParams();
    queryParams.append('start_date', params.startDate);
    queryParams.append('end_date', params.endDate);
    if (params.athleteId) queryParams.append('athlete_id', params.athleteId);
    if (params.format) queryParams.append('format', params.format);
    
    return this.request({
      method: 'GET',
      url: `/reports/attendance?${queryParams.toString()}`,
    });
  }

  async getFeedbackReport(
    params: {
      startDate: string;
      endDate: string;
      sessionId?: string;
      format?: ReportFormat;
    }
  ): Promise<ApiResponse<ReportResponse>> {
    const queryParams = new URLSearchParams();
    queryParams.append('start_date', params.startDate);
    queryParams.append('end_date', params.endDate);
    if (params.sessionId) queryParams.append('session_id', params.sessionId);
    if (params.format) queryParams.append('format', params.format);
    
    return this.request({
      method: 'GET',
      url: `/reports/feedback?${queryParams.toString()}`,
    });
  }

  async exportReport(
    title: string,
    data: any,
    format: ReportFormat = ReportFormat.PDF
  ): Promise<ApiResponse<{url: string}>> {
    return this.request({
      method: 'POST',
      url: '/reports/export',
      data: {
        title,
        data,
        format
      },
    });
  }

  async getMonthlyReport(
    params: {
      startDate: string;
      endDate: string;
      format?: ReportFormat;
    }
  ): Promise<ApiResponse<MonthlyReportData>> {
    const queryParams = new URLSearchParams();
    queryParams.append('start_date', params.startDate);
    queryParams.append('end_date', params.endDate);
    if (params.format) queryParams.append('format', params.format);
    
    return this.request({
      method: 'GET',
      url: `/reports/monthly?${queryParams.toString()}`,
    });
  }

  // Feedback endpoints
  async submitFeedback(feedback: FeedbackSubmitData): Promise<ApiResponse<FeedbackResponse>> {
    return this.request({
      method: 'POST',
      url: '/training/feedback',
      data: feedback,
    });
  }

  // Notification endpoints
  async getNotifications(): Promise<ApiResponse<NotificationsResponse>> {
    return this.request({
      method: 'GET',
      url: '/training/notifications',
    });
  }

  async markNotificationAsRead(id: string): Promise<ApiResponse<{message: string}>> {
    return this.request({
      method: 'POST',
      url: `/training/notifications/${id}/read`,
    });
  }

  async markAllNotificationsAsRead(): Promise<ApiResponse<{message: string}>> {
    return this.request({
      method: 'POST',
      url: '/training/notifications/read-all',
    });
  }

  // Independent Training endpoints
  async createIndependentTraining(
    training: IndependentTrainingCreate
  ): Promise<ApiResponse<IndependentTraining>> {
    return this.request({
      method: 'POST',
      url: '/independent-training',
      data: training,
    });
  }

  async getIndependentTrainingSessions(params: {
    skip?: number;
    limit?: number;
    startDate?: string;
    endDate?: string;
  } = {}): Promise<ApiResponse<IndependentTrainingResponse>> {
    const queryParams = new URLSearchParams();
    if (params.skip) queryParams.append('skip', params.skip.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.startDate) queryParams.append('start_date', params.startDate);
    if (params.endDate) queryParams.append('end_date', params.endDate);
    
    return this.request({
      method: 'GET',
      url: `/independent-training?${queryParams.toString()}`,
    });
  }

  async getIndependentTraining(id: string): Promise<ApiResponse<IndependentTraining>> {
    return this.request({
      method: 'GET',
      url: `/independent-training/${id}`,
    });
  }

  async updateIndependentTraining(
    id: string,
    training: IndependentTrainingCreate
  ): Promise<ApiResponse<IndependentTraining>> {
    return this.request({
      method: 'PUT',
      url: `/independent-training/${id}`,
      data: training,
    });
  }

  async deleteIndependentTraining(id: string): Promise<ApiResponse<{message: string}>> {
    return this.request({
      method: 'DELETE',
      url: `/independent-training/${id}`,
    });
  }

  // Equipment-related methods
  async getEquipment(): Promise<ApiResponse<Equipment[]>> {
    return this.request({
      method: 'GET',
      url: '/equipment',
    });
  }

  async getEquipmentById(id: string): Promise<ApiResponse<Equipment>> {
    return this.request({
      method: 'GET',
      url: `/equipment/${id}`,
    });
  }

  async checkEquipmentAvailability(
    request: CheckEquipmentAvailabilityRequest
  ): Promise<ApiResponse<EquipmentAvailabilityResponse>> {
    return this.request({
      method: 'POST',
      url: '/equipment/check-availability',
      data: request,
    });
  }

  async reserveEquipment(
    request: ReserveEquipmentRequest
  ): Promise<ApiResponse<ReserveEquipmentResponse>> {
    return this.request({
      method: 'POST',
      url: '/equipment/reserve',
      data: request,
    });
  }

  async releaseEquipment(sessionId: string): Promise<ApiResponse<{ success: boolean }>> {
    return this.request({
      method: 'DELETE',
      url: `/equipment/release/${sessionId}`,
    });
  }

  async sendEmail(emailData: EmailRequestData): Promise<ApiResponse<{ message_id: string }>> {
    return this.request<{ message_id: string }>({
      method: 'POST',
      url: '/email/send',
      data: emailData,
    });
  }

  async sendTestEmail(testData?: TestEmailRequestData): Promise<ApiResponse<{ message_id: string }>> {
    return this.request<{ message_id: string }>({
      method: 'POST',
      url: '/email/send-test',
      data: testData || {},
    });
  }
}

// Create React hook for using the API client
export function useApiClient() {
  const [client] = useState<ApiClient>(() => new ApiClient());
  
  useEffect(() => {
    // Load token from localStorage on component mount
    const token = localStorage.getItem('auth_token');
    if (token) {
      client.setToken(token);
    }
  }, [client]);
  
  return client;
}

// Create singleton instance
const API = new ApiClient();
export { ReportFormat };
export default API; 