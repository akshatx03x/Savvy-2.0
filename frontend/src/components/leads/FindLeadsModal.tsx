'use client';

import React, { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import LocationCombobox from '@/components/common/LocationCombobox';
import { useToast } from '@/components/common/ToastContext';

interface FindLeadsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSearchComplete: () => void;
}

export default function FindLeadsModal({ isOpen, onClose, onSearchComplete }: FindLeadsModalProps) {
  const { showToast } = useToast();
  const [searchMode, setSearchMode] = useState<'ai' | 'manual'>('ai');

  // AI Prompt State
  const [promptText, setPromptText] = useState('');
  const [analyzedPlan, setAnalyzedPlan] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Manual Fields State
  const [industry, setIndustry] = useState('');
  const [country, setCountry] = useState('');
  const [countryCode, setCountryCode] = useState('');
  const [region, setRegion] = useState('');
  const [regionCode, setRegionCode] = useState('');
  const [city, setCity] = useState('');
  const [quantity, setQuantity] = useState(100);

  // Search Execution & Lifecycle State
  const [isSearching, setIsSearching] = useState(false);
  const [progressMessage, setProgressMessage] = useState('Finding leads...');
  const [progressPercentage, setProgressPercentage] = useState(10);
  const [searchResult, setSearchResult] = useState<{
    status: 'COMPLETED' | 'PARTIAL' | 'FAILED';
    savedCount: number;
    message: string;
  } | null>(null);

  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Clean up interval on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  if (!isOpen) return null;

  const handleAnalyzeAI = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptText.trim()) return;

    setIsAnalyzing(true);
    setSearchResult(null);
    try {
      const plan = await api.analyzeSearch(promptText);
      setAnalyzedPlan(plan);
    } catch (e: any) {
      showToast('Could not parse search requirements. Try refining your description.', 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleExecuteSearch = async () => {
    setIsSearching(true);
    setSearchResult(null);
    setProgressMessage('Finding leads...');
    setProgressPercentage(10);

    try {
      let planToUse = analyzedPlan;
      if (searchMode === 'manual' || !planToUse) {
        planToUse = {
          niche: industry || 'Real Estate',
          country: country || 'United States',
          country_code: countryCode || null,
          region: region || null,
          region_code: regionCode || null,
          city: city || null,
          quantity: quantity || 100,
          quality: 'high',
          requirements: {
            website_required: false,
            public_email_required: false,
            phone_required: false,
            social_presence_required: false,
            active_business_required: true,
          },
          keywords: industry ? [industry] : ['prospects'],
          confidence_score: 1.0,
          explanation: 'Manual search criteria',
        };
      }

      const job = await api.createJob(planToUse, searchMode, `${planToUse.niche} in ${planToUse.country}`);
      showToast(`Search initialized. Querying lead sources...`, 'info');

      // Realtime job polling loop (1500ms)
      const startTime = Date.now();

      pollIntervalRef.current = setInterval(async () => {
        try {
          // Safety timeout (3 minutes max)
          if (Date.now() - startTime > 180000) {
            if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
            setIsSearching(false);
            setSearchResult({
              status: 'FAILED',
              savedCount: 0,
              message: 'Search timed out. Please try again.',
            });
            showToast('Search request timed out.', 'error');
            return;
          }

          const updatedJob = await api.getJobById(job.id) as any;
          const status = updatedJob.status;
          setProgressPercentage(updatedJob.progress_percentage || 30);

          // Lifecycle UI step mapping
          if (status === 'QUEUED' || status === 'PLANNING') {
            setProgressMessage('Finding leads...');
          } else if (status === 'SEARCHING') {
            setProgressMessage('Checking available sources...');
          } else if (status === 'PROCESSING' || status === 'DEDUPLICATING') {
            setProgressMessage('Validating results...');
          } else if (status === 'SAVING') {
            setProgressMessage('Saving leads...');
          } else if (status === 'COMPLETED') {
            if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
            setIsSearching(false);
            const count = updatedJob.saved_count ?? 0;
            setSearchResult({
              status: 'COMPLETED',
              savedCount: count,
              message: `${count} verified leads found.`,
            });
            showToast(`Search completed. ${count} verified leads found.`, 'success');
            onSearchComplete();
          } else if (status === 'PARTIAL') {
            if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
            setIsSearching(false);
            const count = updatedJob.saved_count ?? 0;
            setSearchResult({
              status: 'PARTIAL',
              savedCount: count,
              message: `${count} verified leads found. Some lead sources were unavailable.`,
            });
            showToast(`Search completed with partial results (${count} leads).`, 'info');
            onSearchComplete();
          } else if (status === 'FAILED') {
            if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
            setIsSearching(false);
            const errorMsg = updatedJob.error_message || 'No live lead source is configured.';
            setSearchResult({
              status: 'FAILED',
              savedCount: 0,
              message: errorMsg,
            });
            showToast(errorMsg, 'error');
          }
        } catch (pollErr) {
          console.warn('Error polling job status:', pollErr);
        }
      }, 1500);

    } catch (e: any) {
      showToast('Could not start lead search. Please try again.', 'error');
      setIsSearching(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-slate-200 rounded-lg max-w-2xl w-full p-6 shadow-xl space-y-6 max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Find leads</h2>
            <p className="text-xs text-slate-500 mt-0.5">Discover verified prospects for your outreach.</p>
          </div>
          <button
            onClick={() => {
              if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
              onClose();
            }}
            className="text-slate-400 hover:text-slate-700 text-lg font-bold"
          >
            ×
          </button>
        </div>

        {/* Mode Selector */}
        <div className="flex border-b border-slate-200 gap-6">
          <button
            type="button"
            onClick={() => { setSearchMode('ai'); setAnalyzedPlan(null); setSearchResult(null); }}
            className={`pb-2.5 text-xs font-medium border-b-2 transition ${
              searchMode === 'ai' ? 'border-slate-900 text-slate-900 font-semibold' : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            Describe what you need
          </button>
          <button
            type="button"
            onClick={() => { setSearchMode('manual'); setSearchResult(null); }}
            className={`pb-2.5 text-xs font-medium border-b-2 transition ${
              searchMode === 'manual' ? 'border-slate-900 text-slate-900 font-semibold' : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            Use filters
          </button>
        </div>

        {/* AI Mode Body */}
        {searchMode === 'ai' && (
          <div className="space-y-4">
            {!analyzedPlan ? (
              <form onSubmit={handleAnalyzeAI} className="space-y-3">
                <label className="block text-xs font-medium text-slate-700">
                  Describe what you are looking for
                </label>
                <textarea
                  value={promptText}
                  onChange={(e) => setPromptText(e.target.value)}
                  placeholder="e.g. Find 100 real estate companies in Ghaziabad, Uttar Pradesh, India with active business listings."
                  rows={4}
                  className="w-full bg-white border border-slate-300 rounded-md p-3 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900 transition"
                />
                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={onClose}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isAnalyzing || !promptText.trim()}
                    className="btn-primary"
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Continue'}
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-md text-xs space-y-2">
                  <div className="font-semibold text-slate-900 mb-1">Search criteria understood:</div>
                  <div className="grid grid-cols-2 gap-2 text-slate-700">
                    <div><span className="text-slate-400">Industry:</span> {analyzedPlan.niche || '—'}</div>
                    <div><span className="text-slate-400">Country:</span> {analyzedPlan.country || '—'}</div>
                    <div><span className="text-slate-400">Region:</span> {analyzedPlan.region || '—'}</div>
                    <div><span className="text-slate-400">City:</span> {analyzedPlan.city || '—'}</div>
                    <div><span className="text-slate-400">Quantity:</span> {analyzedPlan.quantity}</div>
                    <div><span className="text-slate-400">Data Source:</span> Real Live Providers</div>
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setAnalyzedPlan(null)}
                    className="btn-secondary"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    onClick={handleExecuteSearch}
                    disabled={isSearching}
                    className="btn-primary"
                  >
                    {isSearching ? 'Finding leads...' : 'Find leads'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Manual Mode Body */}
        {searchMode === 'manual' && (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Industry</label>
              <input
                type="text"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="e.g. Real Estate, Software, Healthcare"
                className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-slate-900"
              />
            </div>

            {/* Global Location & Cascading Region/City Selector */}
            <LocationCombobox
              countryValue={country}
              regionValue={region}
              cityValue={city}
              onCountryChange={(name, code) => {
                setCountry(name);
                setCountryCode(code);
              }}
              onRegionChange={(regName, regCode) => {
                setRegion(regName);
                if (regCode) setRegionCode(regCode);
              }}
              onCityChange={(cityName) => setCity(cityName)}
            />

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Target Quantity</label>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value) || 100)}
                min={10}
                max={5000}
                className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-slate-900"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={onClose}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleExecuteSearch}
                disabled={isSearching}
                className="btn-primary"
              >
                {isSearching ? 'Finding leads...' : 'Find leads'}
              </button>
            </div>
          </div>
        )}

        {/* Progress Display During Search */}
        {isSearching && (
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-md space-y-2">
            <div className="flex items-center justify-between text-xs font-medium text-slate-800">
              <span>{progressMessage}</span>
              <span className="text-slate-500 font-mono">{progressPercentage}%</span>
            </div>
            <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
              <div
                className="bg-slate-900 h-full transition-all duration-500 ease-out"
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Search Result Banner */}
        {searchResult && (
          <div
            className={`p-4 border rounded-md text-xs font-medium ${
              searchResult.status === 'COMPLETED'
                ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                : searchResult.status === 'PARTIAL'
                ? 'bg-amber-50 border-amber-200 text-amber-900'
                : 'bg-rose-50 border-rose-200 text-rose-900'
            }`}
          >
            <div className="font-semibold text-sm mb-1">
              {searchResult.status === 'COMPLETED'
                ? 'Search Complete'
                : searchResult.status === 'PARTIAL'
                ? 'Partial Search Completed'
                : 'Search Unavailable'}
            </div>
            <div>{searchResult.message}</div>
          </div>
        )}
      </div>
    </div>
  );
}
