'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useToast } from '@/components/common/ToastContext';

function SettingsContent() {
  const searchParams = useSearchParams();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState<'account' | 'email-accounts' | 'offers' | 'sending' | 'health' | 'suppression' | 'integrations'>('account');

  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam && ['account', 'email-accounts', 'offers', 'sending', 'health', 'suppression', 'integrations'].includes(tabParam)) {
      setActiveTab(tabParam as any);
    }
  }, [searchParams]);

  // Account Form
  const [name, setName] = useState('Akshat');
  const [email, setEmail] = useState('akshat@company.com');

  // Mailboxes
  const [accounts, setAccounts] = useState([
    { id: 'm1', email: 'sales@company.com', status: 'Connected', health: 'Healthy' },
    { id: 'm2', email: 'outreach@company.com', status: 'Connected', health: 'Healthy' },
  ]);

  // Offers
  const [offers, setOffers] = useState([
    { id: 'o1', name: 'Website Conversion Optimization', target: 'Real Estate Companies', value: 'Increase inbound lead conversion by 35%' },
  ]);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Settings</h1>
        <p className="text-xs text-slate-500 mt-0.5">Manage your account, email accounts, sending parameters, and deliverability.</p>
      </div>

      {/* Sub-Navigation Tabs */}
      <div className="flex border-b border-slate-200 gap-6 text-xs font-medium text-slate-500 overflow-x-auto">
        {[
          { id: 'account', label: 'Account' },
          { id: 'email-accounts', label: 'Email accounts' },
          { id: 'offers', label: 'Offers' },
          { id: 'sending', label: 'Sending' },
          { id: 'health', label: 'Email health' },
          { id: 'suppression', label: 'Suppression' },
          { id: 'integrations', label: 'Integrations' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`py-2.5 border-b-2 transition whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-slate-900 text-slate-900 font-semibold'
                : 'border-transparent hover:text-slate-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: ACCOUNT */}
      {activeTab === 'account' && (
        <div className="bg-white border border-slate-200 rounded-lg p-6 max-w-xl space-y-4">
          <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Account Information</h2>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-slate-900"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-slate-900"
            />
          </div>
          <div className="pt-2">
            <button onClick={() => showToast('Account settings saved.', 'success')} className="btn-primary">
              Save changes
            </button>
          </div>
        </div>
      )}

      {/* TAB 2: EMAIL ACCOUNTS (MAILBOXES) */}
      {activeTab === 'email-accounts' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Connected Email Accounts</h2>
            <button onClick={() => showToast('Account connection modal opened.', 'info')} className="btn-primary text-xs">
              + Connect account
            </button>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-xs">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                  <th className="p-3">Email Address</th>
                  <th className="p-3">Connection</th>
                  <th className="p-3">Health Status</th>
                  <th className="p-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {accounts.map((acc) => (
                  <tr key={acc.id}>
                    <td className="p-3 font-medium text-slate-900">{acc.email}</td>
                    <td className="p-3 text-emerald-800">{acc.status}</td>
                    <td className="p-3 text-slate-700">{acc.health}</td>
                    <td className="p-3">
                      <button onClick={() => showToast('Managing account settings.', 'info')} className="btn-secondary text-xs py-1 px-2.5">
                        Manage
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: OFFERS */}
      {activeTab === 'offers' && (
        <div className="space-y-4 max-w-2xl">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Outreach Offers</h2>
            <button onClick={() => showToast('Offer created.', 'success')} className="btn-primary text-xs">
              + Add offer
            </button>
          </div>

          <div className="space-y-3">
            {offers.map((off) => (
              <div key={off.id} className="p-4 bg-white border border-slate-200 rounded-lg space-y-1.5 text-xs">
                <div className="font-semibold text-slate-900">{off.name}</div>
                <div className="text-slate-600">Who it's for: {off.target}</div>
                <div className="text-slate-500">Value proposition: {off.value}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 4: SENDING */}
      {activeTab === 'sending' && (
        <div className="bg-white border border-slate-200 rounded-lg p-6 max-w-xl space-y-4">
          <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Sending Limits & Schedule</h2>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Max daily emails per account</label>
            <input
              type="number"
              defaultValue={150}
              className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-slate-900"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Default sending days</label>
            <div className="text-xs text-slate-800 bg-slate-50 p-2.5 rounded-md border border-slate-200">
              Monday through Friday
            </div>
          </div>
          <div className="pt-2">
            <button onClick={() => showToast('Sending settings saved.', 'success')} className="btn-primary">
              Save parameters
            </button>
          </div>
        </div>
      )}

      {/* TAB 5: EMAIL HEALTH (DELIVERABILITY) */}
      {activeTab === 'health' && (
        <div className="space-y-4 max-w-2xl">
          <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Email Health & DNS Authentication</h2>
          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-xs space-y-2 text-emerald-900 font-medium">
            <div>Status: Healthy</div>
            <div className="flex gap-4">
              <span>SPF: Verified</span>
              <span>DKIM: Verified</span>
              <span>DMARC: Verified</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-white border border-slate-200 rounded-lg">
              <div className="text-xs text-slate-500 font-medium">Bounce rate</div>
              <div className="text-lg font-bold text-slate-900 mt-1">1.2%</div>
            </div>
            <div className="p-4 bg-white border border-slate-200 rounded-lg">
              <div className="text-xs text-slate-500 font-medium">Complaint rate</div>
              <div className="text-lg font-bold text-slate-900 mt-1">0.04%</div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 6: SUPPRESSION */}
      {activeTab === 'suppression' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">Suppression & Opt-Out List</h2>
            <button onClick={() => showToast('Added to suppression.', 'success')} className="btn-primary text-xs">
              + Add email
            </button>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-4 text-xs text-slate-500">
            No emails manually suppressed yet.
          </div>
        </div>
      )}

      {/* TAB 7: INTEGRATIONS */}
      {activeTab === 'integrations' && <IntegrationsTab />}

    </div>
  );
}

function IntegrationsTab() {
  const { showToast } = useToast();
  const [leadSources, setLeadSources] = useState<Array<any>>([]);
  const [aiProviders, setAiProviders] = useState<Array<any>>([]);
  const [costMode, setCostMode] = useState<string>('free_only');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadProviders = async () => {
      try {
        const { api } = await import('@/lib/api');
        const res = await api.getProviderStatuses() as any;
        if (res && res.lead_sources) {
          setLeadSources(res.lead_sources || []);
          setAiProviders(res.ai_providers || []);
          setCostMode(res.cost_mode?.lead_cost_mode || 'free_only');
        } else if (Array.isArray(res)) {
          setLeadSources(res);
        }
      } catch (e) {
        console.warn('Failed to load provider statuses:', e);
      } finally {
        setIsLoading(false);
      }
    };
    loadProviders();
  }, []);

  return (
    <div className="space-y-8 max-w-3xl">
      {/* Cost Policy Mode Banner */}
      <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold text-slate-900">Cost Control Policy</div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Operating in <span className="font-mono font-semibold text-slate-800 uppercase">{costMode}</span> mode. Zero paid API charges allowed.
          </div>
        </div>
        <span className="text-[10px] font-mono font-semibold bg-emerald-100 text-emerald-800 px-2.5 py-1 rounded border border-emerald-200">
          FREE ONLY
        </span>
      </div>

      {/* Section 1: Lead Sources */}
      <div className="space-y-4">
        <div>
          <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-0.5">Lead sources</h2>
          <p className="text-xs text-slate-500">Live data providers used for zero-cost business discovery.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {leadSources.map((p) => (
            <div key={p.name} className="p-4 bg-white border border-slate-200 rounded-lg shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-900">{p.name}</span>
                <span
                  className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    p.status === 'Connected' || p.status === 'Available'
                      ? 'bg-emerald-100 text-emerald-800'
                      : p.status === 'Not Configured'
                      ? 'bg-slate-100 text-slate-600'
                      : 'bg-amber-100 text-amber-800'
                  }`}
                >
                  {p.status}
                </span>
              </div>

              <div className="text-[11px] text-slate-500 flex justify-between items-center">
                <span>{p.status === 'Connected' || p.status === 'Available' ? 'Ready for live search' : p.error || 'Credentials not configured.'}</span>
                {p.cost_type && <span className="font-mono text-[10px] text-slate-400">{p.cost_type}</span>}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 2: AI Providers */}
      <div className="space-y-4">
        <div>
          <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-0.5">AI providers</h2>
          <p className="text-xs text-slate-500">Multi-provider AI routing for search planning, research, and outreach drafting.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {aiProviders.map((ai) => (
            <div key={ai.name} className="p-4 bg-white border border-slate-200 rounded-lg shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-900">{ai.name}</span>
                <span
                  className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    ai.status === 'Connected'
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {ai.status}
                </span>
              </div>

              <div className="text-[11px] text-slate-500 flex justify-between items-center">
                <span>{ai.model || 'Default model'}</span>
                <span className="font-mono text-[10px] text-slate-400">{ai.status === 'Connected' ? 'Active' : 'Optional'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <Suspense fallback={<div className="text-xs text-slate-500 p-6">Loading settings...</div>}>
      <SettingsContent />
    </Suspense>
  );
}


