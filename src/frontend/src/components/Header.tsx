/**
 * Header Component - Redesigned
 * Pinned navbar with modern styling
 * Requirements: 1.1
 */

import React from 'react';
import { DiagramType } from '../types';
import { DIAGRAM_TYPE_OPTIONS } from './DiagramTypeSelector';

interface HeaderProps {
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
  selectedDiagramType: DiagramType;
  onDiagramTypeChange: (type: DiagramType) => void;
}

const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  sidebarOpen,
  selectedDiagramType,
  onDiagramTypeChange,
}) => {
  return (
    <header className="sticky top-0 z-50 bg-slate-800/95 backdrop-blur-sm border-b border-slate-700/50 shadow-lg">
      <div className="flex items-center justify-between px-4 py-3">
        {/* Left Section */}
        <div className="flex items-center gap-3">
          {/* Sidebar Toggle */}
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-lg hover:bg-slate-700/50 transition-colors text-slate-400 hover:text-white"
            aria-label={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {sidebarOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>

          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white tracking-tight">Architecture AI</h1>
              <p className="text-xs text-slate-400 hidden sm:block">Generate diagrams with AI</p>
            </div>
          </div>
        </div>

        {/* Center - Diagram Type Selector */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-400 hidden md:block">Diagram:</span>
          <div className="relative">
            <select
              value={selectedDiagramType}
              onChange={(e) => onDiagramTypeChange(e.target.value as DiagramType)}
              className="appearance-none bg-slate-700/50 border border-slate-600/50 text-white text-sm rounded-lg px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 cursor-pointer hover:bg-slate-700 transition-colors"
            >
              {DIAGRAM_TYPE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>

        {/* Right Section - Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
            <span className="text-xs text-emerald-400 font-medium">Online</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
