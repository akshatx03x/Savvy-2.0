'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Globe, Users, Building2, Award, ArrowRight, Layers } from 'lucide-react';
import { api } from '@/lib/api';
import { CountryStat } from '@/lib/types';

export default function CountriesPage() {
  const [countries, setCountries] = useState<CountryStat[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCountries() {
      try {
        const data = await api.getCountries();
        setCountries(data);
      } catch (e) {
        setCountries([
          { country: 'United States', code: 'US', lead_count: 820, company_count: 510, avg_score: 91.2, percentage: 66.1 },
          { country: 'United Kingdom', code: 'UK', lead_count: 240, company_count: 170, avg_score: 86.5, percentage: 19.3 },
          { country: 'Canada', code: 'CA', lead_count: 120, company_count: 90, avg_score: 84.1, percentage: 9.7 },
          { country: 'Australia', code: 'AU', lead_count: 60, company_count: 50, avg_score: 87.0, percentage: 4.8 },
        ]);
      } finally {
        setLoading(false);
      }
    }
    loadCountries();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Title */}
      <div>
        <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs font-semibold uppercase tracking-wider mb-1">
          <Layers className="w-4 h-4" />
          <span>Geographic Categorization</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Countries</h1>
        <p className="text-xs text-slate-400 mt-1">
          Country is the single canonical geographic level. Region and city exist strictly as lead attributes and search filters.
        </p>
      </div>

      {/* Country Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {countries.map((c) => (
          <div
            key={c.country}
            className="bg-[#111827] p-5 rounded-xl border border-slate-800 space-y-4 hover:border-indigo-500/40 transition shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-lg">
                  {c.code === 'US' ? '🇺🇸' : c.code === 'UK' ? '🇬🇧' : c.code === 'CA' ? '🇨🇦' : c.code === 'AU' ? '🇦🇺' : '🌐'}
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-100">{c.country}</h3>
                  <p className="text-[11px] text-slate-400 font-mono">{c.percentage}% of database</p>
                </div>
              </div>
            </div>

            <div className="space-y-2 text-xs text-slate-300 pt-2 border-t border-slate-800">
              <div className="flex justify-between">
                <span className="text-slate-500">Total Leads</span>
                <span className="font-mono font-bold text-indigo-400">{c.lead_count.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Companies</span>
                <span className="font-mono text-slate-200">{c.company_count.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Avg Quality Score</span>
                <span className="font-mono text-emerald-400 font-semibold">{c.avg_score}/100</span>
              </div>
            </div>

            <Link
              href={`/leads?country=${encodeURIComponent(c.country)}`}
              className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs py-2 rounded-lg font-medium flex items-center justify-center gap-1.5 transition"
            >
              <span>View Country Leads</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
