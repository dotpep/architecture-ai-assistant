/**
 * Header Component
 * Displays the application title and branding
 * Requirements: 1.1
 */

import React from 'react';

interface HeaderProps {
  title?: string;
}

const Header: React.FC<HeaderProps> = ({ 
  title = 'Architecture AI Assistant' 
}) => {
  return (
    <header className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {/* Logo/Icon */}
            <div className="flex-shrink-0">
              <svg 
                className="h-8 w-8" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
                aria-hidden="true"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" 
                />
              </svg>
            </div>
            {/* Title */}
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight">
              {title}
            </h1>
          </div>
          {/* Subtitle */}
          <p className="hidden sm:block text-sm text-indigo-100">
            Generate diagrams with AI
          </p>
        </div>
      </div>
    </header>
  );
};

export default Header;
