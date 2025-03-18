export interface Equipment {
  id: string;
  name: string;
  totalCount: number;
  availableCount: number;
  category: EquipmentCategory;
  sessions?: EquipmentSession[];
}

export enum EquipmentCategory {
  WEIGHTS = "WEIGHTS",
  CARDIO = "CARDIO",
  RECOVERY = "RECOVERY",
  SPORTS_SPECIFIC = "SPORTS_SPECIFIC",
  MOBILITY = "MOBILITY",
  OTHER = "OTHER"
}

export interface EquipmentWithQuantity {
  equipmentId: string;
  name: string;
  quantity: number;
  category: EquipmentCategory;
}

export interface EquipmentSession {
  sessionId: string;
  sessionType: "GROUP" | "INDEPENDENT";
  startTime: string;
  endTime: string;
  quantity: number;
  athleteId?: string;
  athleteName?: string;
}

export interface EquipmentReservation {
  equipmentId: string;
  sessionId: string;
  quantity: number;
  startTime: string;
  endTime: string;
  status: ReservationStatus;
  createdAt: string;
}

export enum ReservationStatus {
  PENDING = "PENDING",
  CONFIRMED = "CONFIRMED",
  CANCELLED = "CANCELLED",
  COMPLETED = "COMPLETED"
}

export interface EquipmentConflict {
  equipmentId: string;
  equipmentName: string;
  conflictingSessions: EquipmentSession[];
  availableCount: number;
  requestedCount: number;
  timeRange: {
    start: string;
    end: string;
  };
}

// Response type for equipment availability check
export interface EquipmentAvailabilityResponse {
  available: boolean;
  conflicts: EquipmentConflict[];
}

// Request type for checking equipment availability
export interface CheckEquipmentAvailabilityRequest {
  equipmentNeeded: EquipmentWithQuantity[];
  startTime: string;
  endTime: string;
  sessionId?: string; // Optional for updates to exclude current session
}

// Request type for reserving equipment
export interface ReserveEquipmentRequest {
  sessionId: string;
  sessionType: "GROUP" | "INDEPENDENT";
  equipmentNeeded: EquipmentWithQuantity[];
  startTime: string;
  endTime: string;
  athleteId?: string;
}

// Response type for equipment reservation
export interface ReserveEquipmentResponse {
  success: boolean;
  reservations: EquipmentReservation[];
  conflicts?: EquipmentConflict[];
} 