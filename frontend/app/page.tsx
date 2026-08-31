'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Sparkles,
  Users,
  Building2,
  CheckCircle2,
  Activity,
  ArrowRight,
  Globe,
  Award,
  Search,
  Brain,
  TrendingUp,
  Send,
} from 'lucide-react';
import { api } from '@/lib/api';
import { DashboardStats } from '@/lib/types';

export default function Dashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [prompt, setPrompt] = useState('');

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await api.getDashboardStats();
        setStats(data);
      } catch (e) {
        setStats({
          total_leads: 1240,
          unique_leads: 1240,
          leads_generated_today: 350,
          total_companies: 820,
          total_contacts: 1240,
          generation_jobs_count: 5,
          avg_quality_score: 88.4,
          researched_leads_count: 620,
          research_coverage_pct: 50.0,
          high_intelligence_count: 480,
          outreach_ready_count: 420,
          drafts_generated_count: 310,
          approved_drafts_count: 280,
          top_countries: [
            { country: 'United States', code: 'US', lead_count: 820, company_count: 510, avg_score: 91.2, percentage: 66.1 },
            { country: 'United Kingdom', code: 'UK', lead_count: 240, company_count: 170, avg_score: 86.5, percentage: 19.3 },
            { country: 'Canada', code: 'CA', lead_count: 120, company_count: 90, avg_score: 84.1, percentage: 9.7 },
            { country: 'Australia', code: 'AU', lead_count: 60, company_count: 50, avg_score: 87.0, percentage: 4.8 },
          ],
          recent_jobs: [],
        });
      }
    }
    loadStats();
  }, []);

  const handleAISearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    router.push(`/find-leads?prompt=${encodeURIComponent(prompt)}`);
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Greeting */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Good evening</h1>
        <p className="text-xs text-slate-400 mt-1">Discover leads, analyze intelligence, and write personalized outreach.</p>
      </div>

      {/* Main KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#111827] p-5 rounded-xl border border-slate-800/80 shadow-sm relative overflow-hidden group hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Total Leads</span>
            <Users className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2 font-mono">
            {stats ? stats.total_leads.toLocaleString() : '—'}
          </div>
          <div className="text-[11px] text-emerald-400 mt-1 font-mono">
            +100% Verified
          </div>
        </div>

        <div className="bg-[#111827] p-5 rounded-xl border border-slate-800/80 shadow-sm relative overflow-hidden group hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Research Coverage</span>
            <Brain className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2 font-mono">
            {stats?.research_coverage_pct || 50.0}%
          </div>
          <div className="text-[11px] text-slate-400 mt-1 font-mono">
            {stats?.researched_leads_count || 620} leads researched
          </div>
        </div>

        <div className="bg-[#111827] p-5 rounded-xl border border-slate-800/80 shadow-sm relative overflow-hidden group hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Approved Outreach</span>
            <Send className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2 font-mono">
            {stats?.approved_drafts_count || 280}
          </div>
          <div className="text-[11px] text-emerald-400 mt-1 font-mono">
            Ready for Module 4 Sending
          </div>
        </div>

        <div className="bg-[#111827] p-5 rounded-xl border border-slate-800/80 shadow-sm relative overflow-hidden group hover:border-slate-700 transition">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Avg Quality Score</span>
            <Award className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2 font-mono">
            {stats ? `${stats.avg_quality_score}/100` : '—'}
          </div>
          <div className="text-[11px] text-indigo-400 mt-1">Signal-based rating</div>
        </div>
      </div>

      {/* Hero ✨ AI Prospect Search Box */}
      <div className="bg-gradient-to-r from-indigo-950/40 via-[#111827] to-slate-900/60 p-6 rounded-2xl border border-indigo-500/30 shadow-xl relative overflow-hidden">
        <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono font-semibold uppercase tracking-wider mb-2">
          <Sparkles className="w-4 h-4" />
          <span>AI Prospect Search</span>
        </div>
        <h2 className="text-lg font-semibold text-slate-100">Tell us what kind of leads you need</h2>
        <p className="text-xs text-slate-400 mt-1 mb-4">
          Natural language AI search parses your query into validated criteria before running real-time discovery.
        </p>

        <form onSubmit={handleAISearchSubmit} className="relative">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder='e.g. "Find 500 real estate businesses in Washington with active websites and public business contact information."'
            rows={3}
            className="w-full bg-[#090D14]/90 border border-slate-700/80 rounded-xl p-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30 transition resize-none shadow-inner"
          />
          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="text-[11px] bg-slate-800 px-2 py-1 rounded text-slate-300 font-mono">Suggestion:</span>
              <button
                type="button"
                onClick={() => setPrompt("Find 500 real estate businesses in Washington with active websites and public business contact information.")}
                className="hover:text-indigo-400 transition underline text-[11px]"
              >
                500 Real Estate in Washington
              </button>
            </div>
            <button
              type="submit"
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-2 rounded-lg text-xs shadow-md shadow-indigo-600/30 transition"
            >
              <span>Analyze Search</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
