'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Mail, Plus, ShieldCheck, Activity, Award, CheckCircle2, AlertTriangle, ExternalLink, X } from 'lucide-react';
import { api } from '@/lib/api';
import { Mailbox } from '@/lib/types';

export default function MailboxesPage() {
  const [mailboxes, setMailboxes] = useState<Mailbox[]>([]);
  const [loading, setLoading] = useState(true);
  const [showConnectModal, setShowConnectModal] = useState(false);

  const [connectForm, setConnectForm] = useState({
    provider: 'gmail',
    email: '',
    display_name: '',
    daily_send_limit: 500,
  });

  const loadMailboxes = async () => {
    setLoading(true);
    try {
      const data = await api.getOffers(false); // fetch trigger
      const res = await fetch('http://localhost:8000/api/v1/mailboxes').then((r) => r.json());
      setMailboxes(res);
    } catch (e) {
      setMailboxes([
        {
          id: 'mb1',
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
        },
        {
          id: 'mb2',
          provider: 'microsoft',
          email: 'marketing@company.com',
          display_name: 'Outreach Lead',
          connection_status: 'CONNECTED',
          daily_send_limit: 400,
          current_usage: 241,
          health_score: 87,
          bounce_rate: 0.018,
          complaint_rate: 0.0005,
          reply_rate: 0.069,
          spf_status: 'CONFIGURED',
          dkim_status: 'CONFIGURED',
          dmarc_status: 'CONFIGURED',
          last_sync_at: new Date().toISOString(),
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
    loadMailboxes();
  }, []);

  const handleConnectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!connectForm.email) return;

    try {
      await fetch('http://localhost:8000/api/v1/mailboxes/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(connectForm),
      });
      setShowConnectModal(false);
      setConnectForm({ provider: 'gmail', email: '', display_name: '', daily_send_limit: 500 });
      loadMailboxes();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Mailboxes</h1>
          <p className="text-xs text-slate-400 mt-1">Connect and manage your authorized email sending accounts.</p>
        </div>
        <button
          onClick={() => setShowConnectModal(true)}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-xl text-xs shadow-md shadow-indigo-600/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>Connect Mailbox</span>
        </button>
      </div>

      {/* Mailbox Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {mailboxes.map((mb) => (
          <Link
            key={mb.id}
            href={`/mailboxes/${mb.id}`}
            className="bg-[#111827] p-5 rounded-2xl border border-slate-800 space-y-4 hover:border-indigo-500/40 transition block group shadow-lg"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="text-sm font-bold text-slate-100 group-hover:text-indigo-400 transition">{mb.email}</div>
                <div className="text-xs text-slate-400 mt-0.5 capitalize">{mb.provider === 'gmail' ? 'Google Workspace' : mb.provider === 'microsoft' ? 'Microsoft 365' : mb.provider}</div>
              </div>
              <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                Connected
              </span>
            </div>

            {/* Health & Usage Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs pt-1">
              <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Health Score</div>
                <div className="text-sm font-bold text-emerald-400 font-mono mt-0.5 flex items-center gap-1">
                  <Award className="w-3.5 h-3.5" /> {mb.health_score}/100
                </div>
              </div>
              <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Daily Usage</div>
                <div className="text-sm font-bold text-indigo-400 font-mono mt-0.5">
                  {mb.current_usage} / {mb.daily_send_limit}
                </div>
              </div>
            </div>

            {/* Metrics Bar */}
            <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800/80 text-center text-[11px]">
              <div>
                <div className="text-slate-500 text-[10px] font-mono">Bounce</div>
                <div className="text-slate-300 font-semibold">{Math.round(mb.bounce_rate * 100 * 10) / 10}%</div>
              </div>
              <div>
                <div className="text-slate-500 text-[10px] font-mono">Complaints</div>
                <div className="text-slate-300 font-semibold">{Math.round(mb.complaint_rate * 100 * 100) / 100}%</div>
              </div>
              <div>
                <div className="text-slate-500 text-[10px] font-mono">Reply Rate</div>
                <div className="text-emerald-400 font-semibold">{Math.round(mb.reply_rate * 100 * 10) / 10}%</div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Connect Mailbox Modal */}
      {showConnectModal && (
        <div className="fixed inset-0 z-50 overflow-hidden flex items-center justify-center bg-black/70 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-[#0F172A] border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-100">Connect Legitimate Sending Mailbox</h3>
              <button onClick={() => setShowConnectModal(false)} className="p-1 text-slate-400 hover:text-slate-200 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleConnectSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Select Provider</label>
                <select
                  value={connectForm.provider}
                  onChange={(e) => setConnectForm({ ...connectForm, provider: e.target.value })}
                  className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="gmail">Google Workspace / Gmail (OAuth)</option>
                  <option value="microsoft">Microsoft 365 / Outlook (OAuth)</option>
                  <option value="smtp">Authorized SMTP Account</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Account Email Address</label>
                <input
                  type="email"
                  required
                  value={connectForm.email}
                  onChange={(e) => setConnectForm({ ...connectForm, email: e.target.value })}
                  placeholder="sales@company.com"
                  className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Display Name</label>
                <input
                  type="text"
                  value={connectForm.display_name}
                  onChange={(e) => setConnectForm({ ...connectForm, display_name: e.target.value })}
                  placeholder="Sales Team"
                  className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowConnectModal(false)}
                  className="px-4 py-2 rounded-lg text-slate-400 hover:text-slate-200 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-2.5 rounded-xl transition"
                >
                  Connect Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
