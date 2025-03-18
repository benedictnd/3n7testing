export interface TrainingPhase {
  name: string;
  duration: number; // in minutes
  description: string;
  completed: boolean;
}

export interface TrainingProgram {
  id: string;
  title: string;
  date: string; // ISO format date string
  startTime: string; // Format: "HH:MM" (24-hour)
  totalDuration: number; // Duration in minutes
  description?: string;
  location?: string;
  status: 'scheduled' | 'completed' | 'cancelled';
  coachId?: string;
  athleteIds: string[];
  type: 'integrated' | 'independent';
}

export interface TrainingFeedback {
  id: string;
  programId: string;
  userId: string;
  userType: 'coach' | 'athlete';
  rating: number; // 1-5 scale
  comments: string;
  createdAt: string; // ISO date string
}

export interface TrainingAttendance {
  programId: string;
  athleteId: string;
  status: 'present' | 'absent' | 'late';
  notes?: string;
} 