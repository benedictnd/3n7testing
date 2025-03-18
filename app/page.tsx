"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RegistrationForm } from "@/components/forms/RegistrationForm";
import { TrainingSessionForm } from "@/components/forms/TrainingSessionForm";
import { FeedbackForm } from "@/components/forms/FeedbackForm";

export default function Home() {
  const [activeTab, setActiveTab] = useState("registration");

  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2">Training Management System</h1>
        <p className="text-center text-muted-foreground mb-8">
          Comprehensive platform for managing training sessions and athlete feedback
        </p>

        <Tabs
          defaultValue="registration"
          value={activeTab}
          onValueChange={setActiveTab}
          className="w-full"
        >
          <div className="flex justify-center mb-8">
            <TabsList className="grid w-full max-w-md grid-cols-3">
              <TabsTrigger value="registration">Registration</TabsTrigger>
              <TabsTrigger value="training">Training Session</TabsTrigger>
              <TabsTrigger value="feedback">Feedback</TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="registration">
            <div className="max-w-4xl mx-auto">
              <RegistrationForm />
            </div>
          </TabsContent>

          <TabsContent value="training">
            <div className="max-w-5xl mx-auto">
              <TrainingSessionForm />
            </div>
          </TabsContent>

          <TabsContent value="feedback">
            <div className="max-w-4xl mx-auto">
              <FeedbackForm 
                sessionId="TRN-2023-001"
                sessionName="Advanced Core Training"
                sessionDate="November 15, 2023"
                sessionCoach="Coach Johnson"
              />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </main>
  );
} 