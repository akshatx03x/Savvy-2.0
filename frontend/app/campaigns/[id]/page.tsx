'use client';

import React from 'react';
import Link from 'next/link';

export default function CampaignDetailPage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Washington Real Estate</h1>
            <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded text-[11px] font-medium">
              Active
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">486 recipients • Created Aug 30, 2026</p>
        </div>
        <Link href="/campaigns" className="btn-secondary">
          ← Back to campaigns
        </Link>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
        <div className="p-3.5 bg-white border border-slate-200 rounded-md">
          <div className="text-[11px] text-slate-500 font-medium">Sent</div>
          <div className="text-lg font-bold text-slate-900 mt-0.5">342</div>
        </div>
        <div className="p-3.5 bg-white border border-slate-200 rounded-md">
          <div className="text-[11px] text-slate-500 font-medium">Delivered</div>
          <div className="text-lg font-bold text-slate-900 mt-0.5">337</div>
        </div>
        <div className="p-3.5 bg-white border border-slate-200 rounded-md">
          <div className="text-[11px] text-slate-500 font-medium">Replies</div>
          <div className="text-lg font-bold text-slate-900 mt-0.5">31</div>
        </div>
        <div className="p-3.5 bg-white border border-slate-200 rounded-md">
          <div className="text-[11px] text-slate-500 font-medium">Positive replies</div>
          <div className="text-lg font-bold text-slate-900 mt-0.5">12</div>
        </div>
        <div className="p-3.5 bg-white border border-slate-200 rounded-md">
          <div className="text-[11px] text-slate-500 font-medium">Bounced</div>
          <div className="text-lg font-bold text-slate-900 mt-0.5">5</div>
        </div>
        <div className="p-3.5 bg-white border border-slate-200 rounded-md">
          <div className="text-[11px] text-slate-500 font-medium">Opt-outs</div>
          <div className="text-lg font-bold text-slate-900 mt-0.5">2</div>
        </div>
      </div>

      {/* Recipients Table */}
      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-xs">
        <div className="p-4 border-b border-slate-200 font-semibold text-xs text-slate-900">
          Recipients
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                <th className="p-3">Contact</th>
                <th className="p-3">Company</th>
                <th className="p-3">Email</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              <tr className="hover:bg-slate-50">
                <td className="p-3 font-semibold text-slate-900">John Smith</td>
                <td className="p-3 text-slate-700">ABC Realty</td>
                <td className="p-3 text-slate-600">john@abc.com</td>
                <td className="p-3"><span className="text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded text-[11px]">Sent</span></td>
              </tr>
              <tr className="hover:bg-slate-50">
                <td className="p-3 font-semibold text-slate-900">Sarah Williams</td>
                <td className="p-3 text-slate-700">Cascade Properties</td>
                <td className="p-3 text-slate-600">sarah@cascadeproperties.com</td>
                <td className="p-3"><span className="text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded text-[11px]">Replied</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
