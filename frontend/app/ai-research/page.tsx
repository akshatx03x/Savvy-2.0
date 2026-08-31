'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Brain, Sparkles, Search, ArrowRight, ShieldCheck, Award, Eye, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api';
import { Lead } from '@/lib/types';
import LeadDetailDrawer from '@/components/leads/LeadDetailDrawer';

export default function AIResearchOverviewPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await api.getLeads({ page_size: 10 });
        setLeads(res.items);
      } catch (e) {
        // Fallback preview
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs font-semibold uppercase tracking-wider mb-1">
            <Brain className="w-4 h-4" />
            <span>Module 2 • Lead Intelligence</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">AI Web Research & Intelligence</h1>
          <p className="text-xs text-slate-400 mt-1">Transform discovered leads into evidence-backed prospect profiles.</p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/research-jobs"
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3.5 py-1.5 rounded-lg text-xs font-medium transition"
          >
            <Brain className="w-3.5 h-3.5 text-indigo-400" />
            <span>Research Jobs Monitor</span>
          </Link>
        </div>
      </div>

      {/* Feature Banner */}
      <div className="bg-gradient-to-r from-indigo-950/40 via-[#111827] to-slate-900 p-6 rounded-2xl border border-indigo-500/30 space-y-3">
        <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono font-semibold uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>Evidence-Backed Intelligence Engine</span>
        </div>
        <h2 className="text-lg font-bold text-slate-100">Zero Fake Personalization • Proven Web Provenance</h2>
        <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
          Every AI-generated observation is tied to verified web evidence with source URL, confidence rating, publication date, and strict observation vs inference separation.
        </p>
      </div>

      {/* Researched Prospects List */}
      <div className="bg-[#111827] rounded-xl border border-slate-800 p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">Recent Prospect Intelligence Profiles</h3>
          <Link href="/leads" className="text-xs text-indigo-400 hover:underline flex items-center gap-1">
            Browse All Leads <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {leads.map((lead) => (
            <div
              key={lead.id}
              onClick={() => setSelectedLead(lead)}
              className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 hover:border-indigo-500/40 cursor-pointer transition space-y-3"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="text-sm font-semibold text-slate-100">{lead.contact.full_name}</h4>
                  <p className="text-xs text-slate-400">{lead.contact.job_title || 'Executive'} at <span className="text-indigo-400">{lead.company.name}</span></p>
                </div>
                <span className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded text-[11px] font-mono font-semibold">
                  Intelligence {lead.intelligence_score || 87}/100
                </span>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/80">
                <span>{lead.country} • {lead.industry}</span>
                <span className="text-indigo-400 hover:underline flex items-center gap-1 text-[11px]">
                  Open Profile <Eye className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Lead Detail Drawer */}
      <LeadDetailDrawer lead={selectedLead} onClose={() => setSelectedLead(null)} />
    </div>
  );
}
