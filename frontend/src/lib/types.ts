export interface SearchRequirements {
  website_required: boolean;
  public_email_required: boolean;
  phone_required: boolean;
  social_presence_required: boolean;
  active_business_required: boolean;
}

export interface SearchPlan {
  niche: string;
  country: string;
  region: string | null;
  city: string | null;
  quantity: number;
  quality: 'basic' | 'high' | 'premium' | string;
  requirements: SearchRequirements;
  keywords: string[];
  confidence_score: number;
  explanation?: string;
}

export interface Company {
  id: string;
  name: string;
  normalized_name?: string;
  domain?: string | null;
  normalized_domain?: string | null;
  website?: string | null;
  country: string;
  region?: string | null;
  city?: string | null;
  industry: string;
  description?: string | null;
  employee_count_range?: string | null;
  contact_count?: number;
  lead_score?: number;
  is_synthetic: boolean;
  created_at: string;
  updated_at: string;
}

export interface Contact {
  id: string;
  company_id: string;
  first_name?: string | null;
  last_name?: string | null;
  full_name: string;
  job_title?: string | null;
  email?: string | null;
  phone?: string | null;
  country: string;
  region?: string | null;
  city?: string | null;
  source: string;
  source_url?: string | null;
  verification_status: 'verified' | 'unverified' | 'invalid' | string;
  is_synthetic: boolean;
  created_at: string;
  updated_at: string;
  sources?: LeadSourceProvenance[];
}

export interface LeadSourceProvenance {
  id: string;
  contact_id: string;
  source_name: string;
  source_url?: string | null;
  discovered_at: string;
  verification_status: string;
  is_synthetic: boolean;
}

export interface Lead {
  id: string;
  company_id: string;
  contact_id?: string | null;
  company: Company;
  contact?: Contact | null;
  country: string;
  region?: string | null;
  city?: string | null;
  industry: string;
  lead_score: number;
  intelligence_score?: number;
  research_status?: 'Researched' | 'Not Researched' | 'Stale' | 'Failed' | string;
  outreach_status?: 'Not Generated' | 'Draft' | 'Approved' | 'Needs Research' | string;
  last_researched_at?: string | null;
  status: 'new' | 'contacted' | 'qualified' | 'unqualified' | 'archived' | string;
  source: string;
  source_url?: string | null;
  generation_job_id?: string | null;
  last_verified_at?: string | null;
  notes?: string | null;
  is_synthetic: boolean;
  created_at: string;
  updated_at: string;
}

// Module 2 Intelligence Types
export interface Evidence {
  id?: string;
  source_name: string;
  source_url: string;
  source_type: string;
  supporting_snippet: string;
  published_date?: string | null;
  recency_tier: 'recent' | 'fresh' | 'moderate' | 'old' | string;
  confidence: number;
  is_observation_vs_inference: 'observation' | 'inference' | string;
  is_synthetic: boolean;
}

export interface Finding {
  id?: string;
  category: string;
  title: string;
  summary: string;
  importance: 'low' | 'medium' | 'high' | 'critical' | string;
  confidence: number;
  evidence: Evidence[];
}

export interface ResearchSignal {
  id?: string;
  signal_type: string;
  title: string;
  description: string;
  source_name: string;
  confidence: number;
  recency_tier: string;
  importance: string;
}

export interface ResearchOpportunity {
  id?: string;
  title: string;
  reason: string;
  potential_offer?: string | null;
  confidence: number;
  observation_text: string;
  inference_text: string;
}

export interface PersonalizationAngle {
  id?: string;
  angle_title: string;
  angle_reason: string;
  evidence_ids: string[];
  confidence: number;
}

export interface ResearchProfile {
  id: string;
  company_id: string;
  contact_id?: string | null;
  lead_id?: string | null;
  research_depth: 'basic' | 'standard' | 'deep' | string;
  intelligence_score: number;
  confidence_score: number;
  summary?: string | null;
  company_overview?: string | null;
  business_model?: string | null;
  industry?: string | null;
  products_services: string[];
  recent_activity?: string | null;
  last_researched_at: string;
  is_synthetic: boolean;

