import React, { ReactNode } from 'react';
import Head from 'next/head';
import Link from 'next/link';

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

const Layout: React.FC<LayoutProps> = ({ children, title = '3&7 | Sports Training Platform' }) => {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content="3&7 - Train, Recover, Acclaimed. The premier sport-technology platform in Southeast Asia." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen flex flex-col">
        <header className="bg-white shadow-sm">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <Link href="/" className="text-2xl font-bold text-blue-700">
              3&7
            </Link>
            <nav className="hidden md:flex space-x-6">
              <Link href="/integrated-training" className="text-gray-700 hover:text-blue-600 transition-colors">
                Integrated Training
              </Link>
              <Link href="/ai-reports" className="text-gray-700 hover:text-blue-600 transition-colors">
                AI Reports
              </Link>
              <Link href="/recovery" className="text-gray-700 hover:text-blue-600 transition-colors">
                Recovery
              </Link>
              <Link href="/knowledge-sharing" className="text-gray-700 hover:text-blue-600 transition-colors">
                Knowledge Sharing
              </Link>
              <Link href="/competitions" className="text-gray-700 hover:text-blue-600 transition-colors">
                Competitions
              </Link>
            </nav>
            <div className="flex items-center space-x-4">
              <button className="md:hidden text-gray-700">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="h-6 w-6">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <Link href="/login" className="text-gray-700 hover:text-blue-600 transition-colors hidden md:block">
                Login
              </Link>
              <Link 
                href="/registration" 
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors hidden md:block"
              >
                Sign Up
              </Link>
            </div>
          </div>
        </header>

        <main className="flex-grow bg-gray-50">
          {children}
        </main>

        <footer className="bg-gray-800 text-white">
          <div className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div>
                <h3 className="text-xl font-bold mb-4">3&7</h3>
                <p className="text-gray-300">Southeast Asia's first sport-technology company, enhancing the quality of sports through innovation.</p>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Features</h4>
                <ul className="space-y-2">
                  <li><Link href="/integrated-training" className="text-gray-300 hover:text-white transition-colors">Integrated Training</Link></li>
                  <li><Link href="/ai-reports" className="text-gray-300 hover:text-white transition-colors">AI Reports</Link></li>
                  <li><Link href="/recovery" className="text-gray-300 hover:text-white transition-colors">Recovery</Link></li>
                  <li><Link href="/knowledge-sharing" className="text-gray-300 hover:text-white transition-colors">Knowledge Sharing</Link></li>
                  <li><Link href="/competitions" className="text-gray-300 hover:text-white transition-colors">Competitions</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Company</h4>
                <ul className="space-y-2">
                  <li><Link href="/about" className="text-gray-300 hover:text-white transition-colors">About Us</Link></li>
                  <li><Link href="/contact" className="text-gray-300 hover:text-white transition-colors">Contact</Link></li>
                  <li><Link href="/careers" className="text-gray-300 hover:text-white transition-colors">Careers</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Legal</h4>
                <ul className="space-y-2">
                  <li><Link href="/terms" className="text-gray-300 hover:text-white transition-colors">Terms of Service</Link></li>
                  <li><Link href="/privacy" className="text-gray-300 hover:text-white transition-colors">Privacy Policy</Link></li>
                </ul>
              </div>
            </div>
            <div className="mt-8 pt-6 border-t border-gray-700 text-center text-gray-400">
              <p>&copy; {new Date().getFullYear()} 3&7. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
};

export default Layout; 