"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { ApiClient, useApiClient } from "../lib/api-client";
import { User, TrainingSessionsResponse, Notification, TrainingSession } from "../lib/types/api";

// Type-safe dashboard component props
interface DashboardProps {
  userData: User;
  sessionData: TrainingSessionsResponse;
}

const CoachDashboard = ({ userData, sessionData }: DashboardProps) => (
  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Upcoming Sessions</CardTitle>
        <CardDescription>You have {sessionData?.upcoming?.length || 0} upcoming sessions</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{sessionData?.upcoming?.length || 0}</div>
        <p className="text-xs text-muted-foreground">
          +{sessionData?.change?.upcoming || 0} from last week
        </p>
        <Button variant="outline" size="sm" className="mt-4 w-full">
          View Schedule
        </Button>
      </CardContent>
    </Card>
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Athletes</CardTitle>
        <CardDescription>Athletes managed by you</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{userData?.athletes_count || 0}</div>
        <p className="text-xs text-muted-foreground">Across {userData?.teams_count || 0} teams</p>
        <Button variant="outline" size="sm" className="mt-4 w-full">
          Manage Athletes
        </Button>
      </CardContent>
    </Card>
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Recent Feedback</CardTitle>
        <CardDescription>Feedback from recent sessions</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{sessionData?.recent_feedback?.length || 0}</div>
        <p className="text-xs text-muted-foreground">
          For past {sessionData?.recent_days || 7} days
        </p>
        <Button variant="outline" size="sm" className="mt-4 w-full">
          View Feedback
        </Button>
      </CardContent>
    </Card>
  </div>
);

const AthleteDashboard = ({ userData, sessionData }: DashboardProps) => {
  const router = useRouter();

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Upcoming Sessions</CardTitle>
          <CardDescription>Your upcoming training sessions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{sessionData?.upcoming?.length || 0}</div>
          <p className="text-xs text-muted-foreground">
            Next session: {sessionData?.next_session?.date || "None scheduled"}
          </p>
          <Button variant="outline" size="sm" className="mt-4 w-full">
            View Schedule
          </Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Your Attendance</CardTitle>
          <CardDescription>Session attendance rate</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{userData?.attendance_rate || 0}%</div>
          <p className="text-xs text-muted-foreground">
            {userData?.sessions_attended || 0} of {userData?.total_sessions || 0} sessions
          </p>
          <Button variant="outline" size="sm" className="mt-4 w-full">
            View Details
          </Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Independent Training</CardTitle>
          <CardDescription>Your self-directed training sessions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{userData?.independent_training_count || 0}</div>
          <p className="text-xs text-muted-foreground">
            Last 30 days
          </p>
          <Button 
            variant="outline" 
            size="sm" 
            className="mt-4 w-full"
            onClick={() => router.push('/independent-training')}
          >
            Log Training
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default function Dashboard() {
  const [userData, setUserData] = useState<User | null>(null);
  const [sessionData, setSessionData] = useState<TrainingSessionsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const router = useRouter();
  const api = useApiClient();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check if user is authenticated
        const token = localStorage.getItem("auth_token");
        if (!token) {
          router.push("/login");
          return;
        }

        api.setToken(token);

        // Fetch user data
        const userResponse = await api.getCurrentUser();
        if (!userResponse.success) {
          throw new Error(userResponse.error || "Failed to fetch user data");
        }

        // Ensure data exists before setting state
        if (userResponse.data) {
          setUserData(userResponse.data);
        }

        // Fetch training sessions data
        const sessionResponse = await api.getTrainingSessions();
        if (!sessionResponse.success) {
          throw new Error(sessionResponse.error || "Failed to fetch session data");
        }

        // Ensure data exists before setting state
        if (sessionResponse.data) {
          setSessionData(sessionResponse.data);
        }
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        setError("Failed to load dashboard data. Please refresh or try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router, api]);

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
        <title>Dashboard | 3&7 Training Platform</title>
      </Head>

      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Welcome, {userData?.name || "User"}</h1>
        <Button 
          variant="outline" 
          onClick={() => {
            localStorage.removeItem("auth_token");
            router.push("/login");
          }}
        >
          Sign Out
        </Button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-md">
          {error}
        </div>
      )}

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Your Dashboard</h2>
        {userData?.role === "coach" && userData && sessionData && (
          <CoachDashboard userData={userData} sessionData={sessionData} />
        )}
        {userData?.role === "athlete" && userData && sessionData && (
          <AthleteDashboard userData={userData} sessionData={sessionData} />
        )}
        {!userData?.role && (
          <div className="text-center p-8 border rounded-md bg-gray-50">
            <p>User role not defined. Please contact administrator.</p>
          </div>
        )}
      </div>

      <Separator className="my-6" />

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          <Button onClick={() => router.push("/training-sessions")}>
            Training Sessions
          </Button>
          <Button onClick={() => router.push("/profile")}>
            My Profile
          </Button>
          <Button onClick={() => router.push("/reports")}>
            Reports
          </Button>
        </div>
      </div>

      <Separator className="my-6" />

      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <Tabs defaultValue="sessions">
          <TabsList>
            <TabsTrigger value="sessions">Recent Sessions</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
          </TabsList>
          <TabsContent value="sessions">
            <div className="border rounded-md p-4">
              {sessionData?.recent && sessionData.recent.length > 0 ? (
                <ul className="space-y-2">
                  {sessionData.recent.map((session: TrainingSession) => (
                    <li key={session.id} className="border-b pb-2 last:border-0">
                      <span className="font-medium">{session.title}</span> - {session.date}
                      <p className="text-sm text-gray-500">{session.type} session with {session.coach_name}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No recent sessions found.</p>
              )}
            </div>
          </TabsContent>
          <TabsContent value="notifications">
            <div className="border rounded-md p-4">
              {userData?.notifications && userData.notifications.length > 0 ? (
                <ul className="space-y-2">
                  {userData.notifications.map((notification: Notification) => (
                    <li key={notification.id} className="border-b pb-2 last:border-0">
                      <span className="font-medium">{notification.title}</span>
                      <p className="text-sm text-gray-500">{notification.message}</p>
                      <p className="text-xs text-gray-400">{notification.created_at}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No notifications found.</p>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
} 