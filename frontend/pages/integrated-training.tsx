import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import TrainingCalendar from '../components/TrainingCalendar';
import { TrainingProgram } from '../lib/types/training';

// Sample data for demonstration purposes
const SAMPLE_PROGRAMS: TrainingProgram[] = [
  {
    id: '1',
    title: 'Morning Conditioning',
    date: new Date().toISOString(),
    startTime: '08:00',
    totalDuration: 180, // 3 hours
    description: 'Focus on cardio and strength training',
    location: 'Main Training Field',
    status: 'scheduled',
    athleteIds: ['user1', 'user2', 'user3'],
    type: 'integrated',
  },
  {
    id: '2',
    title: 'Evening Skills Training',
    date: new Date().toISOString(),
    startTime: '17:00',
    totalDuration: 120, // 2 hours
    description: 'Technical skills and tactical awareness',
    location: 'Indoor Arena',
    status: 'scheduled',
    athleteIds: ['user1', 'user2', 'user4'],
    type: 'integrated',
  },
  {
    id: '3',
    title: 'Recovery Session',
    date: new Date(new Date().setDate(new Date().getDate() + 1)).toISOString(),
    startTime: '09:30',
    totalDuration: 90, // 1.5 hours
    description: 'Light recovery and stretching',
    location: 'Recovery Center',
    status: 'scheduled',
    athleteIds: ['user1', 'user3'],
    type: 'integrated',
  }
];

const IntegratedTraining: React.FC = () => {
  const [programs, setPrograms] = useState<TrainingProgram[]>([]);
  
  useEffect(() => {
    // In a real application, this would fetch from an API
    setPrograms(SAMPLE_PROGRAMS);
  }, []);

  return (
    <Layout title="Integrated Training System">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Integrated Training System</h1>
        
        <p className="mb-8">
          The <strong>Integrated Training System</strong> is the foundation of <strong>3&7</strong>, 
          designed to streamline training management, data tracking, and performance analysis. 
          Coaches and athletes can effortlessly organize drills, monitor progress, and 
          receive structured feedback based on real-time data.
        </p>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Training Calendar</h2>
          <p className="mb-4">View all scheduled training sessions and their details.</p>
          <TrainingCalendar programs={programs} />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Create New Training Session</h2>
            <p className="mb-4">
              Design comprehensive training sessions with drills, exercises, and goals. 
              Schedule them for your athletes and track progress.
            </p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors">
              Create New Session
            </button>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Performance Analytics</h2>
            <p className="mb-4">
              Access in-depth analysis through machine learning that helps athletes refine 
              their techniques and maximize their potential.
            </p>
            <button className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded transition-colors">
              View Analytics
            </button>
          </div>
        </div>
        
        <div className="mt-8 text-center">
          <p className="mb-4">Join us in transforming traditional training methods into highly efficient, data-driven approaches.</p>
          <a 
            href="/registration" 
            className="inline-block bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
          >
            Be a part of generational development in sport
          </a>
        </div>
      </div>
    </Layout>
  );
};

export default IntegratedTraining; 