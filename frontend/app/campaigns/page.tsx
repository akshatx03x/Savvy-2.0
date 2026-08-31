'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Sparkles, Plus, Play, Pause, Send, Activity, ArrowRight, CheckCircle2 } from 'lucide-react';
import { api } from '@/lib/api';
import { Campaign } from '@/lib/types';

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);

  const loadCampaigns = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/campaigns').then((r) => r.json());
      setCampaigns(res);
    } catch (e) {
      setCampaigns([
        {
          id: 'c1',
          name: 'Washington Real Estate Outreach',
          description: 'Targeting top real estate brokerages in Washington.',
          status: 'ACTIVE',
          timezone: 'UTC',
          schedule_config: { days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], start_hour: '09:00', end_hour: '17:00' },
          total_recipients: 500,
          sent_count: 342,
          delivered_count: 337,
          opened_count: 143,
          replied_count: 31,
          positive_replied_count: 12,
          bounced_count: 5,
          complaint_count: 0,
          opt_out_count: 2,
          mailbox_ids: ['mb1', 'mb2'],
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
    loadCampaigns();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Campaigns</h1>
          <p className="text-xs text-slate-400 mt-1">Manage and monitor controlled email outreach campaigns.</p>
        </div>
        <Link
          href="/campaigns/new"
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-xl text-xs shadow-md shadow-indigo-600/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>New Campaign</span>
        </Link>
      </div>

      {/* KPI Overview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-[#111827] p-4 rounded-xl border border-slate-800">
          <div className="text-[10px] font-mono text-slate-500 uppercase">Active Campaigns</div>
          <div className="text-xl font-bold text-slate-100 mt-1 font-mono">1</div>
        </div>
        <div className="bg-[#111827] p-4 rounded-xl border border-slate-800">
          <div className="text-[10px] font-mono text-slate-500 uppercase">Scheduled</div>
          <div className="text-xl font-bold text-indigo-400 mt-1 font-mono">158</div>
        </div>
        <div className="bg-[#111827] p-4 rounded-xl border border-slate-800">
          <div className="text-[10px] font-mono text-slate-500 uppercase">Total Sent</div>
          <div className="text-xl font-bold text-slate-100 mt-1 font-mono">342</div>
        </div>
        <div className="bg-[#111827] p-4 rounded-xl border border-slate-800">
          <div className="text-[10px] font-mono text-slate-500 uppercase">Replies</div>
          <div className="text-xl font-bold text-emerald-400 mt-1 font-mono">31</div>
        </div>
        <div className="bg-[#111827] p-4 rounded-xl border border-slate-800">
          <div className="text-[10px] font-mono text-slate-500 uppercase">Positive Replies</div>
          <div className="text-xl font-bold text-emerald-400 mt-1 font-mono">12</div>
        </div>
      </div>

      {/* Campaigns Table */}
      <div className="bg-[#111827] rounded-xl border border-slate-800 overflow-hidden shadow-lg">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 bg-[#090D14]/80 text-slate-400 font-mono text-[10px] uppercase">
              <th className="p-3">Campaign</th>
              <th className="p-3">Recipients</th>
              <th className="p-3">Mailboxes</th>
              <th className="p-3">Sent</th>
              <th className="p-3">Replies</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
            {campaigns.map((c) => (
              <tr key={c.id} className="hover:bg-slate-800/40 transition">
                <td className="p-3 font-sans font-semibold text-slate-100">
                  <Link href={`/campaigns/${c.id}`} className="hover:text-indigo-400 transition">
                    {c.name}
                  </Link>
                </td>
                <td className="p-3">{c.total_recipients}</td>
                <td className="p-3">{c.mailbox_ids?.length || 2} Mailboxes</td>
                <td className="p-3 text-slate-100 font-bold">{c.sent_count}</td>
                <td className="p-3 text-emerald-400 font-bold">{c.replied_count}</td>
                <td className="p-3">
                  <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {c.status}
                  </span>
                </td>
                <td className="p-3 text-right font-sans">
                  <Link href={`/campaigns/${c.id}`} className="text-xs text-indigo-400 hover:underline flex items-center gap-1 justify-end">
                    <span>Manage</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
