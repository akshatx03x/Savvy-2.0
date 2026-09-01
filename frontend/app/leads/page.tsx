'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Lead, PaginatedLeadsResponse } from '@/lib/types';
import LeadDetailDrawer from '@/components/leads/LeadDetailDrawer';
import FindLeadsModal from '@/components/leads/FindLeadsModal';
import { useToast } from '@/components/common/ToastContext';

function LeadsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { showToast } = useToast();

  const [leadsData, setLeadsData] = useState<PaginatedLeadsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  const [industryFilter, setIndustryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showMoreFilters, setShowMoreFilters] = useState(false);

  // Modal / Drawer state
  const [isFindModalOpen, setIsFindModalOpen] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  useEffect(() => {
    if (searchParams.get('modal') === 'find') {
      setIsFindModalOpen(true);
    }
  }, [searchParams]);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const res = await api.getLeads({
        search: search || undefined,
        country: countryFilter || undefined,
        industry: industryFilter || undefined,
        status: statusFilter || undefined,
        page: 1,
        page_size: 50,
      });
      setLeadsData(res);
    } catch (e) {
      showToast('Could not load leads.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, [search, countryFilter, industryFilter, statusFilter]);

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked && leadsData) {
      setSelectedIds(leadsData.items.map((l) => l.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleToggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Leads</h1>
          <p className="text-xs text-slate-500 mt-0.5">Find and manage your prospects.</p>
        </div>
        <button
          onClick={() => setIsFindModalOpen(true)}
          className="btn-primary flex items-center gap-1.5"
        >
          <span>+ Find leads</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {/* Main Search Input */}
          <div className="md:col-span-2">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search companies, people or email..."
              className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900"
            />
          </div>

          {/* Country Filter */}
          <div>
            <select
              value={countryFilter}
              onChange={(e) => setCountryFilter(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-slate-900"
            >
              <option value="">All countries</option>
              <option value="United States">United States</option>
              <option value="United Kingdom">United Kingdom</option>
              <option value="Canada">Canada</option>
              <option value="India">India</option>
              <option value="Australia">Australia</option>
              <option value="Germany">Germany</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-slate-900"
            >
              <option value="">All statuses</option>
              <option value="new">New</option>
              <option value="researched">Researched</option>
              <option value="contacted">Contacted</option>
              <option value="qualified">Qualified</option>
            </select>
          </div>
        </div>

        {/* More Filters Toggle */}
        <div className="flex items-center justify-between pt-1 text-xs">
          <button
            type="button"
            onClick={() => setShowMoreFilters(!showMoreFilters)}
            className="text-slate-600 hover:text-slate-900 font-medium"
          >
            {showMoreFilters ? '- Fewer filters' : '+ More filters'}
          </button>
          <span className="text-slate-500">
            {leadsData ? `${leadsData.total} leads found` : 'Loading...'}
          </span>
        </div>

        {showMoreFilters && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2 border-t border-slate-100">
            <div>
              <label className="block text-[11px] font-medium text-slate-600 mb-1">Industry</label>
              <input
                type="text"
                value={industryFilter}
                onChange={(e) => setIndustryFilter(e.target.value)}
                placeholder="e.g. Real Estate"
                className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-900"
              />
            </div>
          </div>
        )}
      </div>

      {/* Main Leads Table */}
      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                <th className="p-3 w-10">
                  <input
                    type="checkbox"
                    onChange={handleSelectAll}
                    checked={Boolean(
                      leadsData?.items &&
                      leadsData.items.length > 0 &&
                      selectedIds.length === leadsData.items.length
                    )}
                    className="rounded border-slate-300 text-slate-900 focus:ring-0"
                  />
                </th>
                <th className="p-3">Company</th>
                <th className="p-3">Contact</th>
                <th className="p-3">Job title</th>
                <th className="p-3">Email</th>
                <th className="p-3">Country</th>
                <th className="p-3">Score</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-slate-400">
                    Loading leads...
                  </td>
                </tr>
              ) : leadsData?.items && leadsData.items.length > 0 ? (
                leadsData.items.map((lead) => (
                  <tr
                    key={lead.id}
                    onClick={() => setSelectedLead(lead)}
                    className="hover:bg-slate-50 cursor-pointer transition"
                  >
                    <td className="p-3" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(lead.id)}
                        onChange={() => handleToggleSelect(lead.id)}
                        className="rounded border-slate-300 text-slate-900 focus:ring-0"
                      />
                    </td>
                    <td className="p-3 font-semibold text-slate-900">{lead.company.name}</td>
                    <td className="p-3 text-slate-800">{lead.contact?.full_name || 'Not found'}</td>
                    <td className="p-3 text-slate-600">{lead.contact?.job_title || 'Not available'}</td>
                    <td className="p-3 text-slate-600">{lead.contact?.email || 'Not available'}</td>
                    <td className="p-3 text-slate-600">{lead.country}</td>
                    <td className="p-3 font-mono font-medium text-slate-900">{lead.lead_score}</td>
                    <td className="p-3">
                      <span className="inline-block px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-800 border border-slate-200 capitalize">
                        {lead.status || 'new'}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="p-12 text-center text-slate-500 space-y-2">
                    <div>No leads yet.</div>
                    <div className="text-xs text-slate-400">Find your first prospects to get started.</div>
                    <button
                      onClick={() => setIsFindModalOpen(true)}
                      className="btn-primary mt-2"
                    >
                      Find leads
                    </button>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Find Leads Modal */}
      <FindLeadsModal
        isOpen={isFindModalOpen}
        onClose={() => {
          setIsFindModalOpen(false);
          router.replace('/leads');
        }}
        onSearchComplete={fetchLeads}
      />

      {/* Lead Detail Drawer */}
      <LeadDetailDrawer
        lead={selectedLead}
        onClose={() => setSelectedLead(null)}
      />
    </div>
  );
}

export default function LeadsPage() {
  return (
    <Suspense fallback={<div className="text-xs text-slate-500 p-6">Loading leads...</div>}>
      <LeadsContent />
    </Suspense>
  );
}
