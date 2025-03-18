import { parseISO, isWithinInterval, areIntervalsOverlapping } from 'date-fns';
import { 
  Equipment, 
  EquipmentWithQuantity, 
  EquipmentSession, 
  EquipmentConflict,
  EquipmentCategory
} from '../types/equipment';

/**
 * Checks if there are any equipment conflicts for the given equipment needs
 * @param equipmentNeeded Equipment items needed with quantities
 * @param startTime Session start time
 * @param endTime Session end time
 * @param availableEquipment List of all available equipment with their sessions
 * @param currentSessionId Optional current session ID to exclude from conflict check (for updates)
 * @returns Array of conflicts if any exist
 */
export const detectEquipmentConflicts = (
  equipmentNeeded: EquipmentWithQuantity[],
  startTime: string,
  endTime: string,
  availableEquipment: Equipment[],
  currentSessionId?: string
): EquipmentConflict[] => {
  const conflicts: EquipmentConflict[] = [];
  const sessionStart = parseISO(startTime);
  const sessionEnd = parseISO(endTime);

  // Check each requested equipment item for conflicts
  equipmentNeeded.forEach(needed => {
    const equipment = availableEquipment.find(e => e.id === needed.equipmentId);
    
    if (!equipment) {
      // Equipment not found - add as conflict
      conflicts.push({
        equipmentId: needed.equipmentId,
        equipmentName: needed.name,
        conflictingSessions: [],
        availableCount: 0,
        requestedCount: needed.quantity,
        timeRange: { start: startTime, end: endTime }
      });
      return;
    }

    // Find overlapping sessions
    const overlappingSessions = (equipment.sessions || [])
      .filter(session => {
        // Skip current session when updating
        if (currentSessionId && session.sessionId === currentSessionId) {
          return false;
        }

        const sessionStartTime = parseISO(session.startTime);
        const sessionEndTime = parseISO(session.endTime);

        return areIntervalsOverlapping(
          { start: sessionStart, end: sessionEnd },
          { start: sessionStartTime, end: sessionEndTime }
        );
      });

    // Calculate total equipment in use during the time period
    const totalInUse = overlappingSessions.reduce(
      (sum, session) => sum + session.quantity, 
      0
    );

    // Check if there's enough equipment available
    const availableDuringPeriod = equipment.totalCount - totalInUse;
    
    if (availableDuringPeriod < needed.quantity) {
      conflicts.push({
        equipmentId: equipment.id,
        equipmentName: equipment.name,
        conflictingSessions: overlappingSessions,
        availableCount: availableDuringPeriod,
        requestedCount: needed.quantity,
        timeRange: { start: startTime, end: endTime }
      });
    }
  });

  return conflicts;
};

/**
 * Formats equipment list for display
 * @param equipment List of equipment with quantities
 * @returns Formatted string of equipment
 */
export const formatEquipmentList = (equipment: EquipmentWithQuantity[]): string => {
  if (!equipment || equipment.length === 0) return 'None';
  
  return equipment
    .map(item => `${item.name} (${item.quantity})`)
    .join(', ');
};

/**
 * Groups equipment by category
 * @param equipment List of equipment with quantities
 * @returns Equipment grouped by category
 */
export const groupEquipmentByCategory = (
  equipment: EquipmentWithQuantity[]
): Record<EquipmentCategory, EquipmentWithQuantity[]> => {
  const grouped = Object.values(EquipmentCategory).reduce((acc, category) => {
    acc[category] = [];
    return acc;
  }, {} as Record<EquipmentCategory, EquipmentWithQuantity[]>);

  equipment.forEach(item => {
    grouped[item.category].push(item);
  });

  return grouped;
};

/**
 * Calculates equipment availability during a specific time period
 * @param equipment Equipment item
 * @param startTime Period start time
 * @param endTime Period end time
 * @param currentSessionId Optional current session ID to exclude
 * @returns Number of available items during the period
 */
export const calculateEquipmentAvailability = (
  equipment: Equipment,
  startTime: string,
  endTime: string,
  currentSessionId?: string
): number => {
  const sessionStart = parseISO(startTime);
  const sessionEnd = parseISO(endTime);
  
  // Find overlapping sessions
  const overlappingSessions = (equipment.sessions || [])
    .filter(session => {
      // Skip current session when updating
      if (currentSessionId && session.sessionId === currentSessionId) {
        return false;
      }

      const sessionStartTime = parseISO(session.startTime);
      const sessionEndTime = parseISO(session.endTime);

      return areIntervalsOverlapping(
        { start: sessionStart, end: sessionEnd },
        { start: sessionStartTime, end: sessionEndTime }
      );
    });

  // Calculate total equipment in use during the time period
  const totalInUse = overlappingSessions.reduce(
    (sum, session) => sum + session.quantity, 
    0
  );

  return equipment.totalCount - totalInUse;
}; 