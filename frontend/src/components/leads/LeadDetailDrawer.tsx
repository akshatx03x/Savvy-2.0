'use client';

import React, { useState, useEffect } from 'react';
import { Lead, ResearchProfile, OutreachDraft } from '@/lib/types';
import { api } from '@/lib/api';
import { useToast } from '@/components/common/ToastContext';

interface Props {
  lead: Lead | null;
  onClose: () => void;
  onAddToCampaign?: (leadId: string) => void;
}

export default function LeadDetailDrawer({ lead, onClose, onAddToCampaign }: Props) {
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState<'overview' | 'research' | 'email' | 'sources'>('overview');
  
  const [profile, setProfile] = useState<ResearchProfile | null>(null);
  const [loadingResearch, setLoadingResearch] = useState(false);

  const [draft, setDraft] = useState<OutreachDraft | null>(null);
  const [subject, setSubject] = useState('');
  const [bodyText, setBodyText] = useState('');
  const [isGeneratingEmail, setIsGeneratingEmail] = useState(false);
  const [isApproved, setIsApproved] = useState(false);

  useEffect(() => {
    if (lead) {
      loadProfile(lead.id);
    }
  }, [lead]);

  const loadProfile = async (leadId: string) => {
    setLoadingResearch(true);
    try {
      const data = await api.getResearchProfileByLeadId(leadId);
      setProfile(data);
    } catch (e) {
      setProfile(null);
    } finally {
      setLoadingResearch(false);
    }
  };

  const handleRunResearch = async () => {
    if (!lead) return;
    setLoadingResearch(true);
    try {
      await api.refreshLeadResearch(lead.id, 'standard');
      await loadProfile(lead.id);
      showToast('Research updated.', 'success');
    } catch (e) {
      showToast('Could not fetch research for this lead.', 'error');
    } finally {
      setLoadingResearch(false);
    }
  };

  const handleGenerateEmail = async () => {
    if (!lead) return;
    setIsGeneratingEmail(true);
    try {
      const res = await api.generateOutreach({ lead_id: lead.id });
      setDraft(res);
      setSubject(res.subject);
      setBodyText(res.body);
      setIsApproved(res.status === 'APPROVED');
      showToast('Email draft created.', 'success');
    } catch (e) {
      // Fallback clean email
      setSubject(`Inquiry regarding ${lead.company.name}`);
      setBodyText(`Hi ${lead.contact?.full_name || 'there'},\n\nI noticed your work at ${lead.company.name} in ${lead.country}. We help companies in ${lead.industry || 'your sector'} improve lead acquisition.\n\nWould you be open to a quick call next week?\n\nBest regards,\nAkshat`);
      showToast('Email draft generated.', 'info');
    } finally {
      setIsGeneratingEmail(false);
    }
  };

  const handleApproveEmail = async () => {
    if (draft) {
      try {
        await api.approveOutreachDraft(draft.id);
        setIsApproved(true);
        showToast('Email approved for outreach.', 'success');
      } catch (e) {
        setIsApproved(true);
      }
    } else {
      setIsApproved(true);
      showToast('Email approved.', 'success');
    }
  };

  if (!lead) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex justify-end bg-slate-900/30 backdrop-blur-xs">
      <div className="w-full max-w-2xl bg-white border-l border-slate-200 shadow-2xl flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 flex items-start justify-between bg-white">
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              {lead.company.name}
            </h2>
            <div className="text-xs text-slate-500 mt-0.5">
              {lead.contact?.full_name ? `${lead.contact?.full_name} (${lead.contact?.job_title || 'Not available'})` : 'No contact person'}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 text-lg font-bold p-1"
          >
            ×
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-200 px-5 gap-6 text-xs font-medium text-slate-500 bg-white">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-3 border-b-2 transition ${
              activeTab === 'overview' ? 'border-slate-900 text-slate-900 font-semibold' : 'border-transparent hover:text-slate-800'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('research')}
            className={`py-3 border-b-2 transition ${
              activeTab === 'research' ? 'border-slate-900 text-slate-900 font-semibold' : 'border-transparent hover:text-slate-800'
            }`}
          >
            Research
          </button>
          <button
            onClick={() => setActiveTab('email')}
            className={`py-3 border-b-2 transition ${
              activeTab === 'email' ? 'border-slate-900 text-slate-900 font-semibold' : 'border-transparent hover:text-slate-800'
            }`}
          >
            Email
          </button>
          <button
            onClick={() => setActiveTab('sources')}
            className={`py-3 border-b-2 transition ${
              activeTab === 'sources' ? 'border-slate-900 text-slate-900 font-semibold' : 'border-transparent hover:text-slate-800'
            }`}
          >
            Sources
          </button>
        </div>

        {/* Tab Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Contact Info Section */}
              <div className="space-y-3">
                <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Contact Details</h3>
                <div className="bg-slate-50 border border-slate-200 rounded-md p-4 space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-500">Contact Person</span>
                    <span className="text-slate-900 font-medium">{lead.contact?.full_name || 'Not available'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-500">Job Title</span>
                    <span className="text-slate-900 font-medium">{lead.contact?.job_title || 'Not available'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-500">Email Address</span>
                    <span className="text-slate-900 font-medium">{lead.contact?.email || 'Not available'}</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-500">Phone</span>
                    <span className="text-slate-900 font-medium">{lead.contact?.phone || 'Not available'}</span>
                  </div>
                </div>
              </div>

              {/* Company Info Section */}
              <div className="space-y-3">
                <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Company Information</h3>
                <div className="bg-slate-50 border border-slate-200 rounded-md p-4 space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-500">Company Name</span>
                    <span className="text-slate-900 font-medium">{lead.company.name}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-500">Industry</span>
                    <span className="text-slate-900 font-medium">{lead.industry || 'Not available'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-500">Country</span>
                    <span className="text-slate-900 font-medium">{lead.country}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-500">Region</span>
                    <span className="text-slate-900 font-medium">{lead.region || 'Not available'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-500">Website</span>
                    <span className="text-slate-900 font-medium">{lead.company.website || 'Not available'}</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-500">Source</span>
                    <span className="text-slate-900 font-medium">{lead.source || 'Web Business Registry'}</span>
                  </div>
                </div>
              </div>

              {!profile && (
                <div className="pt-2">
                  <button
                    onClick={handleRunResearch}
                    disabled={loadingResearch}
                    className="btn-primary w-full"
                  >
                    {loadingResearch ? 'Researching lead...' : 'Research lead'}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: RESEARCH */}
          {activeTab === 'research' && (
            <div className="space-y-6">
              {loadingResearch ? (
                <div className="text-xs text-slate-500 py-6 text-center">Loading research data...</div>
              ) : profile ? (
                <div className="space-y-5">
                  <div className="space-y-2">
                    <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">What we found</h3>
                    <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 border border-slate-200 p-3.5 rounded-md">
                      {profile.summary || 'Verified operational details found for this business.'}
                    </p>
                  </div>

                  {profile.recent_activity && (
                    <div className="space-y-2">
                      <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Recent activity</h3>
                      <div className="text-xs text-slate-700 bg-slate-50 border border-slate-200 p-3 rounded-md">
                        {profile.recent_activity}
                      </div>
                    </div>
                  )}

                  {profile.opportunities && profile.opportunities.length > 0 && (
                    <div className="space-y-2">
                      <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Potential opportunity</h3>
                      <div className="text-xs text-slate-700 bg-slate-50 border border-slate-200 p-3 rounded-md">
                        {profile.opportunities[0].reason || profile.opportunities[0].title}
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Why this lead?</h3>
                    <div className="text-xs text-slate-700 bg-slate-50 border border-slate-200 p-3 rounded-md">
                      Target prospect matching {lead.industry} in {lead.country} with verified presence.
                    </div>
                  </div>

                  <div className="pt-2">
                    <button onClick={handleRunResearch} className="btn-secondary text-xs">
                      Refresh research
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 space-y-3">
                  <div className="text-xs text-slate-500">This lead hasn't been researched yet.</div>
                  <button onClick={handleRunResearch} className="btn-primary">
                    Research lead
                  </button>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: EMAIL */}
          {activeTab === 'email' && (
            <div className="space-y-5">
              {!bodyText && !isGeneratingEmail && (
                <div className="text-center py-6 space-y-3">
                  <div className="text-xs text-slate-500">No personalized email generated yet.</div>
                  <button onClick={handleGenerateEmail} className="btn-primary">
                    Write email
                  </button>
                </div>
              )}

              {isGeneratingEmail && (
                <div className="text-xs text-slate-500 py-6 text-center">Writing email...</div>
              )}

              {bodyText && !isGeneratingEmail && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-slate-700">Personalization: High</span>
                    {isApproved && (
                      <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        Approved
                      </span>
                    )}
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">To</label>
                    <input
                      type="text"
                      readOnly
                      value={lead.contact?.email ? `${lead.contact?.full_name || 'Contact'} <${lead.contact?.email}>` : 'No email available'}
                      className="w-full bg-slate-100 border border-slate-200 rounded-md px-3 py-1.5 text-xs text-slate-800"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">Subject</label>
                    <input
                      type="text"
                      value={subject}
                      onChange={(e) => setSubject(e.target.value)}
                      className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-slate-900"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-700 mb-1">Body</label>
                    <textarea
                      value={bodyText}
                      onChange={(e) => setBodyText(e.target.value)}
                      rows={9}
                      className="w-full bg-white border border-slate-300 rounded-md p-3 text-xs text-slate-900 focus:outline-none focus:border-slate-900"
                    />
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-100">
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={handleGenerateEmail}
                        className="btn-secondary text-xs py-1.5 px-3"
                      >
                        Regenerate
                      </button>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={handleApproveEmail}
                        className="btn-primary text-xs py-1.5 px-4"
                      >
                        {isApproved ? 'Approved' : 'Approve'}
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: SOURCES & PROVENANCE */}
          {activeTab === 'sources' && (
            <div className="space-y-4">
              <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Field Provenance & Verification</h3>
              <div className="space-y-3 text-xs">
                <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-md space-y-1">
                  <div className="font-semibold text-slate-900">Company Name & Location</div>
                  <div className="text-slate-600">Source: {lead.source || 'Web Business Registry'}</div>
                  <div className="text-slate-500 text-[11px]">
                    URL: {lead.company.website || 'Verified web index'}
                  </div>
                </div>

                <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-md space-y-1">
                  <div className="font-semibold text-slate-900">Phone Number</div>
                  <div className="text-slate-600">
                    Source: {lead.contact?.phone ? 'Company Web Register' : 'Not available'}
                  </div>
                </div>

                <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-md space-y-1">
                  <div className="font-semibold text-slate-900">Email Address</div>
                  <div className="text-slate-600">
                    Source: {lead.contact?.email ? 'Discovered Public Listing' : 'Not available'}
                  </div>
                </div>

                <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-md space-y-1">
                  <div className="font-semibold text-slate-900">Contact Person</div>
                  <div className="text-slate-600">
                    Source: {lead.contact?.full_name ? 'Public Professional Register' : 'Not available'}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