  findings: Finding[];
  evidence_items: Evidence[];
  signals: ResearchSignal[];
  opportunities: ResearchOpportunity[];
  personalization_angles: PersonalizationAngle[];
}

export interface ResearchJobLog {
  id: string;
  level: string;
  message: string;
  step?: string | null;
  lead_id?: string | null;
  created_at: string;
}

export interface ResearchJob {
  id: string;
  name: string;
  research_depth: 'basic' | 'standard' | 'deep' | string;
  status: 'QUEUED' | 'IDENTIFYING' | 'DISCOVERING' | 'FETCHING' | 'ANALYZING' | 'EXTRACTING' | 'SCORING' | 'FINALIZING' | 'COMPLETED' | 'PARTIAL' | 'FAILED' | 'CANCELLED' | string;
  total_leads: number;
  processed_count: number;
  successful_count: number;
  partial_count: number;
  failed_count: number;
  progress_percentage: number;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  is_synthetic: boolean;
  created_at: string;
  logs?: ResearchJobLog[];
}

// Module 3 Personalization & Offer Types
export interface OfferProfile {
  id: string;
  name: string;
  description: string;
  target_customer: string;
  value_proposition: string;
  differentiators?: string | null;
  proof_points?: string | null;
  cta: string;
  tone_preferences?: string | null;
  is_active: boolean;
  is_synthetic: boolean;
  created_at: string;
  updated_at: string;
}

export interface OutreachDraftVersion {
  id: string;
  draft_id: string;
  version_number: number;
  subject: string;
  body: string;
  personalization_score: number;
  change_description?: string | null;
  created_at: string;
}

export interface OutreachDraft {
  id: string;
  lead_id: string;
  contact_id: string;
  offer_id?: string | null;
  objective: string;
  tone: string;
  length: string;
  personalization_level: 'MINIMAL' | 'STANDARD' | 'DEEP' | string;
  cta_type: string;
  subject: string;
  subject_options: string[];
  preview_text?: string | null;
  body: string;
  ps_text?: string | null;
  personalization_score: number;
  evidence_score: number;
  relevance_score: number;
  naturalness_score: number;
  status: 'DRAFT' | 'APPROVED' | 'ARCHIVED' | 'NEEDS_RESEARCH' | string;
  unsupported_claims: any[];
  message_plan?: any;
  evidence_used: any[];
  is_synthetic: boolean;
  created_at: string;
  updated_at: string;
  offer?: OfferProfile | null;
  versions?: OutreachDraftVersion[];
}

export interface OutreachJobLog {
  id: string;
  level: string;
  message: string;
  step?: string | null;
  created_at: string;
}

export interface OutreachJob {
  id: string;
  name: string;
  status: 'QUEUED' | 'PREPARING' | 'SELECTING_EVIDENCE' | 'GENERATING' | 'VALIDATING' | 'SAVING' | 'COMPLETED' | 'PARTIAL' | 'FAILED' | 'CANCELLED' | string;
  total_leads: number;
  processed_count: number;
  successful_count: number;
  failed_count: number;
  needs_research_count: number;
  progress_percentage: number;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  is_synthetic: boolean;
  created_at: string;
  logs?: OutreachJobLog[];
}

// Module 4 Mailbox, Campaign & Deliverability Types
export interface Mailbox {
  id: string;
  provider: 'gmail' | 'microsoft' | 'smtp' | 'simulated' | string;
  email: string;
  provider_account_id?: string | null;
  display_name?: string | null;
  connection_status: 'CONNECTED' | 'NEEDS_ATTENTION' | 'DISCONNECTED' | string;
  daily_send_limit: number;
  current_usage: number;
  health_score: number;
  bounce_rate: number;
  complaint_rate: number;
  reply_rate: number;
  spf_status: string;
  dkim_status: string;
  dmarc_status: string;
  last_sync_at: string;
  is_synthetic: boolean;
  created_at: string;
  updated_at: string;
}

