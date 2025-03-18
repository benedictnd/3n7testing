"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";
import API from "@/lib/api-client";

export default function TrainingSessionsPage() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [coaches, setCoaches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [date, setDate] = useState<Date | undefined>(new Date());
  const [selectedCoachId, setSelectedCoachId] = useState<string>("");
  const [selectedSessionId, setSelectedSessionId] = useState<string>("");
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [isAssigning, setIsAssigning] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check if user is authenticated
        const token = localStorage.getItem("auth_token");
        if (!token) {
          router.push("/login");
          return;
        }

        API.setToken(token);

        // Fetch training sessions
        const sessionResponse = await API.getTrainingSessions({
          startDate: format(new Date(), "yyyy-MM-dd"),
        });

        if (!sessionResponse.success) {
          throw new Error(sessionResponse.error || "Failed to fetch training sessions");
        }

        setSessions(sessionResponse.data.sessions || []);

        // Fetch coaches
        const userResponse = await API.getUsers({ role: "coach" });
        if (!userResponse.success) {
          throw new Error(userResponse.error || "Failed to fetch coaches");
        }

        setCoaches(userResponse.data.users || []);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to load data. Please refresh or try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router]);

  const handleAssignCoach = async () => {
    if (!selectedSessionId || !selectedCoachId) {
      return;
    }

    setIsAssigning(true);
    try {
      const response = await API.updateTrainingSession(selectedSessionId, {
        coach_id: selectedCoachId
      });

      if (response.success) {
        // Update the local state with the new coach assignment
        setSessions(sessions.map(session => {
          if (session.id === selectedSessionId) {
            const assignedCoach = coaches.find(coach => coach.id === selectedCoachId);
            return {
              ...session,
              coach_id: selectedCoachId,
              coach_name: assignedCoach ? assignedCoach.name : "Unknown Coach"
            };
          }
          return session;
        }));

        setShowAssignModal(false);
      } else {
        setError(response.error || "Failed to assign coach");
      }
    } catch (err) {
      console.error("Error assigning coach:", err);
      setError("An error occurred while assigning the coach");
    } finally {
      setIsAssigning(false);
    }
  };

  const handleDateChange = async (newDate: Date | undefined) => {
    if (!newDate) return;
    
    setDate(newDate);
    setLoading(true);
    
    try {
      const sessionResponse = await API.getTrainingSessions({
        startDate: format(newDate, "yyyy-MM-dd"),
      });

      if (sessionResponse.success) {
        setSessions(sessionResponse.data.sessions || []);
      } else {
        setError(sessionResponse.error || "Failed to fetch training sessions for selected date");
      }
    } catch (err) {
      console.error("Error fetching sessions for date:", err);
      setError("Failed to load sessions for the selected date");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-4 px-4 md:px-6 lg:px-8">
      <Head>
        <title>Training Sessions | 3&7 Training Platform</title>
      </Head>

      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Training Sessions</h1>
        <Button onClick={() => router.push("/dashboard")}>
          Back to Dashboard
        </Button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-md">
          {error}
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <Card className="md:w-64">
          <CardHeader>
            <CardTitle className="text-lg">Select Date</CardTitle>
          </CardHeader>
          <CardContent>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-start text-left font-normal"
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {date ? format(date, "PPP") : <span>Pick a date</span>}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={date}
                  onSelect={handleDateChange}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </CardContent>
        </Card>

        <div className="flex-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Training Sessions</CardTitle>
            </CardHeader>
            <CardContent>
              {sessions.length > 0 ? (
                <div className="space-y-4">
                  {sessions.map((session) => (
                    <div key={session.id} className="border p-4 rounded-md">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-medium">{session.title}</h3>
                          <p className="text-sm text-gray-500">
                            {format(new Date(session.date), "PPP")} | {format(new Date(session.start_time), "h:mm a")} - {format(new Date(session.end_time), "h:mm a")}
                          </p>
                          <p className="text-sm text-gray-500">
                            Location: {session.location}
                          </p>
                          <p className="text-sm text-gray-500">
                            Coach: <span className="font-medium">{session.coach_name || "Unassigned"}</span>
                          </p>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedSessionId(session.id);
                            setSelectedCoachId(session.coach_id || "");
                            setShowAssignModal(true);
                          }}
                        >
                          Assign Coach
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center p-8 border rounded-md bg-gray-50">
                  <p>No training sessions found for the selected date.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {showAssignModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Assign Coach</h2>
            
            <div className="mb-4">
              <Label htmlFor="coach-select">Select Coach</Label>
              <Select
                value={selectedCoachId}
                onValueChange={setSelectedCoachId}
              >
                <SelectTrigger id="coach-select" className="w-full">
                  <SelectValue placeholder="Select a coach" />
                </SelectTrigger>
                <SelectContent>
                  {coaches.map((coach) => (
                    <SelectItem key={coach.id} value={coach.id}>
                      {coach.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex justify-end space-x-2">
              <Button
                variant="outline"
                onClick={() => setShowAssignModal(false)}
                disabled={isAssigning}
              >
                Cancel
              </Button>
              <Button
                onClick={handleAssignCoach}
                disabled={!selectedCoachId || isAssigning}
              >
                {isAssigning ? "Assigning..." : "Assign"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 