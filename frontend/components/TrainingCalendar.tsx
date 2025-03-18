import React, { useState, useEffect } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, getDay, addMonths, subMonths } from 'date-fns';
import { TrainingProgram } from '../lib/types/training';

interface TrainingSession {
  id: string;
  type: 'morning' | 'afternoon' | 'night';
  startTime: string;
  endTime: string;
  title: string;
}

interface DayWithSessions {
  date: Date;
  sessions: TrainingSession[];
}

interface TrainingCalendarProps {
  programs: TrainingProgram[];
}

const TrainingCalendar: React.FC<TrainingCalendarProps> = ({ programs }) => {
  const [currentMonth, setCurrentMonth] = useState<Date>(new Date());
  const [calendarDays, setCalendarDays] = useState<DayWithSessions[]>([]);
  const [tooltipDay, setTooltipDay] = useState<number | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    // Generate calendar days for the current month
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(currentMonth);
    const daysInMonth = eachDayOfInterval({ start: monthStart, end: monthEnd });
    
    // Convert training programs to sessions mapped to days
    const daysWithSessions: DayWithSessions[] = daysInMonth.map(date => {
      // Find programs scheduled for this date
      const sessionsForDay = programs
        .filter(program => {
          const programDate = new Date(program.date);
          return programDate.getDate() === date.getDate() && 
                 programDate.getMonth() === date.getMonth() && 
                 programDate.getFullYear() === date.getFullYear();
        })
        .map(program => {
          // Determine session type based on start time
          const startHour = parseInt(program.startTime.split(':')[0]);
          let type: 'morning' | 'afternoon' | 'night' = 'morning';
          
          if (startHour >= 12 && startHour < 17) {
            type = 'afternoon';
          } else if (startHour >= 17) {
            type = 'night';
          }
          
          // Calculate end time based on start time and total duration
          const [hours, minutes] = program.startTime.split(':').map(Number);
          const startDate = new Date();
          startDate.setHours(hours, minutes);
          
          const endDate = new Date(startDate);
          endDate.setMinutes(endDate.getMinutes() + program.totalDuration);
          
          const endTime = `${endDate.getHours().toString().padStart(2, '0')}:${endDate.getMinutes().toString().padStart(2, '0')}`;
          
          return {
            id: program.id,
            type,
            startTime: program.startTime,
            endTime,
            title: program.title
          };
        });
      
      return {
        date,
        sessions: sessionsForDay
      };
    });
    
    setCalendarDays(daysWithSessions);
  }, [currentMonth, programs]);

  const handlePreviousMonth = () => {
    setCurrentMonth(subMonths(currentMonth, 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth(addMonths(currentMonth, 1));
  };

  const handleDayMouseEnter = (dayIndex: number, e: React.MouseEvent) => {
    setTooltipDay(dayIndex);
    setTooltipPosition({ x: e.clientX, y: e.clientY });
  };

  const handleDayMouseLeave = () => {
    setTooltipDay(null);
  };

  // Generate the days of the week header
  const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  // Calculate blank days at the start of the month
  const monthStart = startOfMonth(currentMonth);
  const startDay = getDay(monthStart); // 0 = Sunday, 1 = Monday, etc.

  // Get session type color
  const getSessionTypeColor = (type: 'morning' | 'afternoon' | 'night') => {
    switch (type) {
      case 'morning':
        return 'bg-blue-500';
      case 'afternoon':
        return 'bg-yellow-500';
      case 'night':
        return 'bg-purple-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">{format(currentMonth, 'MMMM yyyy')}</h2>
        <div className="flex gap-2">
          <button 
            onClick={handlePreviousMonth}
            className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
            aria-label="Previous month"
          >
            &lt;
          </button>
          <button 
            onClick={handleNextMonth}
            className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
            aria-label="Next month"
          >
            &gt;
          </button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-1">
        {/* Days of the week headers */}
        {daysOfWeek.map((day) => (
          <div key={day} className="text-center py-2 font-medium text-gray-600">
            {day}
          </div>
        ))}
        
        {/* Calendar grid with days */}
        {[...Array(startDay)].map((_, index) => (
          <div key={`empty-${index}`} className="h-24 border rounded bg-gray-50" />
        ))}
        
        {calendarDays.map((day, index) => {
          const hasSessions = day.sessions.length > 0;
          
          return (
            <div
              key={`day-${index}`}
              className={`h-24 border rounded p-1 relative ${
                hasSessions ? 'hover:bg-gray-50 cursor-pointer' : ''
              }`}
              tabIndex={hasSessions ? 0 : -1}
              onMouseEnter={hasSessions ? (e) => handleDayMouseEnter(index, e) : undefined}
              onMouseLeave={hasSessions ? handleDayMouseLeave : undefined}
              onFocus={hasSessions ? (e) => handleDayMouseEnter(index, e as any) : undefined}
              onBlur={hasSessions ? handleDayMouseLeave : undefined}
              aria-label={hasSessions ? `${format(day.date, 'd MMMM')} - ${day.sessions.length} training sessions` : undefined}
            >
              <div className="text-sm font-medium">{format(day.date, 'd')}</div>
              
              {/* Session indicator dots */}
              {hasSessions && (
                <div className="flex gap-1 mt-1">
                  {day.sessions.slice(0, 3).map((session, sessionIndex) => (
                    <div 
                      key={`session-${sessionIndex}`}
                      className={`h-2 w-2 rounded-full ${getSessionTypeColor(session.type)}`}
                      aria-hidden="true"
                    />
                  ))}
                  {day.sessions.length > 3 && (
                    <div className="text-xs font-medium">+{day.sessions.length - 3}</div>
                  )}
                </div>
              )}
              
              {/* Tooltip */}
              {tooltipDay === index && (
                <div 
                  className="absolute z-10 p-3 bg-white shadow-lg rounded-lg border w-60 text-sm"
                  style={{
                    top: '100%',
                    left: '50%',
                    transform: 'translateX(-50%)'
                  }}
                >
                  <div className="font-medium mb-2">{format(day.date, 'EEEE, MMMM d')}</div>
                  {day.sessions.map((session, sessionIndex) => (
                    <div key={`tooltip-session-${sessionIndex}`} className="mb-2 last:mb-0">
                      <div className="flex items-center">
                        <span 
                          className={`inline-block h-3 w-3 rounded-full mr-2 ${getSessionTypeColor(session.type)}`}
                        />
                        <span className="font-medium capitalize">{session.type} Session:</span>
                      </div>
                      <div className="ml-5">
                        <div>{session.title}</div>
                        <div className="text-gray-600">
                          {session.startTime}–{session.endTime}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
        
        {/* Fill remaining blank days to complete the grid */}
        {[...Array(42 - (startDay + calendarDays.length))].map((_, index) => (
          <div key={`end-empty-${index}`} className="h-24 border rounded bg-gray-50" />
        ))}
      </div>

      <div className="mt-4 flex items-center gap-4">
        <div className="text-sm font-medium">Legend:</div>
        <div className="flex items-center">
          <span className="inline-block h-3 w-3 rounded-full bg-blue-500 mr-1"></span>
          <span className="text-sm">Morning</span>
        </div>
        <div className="flex items-center">
          <span className="inline-block h-3 w-3 rounded-full bg-yellow-500 mr-1"></span>
          <span className="text-sm">Afternoon</span>
        </div>
        <div className="flex items-center">
          <span className="inline-block h-3 w-3 rounded-full bg-purple-500 mr-1"></span>
          <span className="text-sm">Evening</span>
        </div>
      </div>
    </div>
  );
};

export default TrainingCalendar; 