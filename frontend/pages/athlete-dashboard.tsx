import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DataGrid } from "@/components/ui/datagrid";
import { Calendar } from "@/components/ui/calendar";
import { toast } from "@/components/ui/use-toast";

// Mock API fetchers (replace with real API calls)
const fetchSchedule = async () => {
  // Replace with: await fetch("/api/schedule?role=athlete")
  return [];
};
const fetchTrainingHistory = async () => {
  return [];
};
const fetchDrills = async () => {
  return [];
};

export default function AthleteDashboard() {
  const router = useRouter();
  const [userRole, setUserRole] = useState<string>("");
  const [schedule, setSchedule] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [drills, setDrills] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Assume auth token contains role (replace with real logic)
    const token = localStorage.getItem("auth_token");
    if (!token || !token.includes("athlete")) {
      toast({ title: "Restricted to athletes.", description: "Redirected to athlete dashboard." });
      router.replace("/login");
      return;
    }
    setUserRole("athlete");
    Promise.all([fetchSchedule(), fetchTrainingHistory(), fetchDrills()]).then(
      ([sched, hist, drills]) => {
        setSchedule(sched);
        setHistory(hist);
        setDrills(drills);
        setLoading(false);
      }
    );
  }, [router]);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <h1 className="text-3xl font-semibold mb-8 text-gray-800">Athlete Dashboard</h1>
      <div className="grid gap-6 md:grid-cols-3">
        {/* Schedule Card */}
        <Card>
          <CardHeader>
            <CardTitle>This Month's Schedule</CardTitle>
          </CardHeader>
          <CardContent>
            <Calendar /* Pass athlete's schedule here */ />
            {/* Request Leave button, session details modal, etc. */}
            <Button className="mt-4 w-full">View Full Schedule</Button>
          </CardContent>
        </Card>
        {/* History Card */}
        <Card>
          <CardHeader>
            <CardTitle>History of Training Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            <DataGrid /* Pass training history here */ />
            <div className="flex gap-2 mt-4">
              <Button variant="outline">Export PDF</Button>
              <Button variant="outline">Export CSV</Button>
            </div>
          </CardContent>
        </Card>
        {/* Independent Training Card */}
        <Card>
          <CardHeader>
            <CardTitle>Conduct Independent Training</CardTitle>
          </CardHeader>
          <CardContent>
            <Button className="w-full">Start New Session</Button>
            <p className="text-xs mt-2 text-gray-500">Independent sessions are logged under your profile only.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