export interface CampaignRecipient {
  id: string;
  campaign_id: string;
  contact_id: string;
  mailbox_id?: string | null;
  status: string;
  scheduled_at?: string | null;
  sent_at?: string | null;
  error_reason?: string | null;
}

export interface Campaign {
  id: string;
  name: string;
  description?: string | null;
  status: 'DRAFT' | 'SCHEDULED' | 'ACTIVE' | 'PAUSED' | 'COMPLETED' | 'CANCELLED' | 'FAILED' | string;
  timezone: string;
  schedule_config: any;
  total_recipients: number;
  sent_count: number;
  delivered_count: number;
  opened_count: number;
  replied_count: number;
  positive_replied_count: number;
  bounced_count: number;
  complaint_count: number;
  opt_out_count: number;
  mailbox_ids: string[];
  is_synthetic: boolean;
  created_at: string;
  updated_at: string;
  recipients?: CampaignRecipient[];
}

export interface CampaignReviewResponse {
  campaign_name: string;
  total_recipients: number;
  approved_messages_count: number;
  missing_outreach_count: number;
  suppressed_count: number;
  invalid_count: number;
  selected_mailboxes_count: number;
  total_daily_capacity: number;
  warnings: string[];
  can_launch: boolean;
}

export interface GlobalAnalyticsResponse {
  total_leads: number;
  qualified_leads: number;
  researched_leads: number;
  outreach_generated: number;
  outreach_approved: number;
  emails_sent: number;
  emails_delivered: number;
  emails_opened: number;
  replies_count: number;
  positive_replies_count: number;
  delivery_rate: number;
  reply_rate: number;
  positive_reply_rate: number;
  bounce_rate: number;
  complaint_rate: number;
  opt_out_rate: number;
}

export interface DeliverabilityOverviewResponse {
  overall_health_score: number;
  spf_status: string;
  dkim_status: string;
  dmarc_status: string;
  bounce_rate: number;
  complaint_rate: number;
  delivery_rate: number;
  provider_errors_count: number;
  recommendations: string[];
}

export interface Module4Contract {
  draft_id: string;
  lead_id: string;
  contact_id: string;
  recipient_email?: string | null;
  recipient_name: string;
  recipient_title?: string | null;
  company_name: string;
  subject: string;
  body: string;
  preview_text?: string | null;
  ps_text?: string | null;
  offer_name?: string | null;
  personalization_score: number;
  status: string;
  approved_at: string;
}

export interface JobLog {
  id: string;
  level: string;
  message: string;
  step?: string | null;
  created_at: string;
}

export interface GenerationJob {
  id: string;
  name: string;
  search_type: 'ai' | 'manual' | string;
  status: string;
  niche: string;
  country: string;
  query_params: SearchPlan;
  requested_count: number;
  discovered_count: number;
  valid_count: number;
  duplicates_count: number;
  saved_count: number;
  progress_percentage: number;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  is_synthetic: boolean;
  created_at: string;
  updated_at: string;
  logs?: JobLog[];
}

export interface CountryStat {
  country: string;
  code: string;
  lead_count: number;
  company_count: number;
  avg_score: number;
  percentage: number;
}

export interface DashboardStats {
  total_leads: number;
  unique_leads: number;
  leads_generated_today: number;
  total_companies: number;
  total_contacts: number;
  generation_jobs_count: number;
  avg_quality_score: number;
  researched_leads_count?: number;
  research_coverage_pct?: number;
  high_intelligence_count?: number;
  outreach_ready_count?: number;
  drafts_generated_count?: number;
  approved_drafts_count?: number;
  top_countries: CountryStat[];
  recent_jobs: GenerationJob[];
}

export interface LeadFilterParams {
  search?: string;
  country?: string;
  region?: string;
  city?: string;
  industry?: string;
  min_score?: number;
  status?: string;
  has_email?: boolean;
  has_phone?: boolean;
  has_website?: boolean;
  research_status?: string;
  outreach_status?: string;
  source?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: string;
}

export interface PaginatedLeadsResponse {
  items: Lead[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
