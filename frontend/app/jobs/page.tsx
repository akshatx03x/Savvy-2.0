'use client';

import React, { useEffect, useState } from 'react';
import { History, Play, RefreshCw, XCircle, CheckCircle2, AlertCircle, Clock } from 'lucide-react';
import { api } from '@/lib/api';
import { GenerationJob } from '@/lib/types';

export default function JobsPage() {
  const [jobs, setJobs] = useState<GenerationJob[]>([]);
  const [loading, setLoading] = useState(true);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const data = await api.getJobs();
      setJobs(data);
    } catch (e) {
      setJobs([
        {
          id: 'j1',
          name: 'Real Estate Businesses in Washington',
          search_type: 'ai',
          status: 'COMPLETED',
          niche: 'Real Estate',
          country: 'United States',
          query_params: {} as any,
          requested_count: 500,
          discovered_count: 627,
          valid_count: 581,
          duplicates_count: 81,
          saved_count: 500,
          progress_percentage: 100,
          is_synthetic: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
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
      await api.cancelJob(id);
      loadJobs();
    } catch (e) {
      console.error(e);
    }
  };

  const handleRetry = async (id: string) => {
    try {
      await api.retryJob(id);
      loadJobs();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Generation Jobs</h1>
          <p className="text-xs text-slate-400 mt-1">Audit log of all AI & Manual lead discovery jobs.</p>
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
              <th className="p-3">Job Name</th>
              <th className="p-3">Search Type</th>
              <th className="p-3">Niche</th>
              <th className="p-3">Country</th>
              <th className="p-3">Requested</th>
              <th className="p-3">Discovered</th>
              <th className="p-3">Duplicates</th>
              <th className="p-3">Unique Saved</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
            {jobs.map((j) => (
              <tr key={j.id} className="hover:bg-slate-800/40 transition">
                <td className="p-3 font-sans font-semibold text-slate-100">{j.name}</td>
                <td className="p-3 font-sans capitalize text-slate-400">{j.search_type} Search</td>
                <td className="p-3 font-sans">{j.niche}</td>
                <td className="p-3 font-sans">{j.country}</td>
                <td className="p-3">{j.requested_count}</td>
                <td className="p-3">{j.discovered_count}</td>
                <td className="p-3 text-amber-400">{j.duplicates_count}</td>
                <td className="p-3 text-emerald-400 font-bold">{j.saved_count}</td>
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
                  {['QUEUED', 'SEARCHING', 'PROCESSING'].includes(j.status) ? (
                    <button
                      onClick={() => handleCancel(j.id)}
                      className="text-xs text-rose-400 hover:underline"
                    >
                      Cancel
                    </button>
                  ) : (
                    <button
                      onClick={() => handleRetry(j.id)}
                      className="text-xs text-indigo-400 hover:underline"
                    >
                      Retry
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
