'use client';

import React, { useState } from 'react';
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
    <div className="fixed inset-0 z-50 overflow-hidden flex items-center justify-center bg-slate-900/30 backdrop-blur-xs">
      <div className="bg-white border border-slate-200 rounded-lg max-w-md w-full p-6 shadow-xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Research {selectedLeadIds.length} leads</h3>
            <p className="text-xs text-slate-500 mt-0.5">Extract verified company findings and business signals.</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 text-lg font-bold">
            ×
          </button>
        </div>

        {/* Depth Selector Cards */}
        <div className="space-y-3">
          <div
            onClick={() => setDepth('basic')}
            className={`p-3.5 rounded-md border cursor-pointer transition flex items-start gap-3 ${
              depth === 'basic' ? 'bg-slate-50 border-slate-900 text-slate-900' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
            }`}
          >
            <div>
              <div className="text-xs font-semibold">Basic Research</div>
              <p className="text-[11px] text-slate-500 mt-0.5">Company website, public description, and contact info.</p>
            </div>
          </div>

          <div
            onClick={() => setDepth('standard')}
            className={`p-3.5 rounded-md border cursor-pointer transition flex items-start gap-3 ${
              depth === 'standard' ? 'bg-slate-50 border-slate-900 text-slate-900' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
            }`}
          >
            <div>
              <div className="text-xs font-semibold">Standard Research</div>
              <p className="text-[11px] text-slate-500 mt-0.5">Basic + services/products and verified public announcements.</p>
            </div>
          </div>

          <div
            onClick={() => setDepth('deep')}
            className={`p-3.5 rounded-md border cursor-pointer transition flex items-start gap-3 ${
              depth === 'deep' ? 'bg-slate-50 border-slate-900 text-slate-900' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
            }`}
          >
            <div>
              <div className="text-xs font-semibold">Deep Research</div>
              <p className="text-[11px] text-slate-500 mt-0.5">Standard + broader web discovery and hiring/expansion signals.</p>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            onClick={handleStartResearch}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Starting...' : 'Start research'}
          </button>
        </div>
      </div>
    </div>
  );
}
