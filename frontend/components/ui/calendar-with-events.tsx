import * as React from "react";
import { format, isSameDay, isSameMonth } from "date-fns";
import { Calendar as CalendarIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import { Calendar, CalendarProps } from "@/components/ui/calendar";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";

export interface CalendarEvent {
  id: string;
  title: string;
  date: Date;
  startTime: string;
  endTime: string;
  type: "GROUP" | "INDEPENDENT" | "OTHER";
  hasConflict?: boolean;
  color?: string;
  metadata?: Record<string, any>;
}

export interface CalendarWithEventsProps extends Omit<CalendarProps, "selected" | "onSelect"> {
  events: CalendarEvent[];
  onEventClick?: (event: CalendarEvent) => void;
  onDateSelect?: (date: Date) => void;
  selectedDate?: Date;
}

export function CalendarWithEvents({
  events,
  className,
  onEventClick,
  onDateSelect,
  selectedDate,
  ...props
}: CalendarWithEventsProps) {
  // Group events by date for easier rendering
  const eventsByDate = React.useMemo(() => {
    const grouped: Record<string, CalendarEvent[]> = {};
    
    events.forEach(event => {
      const dateKey = format(event.date, "yyyy-MM-dd");
      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      grouped[dateKey].push(event);
    });
    
    return grouped;
  }, [events]);

  // Get event colors based on type
  const getEventColor = (type: CalendarEvent["type"], hasConflict?: boolean): string => {
    if (hasConflict) return "bg-red-500 hover:bg-red-600";
    
    switch (type) {
      case "GROUP":
        return "bg-blue-500 hover:bg-blue-600";
      case "INDEPENDENT":
        return "bg-green-500 hover:bg-green-600";
      default:
        return "bg-gray-500 hover:bg-gray-600";
    }
  };

  // Custom day renderer to show events
  const renderDay = (day: Date, events: CalendarEvent[]) => {
    const formattedDay = format(day, "d");
    const isToday = isSameDay(day, new Date());
    const isSelected = selectedDate ? isSameDay(day, selectedDate) : false;
    
    return (
      <div 
        className={cn(
          "relative h-10 w-10 p-0 font-normal flex items-center justify-center rounded-full",
          isToday && "bg-accent text-accent-foreground",
          isSelected && "bg-primary text-primary-foreground",
          "hover:bg-muted cursor-pointer"
        )}
        onClick={() => onDateSelect?.(day)}
      >
        <span>{formattedDay}</span>
        
        {events.length > 0 && (
          <div className="absolute -bottom-1 flex gap-0.5 justify-center">
            {events.length <= 3 ? (
              events.map((event, i) => (
                <div 
                  key={event.id}
                  className={cn(
                    "h-1.5 w-1.5 rounded-full",
                    getEventColor(event.type, event.hasConflict)
                  )}
                />
              ))
            ) : (
              <>
                <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                <div className="h-1.5 w-1.5 rounded-full bg-green-500" />
                <Badge 
                  variant="outline" 
                  className="h-3 min-w-3 text-[8px] flex items-center justify-center p-0 rounded-full"
                >
                  {events.length}
                </Badge>
              </>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={cn("space-y-4", className)}>
      <Calendar
        {...props}
        mode="single"
        selected={selectedDate}
        onSelect={onDateSelect}
        components={{
          Day: ({ date, ...dayProps }) => {
            // Skip rendering days from other months
            if (!isSameMonth(date, props.month || new Date())) {
              return <div className="h-10 w-10" />;
            }
            
            const dateKey = format(date, "yyyy-MM-dd");
            const dayEvents = eventsByDate[dateKey] || [];
            
            return (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div>
                      {renderDay(date, dayEvents)}
                    </div>
                  </TooltipTrigger>
                  {dayEvents.length > 0 && (
                    <TooltipContent className="p-0">
                      <div className="p-2 space-y-1 max-w-[250px]">
                        <p className="font-medium">{format(date, "EEEE, MMMM d")}</p>
                        <div className="space-y-1">
                          {dayEvents.map(event => (
                            <div 
                              key={event.id}
                              className={cn(
                                "text-xs px-2 py-1 rounded cursor-pointer",
                                getEventColor(event.type, event.hasConflict)
                              )}
                              onClick={(e) => {
                                e.stopPropagation();
                                onEventClick?.(event);
                              }}
                            >
                              <div className="font-medium text-white">{event.title}</div>
                              <div className="text-white/80">{`${event.startTime} - ${event.endTime}`}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </TooltipContent>
                  )}
                </Tooltip>
              </TooltipProvider>
            );
          },
        }}
      />
    </div>
  );
}