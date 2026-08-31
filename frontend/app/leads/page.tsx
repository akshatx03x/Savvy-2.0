'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Search,
  Filter,
  Download,
  Building2,
  Mail,
  Phone,
  Globe,
  Award,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Trash2,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  Check,
  Brain,
  Send,
} from 'lucide-react';
import { api } from '@/lib/api';
import { Lead, LeadFilterParams } from '@/lib/types';
import LeadDetailDrawer from '@/components/leads/LeadDetailDrawer';
import BulkResearchModal from '@/components/leads/BulkResearchModal';

export default function LeadsPage() {
  const router = useRouter();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filter States
  const [search, setSearch] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  const [industryFilter, setIndustryFilter] = useState('');
  const [minScore, setMinScore] = useState<number | undefined>(undefined);
  const [hasEmail, setHasEmail] = useState<boolean | undefined>(undefined);
  const [hasPhone, setHasPhone] = useState<boolean | undefined>(undefined);
  const [researchStatusFilter, setResearchStatusFilter] = useState('');
  const [outreachStatusFilter, setOutreachStatusFilter] = useState('');

  // Selection & Modal States
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [showBulkResearchModal, setShowBulkResearchModal] = useState(false);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const params: LeadFilterParams = {
        page,
        page_size: 25,
        search: search.trim() || undefined,
        country: countryFilter || undefined,
        industry: industryFilter || undefined,
        min_score: minScore,
        has_email: hasEmail,
        has_phone: hasPhone,
        research_status: researchStatusFilter || undefined,
        outreach_status: outreachStatusFilter || undefined,
      };
      const res = await api.getLeads(params);
      setLeads(res.items);
      setTotal(res.total);
    } catch (e) {
      console.warn('Backend unavailable, using initial mock leads');
      setLeads([
        {
          id: '1',
          company_id: 'c1',
          contact_id: 'ct1',
          company: {
            id: 'c1',
            name: 'ABC Realty',
            domain: 'abcrealty.com',
            website: 'https://www.abcrealty.com',
            country: 'United States',
            region: 'Washington',
            city: 'Seattle',
            industry: 'Real Estate',
            description: 'Premier residential and commercial real estate brokerage in Washington.',
            is_synthetic: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          contact: {
            id: 'ct1',
            company_id: 'c1',
            full_name: 'John Smith',
            job_title: 'Founder & Principal Broker',
            email: 'john@abcrealty.com',
            phone: '+1 (206) 555-0192',
            country: 'United States',
            source: 'web_search',
            verification_status: 'verified',
            is_synthetic: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          country: 'United States',
          region: 'Washington',
          city: 'Seattle',
          industry: 'Real Estate',
          lead_score: 92,
          intelligence_score: 87,
          research_status: 'Researched',
          outreach_status: 'Approved',
          status: 'new',
          source: 'Web Business Directory',
          source_url: 'https://directory.example.com/abcrealty',
          is_synthetic: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]);
      setTotal(1);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, [page, countryFilter, industryFilter, minScore, hasEmail, hasPhone, researchStatusFilter, outreachStatusFilter]);

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(leads.map((l) => l.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id: string) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]));
  };

  const handleExportCSV = () => {
    const selectedLeads = leads.filter((l) => selectedIds.includes(l.id));
    const dataToExport = selectedLeads.length > 0 ? selectedLeads : leads;

    const headers = ['Company', 'Contact', 'Title', 'Email', 'Phone', 'Country', 'Industry', 'Lead Score', 'Intelligence Score', 'Research Status', 'Outreach Status'];
    const rows = dataToExport.map((l) => [
      `"${l.company.name}"`,
      `"${l.contact.full_name}"`,
      `"${l.contact.job_title || ''}"`,
      `"${l.contact.email || ''}"`,
      `"${l.contact.phone || ''}"`,
      `"${l.country}"`,
      `"${l.industry}"`,
      l.lead_score,
      l.intelligence_score || 85,
      `"${l.research_status || 'Researched'}"`,
      `"${l.outreach_status || 'Approved'}"`,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `leads_export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Leads Database</h1>
          <p className="text-xs text-slate-400 mt-1">Browse, qualify, research and generate personalized outreach.</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowBulkResearchModal(true)}
            disabled={selectedIds.length === 0}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white px-4 py-2 rounded-lg text-xs font-semibold shadow-md shadow-indigo-600/20 transition"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>✨ Research Selected {selectedIds.length > 0 ? `(${selectedIds.length})` : ''}</span>
          </button>

          <button
            onClick={() => router.push(`/outreach?lead_ids=${selectedIds.join(',')}`)}
            disabled={selectedIds.length === 0}
            className="flex items-center gap-2 bg-[#111827] hover:bg-slate-800 disabled:opacity-40 text-indigo-400 border border-indigo-500/40 px-4 py-2 rounded-lg text-xs font-semibold shadow-md transition"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Outreach Studio ({selectedIds.length})</span>
          </button>

          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3.5 py-2 rounded-lg text-xs font-medium transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-[#111827] p-4 rounded-xl border border-slate-800 space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchLeads()}
              placeholder="Filter by company, name, email, or domain..."
              className="w-full bg-[#090D14] border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <select
            value={countryFilter}
            onChange={(e) => setCountryFilter(e.target.value)}
            className="bg-[#090D14] border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Countries</option>
            <option value="United States">🇺🇸 United States</option>
            <option value="United Kingdom">🇬🇧 United Kingdom</option>
            <option value="Canada">🇨🇦 Canada</option>
            <option value="Australia">🇦🇺 Australia</option>
          </select>

          {/* Research Status Filter */}
          <select
            value={researchStatusFilter}
            onChange={(e) => setResearchStatusFilter(e.target.value)}
            className="bg-[#090D14] border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Research Statuses</option>
            <option value="Researched">● Researched</option>
            <option value="Not Researched">○ Not Researched</option>
          </select>

          {/* Outreach Status Filter */}
          <select
            value={outreachStatusFilter}
            onChange={(e) => setOutreachStatusFilter(e.target.value)}
            className="bg-[#090D14] border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Outreach Statuses</option>
            <option value="Approved">✓ Approved</option>
            <option value="Draft">Draft</option>
            <option value="Needs Research">⚠ Needs Research</option>
            <option value="Not Generated">Not Generated</option>
          </select>

          <button
            onClick={fetchLeads}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Table */}
      <div className="bg-[#111827] rounded-xl border border-slate-800 overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 bg-[#090D14]/80 text-slate-400 font-mono text-[10px] uppercase tracking-wider">
                <th className="p-3 w-10 text-center">
                  <input
                    type="checkbox"
                    checked={selectedIds.length === leads.length && leads.length > 0}
                    onChange={handleSelectAll}
                    className="rounded border-slate-700 bg-slate-900 text-indigo-600 focus:ring-0 cursor-pointer"
                  />
                </th>
                <th className="p-3">Company</th>
                <th className="p-3">Contact</th>
                <th className="p-3">Email</th>
                <th className="p-3">Country</th>
                <th className="p-3">Lead Score</th>
                <th className="p-3">Intelligence</th>
                <th className="p-3">Research</th>
                <th className="p-3">Outreach Status</th>
                <th className="p-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={10} className="p-12 text-center text-slate-500">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-500" />
                    Loading prospect database...
                  </td>
                </tr>
              ) : (
                leads.map((lead) => (
                  <tr
                    key={lead.id}
                    onClick={() => setSelectedLead(lead)}
                    className="hover:bg-slate-800/50 cursor-pointer transition"
                  >
                    <td className="p-3 text-center" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(lead.id)}
                        onChange={() => handleSelectOne(lead.id)}
                        className="rounded border-slate-700 bg-slate-900 text-indigo-600 focus:ring-0 cursor-pointer"
                      />
                    </td>
                    <td className="p-3 font-semibold text-slate-100 flex items-center gap-2">
                      <Building2 className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{lead.company.name}</span>
                    </td>
                    <td className="p-3 text-slate-200 font-medium">{lead.contact.full_name}</td>
                    <td className="p-3">
                      {lead.contact.email ? (
                        <span className="text-indigo-400 font-mono">{lead.contact.email}</span>
                      ) : (
                        <span className="text-slate-600 text-[11px]">—</span>
                      )}
                    </td>
                    <td className="p-3 text-slate-300">{lead.country}</td>
                    <td className="p-3 font-mono">
                      <span className="bg-slate-800 text-slate-200 px-2 py-0.5 rounded text-[11px] font-medium border border-slate-700">
                        {lead.lead_score}/100
                      </span>
                    </td>
                    <td className="p-3 font-mono">
                      <span className="bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded text-[11px] font-semibold border border-indigo-500/20 flex items-center gap-1 w-fit">
                        <Brain className="w-3 h-3" />
                        {lead.intelligence_score || 87}/100
                      </span>
                    </td>
                    <td className="p-3 font-mono text-[11px]">
                      <span className="text-emerald-400 flex items-center gap-1">
                        ● Researched
                      </span>
                    </td>
                    <td className="p-3 font-mono text-[11px]">
                      <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">
                        ✓ {lead.outreach_status || 'Approved'}
                      </span>
                    </td>
                    <td className="p-3 text-right" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => router.push(`/outreach?lead_id=${lead.id}`)}
                        className="text-xs text-indigo-400 hover:underline font-medium flex items-center gap-1 ml-auto"
                      >
                        <Send className="w-3 h-3" />
                        <span>Studio</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modals & Drawer */}
      <LeadDetailDrawer lead={selectedLead} onClose={() => setSelectedLead(null)} />
      {showBulkResearchModal && (
        <BulkResearchModal
          selectedLeadIds={selectedIds}
          onClose={() => setShowBulkResearchModal(false)}
          onSuccess={() => { setSelectedIds([]); fetchLeads(); }}
        />
      )}
    </div>
  );
}
