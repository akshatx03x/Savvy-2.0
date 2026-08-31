from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class ContactBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: str
    job_title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    country: str
    region: Optional[str] = None
    city: Optional[str] = None
    source: str = "web"
    source_url: Optional[str] = None
    verification_status: str = "unverified"


class ContactCreate(ContactBase):
    company_id: str


class ContactResponse(ContactBase):
    id: str
    company_id: str
    normalized_email: Optional[str] = None
    normalized_phone: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    is_synthetic: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
