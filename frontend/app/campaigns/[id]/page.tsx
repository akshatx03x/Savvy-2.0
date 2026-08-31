'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Pause, Send, Activity, CheckCircle2, Award, Users } from 'lucide-react';
import { Campaign } from '@/lib/types';

export default function CampaignDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const [campaign, setCampaign] = useState<Campaign | null>(null);

  useEffect(() => {
    async function load() {
      const resolvedParams = await params;
      try {
        const res = await fetch(`http://localhost:8000/api/v1/campaigns/${resolvedParams.id}`).then((r) => r.json());
        setCampaign(res);
      } catch (e) {
        setCampaign({
          id: resolvedParams.id,
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
        });
      }
    }
    load();
  }, [params]);

  if (!campaign) return null;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <Link href="/campaigns" className="text-xs text-indigo-400 hover:underline flex items-center gap-1">
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Campaigns
      </Link>

      <div className="bg-[#111827] p-6 rounded-2xl border border-slate-800 space-y-6 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h1 className="text-xl font-bold text-slate-100">{campaign.name}</h1>
            <p className="text-xs text-slate-400 mt-0.5">{campaign.description}</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs font-mono bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-lg border border-emerald-500/20">
              ● {campaign.status}
            </span>
            <button className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-3.5 py-1.5 rounded-lg text-xs font-medium border border-slate-700 transition flex items-center gap-1.5">
              <Pause className="w-3.5 h-3.5" /> Pause
            </button>
          </div>
        </div>

        {/* Campaign Funnel Grid */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3 text-center text-xs">
          <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
            <div className="text-[10px] font-mono uppercase text-slate-500">Recipients</div>
            <div className="text-base font-bold text-slate-100 font-mono mt-1">{campaign.total_recipients}</div>
          </div>
          <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
            <div className="text-[10px] font-mono uppercase text-slate-500">Sent</div>
            <div className="text-base font-bold text-slate-100 font-mono mt-1">{campaign.sent_count}</div>
          </div>
          <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
            <div className="text-[10px] font-mono uppercase text-slate-500">Delivered</div>
            <div className="text-base font-bold text-emerald-400 font-mono mt-1">{campaign.delivered_count}</div>
          </div>
          <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
            <div className="text-[10px] font-mono uppercase text-slate-500">Opened</div>
            <div className="text-base font-bold text-indigo-400 font-mono mt-1">{campaign.opened_count}</div>
          </div>
          <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
            <div className="text-[10px] font-mono uppercase text-slate-500">Replies</div>
            <div className="text-base font-bold text-emerald-400 font-mono mt-1">{campaign.replied_count}</div>
          </div>
          <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
            <div className="text-[10px] font-mono uppercase text-slate-500">Positive</div>
            <div className="text-base font-bold text-emerald-400 font-mono mt-1">{campaign.positive_replied_count}</div>
          </div>
        </div>

        {/* Sending Timeline & Log */}
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 space-y-3">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">Live Recipient Activity Timeline</h3>
          <div className="space-y-2 text-xs font-mono text-slate-300">
            <div className="p-3 bg-[#090D14] rounded-lg border border-slate-800 flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-100">John Smith (ABC Realty)</span>
                <div className="text-[11px] text-slate-400 font-sans">Subject: Quick question re: ABC Realty's expansion</div>
              </div>
              <span className="text-emerald-400 text-[11px]">✓ Replied (Positive)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
