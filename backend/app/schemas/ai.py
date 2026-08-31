from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequirements(BaseModel):
    website_required: bool = True
    public_email_required: bool = True
    phone_required: bool = False
    social_presence_required: bool = False
    active_business_required: bool = True


class SearchPlanRequest(BaseModel):
    prompt: str = Field(..., description="Natural language search prompt", min_length=3)


class SearchPlanResponse(BaseModel):
    niche: str = Field(..., json_schema_extra={"example": "Real Estate"})
    country: str = Field(..., json_schema_extra={"example": "United States"})
    region: Optional[str] = Field(None, json_schema_extra={"example": "Washington"})
    city: Optional[str] = Field(None, json_schema_extra={"example": "Seattle"})
    quantity: int = Field(100, ge=1, le=5000)
    quality: str = Field("high", json_schema_extra={"example": "high"}) # basic, high, premium
    requirements: SearchRequirements = Field(default_factory=SearchRequirements)
    keywords: List[str] = Field(default_factory=list)
    confidence_score: float = Field(0.95, ge=0.0, le=1.0)
    explanation: Optional[str] = None
