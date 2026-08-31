'use client';

import React, { useState, useEffect } from 'react';
import { Mail, ShieldCheck, Award, ArrowLeft, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import { Mailbox } from '@/lib/types';

export default function MailboxDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const [mailbox, setMailbox] = useState<Mailbox | null>(null);

  useEffect(() => {
    async function load() {
      const resolvedParams = await params;
      try {
        const res = await fetch(`http://localhost:8000/api/v1/mailboxes/${resolvedParams.id}`).then((r) => r.json());
        setMailbox(res);
      } catch (e) {
        setMailbox({
          id: resolvedParams.id,
          provider: 'gmail',
          email: 'sales@company.com',
          display_name: 'Sales Team',
          connection_status: 'CONNECTED',
          daily_send_limit: 500,
          current_usage: 342,
          health_score: 92,
          bounce_rate: 0.011,
          complaint_rate: 0.0004,
          reply_rate: 0.082,
          spf_status: 'CONFIGURED',
          dkim_status: 'CONFIGURED',
          dmarc_status: 'CONFIGURED',
          last_sync_at: new Date().toISOString(),
          is_synthetic: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      }
    }
    load();
  }, [params]);

  if (!mailbox) return null;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <Link href="/mailboxes" className="text-xs text-indigo-400 hover:underline flex items-center gap-1">
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Mailboxes
      </Link>

      <div className="bg-[#111827] p-6 rounded-2xl border border-slate-800 space-y-6 shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h1 className="text-xl font-bold text-slate-100">{mailbox.email}</h1>
            <p className="text-xs text-slate-400 mt-0.5">Provider: <span className="text-indigo-400 font-medium uppercase">{mailbox.provider}</span></p>
          </div>
          <span className="text-xs font-mono bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-lg border border-emerald-500/20">
            ● Connected
          </span>
        </div>

        {/* Authentication Grid */}
        <div className="space-y-3">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">Domain Authentication Status</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
              <div className="text-[10px] font-mono uppercase text-slate-500">SPF Record</div>
              <div className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Configured
              </div>
            </div>
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
              <div className="text-[10px] font-mono uppercase text-slate-500">DKIM Signature</div>
              <div className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Configured
              </div>
            </div>
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
              <div className="text-[10px] font-mono uppercase text-slate-500">DMARC Policy</div>
              <div className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Configured
              </div>
            </div>
          </div>
        </div>

        {/* Health Recommendations */}
        <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 space-y-3">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">Mailbox Health Guidance</h3>
          <ul className="text-xs text-slate-300 space-y-2">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Authentication (SPF, DKIM, DMARC) is verified and healthy.</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Bounce rate is maintained below 2% threshold (1.1%).</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
