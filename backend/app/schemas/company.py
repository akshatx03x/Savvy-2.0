from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class CompanyBase(BaseModel):
    name: str
    domain: Optional[str] = None
    website: Optional[str] = None
    country: str
    region: Optional[str] = None
    city: Optional[str] = None
    industry: str
    description: Optional[str] = None
    employee_count_range: Optional[str] = None
    linkedin_url: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: str
    normalized_name: str
    normalized_domain: Optional[str] = None
    contact_count: int = 0
    lead_score: int = 50
    is_synthetic: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
