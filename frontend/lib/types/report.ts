import { ReportFormat, IndependentTrainingType } from './api';

export interface TrainingSessionSummary {
  id: string;
  title: string;
  date: string;
  type: string;
  attendees: Array<{
    id: string;
    name: string;
    check_in_time: string;
  }>;
  total_attendees: number;
  average_rating?: number;
  feedback_count?: number;
  coach_name: string;
  duration_minutes: number;
  attendees_count: number;
  feedback: {
    training_quality_avg: number;
    expectations_avg: number;
    body_condition_avg: number;
    intensity_avg: number;
    feedback_count: number;
  };
}

export interface AttendanceAthleteSummary {
  athlete_id: string;
  athlete_name: string;
  sessions_attended: number;
  sessions_missed: number;
  attendance_rate: number;
}

export interface SessionAttendance {
  id: string;
  date: string;
  type: string;
  coach_name: string;
  attended: boolean;
  check_in_time?: string;
}

export interface AthleteAttendanceReport {
  athlete_id: string;
  athlete_name: string;
  attended_count: number;
  total_count: number;
  attendance_rate: number;
  sessions: SessionAttendance[];
}

export interface TeamAttendanceReport {
  total_athletes: number;
  avg_attendance_rate: number;
  athletes: AttendanceAthleteSummary[];
}

export interface FeedbackDetail {
  id: string;
  athlete_id: string;
  athlete_name: string;
  training_quality: number;
  expectations: number;
  body_condition: number;
  intensity: number;
  notes?: string;
  created_at: string;
}

export interface SessionFeedbackSummary {
  session_id: string;
  date: string;
  type: string;
  coach_name: string;
  feedback_count: number;
  training_quality_avg: number;
  expectations_avg: number;
  body_condition_avg: number;
  intensity_avg: number;
}

export interface TrainingReportData {
  title: string;
  generated_at: string;
  date_range: string;
  summary: {
    total_sessions: number;
    total_attendees: number;
    avg_attendees_per_session: number;
    avg_training_quality?: number;
    avg_expectations?: number;
  };
  data: TrainingSessionSummary[];
}

export interface AttendanceReportData {
  title: string;
  generated_at: string;
  date_range: string;
  summary: {
    total_athletes?: number;
    avg_attendance_rate?: number;
  };
  data: AthleteAttendanceReport[] | TeamAttendanceReport[];
}

export interface FeedbackReportData {
  title: string;
  generated_at: string;
  date_range: string;
  summary: {
    total_feedback?: number;
    feedback_count?: number;
    avg_training_quality?: number;
    training_quality_avg?: number;
    avg_expectations?: number;
    expectations_avg?: number;
    avg_body_condition?: number;
    body_condition_avg?: number;
    avg_intensity?: number;
    intensity_avg?: number;
  };
  data: FeedbackDetail[] | SessionFeedbackSummary[];
}

export interface ReportFormValues {
  dateRange: [Date, Date];
  format: ReportFormat;
  athleteId?: string;
  sessionId?: string;
}

export interface IndependentTrainingSummary {
  id: string;
  date: string;
  type: IndependentTrainingType;
  start_time: string;
  end_time: string;
  location: string;
  intensity: number;
  body_condition: number;
}

export interface MonthlyReportData {
  title: string;
  generated_at: string;
  date_range: string;
  summary: {
    total_sessions: number;
    total_attendees: number;
    avg_attendees_per_session: number;
    avg_training_quality?: number;
    avg_expectations?: number;
    independent_training_count: number;
    independent_training_types: Record<IndependentTrainingType, number>;
  };
  data: TrainingSessionSummary[];
  independent_training: IndependentTrainingSummary[];
} 