// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  statusCode?: number;
}

// Report Types
export enum ReportFormat {
  JSON = 'json',
  PDF = 'pdf',
  PPT = 'ppt'
}

// User Types
export interface UserRole {
  id: string;
  name: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  // Optional fields based on role
  sports?: string[];
  experience_level?: string;
  achievements?: string[];
  specializations?: string[];
  certifications?: string[];
  years_experience?: number;
  organization?: string;
  position?: string;
  interests?: string[];
  profession?: string;
  qualifications?: string[];
  services?: string[];
  // Stats
  attendance_rate?: number;
  sessions_attended?: number;
  total_sessions?: number;
  athletes_count?: number;
  teams_count?: number;
  independent_training_count?: number;
  notifications?: Notification[];
}

// Session Types
export interface TrainingPhase {
  name: string;
  description: string;
  duration_minutes: number;
  exercises: string[];
}

export interface TrainingSession {
  id: string;
  title: string;
  type: string;
  date: string;
  start_time: string;
  end_time: string;
  location: string;
  description?: string;
  max_participants?: number;
  phases: TrainingPhase[];
  equipment_needed?: string[];
  notes?: string;
  coach_id: string;
  coach_name: string;
  created_at: string;
  updated_at: string;
}

export interface TrainingSessionDetail extends TrainingSession {
  attendees: AttendanceRecord[];
  feedback?: FeedbackSummary;
}

export interface TrainingSessionsResponse {
  sessions: TrainingSession[];
  total: number;
  page: number;
  size: number;
  upcoming?: TrainingSession[];
  recent?: TrainingSession[];
  next_session?: TrainingSession;
  pending_feedback?: TrainingSession[];
  recent_feedback?: FeedbackSummary[];
  recent_days?: number;
  change?: {
    upcoming: number;
  };
}

// Attendance Types
export interface AttendanceRecord {
  id: string;
  session_id: string;
  athlete_id: string;
  athlete_name: string;
  check_in_time: string;
}

// Feedback Types
export interface FeedbackSummary {
  feedback_count: number;
  average_rating: number;
  sentiment?: string;
}

export interface FeedbackDetail {
  id: string;
  training_session_id: string;
  athlete_id: string;
  training_quality: number;
  expectations: number;
  body_condition: number;
  intensity: number;
  notes?: string;
  created_at: string;
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

// Notification Types
export interface Notification {
  id: string;
  title: string;
  message: string;
  notification_type: string;
  recipient_id: string;
  sender_id?: string;
  related_id?: string;
  link?: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationsResponse {
  notifications: Notification[];
  unread_count: number;
}

// Report Types
export interface ReportRequest {
  start_date: string;
  end_date: string;
  format?: ReportFormat;
  athlete_id?: string;
  session_id?: string;
}

export interface ReportExportRequest {
  title: string;
  data: any;
  format: ReportFormat;
}

export interface ReportResponse {
  title: string;
  generated_at: string;
  date_range: string;
  summary: Record<string, any>;
  data: any[];
}

// Independent Training Types
export enum IndependentTrainingType {
  STRENGTH = "strength",
  CONDITIONING = "conditioning",
  RECOVERY = "recovery",
  SKILLS = "skills",
  CARDIO = "cardio",
  OTHER = "other"
}

export interface IndependentTraining {
  id: string;
  athlete_id: string;
  athlete_name: string;
  title: string;
  type: IndependentTrainingType;
  date: string;
  start_time: string;
  end_time: string;
  location: string;
  description?: string;
  phases: TrainingPhase[];
  equipment_needed?: string[];
  notes?: string;
  intensity: number;
  body_condition: number;
  coach_notified: boolean;
  created_at: string;
  updated_at: string;
}

export interface IndependentTrainingCreate {
  title: string;
  type: IndependentTrainingType;
  date: string;
  start_time: string;
  end_time: string;
  location: string;
  description?: string;
  phases: TrainingPhase[];
  equipment_needed?: string[];
  notes?: string;
  intensity: number;
  body_condition: number;
}

export interface IndependentTrainingResponse {
  sessions: IndependentTraining[];
  total: number;
  page: number;
  size: number;
} 