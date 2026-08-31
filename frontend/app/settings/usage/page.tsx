'use client';

import React from 'react';

export default function UsageSettingsPage() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Usage & Quotas</h1>
        <p className="text-xs text-slate-400 mt-1">Track monthly lead generation, research, outreach, and email sending usage.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#111827] p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="text-[10px] font-mono uppercase text-slate-500">Lead Discovery</div>
          <div className="text-2xl font-bold text-slate-100 font-mono">4,821</div>
          <div className="text-[11px] text-slate-400 font-mono">Leads Found</div>
        </div>

        <div className="bg-[#111827] p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="text-[10px] font-mono uppercase text-slate-500">AI Web Research</div>
          <div className="text-2xl font-bold text-indigo-400 font-mono">2,341</div>
          <div className="text-[11px] text-slate-400 font-mono">Profiles Created</div>
        </div>

        <div className="bg-[#111827] p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="text-[10px] font-mono uppercase text-slate-500">AI Outreach Studio</div>
          <div className="text-2xl font-bold text-slate-100 font-mono">1,892</div>
          <div className="text-[11px] text-slate-400 font-mono">Drafts Generated</div>
        </div>

        <div className="bg-[#111827] p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="text-[10px] font-mono uppercase text-slate-500">Emails Sent</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">1,204</div>
          <div className="text-[11px] text-emerald-400 font-mono">Mailbox Deliveries</div>
        </div>
      </div>
    </div>
  );
}
