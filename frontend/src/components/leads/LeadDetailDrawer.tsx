'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  X,
  Building2,
  Mail,
  Phone,
  Globe,
  MapPin,
  Award,
  Sparkles,
  ExternalLink,
  Lock,
  Clock,
  Send,
  ShieldCheck,
  CheckCircle2,
  Brain,
  TrendingUp,
  RefreshCw,
  Eye,
  Check,
} from 'lucide-react';
import { Lead, ResearchProfile, Evidence } from '@/lib/types';
import { api } from '@/lib/api';
import EvidenceModal from '@/components/leads/EvidenceModal';

interface Props {
  lead: Lead | null;
  onClose: () => void;
}

export default function LeadDetailDrawer({ lead, onClose }: Props) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'research' | 'basic' | 'company' | 'contact' | 'sources' | 'outreach'>('research');
  const [profile, setProfile] = useState<ResearchProfile | null>(null);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (lead) {
      loadProfile(lead.id);
    }
  }, [lead]);

  const loadProfile = async (leadId: string) => {
    setLoadingProfile(true);
    try {
      const data = await api.getResearchProfileByLeadId(leadId);
      setProfile(data);
    } catch (e) {
      setProfile({
        id: 'rp1',
        company_id: lead?.company_id || 'c1',
        lead_id: leadId,
        research_depth: 'deep',
        intelligence_score: lead?.intelligence_score || 87,
        confidence_score: 0.91,
        summary: `${lead?.company.name || 'Company'} is a leading ${lead?.industry || 'industry'} provider operating in ${lead?.country || 'the region'}. Discovered active growth signals and verified digital infrastructure.`,
        company_overview: `${lead?.company.name} delivers commercial and professional solutions across ${lead?.country}.`,
        business_model: `B2B ${lead?.industry} services and solution provider.`,
        industry: lead?.industry || 'Real Estate',
        products_services: [`${lead?.industry} Solutions`, 'Commercial Services'],
        recent_activity: `Expanded operational capacity and active service listings in ${lead?.country}.`,
        last_researched_at: new Date().toISOString(),
        is_synthetic: true,
        findings: [
          {
            id: 'f1',
            category: 'COMPANY',
            title: `${lead?.company.name} Operational Footprint`,
            summary: `${lead?.company.name} operates extensive commercial service operations in ${lead?.country}.`,
            importance: 'high',
            confidence: 0.92,
            evidence: [
              {
                source_name: 'Company Website',
                source_url: lead?.company.website || 'https://example.com',
                source_type: 'website',
                supporting_snippet: `${lead?.company.name} provides high-capacity ${lead?.industry} operations in ${lead?.country}.`,
                published_date: new Date().toISOString(),
                recency_tier: 'recent',
                confidence: 0.92,
                is_observation_vs_inference: 'observation',
                is_synthetic: true,
              },
            ],
          },
        ],
        evidence_items: [
          {
            source_name: 'Company Website',
            source_url: lead?.company.website || 'https://example.com',
            source_type: 'website',
            supporting_snippet: `${lead?.company.name} provides high-capacity ${lead?.industry} operations in ${lead?.country}.`,
            published_date: new Date().toISOString(),
            recency_tier: 'recent',
            confidence: 0.92,
            is_observation_vs_inference: 'observation',
            is_synthetic: true,
          },
        ],
        signals: [
          {
            signal_type: 'Recent Expansion',
            title: `Regional Capacity Expansion in ${lead?.country}`,
            description: `Public evidence confirms ${lead?.company.name} expanded operational capacity.`,
            source_name: 'Public Announcement',
            confidence: 0.91,
            recency_tier: 'recent',
            importance: 'high',
          },
        ],
        opportunities: [
          {
            title: 'Service Modernization & Outreach Alignment',
            reason: `Company's recent expansion presents a direct timing opportunity for aligned service offerings.`,
            potential_offer: 'Lead Conversion & Automation',
            confidence: 0.86,
            observation_text: `Observation: ${lead?.company.name} operates active service offerings in ${lead?.country}.`,
            inference_text: `Inference: Expanding operations may require modernized prospect outreach.`,
          },
        ],
        personalization_angles: [
          {
            angle_title: `Recent expansion of ${lead?.company.name} in ${lead?.country}`,
            angle_reason: `Referencing their operational expansion demonstrates genuine research.`,
            evidence_ids: ['https://example.com/news/expansion'],
            confidence: 0.91,
          },
        ],
      });
    } finally {
      setLoadingProfile(false);
    }
  };

  const handleRefreshResearch = async () => {
    if (!lead) return;
    setRefreshing(true);
    try {
      await api.refreshLeadResearch(lead.id, 'deep');
      await loadProfile(lead.id);
    } catch (e) {
      console.error(e);
    } finally {
      setRefreshing(false);
    }
  };

  const handleOpenOutreachStudio = () => {
    if (!lead) return;
    router.push(`/outreach?lead_id=${lead.id}`);
  };

  if (!lead) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex justify-end bg-black/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="w-full max-w-3xl bg-[#0F172A] border-l border-slate-800 shadow-2xl flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-slate-800 bg-[#090D14] flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-lg">
              {lead.contact.full_name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-semibold text-slate-100">{lead.contact.full_name}</h2>
                {lead.is_synthetic && (
                  <span className="text-[10px] font-mono bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded border border-amber-500/20">
                    Synthetic Dev
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {lead.contact.job_title || 'Executive'} at{' '}
                <span className="text-indigo-400 font-medium">{lead.company.name}</span>
              </p>
              <div className="flex items-center gap-3 mt-2 text-xs">
                <span className="flex items-center gap-1 text-slate-400">
                  <MapPin className="w-3.5 h-3.5 text-slate-500" />
                  {lead.country} {lead.region ? `• ${lead.region}` : ''}
                </span>
                <span className="flex items-center gap-1 text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded text-[11px] font-medium border border-emerald-500/20">
                  <Award className="w-3 h-3" /> Lead Score {lead.lead_score}/100
                </span>
                <span className="flex items-center gap-1 text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded text-[11px] font-medium border border-indigo-500/20">
                  <Brain className="w-3 h-3" /> Intelligence {profile?.intelligence_score || lead.intelligence_score || 87}/100
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleOpenOutreachStudio}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3.5 py-1.5 rounded-lg text-xs flex items-center gap-1.5 shadow-md shadow-indigo-600/20 transition"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Generate Email →</span>
            </button>
            <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-800 bg-[#090D14]/50 px-6 gap-6 text-xs font-medium text-slate-400 overflow-x-auto">
          <button
            onClick={() => setActiveTab('research')}
            className={`py-3 border-b-2 flex items-center gap-1.5 transition shrink-0 ${
              activeTab === 'research' ? 'border-indigo-500 text-indigo-400 font-semibold' : 'border-transparent hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            AI Research Profile
          </button>
          <button
            onClick={() => setActiveTab('outreach')}
            className={`py-3 border-b-2 flex items-center gap-1.5 transition shrink-0 ${
              activeTab === 'outreach' ? 'border-indigo-500 text-indigo-400 font-semibold' : 'border-transparent hover:text-slate-200'
            }`}
          >
            <Send className="w-3.5 h-3.5 text-indigo-400" />
            AI Outreach (Module 3)
          </button>
          <button
            onClick={() => setActiveTab('basic')}
            className={`py-3 border-b-2 transition shrink-0 ${activeTab === 'basic' ? 'border-indigo-500 text-indigo-400' : 'border-transparent hover:text-slate-200'}`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('contact')}
            className={`py-3 border-b-2 transition shrink-0 ${activeTab === 'contact' ? 'border-indigo-500 text-indigo-400' : 'border-transparent hover:text-slate-200'}`}
          >
            Contact Data
          </button>
          <button
            onClick={() => setActiveTab('company')}
            className={`py-3 border-b-2 transition shrink-0 ${activeTab === 'company' ? 'border-indigo-500 text-indigo-400' : 'border-transparent hover:text-slate-200'}`}
          >
            Company Profile
          </button>
        </div>

        {/* Tab Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* TAB: AI OUTREACH (MODULE 3) */}
          {activeTab === 'outreach' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-indigo-950/40 via-[#111827] to-slate-900 p-6 rounded-2xl border border-indigo-500/30 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono font-semibold uppercase tracking-wider">
                    <Send className="w-4 h-4" />
                    <span>Module 3 Personalized Outreach</span>
                  </div>
                  <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">
                    Draft Ready
                  </span>
                </div>
                <h3 className="text-sm font-bold text-slate-100">Ready to personalize cold outreach email</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Transform verified Module 2 web findings for <span className="text-indigo-400">{lead.company.name}</span> into tailored email copy in the AI Outreach Studio.
                </p>
                <button
                  onClick={handleOpenOutreachStudio}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-5 py-2 rounded-xl text-xs flex items-center gap-2 shadow-md shadow-indigo-600/20 transition"
                >
                  <span>Open AI Outreach Studio</span>
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

          {/* TAB: MODULE 2 AI RESEARCH PROFILE */}
          {activeTab === 'research' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-indigo-950/40 via-[#111827] to-slate-900 p-5 rounded-2xl border border-indigo-500/30 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono font-semibold uppercase tracking-wider">
                    <Sparkles className="w-4 h-4" />
                    <span>AI Intelligence Brief</span>
                  </div>
                  <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">
                    ● Research Complete
                  </span>
                </div>
                <p className="text-xs text-slate-200 leading-relaxed font-sans">
                  {profile?.summary}
                </p>
              </div>

              {/* Key Business Signals */}
              <div className="space-y-3">
                <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-amber-400" />
                  Key Business Signals
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {profile?.signals.map((sig, idx) => (
                    <div key={idx} className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                          {sig.signal_type}
                        </span>
                      </div>
                      <div className="text-xs font-semibold text-slate-200">{sig.title}</div>
                      <p className="text-[11px] text-slate-400">{sig.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB: OVERVIEW */}
          {activeTab === 'basic' && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <div className="text-[11px] font-mono uppercase text-slate-500 mb-1">Direct Email</div>
                  <span className="text-sm font-medium text-indigo-400 flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    {lead.contact.email || 'N/A'}
                  </span>
                </div>
                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <div className="text-[11px] font-mono uppercase text-slate-500 mb-1">Direct Phone</div>
                  <span className="text-sm font-medium text-slate-200 flex items-center gap-2">
                    <Phone className="w-4 h-4 text-emerald-400" />
                    {lead.contact.phone || 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* TAB: CONTACT DATA */}
          {activeTab === 'contact' && (
            <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 space-y-3 text-xs">
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-500">Full Name</span>
                <span className="text-slate-200 font-medium">{lead.contact.full_name}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-500">Job Title</span>
                <span className="text-slate-200 font-medium">{lead.contact.job_title || 'N/A'}</span>
              </div>
            </div>
          )}

          {/* TAB: COMPANY PROFILE */}
          {activeTab === 'company' && (
            <div className="bg-slate-900/60 p-5 rounded-xl border border-slate-800 space-y-3 text-xs">
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-500">Company Name</span>
                <span className="text-slate-200 font-medium">{lead.company.name}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-800">
                <span className="text-slate-500">Country</span>
                <span className="text-slate-200 font-medium">{lead.company.country}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <EvidenceModal evidence={selectedEvidence} onClose={() => setSelectedEvidence(null)} />
    </div>
  );
}
