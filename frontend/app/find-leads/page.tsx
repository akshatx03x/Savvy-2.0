'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  Sparkles,
  SlidersHorizontal,
  ArrowRight,
  CheckCircle2,
  Edit3,
  Play,
  Loader2,
  ShieldCheck,
  Globe,
  Building2,
  Check,
  Activity,
  Layers,
} from 'lucide-react';
import { api } from '@/lib/api';
import { SearchPlan, GenerationJob } from '@/lib/types';

function FindLeadsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialPrompt = searchParams.get('prompt') || '';

  const [mode, setMode] = useState<'ai' | 'manual'>('ai');
  const [prompt, setPrompt] = useState(initialPrompt);
  const [analyzing, setAnalyzing] = useState(false);
  const [searchPlan, setSearchPlan] = useState<SearchPlan | null>(null);
  const [isEditingPlan, setIsEditingPlan] = useState(false);

  // Manual Search Form State
  const [manualForm, setManualForm] = useState({
    niche: 'Real Estate',
    customNiche: '',
    country: 'United States',
    region: 'Washington',
    city: '',
    keywords: '',
    quantity: 500,
    quality: 'high',
    website_required: true,
    public_email_required: true,
    phone_required: false,
    social_presence_required: false,
    active_business_required: true,
  });

  // Active Job Execution Monitor State
  const [activeJob, setActiveJob] = useState<GenerationJob | null>(null);

  useEffect(() => {
    if (initialPrompt && !searchPlan) {
      handleAnalyzeAISearch(initialPrompt);
    }
  }, [initialPrompt]);

  // Handle AI Search Analysis
  const handleAnalyzeAISearch = async (queryToAnalyze?: string) => {
    const query = queryToAnalyze || prompt;
    if (!query.trim()) return;

    setAnalyzing(true);
    try {
      const plan = await api.analyzeSearch(query);
      setSearchPlan(plan);
      setIsEditingPlan(false);
    } catch (e) {
      console.error('Failed to analyze search prompt:', e);
    } finally {
      setAnalyzing(false);
    }
  };

  // Handle Manual Search Plan Generation
  const handleManualPlanGenerate = () => {
    const plan: SearchPlan = {
      niche: manualForm.customNiche.trim() || manualForm.niche,
      country: manualForm.country,
      region: manualForm.region.trim() || null,
      city: manualForm.city.trim() || null,
      quantity: manualForm.quantity,
      quality: manualForm.quality,
      requirements: {
        website_required: manualForm.website_required,
        public_email_required: manualForm.public_email_required,
        phone_required: manualForm.phone_required,
        social_presence_required: manualForm.social_presence_required,
        active_business_required: manualForm.active_business_required,
      },
      keywords: manualForm.keywords.split(',').map((k) => k.trim()).filter(Boolean),
      confidence_score: 1.0,
      explanation: 'Manual search plan configured by user.',
    };
    setSearchPlan(plan);
    setIsEditingPlan(false);
  };

  // Start Lead Generation Job
  const handleStartSearchJob = async () => {
    if (!searchPlan) return;

    try {
      const job = await api.createJob(searchPlan, mode);
      setActiveJob(job);

      // Poll job progress real-time
      const pollInterval = setInterval(async () => {
        try {
          const updated = await api.getJobById(job.id);
          setActiveJob(updated);
          if (['COMPLETED', 'PARTIAL', 'FAILED', 'CANCELLED'].includes(updated.status)) {
            clearInterval(pollInterval);
          }
        } catch (err) {
          clearInterval(pollInterval);
        }
      }, 1500);
    } catch (e) {
      console.error('Failed to start search job:', e);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Find Leads</h1>
          <p className="text-xs text-slate-400 mt-1">Discover, parse and qualify verified B2B prospects.</p>
        </div>

        {/* Search Mode Selector */}
        <div className="flex bg-[#090D14] p-1 rounded-xl border border-slate-800 text-xs font-medium">
          <button
            onClick={() => { setMode('ai'); setSearchPlan(null); }}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
              mode === 'ai'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Search</span>
          </button>
          <button
            onClick={() => { setMode('manual'); setSearchPlan(null); }}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
              mode === 'manual'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Manual Search</span>
          </button>
        </div>
      </div>

      {/* Real-time Active Job Execution Monitor */}
      {activeJob && (
        <div className="bg-[#111827] border border-indigo-500/40 rounded-2xl p-6 shadow-2xl space-y-4 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <Activity className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                  <span>Generating Leads: {activeJob.name}</span>
                  <span className="text-[10px] font-mono bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/30">
                    {activeJob.status}
                  </span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Niche: {activeJob.niche} • Country: {activeJob.country}
                </p>
              </div>
            </div>
            {['COMPLETED', 'PARTIAL'].includes(activeJob.status) && (
              <button
                onClick={() => router.push('/leads')}
                className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium px-4 py-2 rounded-lg flex items-center gap-2 shadow-md transition"
              >
                <span>View Discovered Leads</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Progress Bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-slate-400 font-mono">
              <span>Progress</span>
              <span>{activeJob.progress_percentage}%</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full transition-all duration-500"
                style={{ width: `${activeJob.progress_percentage}%` }}
              />
            </div>
          </div>

          {/* Live Progress Stats Grid */}
          <div className="grid grid-cols-4 gap-3 text-center pt-2">
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-[10px] font-mono text-slate-500 uppercase">Requested</div>
              <div className="text-sm font-bold text-slate-200 mt-0.5">{activeJob.requested_count}</div>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-[10px] font-mono text-slate-500 uppercase">Discovered</div>
              <div className="text-sm font-bold text-slate-200 mt-0.5">{activeJob.discovered_count}</div>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-[10px] font-mono text-slate-500 uppercase">Duplicates Merged</div>
              <div className="text-sm font-bold text-amber-400 mt-0.5">{activeJob.duplicates_count}</div>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div className="text-[10px] font-mono text-slate-500 uppercase">Unique Saved</div>
              <div className="text-sm font-bold text-emerald-400 mt-0.5">{activeJob.saved_count}</div>
            </div>
          </div>
        </div>
      )}

      {/* MODE 1: AI SEARCH */}
      {mode === 'ai' && (
        <div className="space-y-6">
          <div className="bg-[#111827] p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono font-semibold uppercase tracking-wider">
              <Sparkles className="w-4 h-4" />
              <span>✨ AI Prospect Search</span>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-100">Tell AI what leads you need</h2>
              <p className="text-xs text-slate-400 mt-1">
                Describe target industry, location filters, quantity, and requirements in natural language.
              </p>
            </div>

            <div className="space-y-3">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder='e.g. "Find 500 real estate businesses in Washington with active websites and public business contact information."'
                rows={4}
                className="w-full bg-[#090D14] border border-slate-700/80 rounded-xl p-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30 transition resize-none shadow-inner"
              />
              <div className="flex justify-end">
                <button
                  onClick={() => handleAnalyzeAISearch()}
                  disabled={analyzing || !prompt.trim()}
                  className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium px-6 py-2.5 rounded-xl text-xs flex items-center gap-2 shadow-md shadow-indigo-600/20 transition"
                >
                  {analyzing ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Analyzing Query...</span>
                    </>
                  ) : (
                    <>
                      <span>Analyze Search</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODE 2: MANUAL SEARCH FORM */}
      {mode === 'manual' && (
        <div className="bg-[#111827] p-6 rounded-2xl border border-slate-800 shadow-xl space-y-6">
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono font-semibold uppercase tracking-wider">
            <SlidersHorizontal className="w-4 h-4" />
            <span>Structured Filter Builder</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 font-medium mb-1">Industry / Niche</label>
              <select
                value={manualForm.niche}
                onChange={(e) => setManualForm({ ...manualForm, niche: e.target.value })}
                className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="Real Estate">Real Estate</option>
                <option value="Software & Technology">Software & Technology</option>
                <option value="E-Commerce & Retail">E-Commerce & Retail</option>
                <option value="Healthcare & Medical">Healthcare & Medical</option>
                <option value="Construction & Engineering">Construction & Engineering</option>
                <option value="Marketing & Advertising">Marketing & Advertising</option>
                <option value="Financial Services">Financial Services</option>
                <option value="Legal Services">Legal Services</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Custom Niche (Optional)</label>
              <input
                type="text"
                value={manualForm.customNiche}
                onChange={(e) => setManualForm({ ...manualForm, customNiche: e.target.value })}
                placeholder="e.g. Commercial Property Managers"
                className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Country (Geographic Category)</label>
              <select
                value={manualForm.country}
                onChange={(e) => setManualForm({ ...manualForm, country: e.target.value })}
                className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="United States">🇺🇸 United States</option>
                <option value="United Kingdom">🇬🇧 United Kingdom</option>
                <option value="Canada">🇨🇦 Canada</option>
                <option value="Australia">🇦🇺 Australia</option>
                <option value="Germany">🇩🇪 Germany</option>
                <option value="France">🇫🇷 France</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Region / State Filter (Optional)</label>
              <input
                type="text"
                value={manualForm.region}
                onChange={(e) => setManualForm({ ...manualForm, region: e.target.value })}
                placeholder="e.g. Washington, California"
                className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Desired Quantity</label>
              <select
                value={manualForm.quantity}
                onChange={(e) => setManualForm({ ...manualForm, quantity: parseInt(e.target.value) })}
                className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value={100}>100 Leads</option>
                <option value={250}>250 Leads</option>
                <option value={500}>500 Leads</option>
                <option value={1000}>1,000 Leads</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Quality Level</label>
              <select
                value={manualForm.quality}
                onChange={(e) => setManualForm({ ...manualForm, quality: e.target.value })}
                className="w-full bg-[#090D14] border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="basic">Basic (Standard Filters)</option>
                <option value="high">High Quality (Website & Email Required)</option>
                <option value="premium">Premium (Fully Verified Data)</option>
              </select>
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-800">
            <label className="block text-xs font-semibold text-slate-300">Data Requirements</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs text-slate-300">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={manualForm.website_required}
                  onChange={(e) => setManualForm({ ...manualForm, website_required: e.target.checked })}
                  className="rounded border-slate-700 bg-slate-900 text-indigo-600 focus:ring-0"
                />
                <span>Website required</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={manualForm.public_email_required}
                  onChange={(e) => setManualForm({ ...manualForm, public_email_required: e.target.checked })}
                  className="rounded border-slate-700 bg-slate-900 text-indigo-600 focus:ring-0"
                />
                <span>Public email required</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={manualForm.phone_required}
                  onChange={(e) => setManualForm({ ...manualForm, phone_required: e.target.checked })}
                  className="rounded border-slate-700 bg-slate-900 text-indigo-600 focus:ring-0"
                />
                <span>Phone required</span>
              </label>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleManualPlanGenerate}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-6 py-2.5 rounded-xl text-xs flex items-center gap-2 shadow-md shadow-indigo-600/20 transition"
            >
              <span>Build Search Plan</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* SEARCH PLAN REVIEW PANEL */}
      {searchPlan && (
        <div className="bg-[#111827] border border-indigo-500/30 rounded-2xl p-6 shadow-2xl space-y-6 animate-in fade-in duration-200">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs font-semibold uppercase tracking-wider">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Search Plan Preview</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsEditingPlan(!isEditingPlan)}
                className="text-xs text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition"
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>{isEditingPlan ? 'Done Editing' : 'Edit Plan'}</span>
              </button>
            </div>
          </div>

          {isEditingPlan ? (
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Niche</label>
                <input
                  type="text"
                  value={searchPlan.niche}
                  onChange={(e) => setSearchPlan({ ...searchPlan, niche: e.target.value })}
                  className="w-full bg-[#090D14] border border-slate-700 rounded p-2 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-medium mb-1">Country</label>
                <input
                  type="text"
                  value={searchPlan.country}
                  onChange={(e) => setSearchPlan({ ...searchPlan, country: e.target.value })}
                  className="w-full bg-[#090D14] border border-slate-700 rounded p-2 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-medium mb-1">Region</label>
                <input
                  type="text"
                  value={searchPlan.region || ''}
                  onChange={(e) => setSearchPlan({ ...searchPlan, region: e.target.value || null })}
                  className="w-full bg-[#090D14] border border-slate-700 rounded p-2 text-slate-200"
                />
              </div>
              <div>
                <label className="block text-slate-400 font-medium mb-1">Quantity</label>
                <input
                  type="number"
                  value={searchPlan.quantity}
                  onChange={(e) => setSearchPlan({ ...searchPlan, quantity: parseInt(e.target.value) || 100 })}
                  className="w-full bg-[#090D14] border border-slate-700 rounded p-2 text-slate-200"
                />
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Target Niche</div>
                <div className="text-sm font-semibold text-slate-200 mt-1">{searchPlan.niche}</div>
              </div>
              <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Country (Category)</div>
                <div className="text-sm font-semibold text-slate-200 mt-1">{searchPlan.country}</div>
              </div>
              <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Region / State Filter</div>
                <div className="text-sm font-semibold text-slate-200 mt-1">{searchPlan.region || 'Any Region'}</div>
              </div>
              <div className="bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Requested Quantity</div>
                <div className="text-sm font-bold text-indigo-400 font-mono mt-1">{searchPlan.quantity} Prospects</div>
              </div>
            </div>
          )}

          <div className="space-y-2">
            <div className="text-xs font-semibold text-slate-300">Target Requirements:</div>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className={`px-2.5 py-1 rounded-md border flex items-center gap-1.5 ${
                searchPlan.requirements.website_required ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-800 text-slate-500 border-slate-700'
              }`}>
                <Check className="w-3.5 h-3.5" /> Website Required
              </span>
              <span className={`px-2.5 py-1 rounded-md border flex items-center gap-1.5 ${
                searchPlan.requirements.public_email_required ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-800 text-slate-500 border-slate-700'
              }`}>
                <Check className="w-3.5 h-3.5" /> Public Email Required
              </span>
              <span className={`px-2.5 py-1 rounded-md border flex items-center gap-1.5 ${
                searchPlan.requirements.phone_required ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-800 text-slate-500 border-slate-700'
              }`}>
                <Check className="w-3.5 h-3.5" /> Phone Required
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-slate-800">
            <div className="text-xs text-slate-400 font-mono">
              Ready to execute background search job
            </div>
            <button
              onClick={handleStartSearchJob}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-6 py-2.5 rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-emerald-600/20 transition"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>Start Search Job</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function FindLeadsPage() {
  return (
    <Suspense fallback={
      <div className="p-12 text-center text-slate-400 text-xs">
        <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-500" />
        Loading Find Leads...
      </div>
    }>
      <FindLeadsContent />
    </Suspense>
  );
}
