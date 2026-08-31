from typing import List, Dict, Any
from pydantic import BaseModel


class GlobalAnalyticsResponse(BaseModel):
    total_leads: int
    qualified_leads: int
    researched_leads: int
    outreach_generated: int
    outreach_approved: int
    emails_sent: int
    emails_delivered: int
    emails_opened: int
    replies_count: int
    positive_replies_count: int
    delivery_rate: float
    reply_rate: float
    positive_reply_rate: float
    bounce_rate: float
    complaint_rate: float
    opt_out_rate: float


class DeliverabilityOverviewResponse(BaseModel):
    overall_health_score: int
    spf_status: str
    dkim_status: str
    dmarc_status: str
    bounce_rate: float
    complaint_rate: float
    delivery_rate: float
    provider_errors_count: int
    recommendations: List[str]
