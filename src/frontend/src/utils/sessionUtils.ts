/**
 * Session Utilities
 * Utility functions for session management and display
 * Requirements: 3.1
 */

import { Session } from '../types';

/**
 * Session group type for date-based grouping
 */
export type SessionGroup = 'Today' | 'Yesterday' | 'Last 7 Days' | 'Older';

/**
 * Grouped sessions interface
 */
export interface GroupedSessions {
  [key: string]: Session[];
}

/**
 * Group sessions by date categories
 * Requirements: 3.1 - Display sessions grouped by date
 * 
 * Groups sessions into:
 * - Today: Sessions created today
 * - Yesterday: Sessions created yesterday
 * - Last 7 Days: Sessions created in the last 7 days (excluding today and yesterday)
 * - Older: Sessions older than 7 days
 * 
 * @param sessions - Array of sessions to group
 * @returns Object with sessions grouped by date categories
 */
export const groupSessionsByDate = (sessions: Session[]): GroupedSessions => {
  const groups: GroupedSessions = {};
  const now = new Date();
  
  // Calculate date boundaries in milliseconds
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const yesterday = today - 86400000; // 24 hours in milliseconds
  const lastWeek = today - 7 * 86400000; // 7 days in milliseconds

  sessions.forEach((session) => {
    // Convert session timestamp (seconds) to milliseconds for comparison
    const sessionDate = session.createdAt * 1000;
    let groupKey: SessionGroup;

    if (sessionDate >= today) {
      groupKey = 'Today';
    } else if (sessionDate >= yesterday) {
      groupKey = 'Yesterday';
    } else if (sessionDate >= lastWeek) {
      groupKey = 'Last 7 Days';
    } else {
      groupKey = 'Older';
    }

    if (!groups[groupKey]) {
      groups[groupKey] = [];
    }
    groups[groupKey].push(session);
  });

  // Sort sessions within each group by createdAt (newest first)
  Object.keys(groups).forEach(groupKey => {
    groups[groupKey].sort((a, b) => b.createdAt - a.createdAt);
  });

  return groups;
};