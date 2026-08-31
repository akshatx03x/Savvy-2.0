'use client';

import React from 'react';
import Link from 'next/link';
import { Tag, ShieldCheck, Activity, ArrowRight, Settings as SettingsIcon } from 'lucide-react';

export default function SettingsOverviewPage() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Platform Settings</h1>
        <p className="text-xs text-slate-400 mt-1">Configure offers, suppression lists, sending preferences, and view account usage.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Link
          href="/settings/offers"
          className="bg-[#111827] p-6 rounded-2xl border border-slate-800 space-y-3 hover:border-indigo-500/40 transition block group shadow-lg"
        >
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Tag className="w-5 h-5" />
          </div>
          <div className="text-sm font-bold text-slate-100 group-hover:text-indigo-400 transition flex items-center justify-between">
            <span>User Offers</span>
            <ArrowRight className="w-4 h-4" />
          </div>
          <p className="text-xs text-slate-400">Manage user product and service offer profiles for Module 3 personalization.</p>
        </Link>

        <Link
          href="/settings/suppression"
          className="bg-[#111827] p-6 rounded-2xl border border-slate-800 space-y-3 hover:border-indigo-500/40 transition block group shadow-lg"
        >
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div className="text-sm font-bold text-slate-100 group-hover:text-indigo-400 transition flex items-center justify-between">
            <span>Suppression List</span>
            <ArrowRight className="w-4 h-4" />
          </div>
          <p className="text-xs text-slate-400">Manage server-side opt-out, bounce, and suppressed recipient email addresses.</p>
        </Link>

        <Link
          href="/settings/usage"
          className="bg-[#111827] p-6 rounded-2xl border border-slate-800 space-y-3 hover:border-indigo-500/40 transition block group shadow-lg"
        >
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Activity className="w-5 h-5" />
          </div>
          <div className="text-sm font-bold text-slate-100 group-hover:text-indigo-400 transition flex items-center justify-between">
            <span>Usage & Limits</span>
            <ArrowRight className="w-4 h-4" />
          </div>
          <p className="text-xs text-slate-400">Track monthly discovery, research, outreach, and email sending metrics.</p>
        </Link>
      </div>
    </div>
  );
}
