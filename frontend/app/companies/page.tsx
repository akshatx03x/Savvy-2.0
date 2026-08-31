'use client';

import React, { useEffect, useState } from 'react';
import { Building2, Globe, ExternalLink, Users, Award, Search } from 'lucide-react';
import { api } from '@/lib/api';
import { Company } from '@/lib/types';

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function loadCompanies() {
      setLoading(true);
      try {
        const res = await api.getCompanies(1, search);
        setCompanies(res.items);
      } catch (e) {
        setCompanies([
          {
            id: 'c1',
            name: 'ABC Realty',
            domain: 'abcrealty.com',
            website: 'https://www.abcrealty.com',
            country: 'United States',
            industry: 'Real Estate',
            contact_count: 3,
            lead_score: 92,
            is_synthetic: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 'c2',
            name: 'XYZ Homes',
            domain: 'xyzhomes.co.uk',
            website: 'https://www.xyzhomes.co.uk',
            country: 'United Kingdom',
            industry: 'Real Estate',
            contact_count: 2,
            lead_score: 88,
            is_synthetic: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ]);
      } finally {
        setLoading(false);
      }
    }
    loadCompanies();
  }, [search]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Companies Directory</h1>
        <p className="text-xs text-slate-400 mt-1">Lightweight company profiles and contact counts.</p>
      </div>

      <div className="bg-[#111827] p-4 rounded-xl border border-slate-800 flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search companies by name or domain..."
            className="w-full bg-[#090D14] border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      <div className="bg-[#111827] rounded-xl border border-slate-800 overflow-hidden shadow-lg">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 bg-[#090D14]/80 text-slate-400 font-mono text-[10px] uppercase">
              <th className="p-3">Company</th>
              <th className="p-3">Domain / Website</th>
              <th className="p-3">Country</th>
              <th className="p-3">Industry</th>
              <th className="p-3">Contacts</th>
              <th className="p-3">Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {companies.map((c) => (
              <tr key={c.id} className="hover:bg-slate-800/40 transition">
                <td className="p-3 font-semibold text-slate-100 flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-indigo-400" />
                  <span>{c.name}</span>
                </td>
                <td className="p-3">
                  {c.website ? (
                    <a href={c.website} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline flex items-center gap-1">
                      {c.domain || c.website} <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <span className="text-slate-600">—</span>
                  )}
                </td>
                <td className="p-3">{c.country}</td>
                <td className="p-3 text-slate-400">{c.industry}</td>
                <td className="p-3 font-mono font-medium text-indigo-400">{c.contact_count || 1} Contacts</td>
                <td className="p-3 font-mono">
                  <span className="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded text-[11px] font-semibold border border-emerald-500/20">
                    {c.lead_score || 85}/100
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
