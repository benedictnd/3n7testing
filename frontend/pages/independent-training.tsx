import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import TrainingCalendar from '../components/TrainingCalendar';
import { TrainingProgram } from '../lib/types/training';
import { OptimizedImage } from '../components/ui/optimized-image';
import { Skeleton, SkeletonText } from '../components/ui/skeleton';
import { ToastProvider } from '../components/ui/toast';
import { useToasts } from '../components/ui/toast';
import { Button } from '../components/ui/button';

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

const IndependentTrainingContent: React.FC = () => {
  const [programs, setPrograms] = useState<TrainingProgram[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { showSuccess, showError } = useToasts();

  useEffect(() => {
    // Simulate API loading delay
    const timer = setTimeout(() => {
      setPrograms(SAMPLE_PROGRAMS);
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  const handleLogNewSession = () => {
    setIsSubmitting(true);
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      showSuccess('New training session form is ready', 3000);
      // In a real app, this would open a form or modal
    }, 1000);
  };

  const handleViewMetrics = () => {
    showSuccess('Loading your performance metrics...', 3000);
    // In a real app, this would navigate to the metrics page or open a modal
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 dark:text-gray-100">Independent Training System</h1>
      
      <p className="mb-8 dark:text-gray-300">
        Track your personal training sessions, set goals, and monitor your progress. 
        The Independent Training System allows you to manage your own workouts while 
        still being connected to your coaches and team.
      </p>
      
      <div className="bg-white dark:bg-dark-secondary rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 dark:text-gray-100">My Training Calendar</h2>
        <p className="mb-4 dark:text-gray-300">View all your scheduled independent training sessions and team sessions.</p>
        
        {isLoading ? (
          <div className="space-y-4">
            <SkeletonText lines={2} className="mb-6" />
            <Skeleton className="h-64 w-full" />
          </div>
        ) : (
          <TrainingCalendar programs={programs} />
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-dark-secondary rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 dark:text-gray-100">Log New Training Session</h2>
          <p className="mb-4 dark:text-gray-300">
            Record your independent training sessions to keep track of your workouts 
            and share progress with your coach.
          </p>
          <Button 
            variant="primary"
            size="lg"
            isLoading={isSubmitting}
            onClick={handleLogNewSession}
            leftIcon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
            }
          >
            Log New Session
          </Button>
        </div>

        <div className="bg-white dark:bg-dark-secondary rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 dark:text-gray-100">My Performance Metrics</h2>
          <p className="mb-4 dark:text-gray-300">
            View your performance trends, achievements, and areas for improvement
            based on your training history.
          </p>
          <Button 
            variant="outline"
            size="lg"
            onClick={handleViewMetrics}
            leftIcon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
              </svg>
            }
          >
            View My Metrics
          </Button>
        </div>
      </div>
        
      <div className="mt-12 text-center">
        <p className="mb-6 dark:text-gray-300">Join us in transforming traditional training methods into highly efficient, data-driven approaches.</p>
        <Button
          variant="success"
          size="xl"
          fullWidth 
          className="md:w-auto md:px-12"
        >
          Be a part of generational development in sport
        </Button>
      </div>
    </div>
  );
};

const IndependentTraining: React.FC = () => {
  return (
    <ToastProvider>
      <Layout title="Independent Training System">
        <IndependentTrainingContent />
      </Layout>
    </ToastProvider>
  );
};

export default IndependentTraining; 