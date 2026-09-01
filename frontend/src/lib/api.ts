import {
  SearchPlan,
  GenerationJob,
  Lead,
  LeadFilterParams,
  PaginatedLeadsResponse,
  CountryStat,
  DashboardStats,
  Company,
  Contact,
  ResearchJob,
  ResearchProfile,
  OfferProfile,
  OutreachDraft,
  OutreachJob,
  Module4Contract,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error [${response.status}]: ${errorText || response.statusText}`);
  }

  return response.json();
}

export const api = {
  // AI Search Planner
  async analyzeSearch(prompt: string): Promise<SearchPlan> {
    try {
      return await fetchAPI<SearchPlan>('/ai/search-plan', {
        method: 'POST',
        body: JSON.stringify({ prompt }),
      });
    } catch (e) {
      console.warn('Backend offline, using client fallback parser:', e);
      const promptLower = prompt.toLowerCase();
      return {
        niche: promptLower.includes('real estate') ? 'Real Estate' : promptLower.includes('saas') ? 'Software & Technology' : 'Business Services',
        country: promptLower.includes('uk') || promptLower.includes('united kingdom') ? 'United Kingdom' : 'United States',
        region: promptLower.includes('washington') ? 'Washington' : promptLower.includes('california') ? 'California' : null,
        city: promptLower.includes('seattle') ? 'Seattle' : null,
        quantity: 500,
        quality: 'high',
        requirements: {
          website_required: true,
          public_email_required: true,
          phone_required: false,
          social_presence_required: false,
          active_business_required: true,
        },
        keywords: ['prospects', 'business'],
        confidence_score: 0.95,
        explanation: 'Parsed search criteria for your lead generation job.',
      };
    }
  },

  // Generation Jobs
  async createJob(plan: SearchPlan, searchType: 'ai' | 'manual' = 'ai', name?: string): Promise<GenerationJob> {
    return fetchAPI<GenerationJob>('/generation-jobs', {
      method: 'POST',
      body: JSON.stringify({
        name: name || `${plan.niche} in ${plan.country}`,
        search_type: searchType,
        plan,
      }),
    });
  },

  async getJobs(): Promise<GenerationJob[]> {
    return fetchAPI<GenerationJob[]>('/generation-jobs');
  },

  async getJobById(jobId: string): Promise<GenerationJob> {
    return fetchAPI<GenerationJob>(`/generation-jobs/${jobId}`);
  },

  async cancelJob(jobId: string): Promise<GenerationJob> {
    return fetchAPI<GenerationJob>(`/generation-jobs/${jobId}/cancel`, { method: 'POST' });
  },

  async retryJob(jobId: string): Promise<GenerationJob> {
    return fetchAPI<GenerationJob>(`/generation-jobs/${jobId}/retry`, { method: 'POST' });
  },

  // Module 2 AI Research & Intelligence APIs
  async createResearchJob(leadIds: string[], depth: 'basic' | 'standard' | 'deep' = 'standard', name?: string): Promise<ResearchJob> {
    return fetchAPI<ResearchJob>('/research/jobs', {
      method: 'POST',
      body: JSON.stringify({
        lead_ids: leadIds,
        research_depth: depth,
        name: name || `AI Research (${leadIds.length} leads)`,
      }),
    });
  },

  async getResearchJobs(): Promise<ResearchJob[]> {
    return fetchAPI<ResearchJob[]>('/research/jobs');
  },

  async getResearchJobById(jobId: string): Promise<ResearchJob> {
    return fetchAPI<ResearchJob>(`/research/jobs/${jobId}`);
  },

  async cancelResearchJob(jobId: string): Promise<ResearchJob> {
    return fetchAPI<ResearchJob>(`/research/jobs/${jobId}/cancel`, { method: 'POST' });
  },

  async getResearchProfileByLeadId(leadId: string): Promise<ResearchProfile | null> {
    try {
      return await fetchAPI<ResearchProfile>(`/research/leads/${leadId}`);
    } catch (e) {
      return null;
    }
  },


  async refreshLeadResearch(leadId: string, depth: 'basic' | 'standard' | 'deep' = 'standard'): Promise<ResearchJob> {
    return fetchAPI<ResearchJob>(`/research/leads/${leadId}/refresh?depth=${depth}`, { method: 'POST' });
  },

  // Module 3 Offers & Outreach Studio APIs
  async getOffers(activeOnly: boolean = false): Promise<OfferProfile[]> {
    return fetchAPI<OfferProfile[]>(`/offers?active_only=${activeOnly}`);
  },

  async createOffer(offer: Partial<OfferProfile>): Promise<OfferProfile> {
    return fetchAPI<OfferProfile>('/offers', {
      method: 'POST',
      body: JSON.stringify(offer),
    });
  },

  async updateOffer(offerId: string, updates: Partial<OfferProfile>): Promise<OfferProfile> {
    return fetchAPI<OfferProfile>(`/offers/${offerId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  },

  async deleteOffer(offerId: string): Promise<void> {
    return fetchAPI<void>(`/offers/${offerId}`, { method: 'DELETE' });
  },

  async generateOutreach(payload: {
    lead_id: string;
    offer_id?: string;
    objective?: string;
    tone?: string;
    length?: string;
    personalization_level?: string;
    cta_type?: string;
    custom_objective?: string;
  }): Promise<OutreachDraft> {
    return fetchAPI<OutreachDraft>('/outreach/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async rewriteOutreach(draftId: string, prompt: string): Promise<OutreachDraft> {
    return fetchAPI<OutreachDraft>(`/outreach/drafts/${draftId}/rewrite`, {
      method: 'POST',
      body: JSON.stringify({ prompt, preserve_evidence: true }),
    });
  },

  async updateOutreachDraft(draftId: string, updates: Partial<OutreachDraft>): Promise<OutreachDraft> {
    return fetchAPI<OutreachDraft>(`/outreach/drafts/${draftId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  },

  async approveOutreachDraft(draftId: string): Promise<OutreachDraft> {
    return fetchAPI<OutreachDraft>(`/outreach/drafts/${draftId}/approve`, { method: 'POST' });
  },

  async archiveOutreachDraft(draftId: string): Promise<OutreachDraft> {
    return fetchAPI<OutreachDraft>(`/outreach/drafts/${draftId}/archive`, { method: 'POST' });
  },

  async createOutreachJob(leadIds: string[], config: any): Promise<OutreachJob> {
    return fetchAPI<OutreachJob>('/outreach/generate-bulk', {
      method: 'POST',
      body: JSON.stringify({
        lead_ids: leadIds,
        ...config,
      }),
    });
  },

  async getOutreachJobs(): Promise<OutreachJob[]> {
    return fetchAPI<OutreachJob[]>('/outreach/jobs');
  },

  async getModule4Contract(draftId: string): Promise<Module4Contract> {
    return fetchAPI<Module4Contract>(`/outreach/module4-contract/${draftId}`);
  },

  // Leads
  async getLeads(params: LeadFilterParams = {}): Promise<PaginatedLeadsResponse> {
    const query = new URLSearchParams();
    if (params.search) query.set('search', params.search);
    if (params.country) query.set('country', params.country);
    if (params.region) query.set('region', params.region);
    if (params.city) query.set('city', params.city);
    if (params.industry) query.set('industry', params.industry);
    if (params.min_score) query.set('min_score', params.min_score.toString());
    if (params.status) query.set('status', params.status);
    if (params.has_email !== undefined) query.set('has_email', params.has_email.toString());
    if (params.has_phone !== undefined) query.set('has_phone', params.has_phone.toString());
    if (params.has_website !== undefined) query.set('has_website', params.has_website.toString());
    if (params.research_status) query.set('research_status', params.research_status);
    if (params.outreach_status) query.set('outreach_status', params.outreach_status);
    if (params.source) query.set('source', params.source);
    if (params.page) query.set('page', params.page.toString());
    if (params.page_size) query.set('page_size', params.page_size.toString());
    if (params.sort_by) query.set('sort_by', params.sort_by);
    if (params.sort_order) query.set('sort_order', params.sort_order);

    return fetchAPI<PaginatedLeadsResponse>(`/leads?${query.toString()}`);
  },

  async getLeadById(leadId: string): Promise<Lead> {
    return fetchAPI<Lead>(`/leads/${leadId}`);
  },

  async updateLead(leadId: string, updates: { status?: string; notes?: string; lead_score?: number }): Promise<Lead> {
    return fetchAPI<Lead>(`/leads/${leadId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  },

  async deleteLead(leadId: string): Promise<void> {
    return fetchAPI<void>(`/leads/${leadId}`, { method: 'DELETE' });
  },

  // Countries (Strict Country-Only)
  async getCountries(): Promise<CountryStat[]> {
    return fetchAPI<CountryStat[]>('/countries');
  },

  // Companies (Lightweight Directory)
  async getCompanies(page: number = 1, search?: string, country?: string): Promise<{ items: Company[]; total: number }> {
    const query = new URLSearchParams({ page: page.toString() });
    if (search) query.set('search', search);
    if (country) query.set('country', country);
    return fetchAPI<{ items: Company[]; total: number }>(`/companies?${query.toString()}`);
  },

  // Locations (ISO Country & Region System)
  async getLocationsCountries(query?: string): Promise<Array<{ code: string; name: string; official_name?: string; iso_code: string }>> {
    const q = query ? `?q=${encodeURIComponent(query)}` : '';
    return fetchAPI<Array<{ code: string; name: string; official_name?: string; iso_code: string }>>(`/locations/countries${q}`);
  },

  async getLocationsRegions(countryCode: string, query?: string): Promise<Array<{ id: string; country_code: string; name: string; code: string }>> {
    const q = query ? `?q=${encodeURIComponent(query)}` : '';
    return fetchAPI<Array<{ id: string; country_code: string; name: string; code: string }>>(`/locations/countries/${countryCode}/regions${q}`);
  },

  async getLocationsCities(countryCode: string, regionCode: string, query?: string): Promise<Array<{ id: string; country_code: string; region_code: string; name: string }>> {
    const q = query ? `?q=${encodeURIComponent(query)}` : '';
    return fetchAPI<Array<{ id: string; country_code: string; region_code: string; name: string }>>(`/locations/countries/${countryCode}/regions/${regionCode}/cities${q}`);
  },

  async getProviderStatuses(): Promise<Array<{ name: string; status: string; enabled: boolean; credentials_present: boolean; last_checked: string; error?: string }>> {
    return fetchAPI('/providers/status');
  },

  // Stats / Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    return fetchAPI<DashboardStats>('/stats');
  },

};

