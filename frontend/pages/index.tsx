import React from 'react';
import Link from 'next/link';
import Layout from '../components/Layout';

const Home: React.FC = () => {
  return (
    <Layout title="3&7 - Train, Recover, Acclaimed">
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <section className="text-center py-16 md:py-24">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Train, Recover, Acclaimed.</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Elevating sports performance through data-driven insights and innovative technology.
          </p>
          <Link 
            href="/registration" 
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg text-lg transition-colors"
          >
            Get Started
          </Link>
        </section>

        {/* About Section */}
        <section className="mb-16">
          <div className="bg-white rounded-lg shadow-md p-8">
            <p className="mb-4 text-lg">
              Since 2024, <strong>3&7</strong> has been committed to enhancing the quality of sports, ensuring high-level and well-structured competition environments. Developed by top sports professionals, technology experts, and industry stakeholders, we combine expertise and innovation to elevate sports training and performance.
            </p>
            <p className="mb-4 text-lg">
              As Southeast Asia's first sport-technology company, our vision is to create a sustainable ecosystem that benefits athletes, coaches, and organizations. By integrating advanced technology, we provide tools that maximize efficiency, performance tracking, and injury prevention.
            </p>
            <p className="mb-4 text-lg">
              We believe that sports should be backed by data-driven insights, allowing for better decision-making and higher competitiveness. From youth training to professional-level competitions, <strong>3&7</strong> ensures that every athlete has access to the best possible environment to grow and succeed.
            </p>
            <p className="text-lg">
              Our goal is to bridge the gap between traditional training and modern advancements, enabling a new era of sports development. Join us in shaping the future of competitive sports.
            </p>
          </div>
        </section>

        {/* Features Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-center">Our Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="h-40 bg-blue-100 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">Integrated Training System</h3>
                <p className="text-gray-600 mb-4">
                  Streamline training management, data tracking, and performance analysis with our comprehensive system.
                </p>
                <Link 
                  href="/integrated-training" 
                  className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center"
                >
                  Learn More
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="h-40 bg-purple-100 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">AI-Driven Reports</h3>
                <p className="text-gray-600 mb-4">
                  Gain deeper insights with our AI-powered analytics that generate comprehensive performance reports.
                </p>
                <Link 
                  href="/ai-reports" 
                  className="text-purple-600 hover:text-purple-800 font-medium inline-flex items-center"
                >
                  Learn More
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="h-40 bg-green-100 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">Physical & Mental Recovery</h3>
                <p className="text-gray-600 mb-4">
                  Support for injury prevention, rehabilitation, and mental resilience to ensure optimal performance.
                </p>
                <Link 
                  href="/recovery" 
                  className="text-green-600 hover:text-green-800 font-medium inline-flex items-center"
                >
                  Learn More
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>

            {/* Feature 4 */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="h-40 bg-yellow-100 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">Journals & Knowledge Sharing</h3>
                <p className="text-gray-600 mb-4">
                  Access and share scientific findings, training methods, and best practices with the sports community.
                </p>
                <Link 
                  href="/knowledge-sharing" 
                  className="text-yellow-600 hover:text-yellow-800 font-medium inline-flex items-center"
                >
                  Learn More
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>

            {/* Feature 5 */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="h-40 bg-red-100 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">Find Competitions & Workshops</h3>
                <p className="text-gray-600 mb-4">
                  Connect with sporting events, workshops, and competitions through our digital platform.
                </p>
                <Link 
                  href="/competitions" 
                  className="text-red-600 hover:text-red-800 font-medium inline-flex items-center"
                >
                  Learn More
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>

            {/* Independent Training */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="h-40 bg-indigo-100 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">Independent Training</h3>
                <p className="text-gray-600 mb-4">
                  Track your personal training sessions, set goals, and monitor your progress on your own schedule.
                </p>
                <Link 
                  href="/independent-training" 
                  className="text-indigo-600 hover:text-indigo-800 font-medium inline-flex items-center"
                >
                  Learn More
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center py-12 bg-blue-700 rounded-lg shadow-md mb-16">
          <h2 className="text-3xl font-bold text-white mb-4">Join the Revolution in Sports Training</h2>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto mb-8">
            Be a part of the generational development in sport with 3&7's cutting-edge technology.
          </p>
          <Link 
            href="/registration" 
            className="inline-block bg-white text-blue-700 hover:bg-blue-50 font-bold py-3 px-8 rounded-lg text-lg transition-colors"
          >
            Register Now
          </Link>
        </section>
      </div>
    </Layout>
  );
};

export default Home; 