import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Layout from '../components/Layout';

const AboutPage: React.FC = () => {
  // For smooth scrolling functionality
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    const headerOffset = 80;
    
    if (element) {
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  // For fade-in animation on scroll - will run on the client
  React.useEffect(() => {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in');
        }
      });
    }, observerOptions);

    document.querySelectorAll('.fade-in-section').forEach(element => {
      observer.observe(element);
    });

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <Layout title="About Us - 3&7 Training Platform">
      <Head>
        <style jsx global>{`
          .fade-in-section {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 1s ease-in, transform 1s ease-in;
          }
          
          .fade-in {
            opacity: 1;
            transform: translateY(0);
          }

          .hover-underline {
            position: relative;
          }

          .hover-underline::after {
            content: '';
            position: absolute;
            width: 0;
            height: 2px;
            bottom: -2px;
            left: 0;
            background-color: white;
            transition: width 0.3s ease;
          }

          .hover-underline:hover::after {
            width: 100%;
          }

          .team-member {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
          }

          .team-member:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
          }

          .scroll-container {
            scroll-behavior: smooth;
            scrollbar-width: none;
            -ms-overflow-style: none;
            padding: 20px;
            margin: -20px;
          }

          .scroll-container::-webkit-scrollbar {
            display: none;
          }

          .scroll-box {
            transition: transform 0.75s ease;
          }
          
          .scroll-box:hover {
            transform: translateX(10px);
          }
        `}</style>
      </Head>

      {/* Navigation for section links */}
      <nav className="bg-blue-900 shadow-md dark:bg-gray-800 sticky top-16 z-40">
        <div className="container mx-auto px-6 py-3">
          <div className="flex justify-center md:justify-start space-x-8 overflow-x-auto hide-scrollbar">
            <button 
              onClick={() => scrollToSection('who-we-are')} 
              className="text-white hover:text-blue-300 transition-colors whitespace-nowrap"
            >
              Who We Are
            </button>
            <button 
              onClick={() => scrollToSection('our-vision')} 
              className="text-white hover:text-blue-300 transition-colors whitespace-nowrap"
            >
              Our Vision
            </button>
            <button 
              onClick={() => scrollToSection('meet-people')} 
              className="text-white hover:text-blue-300 transition-colors whitespace-nowrap"
            >
              Meet the People
            </button>
            <button 
              onClick={() => scrollToSection('more-about')} 
              className="text-white hover:text-blue-300 transition-colors whitespace-nowrap"
            >
              More About 3&7
            </button>
          </div>
        </div>
      </nav>

      {/* Who We Are Section */}
      <section 
        id="who-we-are" 
        className="min-h-screen flex items-center pt-20 bg-cover bg-center" 
        style={{
          backgroundImage: "linear-gradient(rgba(9, 16, 78, 0.7), rgba(9, 16, 78, 0.7)), url('/static/image/who we are sec.png')"
        }}
      >
        <div className="container mx-auto px-6 py-24">
          <div className="max-w-4xl mx-auto text-center fade-in-section">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-8">Who We Are</h1>
            <p className="text-lg md:text-xl text-white mb-6">
              Founded in 2024, we represent a strategic advancement in how athletes, coaches, and key stakeholders—including sporting bodies and recovery centers—engage with each other.
            </p>
            <p className="text-lg md:text-xl text-white mb-6">
              By harnessing the power of machine learning, our system delivers precise training protocols, comprehensive mental wellness support, and safeguards against misinformation and unprofessional conduct.
            </p>
            <p className="text-lg md:text-xl text-white">
              We are committed to fostering an environment where integrity, data-driven insights, and professional standards converge to drive the nation's sporting success.
            </p>
          </div>
        </div>
      </section>

      {/* Our Vision Section */}
      <section 
        id="our-vision" 
        className="min-h-screen flex items-center bg-cover bg-center" 
        style={{
          backgroundImage: "linear-gradient(rgba(53, 61, 255, 0.5), rgba(53, 61, 255, 0.5)), url('/static/image/Our Vision sec.png')"
        }}
      >
        <div className="container mx-auto px-6 py-24">
          <div className="max-w-3xl pl-0 md:pl-9">
            <div className="fade-in-section">
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-8">Our Vision</h2>
              <div className="space-y-6">
                <p className="text-xl text-white hover-underline inline-block">
                  Create sustainability in sporting industry, from creating champions eversince to influence a healthier life.
                </p>
                <p className="text-xl text-white hover-underline inline-block">
                  Raise quality of competition
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Meet the People Section */}
      <section 
        id="meet-people" 
        className="min-h-screen flex items-center bg-cover bg-center" 
        style={{
          backgroundImage: "linear-gradient(rgba(9, 16, 78, 0.5), rgba(9, 16, 78, 0.5)), url('/static/image/Who We Are.png')"
        }}
      >
        <div className="container mx-auto px-6 py-24">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-16 text-center">Meet the People</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-9 max-w-6xl mx-auto">
            {/* Team Member 1 */}
            <div className="team-member w-full md:w-[250px] h-[300px] mx-auto bg-gradient-to-br from-blue-500 to-blue-900 dark:from-blue-600 dark:to-blue-950 rounded-xl overflow-hidden">
              <div className="h-full flex flex-col items-center justify-end p-6 text-center">
                <h3 className="text-xl font-bold text-white mb-2">Benedictus Nathaniel Davin</h3>
                <p className="text-white/80">Co-Founder, CEO</p>
              </div>
            </div>

            {/* Team Member 2 */}
            <div className="team-member w-full md:w-[250px] h-[300px] mx-auto bg-gradient-to-br from-blue-500 to-blue-900 dark:from-blue-600 dark:to-blue-950 rounded-xl overflow-hidden">
              <div className="h-full flex flex-col items-center justify-end p-6 text-center">
                <h3 className="text-xl font-bold text-white mb-2">Muhammad Awatarino</h3>
                <p className="text-white/80">Co-Founder, CFO</p>
              </div>
            </div>

            {/* Team Member 3 */}
            <div className="team-member w-full md:w-[250px] h-[300px] mx-auto bg-gradient-to-br from-blue-500 to-blue-900 dark:from-blue-600 dark:to-blue-950 rounded-xl overflow-hidden">
              <div className="h-full flex flex-col items-center justify-end p-6 text-center">
                <h3 className="text-xl font-bold text-white mb-2">Nuroji Lukman</h3>
                <p className="text-white/80">Co-Founder, Advisory</p>
              </div>
            </div>

            {/* Team Member 4 */}
            <div className="team-member w-full md:w-[250px] h-[300px] mx-auto bg-gradient-to-br from-blue-500 to-blue-900 dark:from-blue-600 dark:to-blue-950 rounded-xl overflow-hidden">
              <div className="h-full flex flex-col items-center justify-end p-6 text-center">
                <h3 className="text-xl font-bold text-white mb-2">Abi Hasbullah</h3>
                <p className="text-white/80">Head Advisory, Head Coach of 3&7</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* More About 3&7 Section */}
      <section id="more-about" className="min-h-screen bg-blue-600 dark:bg-blue-800 flex items-center">
        <div className="container mx-auto px-6 py-24">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-12 text-center">More About 3&7</h2>
          
          <div className="scroll-container overflow-x-auto pb-8">
            <div className="flex gap-4 snap-x snap-mandatory">
              {/* Box 1 */}
              <div className="scroll-box flex-none w-[200px] h-[120px] rounded-lg shadow-sm snap-center transform transition-all duration-300 hover:shadow-md hover:-translate-y-1 bg-gradient-to-br from-blue-900 to-blue-500 dark:from-blue-950 dark:to-blue-700">
                <div className="w-full h-full flex items-end p-6">
                  <h3 className="text-xs font-normal font-sans text-white">Our Mission</h3>
                </div>
              </div>

              {/* Box 2 */}
              <div className="scroll-box flex-none w-[200px] h-[120px] rounded-lg shadow-sm snap-center transform transition-all duration-300 hover:shadow-md hover:-translate-y-1 bg-gradient-to-br from-blue-900 to-blue-500 dark:from-blue-950 dark:to-blue-700">
                <div className="w-full h-full flex items-end p-6">
                  <h3 className="text-xs font-normal font-sans text-white">Our Values</h3>
                </div>
              </div>

              {/* Box 3 */}
              <div className="scroll-box flex-none w-[200px] h-[120px] rounded-lg shadow-sm snap-center transform transition-all duration-300 hover:shadow-md hover:-translate-y-1 bg-gradient-to-br from-blue-900 to-blue-500 dark:from-blue-950 dark:to-blue-700">
                <div className="w-full h-full flex items-end p-6">
                  <h3 className="text-xs font-normal font-sans text-white">Our Journey</h3>
                </div>
              </div>

              {/* Box 4 */}
              <div className="scroll-box flex-none w-[200px] h-[120px] rounded-lg shadow-sm snap-center transform transition-all duration-300 hover:shadow-md hover:-translate-y-1 bg-gradient-to-br from-blue-900 to-blue-500 dark:from-blue-950 dark:to-blue-700">
                <div className="w-full h-full flex items-end p-6">
                  <h3 className="text-xs font-normal font-sans text-white">Our Technology</h3>
                </div>
              </div>

              {/* Box 5 */}
              <div className="scroll-box flex-none w-[200px] h-[120px] rounded-lg shadow-sm snap-center transform transition-all duration-300 hover:shadow-md hover:-translate-y-1 bg-gradient-to-br from-blue-900 to-blue-500 dark:from-blue-950 dark:to-blue-700">
                <div className="w-full h-full flex items-end p-6">
                  <h3 className="text-xs font-normal font-sans text-white">Our Impact</h3>
                </div>
              </div>

              {/* Box 6 */}
              <div className="scroll-box flex-none w-[200px] h-[120px] rounded-lg shadow-sm snap-center transform transition-all duration-300 hover:shadow-md hover:-translate-y-1 bg-gradient-to-br from-blue-900 to-blue-500 dark:from-blue-950 dark:to-blue-700">
                <div className="w-full h-full flex items-end p-6">
                  <h3 className="text-xs font-normal font-sans text-white">Future Plans</h3>
                </div>
              </div>
            </div>
          </div>

          {/* Back to Home Button */}
          <div className="text-center mt-8">
            <Link 
              href="/" 
              className="inline-block px-6 py-2 bg-blue-900 dark:bg-blue-950 text-white rounded-lg hover:bg-opacity-80 transition-colors text-base font-medium"
            >
              Back to Home
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default AboutPage; 