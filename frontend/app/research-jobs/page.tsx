'use client';

import React, { useEffect, useState } from 'react';
import { Brain, RefreshCw, Activity, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { ResearchJob } from '@/lib/types';

export default function ResearchJobsPage() {
  const [jobs, setJobs] = useState<ResearchJob[]>([]);
  const [loading, setLoading] = useState(true);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const data = await api.getResearchJobs();
      setJobs(data);
    } catch (e) {
      setJobs([
        {
          id: 'rj1',
          name: 'Deep AI Research (50 Washington Leads)',
          research_depth: 'deep',
          status: 'COMPLETED',
          total_leads: 50,
          processed_count: 50,
          successful_count: 47,
          partial_count: 3,
          failed_count: 0,
          progress_percentage: 100,
          is_synthetic: true,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
    const interval = setInterval(loadJobs, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleCancel = async (id: string) => {
    try {
      await api.cancelResearchJob(id);
      loadJobs();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">AI Research Jobs</h1>
          <p className="text-xs text-slate-400 mt-1">Audit log and progress monitor for AI Web Research jobs.</p>
        </div>
        <button
          onClick={loadJobs}
          className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg border border-slate-700 transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="bg-[#111827] rounded-xl border border-slate-800 overflow-hidden shadow-lg">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 bg-[#090D14]/80 text-slate-400 font-mono text-[10px] uppercase">
              <th className="p-3">Research Job</th>
              <th className="p-3">Depth</th>
              <th className="p-3">Total Leads</th>
              <th className="p-3">Processed</th>
              <th className="p-3">Successful</th>
              <th className="p-3">Partial</th>
              <th className="p-3">Failed</th>
              <th className="p-3">Progress</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
            {jobs.map((j) => (
              <tr key={j.id} className="hover:bg-slate-800/40 transition">
                <td className="p-3 font-sans font-semibold text-slate-100 flex items-center gap-2">
                  <Brain className="w-4 h-4 text-indigo-400" />
                  <span>{j.name}</span>
                </td>
                <td className="p-3 uppercase text-indigo-400 font-bold">{j.research_depth}</td>
                <td className="p-3">{j.total_leads}</td>
                <td className="p-3">{j.processed_count}</td>
                <td className="p-3 text-emerald-400 font-bold">{j.successful_count}</td>
                <td className="p-3 text-amber-400">{j.partial_count}</td>
                <td className="p-3 text-rose-400">{j.failed_count}</td>
                <td className="p-3 w-32">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${j.progress_percentage}%` }} />
                    </div>
                    <span className="text-[10px]">{j.progress_percentage}%</span>
                  </div>
                </td>
                <td className="p-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] border ${
                    j.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                    j.status === 'CANCELLED' ? 'bg-slate-800 text-slate-500 border-slate-700' :
                    'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                  }`}>
                    {j.status}
                  </span>
                </td>
                <td className="p-3 text-right font-sans">
                  {['QUEUED', 'DISCOVERING', 'FETCHING', 'ANALYZING'].includes(j.status) && (
                    <button
                      onClick={() => handleCancel(j.id)}
                      className="text-xs text-rose-400 hover:underline"
                    >
                      Cancel
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
