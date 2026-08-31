'use client';

import React from 'react';
import { X, ExternalLink, ShieldCheck, Calendar, Award, CheckCircle2 } from 'lucide-react';
import { Evidence } from '@/lib/types';

interface Props {
  evidence: Evidence | null;
  findingTitle?: string;
  onClose: () => void;
}

export default function EvidenceModal({ evidence, findingTitle, onClose }: Props) {
  if (!evidence) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex items-center justify-center bg-black/70 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-[#0F172A] border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-6 relative">
        <div className="flex items-start justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100">Verified Evidence Provenance</h3>
              <p className="text-xs text-slate-400">{evidence.source_name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Finding Subject */}
        {findingTitle && (
          <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800 text-xs">
            <div className="text-[10px] font-mono uppercase text-slate-500 mb-0.5">Finding Subject</div>
            <div className="font-semibold text-slate-200">{findingTitle}</div>
          </div>
        )}

        {/* Evidence Snippet */}
        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-300">Supporting Context Snippet</div>
          <div className="bg-[#090D14] p-4 rounded-xl border border-slate-800/80 text-xs text-slate-300 italic leading-relaxed">
            "{evidence.supporting_snippet}"
          </div>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <div className="text-[10px] font-mono text-slate-500 uppercase">Confidence Score</div>
            <div className="text-sm font-bold text-emerald-400 font-mono mt-0.5 flex items-center gap-1">
              <Award className="w-3.5 h-3.5" />
              {Math.round(evidence.confidence * 100)}% Verified
            </div>
          </div>

          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <div className="text-[10px] font-mono text-slate-500 uppercase">Type & Classification</div>
            <div className="text-xs font-semibold text-slate-200 capitalize mt-0.5">
              {evidence.is_observation_vs_inference} ({evidence.recency_tier})
            </div>
          </div>
        </div>

        {/* Source Action Link */}
        <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
          <div className="text-[11px] text-slate-500 font-mono flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            Discovered: {evidence.published_date ? new Date(evidence.published_date).toLocaleDateString() : 'Recent'}
          </div>
          <a
            href={evidence.source_url}
            target="_blank"
            rel="noreferrer"
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-xs font-medium flex items-center gap-1.5 shadow-md shadow-indigo-600/20 transition"
          >
            <span>Open Source Webpage</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
}
