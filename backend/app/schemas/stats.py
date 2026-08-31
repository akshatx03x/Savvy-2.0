from typing import List, Dict
from pydantic import BaseModel


class CountryStat(BaseModel):
    country: str
    code: str
    lead_count: int
    company_count: int
    avg_score: float
    percentage: float


class DashboardStatsResponse(BaseModel):
    total_leads: int
    unique_leads: int
    leads_generated_today: int
    total_companies: int
    total_contacts: int
    generation_jobs_count: int
    avg_quality_score: float
    top_countries: List[CountryStat]
    recent_jobs: List[dict]
