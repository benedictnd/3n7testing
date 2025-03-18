import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import TrainingCalendar from '../components/TrainingCalendar';
import { TrainingProgram } from '../lib/types/training';

// Sample data for demonstration purposes
const SAMPLE_PROGRAMS: TrainingProgram[] = [
  {
    id: '1',
    title: 'Individual Fitness Session',
    date: new Date().toISOString(),
    startTime: '07:00',
    totalDuration: 60, // 1 hour
    description: 'Focus on core strength and mobility',
    location: 'Home Gym',
    status: 'scheduled',
    athleteIds: ['user1'],
    type: 'independent',
  },
  {
    id: '2',
    title: 'Evening Recovery Run',
    date: new Date().toISOString(),
    startTime: '18:30',
    totalDuration: 45, // 45 minutes
    description: 'Easy 5km run at conversational pace',
    location: 'Local Park',
    status: 'scheduled',
    athleteIds: ['user1'],
    type: 'independent',
  },
  {
    id: '3',
    title: 'Flexibility & Mobility Work',
    date: new Date(new Date().setDate(new Date().getDate() + 2)).toISOString(),
    startTime: '08:00',
    totalDuration: 30, // 30 minutes
    description: 'Full body stretching and mobility exercises',
    location: 'Home',
    status: 'scheduled',
    athleteIds: ['user1'],
    type: 'independent',
  }
];

const IndependentTraining: React.FC = () => {
  const [programs, setPrograms] = useState<TrainingProgram[]>([]);

  useEffect(() => {
    // In a real application, this would fetch from an API
    setPrograms(SAMPLE_PROGRAMS);
  }, []);

  return (
    <Layout title="Independent Training System">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Independent Training System</h1>
        
        <p className="mb-8">
          Track your personal training sessions, set goals, and monitor your progress. 
          The Independent Training System allows you to manage your own workouts while 
          still being connected to your coaches and team.
        </p>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">My Training Calendar</h2>
          <p className="mb-4">View all your scheduled independent training sessions and team sessions.</p>
          <TrainingCalendar programs={programs} />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Log New Training Session</h2>
            <p className="mb-4">
              Record your independent training sessions to keep track of your workouts 
              and share progress with your coach.
            </p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors">
              Log New Session
            </button>
                </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">My Performance Metrics</h2>
            <p className="mb-4">
              View your performance trends, achievements, and areas for improvement
              based on your training history.
            </p>
            <button className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded transition-colors">
              View My Metrics
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

export default IndependentTraining; 