'use client';

import React, { useState, useEffect } from 'react';
import { ShieldCheck, Plus, Trash2, X } from 'lucide-react';

interface SuppressionItem {
  id: string;
  email: string;
  reason: string;
  source: string;
  created_at: string;
}

export default function SuppressionSettingsPage() {
  const [entries, setEntries] = useState<SuppressionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [email, setEmail] = useState('');
  const [reason, setReason] = useState('OPT_OUT');

  const loadSuppressed = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/suppression').then((r) => r.json());
      setEntries(res);
    } catch (e) {
      setEntries([
        { id: 's1', email: 'optout@example.com', reason: 'OPT_OUT', source: 'optout_link', created_at: new Date().toISOString() },
        { id: 's2', email: 'bounce@invalid.com', reason: 'HARD_BOUNCE', source: 'provider_bounce', created_at: new Date().toISOString() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSuppressed();
  }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    try {
      await fetch('http://localhost:8000/api/v1/suppression', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, reason, source: 'user_manual' }),
      });
      setShowModal(false);
      setEmail('');
      loadSuppressed();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/suppression/${id}`, { method: 'DELETE' });
      loadSuppressed();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Suppression List</h1>
          <p className="text-xs text-slate-400 mt-1">Suppressed recipients are automatically blocked server-side before campaign sending.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-xl text-xs shadow-md transition"
        >
          <Plus className="w-4 h-4" />
          <span>Add Suppression</span>
        </button>
      </div>

      <div className="bg-[#111827] rounded-xl border border-slate-800 overflow-hidden shadow-lg">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 bg-[#090D14]/80 text-slate-400 font-mono text-[10px] uppercase">
              <th className="p-3">Email Address</th>
              <th className="p-3">Reason</th>
              <th className="p-3">Source</th>
              <th className="p-3">Added Date</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
            {entries.map((e) => (
              <tr key={e.id} className="hover:bg-slate-800/40 transition">
                <td className="p-3 font-semibold text-slate-100">{e.email}</td>
                <td className="p-3">
                  <span className="px-2 py-0.5 rounded text-[10px] bg-rose-500/10 text-rose-400 border border-rose-500/20">
                    {e.reason}
                  </span>
                </td>
                <td className="p-3 text-slate-400">{e.source}</td>
                <td className="p-3 text-slate-400">{new Date(e.created_at).toLocaleDateString()}</td>
                <td className="p-3 text-right font-sans">
                  <button onClick={() => handleDelete(e.id)} className="text-slate-400 hover:text-rose-400 transition">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 overflow-hidden flex items-center justify-center bg-black/70 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-[#0F172A] border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-100">Add Email to Suppression List</h3>
              <button onClick={() => setShowModal(false)} className="p-1 text-slate-400 hover:text-slate-200 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAdd} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="optout@example.com"
                  className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Reason</label>
                <select
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="OPT_OUT">User Opt-Out</option>
                  <option value="HARD_BOUNCE">Hard Bounce</option>
                  <option value="COMPLAINT">Complaint</option>
                  <option value="MANUAL">Manual Suppression</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-slate-400 hover:text-slate-200">
                  Cancel
                </button>
                <button type="submit" className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-2.5 rounded-xl">
                  Add Entry
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
