import React from 'react';
import { Layout } from '@/components/Layout';
import SendTestEmailButton from '@/components/SendTestEmailButton';

export default function EmailTestPage() {
  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Email Test Page</h1>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Test Email Functionality</h2>
          <p className="mb-6 text-gray-600 dark:text-gray-300">
            Use this page to test the email functionality of the 3&7 Training Platform.
            Click the button below to send a test email to your registered email address.
          </p>
          
          <div className="flex justify-center">
            <SendTestEmailButton />
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Email Configuration</h2>
          <p className="mb-4 text-gray-600 dark:text-gray-300">
            The email functionality uses the Resend API to send emails. Make sure the following environment variables are set:
          </p>
          
          <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-md">
            <code className="text-sm">
              RESEND_API_KEY=your_api_key_here
            </code>
          </div>
          
          <p className="mt-4 text-gray-600 dark:text-gray-300">
            For more information about the Resend API, visit the <a href="https://resend.com/docs" className="text-blue-500 hover:underline">Resend documentation</a>.
          </p>
        </div>
      </div>
    </Layout>
  );
} 