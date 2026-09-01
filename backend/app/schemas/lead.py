from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.company import CompanyResponse
from app.schemas.contact import ContactResponse


class LeadBase(BaseModel):
    country: str
    region: Optional[str] = None
    city: Optional[str] = None
    industry: str
    lead_score: int = 50
    status: str = "new"
    source: str = "web"
    source_url: Optional[str] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    company_id: str
    contact_id: Optional[str] = None
    generation_job_id: Optional[str] = None


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    lead_score: Optional[int] = None


class LeadResponse(LeadBase):
    id: str
    company_id: str
    contact_id: Optional[str] = None
    company: CompanyResponse
    contact: Optional[ContactResponse] = None
    generation_job_id: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    is_synthetic: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadFilter(BaseModel):
    search: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    industry: Optional[str] = None
    min_score: Optional[int] = None
    status: Optional[str] = None
    has_email: Optional[bool] = None
    has_phone: Optional[bool] = None
    has_website: Optional[bool] = None
    source: Optional[str] = None
    page: int = 1
    page_size: int = 25
    sort_by: str = "created_at"
    sort_order: str = "desc"
