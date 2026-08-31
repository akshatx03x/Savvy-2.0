from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.offer import OfferResponse


class OutreachGenerationRequest(BaseModel):
    lead_id: str
    offer_id: Optional[str] = None
    objective: str = "Book a meeting"
    tone: str = "Consultative"
    length: str = "Short"
    personalization_level: str = "DEEP" # MINIMAL, STANDARD, DEEP
    cta_type: str = "Soft CTA font"
    variants_count: int = Field(3, ge=1, le=3)
    custom_objective: Optional[str] = None


class OutreachRewriteRequest(BaseModel):
    prompt: str = Field(..., min_length=2) # e.g. "Make this less salesy", "Make opening stronger"
    preserve_evidence: bool = True


class ClaimValidationResult(BaseModel):
    is_valid: bool
    unsupported_claims: List[Dict[str, Any]] = Field(default_factory=list)
    verified_claims: List[Dict[str, Any]] = Field(default_factory=list)
    quality_score: int = Field(90, ge=0, le=100)


class MessagePlan(BaseModel):
    opening: Dict[str, Any]
    problem_or_opportunity: Dict[str, Any]
    value_proposition: Dict[str, Any]
    cta: Dict[str, Any]


class OutreachDraftVersionResponse(BaseModel):
    id: str
    draft_id: str
    version_number: int
    subject: str
    body: str
    personalization_score: int
    change_description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OutreachDraftResponse(BaseModel):
    id: str
    lead_id: str
    contact_id: str
    offer_id: Optional[str] = None
    objective: str
    tone: str
    length: str
    personalization_level: str
    cta_type: str
    subject: str
    subject_options: List[str] = Field(default_factory=list)
    preview_text: Optional[str] = None
    body: str
    ps_text: Optional[str] = None
    personalization_score: int
    evidence_score: int
    relevance_score: int
    naturalness_score: int
    status: str # DRAFT, APPROVED, ARCHIVED, NEEDS_RESEARCH
    unsupported_claims: List[Dict[str, Any]] = Field(default_factory=list)
    message_plan: Optional[Dict[str, Any]] = None
    evidence_used: List[Dict[str, Any]] = Field(default_factory=list)
    is_synthetic: bool = False
    created_at: datetime
    updated_at: datetime
    offer: Optional[OfferResponse] = None
    versions: Optional[List[OutreachDraftVersionResponse]] = None

    model_config = ConfigDict(from_attributes=True)


class OutreachJobCreate(BaseModel):
    lead_ids: List[str] = Field(..., min_length=1)
    offer_id: Optional[str] = None
    objective: str = "Book a meeting"
    tone: str = "Consultative"
    length: str = "Short"
    personalization_level: str = "DEEP"
    cta_type: str = "Soft CTA"
    name: Optional[str] = None


class OutreachJobLogResponse(BaseModel):
    id: str
    level: str
    message: str
    step: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OutreachJobResponse(BaseModel):
    id: str
    name: str
    status: str
    total_leads: int
    processed_count: int
    successful_count: int
    failed_count: int
    needs_research_count: int
    progress_percentage: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_synthetic: bool = False
    created_at: datetime
    logs: Optional[List[OutreachJobLogResponse]] = None

    model_config = ConfigDict(from_attributes=True)


# Module 4 Interface Contract
class Module4OutreachContract(BaseModel):
    draft_id: str
    lead_id: str
    contact_id: str
    recipient_email: Optional[str] = None
    recipient_name: str
    recipient_title: Optional[str] = None
    company_name: str
    subject: str
    body: str
    preview_text: Optional[str] = None
    ps_text: Optional[str] = None
    offer_name: Optional[str] = None
    personalization_score: int
    status: str
    approved_at: datetime

    model_config = ConfigDict(from_attributes=True)
