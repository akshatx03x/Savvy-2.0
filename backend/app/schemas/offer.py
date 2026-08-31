from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class OfferCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: str
    target_customer: str
    value_proposition: str
    differentiators: Optional[str] = None
    proof_points: Optional[str] = None
    cta: str = "Would you be open to a 15-minute call?"
    tone_preferences: Optional[str] = "Consultative"
    is_active: bool = True


class OfferUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_customer: Optional[str] = None
    value_proposition: Optional[str] = None
    differentiators: Optional[str] = None
    proof_points: Optional[str] = None
    cta: Optional[str] = None
    tone_preferences: Optional[str] = None
    is_active: Optional[bool] = None


class OfferResponse(BaseModel):
    id: str
    name: str
    description: str
    target_customer: str
    value_proposition: str
    differentiators: Optional[str] = None
    proof_points: Optional[str] = None
    cta: str
    tone_preferences: Optional[str] = None
    is_active: bool
    is_synthetic: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
