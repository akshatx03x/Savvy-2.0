'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Search, Sparkles, Activity, Plus } from 'lucide-react';
import { api } from '@/lib/api';
import { GenerationJob } from '@/lib/types';

export default function Header() {
  const [activeJobs, setActiveJobs] = useState<GenerationJob[]>([]);

  useEffect(() => {
    const checkJobs = async () => {
      try {
        const jobs = await api.getJobs();
        const running = jobs.filter((j) => ['QUEUED', 'PLANNING', 'SEARCHING', 'PROCESSING', 'DEDUPLICATING', 'SAVING'].includes(j.status));
        setActiveJobs(running);
      } catch (e) {
        // Silent catch if offline
      }
    };
    checkJobs();
    const interval = setInterval(checkJobs, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 bg-[#090D14]/90 backdrop-blur border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Search Input */}
      <div className="flex items-center gap-3 w-96">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search leads, companies, domains..."
            className="w-full bg-slate-900/80 border border-slate-800 rounded-lg pl-9 pr-4 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30 transition"
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Active Jobs Pill */}
        {activeJobs.length > 0 && (
          <Link
            href="/jobs"
            className="flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-mono animate-pulse hover:bg-indigo-500/20 transition"
          >
            <Activity className="w-3.5 h-3.5" />
            <span>{activeJobs.length} Job Running</span>
          </Link>
        )}

        {/* Quick Launch Button */}
        <Link
          href="/find-leads"
          className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-medium shadow-md shadow-indigo-600/20 transition"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Find Leads</span>
        </Link>

        {/* Profile Avatar Placeholder */}
        <div className="flex items-center gap-2.5 pl-3 border-l border-slate-800/80">
          <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-300">
            A
          </div>
        </div>
      </div>
    </header>
  );
}
