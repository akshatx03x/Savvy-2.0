from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class EvidenceSchema(BaseModel):
    id: Optional[str] = None
    source_name: str
    source_url: str
    source_type: str = "website"
    supporting_snippet: str
    published_date: Optional[datetime] = None
    recency_tier: str = "fresh" # recent, fresh, moderate, old
    confidence: float = Field(0.90, ge=0.0, le=1.0)
    is_observation_vs_inference: str = "observation" # observation, inference
    is_synthetic: bool = False

    model_config = ConfigDict(from_attributes=True)


class FindingSchema(BaseModel):
    id: Optional[str] = None
    category: str
    title: str
    summary: str
    importance: str = "medium"
    confidence: float = Field(0.85, ge=0.0, le=1.0)
    evidence: List[EvidenceSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SignalSchema(BaseModel):
    id: Optional[str] = None
    signal_type: str
    title: str
    description: str
    source_name: str
    confidence: float = 0.85
    recency_tier: str = "recent"
    importance: str = "high"

    model_config = ConfigDict(from_attributes=True)


class OpportunitySchema(BaseModel):
    id: Optional[str] = None
    title: str
    reason: str
    potential_offer: Optional[str] = None
    confidence: float = 0.85
    observation_text: str
    inference_text: str

    model_config = ConfigDict(from_attributes=True)


class PersonalizationAngleSchema(BaseModel):
    id: Optional[str] = None
    angle_title: str
    angle_reason: str
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.90

    model_config = ConfigDict(from_attributes=True)


class ResearchProfileResponse(BaseModel):
    id: str
    company_id: str
    contact_id: Optional[str] = None
    lead_id: Optional[str] = None
    research_depth: str
    intelligence_score: int
    confidence_score: float
    summary: Optional[str] = None
    company_overview: Optional[str] = None
    business_model: Optional[str] = None
    industry: Optional[str] = None
    products_services: List[str] = Field(default_factory=list)
    recent_activity: Optional[str] = None
    last_researched_at: datetime
    is_synthetic: bool = False

    findings: List[FindingSchema] = Field(default_factory=list)
    evidence_items: List[EvidenceSchema] = Field(default_factory=list)
    signals: List[SignalSchema] = Field(default_factory=list)
    opportunities: List[OpportunitySchema] = Field(default_factory=list)
    personalization_angles: List[PersonalizationAngleSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ResearchJobCreate(BaseModel):
    lead_ids: List[str] = Field(..., min_length=1)
    research_depth: str = "standard" # basic, standard, deep
    name: Optional[str] = None


class ResearchJobLogResponse(BaseModel):
    id: str
    level: str
    message: str
    step: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResearchJobResponse(BaseModel):
    id: str
    name: str
    research_depth: str
    status: str
    total_leads: int
    processed_count: int
    successful_count: int
    partial_count: int
    failed_count: int
    progress_percentage: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_synthetic: bool = False
    created_at: datetime
    logs: Optional[List[ResearchJobLogResponse]] = None

    model_config = ConfigDict(from_attributes=True)


# Module 3 Interface Contract
class Module3ResearchContract(BaseModel):
    lead_id: str
    company_name: str
    contact_name: str
    contact_title: Optional[str] = None
    company_summary: str
    contact_summary: str
    key_findings: List[Dict[str, Any]]
    signals: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    personalization_angles: List[Dict[str, Any]]
    confidence: float
    last_researched_at: datetime

    model_config = ConfigDict(from_attributes=True)
