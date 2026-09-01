'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import NewCampaignModal from '@/components/campaigns/NewCampaignModal';

interface Campaign {
  id: string;
  name: string;
  recipients_count: number;
  sent_count: number;
  replies_count: number;
  status: 'active' | 'paused' | 'completed' | 'draft';
  created_at: string;
}

function CampaignsContent() {
  const searchParams = useSearchParams();
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    if (searchParams.get('modal') === 'new') {
      setIsModalOpen(true);
    }
  }, [searchParams]);

  const [campaigns, setCampaigns] = useState<Campaign[]>([
    {
      id: 'c1',
      name: 'Washington Real Estate',
      recipients_count: 486,
      sent_count: 342,
      replies_count: 31,
      status: 'active',
      created_at: '2026-08-30',
    },
    {
      id: 'c2',
      name: 'SaaS Decision Makers Outreach',
      recipients_count: 210,
      sent_count: 210,
      replies_count: 18,
      status: 'completed',
      created_at: '2026-08-25',
    },
  ]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Campaigns</h1>
          <p className="text-xs text-slate-500 mt-0.5">Manage and send your automated outreach campaigns.</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="btn-primary"
        >
          + New campaign
        </button>
      </div>

      {/* Campaigns Table */}
      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                <th className="p-3">Campaign</th>
                <th className="p-3">Recipients</th>
                <th className="p-3">Sent</th>
                <th className="p-3">Replies</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {campaigns.length > 0 ? (
                campaigns.map((camp) => (
                  <tr key={camp.id} className="hover:bg-slate-50 transition">
                    <td className="p-3">
                      <Link href={`/campaigns/${camp.id}`} className="font-semibold text-slate-900 hover:underline">
                        {camp.name}
                      </Link>
                    </td>
                    <td className="p-3 text-slate-700">{camp.recipients_count}</td>
                    <td className="p-3 text-slate-700">{camp.sent_count}</td>
                    <td className="p-3 text-slate-700">{camp.replies_count}</td>
                    <td className="p-3">
                      <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-medium capitalize border ${
                        camp.status === 'active'
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                          : 'bg-slate-100 text-slate-700 border-slate-200'
                      }`}>
                        {camp.status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="p-12 text-center text-slate-500 space-y-2">
                    <div>No campaigns yet.</div>
                    <button onClick={() => setIsModalOpen(true)} className="btn-primary mt-2">
                      Create campaign
                    </button>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <NewCampaignModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCampaignCreated={() => {
          setCampaigns((prev) => [
            {
              id: `c_${Date.now()}`,
              name: 'New Outreach Campaign',
              recipients_count: 150,
              sent_count: 0,
              replies_count: 0,
              status: 'active',
              created_at: new Date().toISOString().split('T')[0],
            },
            ...prev,
          ]);
        }}
      />
    </div>
  );
}

export default function CampaignsPage() {
  return (
    <Suspense fallback={<div className="text-xs text-slate-500 p-6">Loading campaigns...</div>}>
      <CampaignsContent />
    </Suspense>
  );
}
