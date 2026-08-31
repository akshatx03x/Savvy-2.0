'use client';

import React, { useState, useEffect } from 'react';
import { Tag, Plus, Edit2, Trash2, CheckCircle2, Sparkles, X, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { OfferProfile } from '@/lib/types';

export default function OffersSettingsPage() {
  const [offers, setOffers] = useState<OfferProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingOffer, setEditingOffer] = useState<OfferProfile | null>(null);

  const [form, setForm] = useState({
    name: '',
    description: '',
    target_customer: '',
    value_proposition: '',
    differentiators: '',
    proof_points: '',
    cta: 'Would you be open to a 15-minute call?',
    tone_preferences: 'Consultative',
  });

  const loadOffers = async () => {
    setLoading(true);
    try {
      const data = await api.getOffers(false);
      setOffers(data);
    } catch (e) {
      setOffers([
        {
          id: 'o1',
          name: 'Website Conversion Optimization',
          description: 'We help real estate businesses improve website inquiry conversion rates.',
          target_customer: 'Real Estate Businesses',
          value_proposition: 'Turn more website visitors into qualified buyer & seller inquiries.',
          differentiators: 'Dedicated real estate conversion workflows.',
          proof_points: 'Average 34% increase in online inquiries.',
          cta: 'Would you be open to a 15-minute audit?',
          tone_preferences: 'Consultative',
          is_active: true,
          is_synthetic: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'o2',
          name: 'AI Lead Generation',
          description: 'Automated lead discovery and intelligence platform.',
          target_customer: 'B2B Businesses',
          value_proposition: 'Discover verified prospects with zero manual research.',
          cta: 'Would you be open to seeing a 2-minute demo?',
          tone_preferences: 'Direct',
          is_active: true,
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
    loadOffers();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.value_proposition) return;

    try {
      if (editingOffer) {
        await api.updateOffer(editingOffer.id, form);
      } else {
        await api.createOffer(form);
      }
      setShowModal(false);
      setEditingOffer(null);
      resetForm();
      loadOffers();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this offer?')) return;
    try {
      await api.deleteOffer(id);
      loadOffers();
    } catch (e) {
      console.error(e);
    }
  };

  const resetForm = () => {
    setForm({
      name: '',
      description: '',
      target_customer: '',
      value_proposition: '',
      differentiators: '',
      proof_points: '',
      cta: 'Would you be open to a 15-minute call?',
      tone_preferences: 'Consultative',
    });
  };

  const openCreateModal = () => {
    resetForm();
    setEditingOffer(null);
    setShowModal(true);
  };

  const openEditModal = (off: OfferProfile) => {
    setEditingOffer(off);
    setForm({
      name: off.name,
      description: off.description,
      target_customer: off.target_customer,
      value_proposition: off.value_proposition,
      differentiators: off.differentiators || '',
      proof_points: off.proof_points || '',
      cta: off.cta,
      tone_preferences: off.tone_preferences || 'Consultative',
    });
    setShowModal(true);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Your Offers</h1>
          <p className="text-xs text-slate-400 mt-1">Configure user offer profiles consumed by Module 3 AI outreach generator.</p>
        </div>
        <button
          onClick={openCreateModal}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-xl text-xs shadow-md shadow-indigo-600/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>Create Offer</span>
        </button>
      </div>

      {/* Offer Cards List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {offers.map((off) => (
          <div key={off.id} className="bg-[#111827] p-5 rounded-2xl border border-slate-800 space-y-3 relative group hover:border-indigo-500/40 transition">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-slate-100">{off.name}</h3>
                  <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">
                    Active
                  </span>
                </div>
                <p className="text-xs text-indigo-400 mt-0.5 font-medium">{off.target_customer}</p>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => openEditModal(off)}
                  className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(off.id)}
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">{off.value_proposition}</p>

            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
              <span className="font-mono">CTA: {off.cta}</span>
              <span className="text-slate-500">{off.tone_preferences}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Create / Edit Offer Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 overflow-hidden flex items-center justify-center bg-black/70 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-[#0F172A] border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-100">{editingOffer ? 'Edit Offer Profile' : 'Create Offer Profile'}</h3>
              <button onClick={() => setShowModal(false)} className="p-1 text-slate-400 hover:text-slate-200 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSave} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Offer Name</label>
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="e.g. Website Conversion Optimization"
                  className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">What do you sell?</label>
                <textarea
                  rows={2}
                  required
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder="e.g. We help real estate businesses improve website lead conversion."
                  className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500 resize-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Who is it for?</label>
                <input
                  type="text"
                  required
                  value={form.target_customer}
                  onChange={(e) => setForm({ ...form, target_customer: e.target.value })}
                  placeholder="e.g. Real Estate Brokers & Property Managers"
                  className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Main Value Proposition</label>
                <input
                  type="text"
                  required
                  value={form.value_proposition}
                  onChange={(e) => setForm({ ...form, value_proposition: e.target.value })}
                  placeholder="e.g. Turn more website visitors into qualified inquiries."
                  className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Preferred CTA</label>
                <input
                  type="text"
                  required
                  value={form.cta}
                  onChange={(e) => setForm({ ...form, cta: e.target.value })}
                  placeholder="e.g. Would you be open to a 15-minute audit?"
                  className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-lg text-slate-400 hover:text-slate-200 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-2.5 rounded-xl transition"
                >
                  Save Offer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
