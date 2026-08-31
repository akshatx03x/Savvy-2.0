'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  Send,
  Sparkles,
  Building2,
  User,
  Award,
  Brain,
  ShieldCheck,
  CheckCircle2,
  RefreshCw,
  Edit3,
  ExternalLink,
  ChevronDown,
  RotateCcw,
  Check,
  AlertTriangle,
  Play,
  History,
  Tag,
  Loader2,
  Eye,
} from 'lucide-react';
import { api } from '@/lib/api';
import { Lead, OfferProfile, OutreachDraft, Evidence } from '@/lib/types';
import EvidenceModal from '@/components/leads/EvidenceModal';

function OutreachStudioContent() {
  const searchParams = useSearchParams();
  const leadIdParam = searchParams.get('lead_id');

  const [leads, setLeads] = useState<Lead[]>([]);
  const [offers, setOffers] = useState<OfferProfile[]>([]);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [selectedOffer, setSelectedOffer] = useState<string>('');

  // Generation Controls State
  const [objective, setObjective] = useState('Book a meeting');
  const [tone, setTone] = useState('Consultative');
  const [length, setLength] = useState('Short');
  const [personalizationLevel, setPersonalizationLevel] = useState<'MINIMAL' | 'STANDARD' | 'DEEP'>('DEEP');
  const [ctaType, setCtaType] = useState('Soft CTA');

  // Draft State
  const [draft, setDraft] = useState<OutreachDraft | null>(null);
  const [generating, setGenerating] = useState(false);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [rewritePrompt, setRewritePrompt] = useState('');
  const [rewriting, setRewriting] = useState(false);

  // Evidence Modal State
  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);

  useEffect(() => {
    async function loadInitialData() {
      try {
        const [leadsRes, offersRes] = await Promise.all([
          api.getLeads({ page_size: 20 }),
          api.getOffers(true),
        ]);
        setLeads(leadsRes.items);
        setOffers(offersRes);

        if (offersRes.length > 0) {
          setSelectedOffer(offersRes[0].id);
        }

        if (leadsRes.items.length > 0) {
          const target = leadIdParam ? leadsRes.items.find((l) => l.id === leadIdParam) || leadsRes.items[0] : leadsRes.items[0];
          setSelectedLead(target);
          loadOrCreateDraft(target.id, offersRes[0]?.id);
        }
      } catch (e) {
        console.error(e);
      }
    }
    loadInitialData();
  }, [leadIdParam]);

  const loadOrCreateDraft = async (leadId: string, offerId?: string) => {
    setGenerating(true);
    try {
      const res = await api.generateOutreach({
        lead_id: leadId,
        offer_id: offerId || selectedOffer,
        objective,
        tone,
        length,
        personalization_level: personalizationLevel,
        cta_type: ctaType,
      });
      setDraft(res);
      setSubject(res.subject);
      setBody(res.body);
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  const handleLeadSelect = (lead: Lead) => {
    setSelectedLead(lead);
    loadOrCreateDraft(lead.id);
  };

  const handleGenerate = () => {
    if (!selectedLead) return;
    loadOrCreateDraft(selectedLead.id);
  };

  const handleRewrite = async (promptToUse?: string) => {
    if (!draft) return;
    const prompt = promptToUse || rewritePrompt;
    if (!prompt.trim()) return;

    setRewriting(true);
    try {
      const updated = await api.rewriteOutreach(draft.id, prompt);
      setDraft(updated);
      setSubject(updated.subject);
      setBody(updated.body);
      setRewritePrompt('');
    } catch (e) {
      console.error(e);
    } finally {
      setRewriting(false);
    }
  };

  const handleApprove = async () => {
    if (!draft) return;
    try {
      const updated = await api.approveOutreachDraft(draft.id);
      setDraft(updated);
    } catch (e) {
      alert((e as Error).message);
    }
  };

  const handleSaveDraft = async () => {
    if (!draft) return;
    try {
      const updated = await api.updateOutreachDraft(draft.id, { subject, body });
      setDraft(updated);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs font-semibold uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span>Module 3 • AI Outreach Studio</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Turn prospect intelligence into personalized outreach</h1>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => window.location.href = '/settings/offers'}
            className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 rounded-lg text-xs transition"
          >
            <Tag className="w-3.5 h-3.5 text-indigo-400" />
            <span>Manage Offers</span>
          </button>
        </div>
      </div>

      {/* Top Compact Generation Settings Bar */}
      <div className="bg-[#111827] p-4 rounded-xl border border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          {/* Offer Selector */}
          <div>
            <span className="text-slate-500 font-mono block text-[10px] uppercase">User Offer</span>
            <select
              value={selectedOffer}
              onChange={(e) => setSelectedOffer(e.target.value)}
              className="bg-[#090D14] border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 font-medium focus:outline-none focus:border-indigo-500"
            >
              {offers.map((off) => (
                <option key={off.id} value={off.id}>{off.name}</option>
              ))}
            </select>
          </div>

          {/* Objective */}
          <div>
            <span className="text-slate-500 font-mono block text-[10px] uppercase">Objective</span>
            <select
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              className="bg-[#090D14] border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="Book a meeting">Book a meeting</option>
              <option value="Start a conversation">Start a conversation</option>
              <option value="Introduce service">Introduce service</option>
              <option value="Request feedback">Request feedback</option>
            </select>
          </div>

          {/* Tone */}
          <div>
            <span className="text-slate-500 font-mono block text-[10px] uppercase">Tone</span>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="bg-[#090D14] border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="Consultative">Consultative</option>
              <option value="Professional">Professional</option>
              <option value="Friendly">Friendly</option>
              <option value="Direct">Direct</option>
              <option value="Conversational">Conversational</option>
            </select>
          </div>

          {/* Length */}
          <div>
            <span className="text-slate-500 font-mono block text-[10px] uppercase">Length</span>
            <select
              value={length}
              onChange={(e) => setLength(e.target.value)}
              className="bg-[#090D14] border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="Short">Short</option>
              <option value="Very Short">Very Short</option>
              <option value="Medium">Medium</option>
            </select>
          </div>

          {/* Personalization Level */}
          <div>
            <span className="text-slate-500 font-mono block text-[10px] uppercase">Personalization Level</span>
            <select
              value={personalizationLevel}
              onChange={(e) => setPersonalizationLevel(e.target.value as any)}
              className="bg-[#090D14] border border-slate-700 rounded-lg px-2.5 py-1.5 text-indigo-400 font-bold focus:outline-none focus:border-indigo-500"
            >
              <option value="DEEP">DEEP (Evidence-Backed)</option>
              <option value="STANDARD">STANDARD</option>
              <option value="MINIMAL">MINIMAL</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={generating}
          className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-2 rounded-xl text-xs flex items-center gap-2 shadow-md shadow-indigo-600/20 transition"
        >
          {generating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
          <span>✨ Generate Outreach</span>
        </button>
      </div>

      {/* 3-PANEL DESKTOP WORKSPACE LAYOUT */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LEFT PANEL: SELECTED CONTACT & QUEUE (Cols 3) */}
        <div className="lg:col-span-3 space-y-4">
          {/* Selected Lead Card */}
          {selectedLead && (
            <div className="bg-[#111827] p-5 rounded-2xl border border-slate-800 space-y-4 shadow-lg">
              <div className="flex items-center gap-3 border-b border-slate-800 pb-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold">
                  {selectedLead.contact.full_name.charAt(0)}
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-100">{selectedLead.contact.full_name}</h3>
                  <p className="text-xs text-slate-400">{selectedLead.contact.job_title || 'Executive'}</p>
                </div>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Company</span>
                  <span className="text-indigo-400 font-medium">{selectedLead.company.name}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Country</span>
                  <span className="text-slate-300 font-medium">{selectedLead.country}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Lead Score</span>
                  <span className="text-emerald-400 font-mono font-bold">⭐ {selectedLead.lead_score}/100</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-500">Intelligence</span>
                  <span className="text-indigo-400 font-mono font-bold">🧠 {selectedLead.intelligence_score || 87}/100</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Research Status</span>
                  <span className="text-emerald-400 font-mono text-[11px]">● Complete</span>
                </div>
              </div>
            </div>
          )}

          {/* Lead Queue Selector */}
          <div className="bg-[#111827] p-4 rounded-2xl border border-slate-800 space-y-3">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">Lead Queue ({leads.length})</h4>
            <div className="space-y-1.5 max-h-72 overflow-y-auto pr-1">
              {leads.map((l) => (
                <div
                  key={l.id}
                  onClick={() => handleLeadSelect(l)}
                  className={`p-2.5 rounded-xl border text-xs cursor-pointer transition flex items-center justify-between ${
                    selectedLead?.id === l.id ? 'bg-indigo-600/15 border-indigo-500/50 text-slate-100' : 'bg-slate-900/40 border-slate-800/80 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="truncate pr-2">
                    <div className="font-medium truncate">{l.contact.full_name}</div>
                    <div className="text-[10px] text-slate-500 truncate">{l.company.name}</div>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-400 shrink-0">✓</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CENTER PANEL: EMAIL EDITOR (Cols 6) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-[#111827] p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
            {/* Header & Personalization Score */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-slate-200">Email Studio Draft</span>
                {draft?.status === 'APPROVED' ? (
                  <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">
                    ✓ Approved for Campaign
                  </span>
                ) : draft?.status === 'NEEDS_RESEARCH' ? (
                  <span className="text-[10px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded">
                    ⚠ Research Required
                  </span>
                ) : (
                  <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded">
                    Drafting
                  </span>
                )}
              </div>

              {draft && draft.status !== 'NEEDS_RESEARCH' && (
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-indigo-400 font-bold bg-indigo-500/10 px-2.5 py-1 rounded border border-indigo-500/20">
                    Personalization: {draft.personalization_score}/100
                  </span>
                </div>
              )}
            </div>

            {draft?.status === 'NEEDS_RESEARCH' ? (
              <div className="bg-slate-900/60 p-6 rounded-xl border border-slate-800 text-center space-y-3">
                <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
                <h3 className="text-sm font-semibold text-slate-200">Deep Research Required</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto">
                  Deep personalization requested, but verified Module 2 research is incomplete. We reject fake deep personalization to preserve deliverability.
                </p>
                <button
                  onClick={() => api.refreshLeadResearch(selectedLead?.id || '', 'deep')}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-xs font-medium transition"
                >
                  Run Deep AI Research Now
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Subject Line Input */}
                <div>
                  <label className="block text-[11px] font-mono text-slate-400 uppercase mb-1">Subject Line</label>
                  <input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    className="w-full bg-[#090D14] border border-slate-700 rounded-xl p-3 text-xs text-slate-100 font-semibold focus:outline-none focus:border-indigo-500"
                  />
                  {draft?.subject_options && draft.subject_options.length > 1 && (
                    <div className="mt-1.5 flex items-center gap-2 text-[11px] text-slate-500">
                      <span>Suggestions:</span>
                      {draft.subject_options.map((opt, i) => (
                        <button
                          key={i}
                          onClick={() => setSubject(opt)}
                          className="hover:text-indigo-400 transition underline truncate max-w-xs"
                        >
                          "{opt}"
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Email Body Textarea */}
                <div>
                  <label className="block text-[11px] font-mono text-slate-400 uppercase mb-1">Body Copy</label>
                  <textarea
                    rows={10}
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                    className="w-full bg-[#090D14] border border-slate-700/80 rounded-xl p-4 text-xs text-slate-200 font-sans leading-relaxed focus:outline-none focus:border-indigo-500 resize-none"
                  />
                </div>

                {/* Quick AI Rewrite Actions */}
                <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800">
                  <button
                    onClick={() => handleRewrite("Make this 50% shorter")}
                    disabled={rewriting}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] font-medium transition"
                  >
                    Shorten
                  </button>
                  <button
                    onClick={() => handleRewrite("Make this more direct")}
                    disabled={rewriting}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] font-medium transition"
                  >
                    More Direct
                  </button>
                  <button
                    onClick={() => handleRewrite("Make this softer and less salesy")}
                    disabled={rewriting}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] font-medium transition"
                  >
                    Less Salesy
                  </button>
                  <button
                    onClick={() => handleRewrite("Rewrite opening to reference recent company activity")}
                    disabled={rewriting}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] font-medium transition"
                  >
                    Rewrite Opening
                  </button>
                </div>

                {/* Custom AI Natural Language Rewrite Bar */}
                <div className="relative pt-1">
                  <input
                    type="text"
                    value={rewritePrompt}
                    onChange={(e) => setRewritePrompt(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleRewrite()}
                    placeholder='Ask AI to edit e.g. "Make the CTA softer" or "Remove the website observation"'
                    className="w-full bg-[#090D14] border border-slate-700 rounded-xl pl-3 pr-20 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                  <button
                    onClick={() => handleRewrite()}
                    disabled={rewriting || !rewritePrompt.trim()}
                    className="absolute right-1.5 top-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-3 py-1 rounded-lg text-xs font-medium transition flex items-center gap-1"
                  >
                    {rewriting ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                    <span>Rewrite</span>
                  </button>
                </div>

                {/* Action Bar */}
                <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                  <button
                    onClick={handleSaveDraft}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-medium transition"
                  >
                    Save Draft
                  </button>

                  <button
                    onClick={handleApprove}
                    disabled={draft?.status === 'APPROVED'}
                    className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold px-6 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-md shadow-emerald-600/20 transition"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{draft?.status === 'APPROVED' ? 'Approved' : 'Approve Draft'}</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT PANEL: AI CONTEXT & EVIDENCE PROVENANCE (Cols 3) */}
        <div className="lg:col-span-3 space-y-4">
          <div className="bg-[#111827] p-5 rounded-2xl border border-slate-800 space-y-5 shadow-lg">
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs font-semibold uppercase tracking-wider border-b border-slate-800 pb-3">
              <Brain className="w-4 h-4 text-indigo-400" />
              <span>AI Research Context</span>
            </div>

            {/* Why This Message */}
            <div className="space-y-2">
              <h4 className="text-[11px] font-mono text-slate-400 uppercase">Why This Message</h4>
              <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800 space-y-1.5 text-xs text-slate-300">
                <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
                  <Check className="w-3.5 h-3.5" /> Recent company expansion
                </div>
                <div className="flex items-center gap-1.5 text-indigo-400 font-medium">
                  <Check className="w-3.5 h-3.5" /> Verified website channels
                </div>
                <div className="flex items-center gap-1.5 text-amber-400 font-medium">
                  <Check className="w-3.5 h-3.5" /> Outreach opportunity match
                </div>
              </div>
            </div>

            {/* Evidence Provenance Items */}
            <div className="space-y-2">
              <h4 className="text-[11px] font-mono text-slate-400 uppercase">Selected Evidence Items</h4>
              <div className="space-y-2">
                {draft?.evidence_used.map((ev, idx) => (
                  <div
                    key={idx}
                    onClick={() => setSelectedEvidence(ev)}
                    className="bg-slate-900/60 p-3 rounded-xl border border-slate-800 hover:border-indigo-500/40 cursor-pointer transition space-y-1 text-xs"
                  >
                    <div className="flex items-center justify-between text-slate-200 font-medium">
                      <span>{ev.source_name}</span>
                      <span className="text-[10px] font-mono text-emerald-400">92%</span>
                    </div>
                    <p className="text-[11px] text-slate-400 line-clamp-2 italic">"{ev.snippet}"</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Evidence Modal */}
      <EvidenceModal evidence={selectedEvidence} onClose={() => setSelectedEvidence(null)} />
    </div>
  );
}

export default function OutreachStudioPage() {
  return (
    <Suspense fallback={
      <div className="p-12 text-center text-slate-400 text-xs">
        <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-500" />
        Loading AI Outreach Studio...
      </div>
    }>
      <OutreachStudioContent />
    </Suspense>
  );
}
