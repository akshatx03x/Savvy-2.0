'use client';

import React, { useState } from 'react';
import { X, Sparkles, Brain, Check, Play, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

interface Props {
  selectedLeadIds: string[];
  onClose: () => void;
  onSuccess: () => void;
}

export default function BulkResearchModal({ selectedLeadIds, onClose, onSuccess }: Props) {
  const [depth, setDepth] = useState<'basic' | 'standard' | 'deep'>('standard');
  const [loading, setLoading] = useState(false);

  const handleStartResearch = async () => {
    if (selectedLeadIds.length === 0) return;
    setLoading(true);
    try {
      await api.createResearchJob(selectedLeadIds, depth);
      onSuccess();
      onClose();
    } catch (e) {
      console.error('Failed to start research job:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex items-center justify-center bg-black/70 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-[#0F172A] border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-4 h-4" />
            <span>AI Web Research</span>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-200 rounded-lg transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div>
          <h3 className="text-base font-bold text-slate-100">Research {selectedLeadIds.length} Selected Leads</h3>
          <p className="text-xs text-slate-400 mt-1">
            Choose AI web research depth to extract business signals and outreach opportunities.
          </p>
        </div>

        {/* Depth Selector Cards */}
        <div className="space-y-3">
          <div
            onClick={() => setDepth('basic')}
            className={`p-3.5 rounded-xl border cursor-pointer transition flex items-start gap-3 ${
              depth === 'basic' ? 'bg-indigo-600/15 border-indigo-500 text-indigo-300' : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className={`w-4 h-4 rounded-full border flex items-center justify-center mt-0.5 ${depth === 'basic' ? 'border-indigo-400 bg-indigo-500' : 'border-slate-600'}`}>
              {depth === 'basic' && <Check className="w-2.5 h-2.5 text-white" />}
            </div>
            <div>
              <div className="text-xs font-semibold text-slate-200">Basic Research</div>
              <p className="text-[11px] text-slate-400">Company website homepage, description, contact details & primary profiles.</p>
            </div>
          </div>

          <div
            onClick={() => setDepth('standard')}
            className={`p-3.5 rounded-xl border cursor-pointer transition flex items-start gap-3 ${
              depth === 'standard' ? 'bg-indigo-600/15 border-indigo-500 text-indigo-300' : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className={`w-4 h-4 rounded-full border flex items-center justify-center mt-0.5 ${depth === 'standard' ? 'border-indigo-400 bg-indigo-500' : 'border-slate-600'}`}>
              {depth === 'standard' && <Check className="w-2.5 h-2.5 text-white" />}
            </div>
            <div>
              <div className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                <span>Standard Research</span>
                <span className="text-[9px] bg-indigo-500/20 text-indigo-400 px-1.5 py-0.5 rounded font-mono">Recommended</span>
              </div>
              <p className="text-[11px] text-slate-400">Basic + services/products, recent public announcements, and business signals.</p>
            </div>
          </div>

          <div
            onClick={() => setDepth('deep')}
            className={`p-3.5 rounded-xl border cursor-pointer transition flex items-start gap-3 ${
              depth === 'deep' ? 'bg-indigo-600/15 border-indigo-500 text-indigo-300' : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className={`w-4 h-4 rounded-full border flex items-center justify-center mt-0.5 ${depth === 'deep' ? 'border-indigo-400 bg-indigo-500' : 'border-slate-600'}`}>
              {depth === 'deep' && <Check className="w-2.5 h-2.5 text-white" />}
            </div>
            <div>
              <div className="text-xs font-semibold text-slate-200">Deep Research</div>
              <p className="text-[11px] text-slate-400">Standard + broader web discovery, news, hiring signals, and detailed personalization angles.</p>
            </div>
          </div>
        </div>

        {/* Workload Preview */}
        <div className="bg-slate-900/80 p-3.5 rounded-xl border border-slate-800 text-xs text-slate-400 font-mono flex items-center justify-between">
          <span>Estimated Sources Analyzed:</span>
          <span className="text-indigo-400 font-bold">{selectedLeadIds.length * (depth === 'deep' ? 4 : depth === 'standard' ? 3 : 2)} Sources</span>
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <button onClick={onClose} className="px-4 py-2 rounded-lg text-xs text-slate-400 hover:text-slate-200 transition">
            Cancel
          </button>
          <button
            onClick={handleStartResearch}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-2.5 rounded-xl text-xs flex items-center gap-2 shadow-md shadow-indigo-600/20 transition"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
            <span>Start Research Job</span>
          </button>
        </div>
      </div>
    </div>
  );
}
