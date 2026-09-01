'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { DashboardStats } from '@/lib/types';

export default function HomePage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await api.getDashboardStats();
        setStats(data);
      } catch (e) {
        // Real missing stats fallback to 0
        setStats({
          total_leads: 0,
          unique_leads: 0,
          leads_generated_today: 0,
          total_companies: 0,
          total_contacts: 0,
          generation_jobs_count: 0,
          avg_quality_score: 0,
          researched_leads_count: 0,
          research_coverage_pct: 0,
          high_intelligence_count: 0,
          outreach_ready_count: 0,
          drafts_generated_count: 0,
          approved_drafts_count: 0,
          top_countries: [],
          recent_jobs: [],
        });
      }
    }
    loadStats();
  }, []);

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Top Greeting */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Good morning, Akshat</h1>
        <p className="text-xs text-slate-500 mt-1">What do you want to do?</p>
      </div>

      {/* 3 Core Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Card 1: Find Leads */}
        <div className="p-6 bg-white border border-slate-200 rounded-lg shadow-xs flex flex-col justify-between hover:border-slate-400 transition">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Find leads</h2>
            <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
              Find new prospects based on your target customer.
            </p>
          </div>
          <div className="mt-6">
            <Link
              href="/leads?modal=find"
              className="inline-block bg-slate-900 hover:bg-black text-white px-4 py-2 rounded-md text-xs font-medium transition"
            >
              Find leads
            </Link>
          </div>
        </div>

        {/* Card 2: Write Emails */}
        <div className="p-6 bg-white border border-slate-200 rounded-lg shadow-xs flex flex-col justify-between hover:border-slate-400 transition">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Write emails</h2>
            <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
              Create personalized emails from your researched leads.
            </p>
          </div>
          <div className="mt-6">
            <Link
              href="/leads"
              className="inline-block bg-slate-900 hover:bg-black text-white px-4 py-2 rounded-md text-xs font-medium transition"
            >
              Write emails
            </Link>
          </div>
        </div>

        {/* Card 3: Send Campaign */}
        <div className="p-6 bg-white border border-slate-200 rounded-lg shadow-xs flex flex-col justify-between hover:border-slate-400 transition">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Send campaign</h2>
            <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
              Review and send approved emails.
            </p>
          </div>
          <div className="mt-6">
            <Link
              href="/campaigns?modal=new"
              className="inline-block bg-slate-900 hover:bg-black text-white px-4 py-2 rounded-md text-xs font-medium transition"
            >
              Send campaign
            </Link>
          </div>
        </div>
      </div>

      {/* 4 Main Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-white border border-slate-200 rounded-lg">
          <div className="text-xs text-slate-500 font-medium">Leads</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {stats ? stats.total_leads.toLocaleString() : 0}
          </div>
        </div>

        <div className="p-4 bg-white border border-slate-200 rounded-lg">
          <div className="text-xs text-slate-500 font-medium">Researched</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {stats?.researched_leads_count ? stats.researched_leads_count.toLocaleString() : 0}
          </div>
        </div>

        <div className="p-4 bg-white border border-slate-200 rounded-lg">
          <div className="text-xs text-slate-500 font-medium">Emails ready</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {stats?.approved_drafts_count ? stats.approved_drafts_count.toLocaleString() : 0}
          </div>
        </div>

        <div className="p-4 bg-white border border-slate-200 rounded-lg">
          <div className="text-xs text-slate-500 font-medium">Replies</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">0</div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="p-5 bg-white border border-slate-200 rounded-lg space-y-3">
        <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Recent activity</h3>
        {stats && stats.recent_jobs && stats.recent_jobs.length > 0 ? (
          <div className="space-y-2">
            {stats.recent_jobs.slice(0, 5).map((job: any) => (
              <div key={job.id} className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 last:border-0">
                <span className="text-slate-800 font-medium">{job.name}</span>
                <span className="text-slate-500 text-[11px]">{job.created_leads_count || 0} leads found</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-slate-400 italic py-2">No activity yet.</div>
        )}

      </div>
    </div>
  );
}
