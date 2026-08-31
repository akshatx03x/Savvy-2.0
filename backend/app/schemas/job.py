from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.ai import SearchPlanResponse


class JobCreate(BaseModel):
    name: Optional[str] = None
    search_type: str = "ai" # ai, manual
    plan: SearchPlanResponse


class JobLogResponse(BaseModel):
    id: str
    level: str
    message: str
    step: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobResponse(BaseModel):
    id: str
    name: str
    search_type: str
    status: str
    niche: str
    country: str
    query_params: Dict[str, Any]
    requested_count: int
    discovered_count: int
    valid_count: int
    duplicates_count: int
    saved_count: int
    progress_percentage: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_synthetic: bool = False
    created_at: datetime
    updated_at: datetime
    logs: Optional[List[JobLogResponse]] = None

    model_config = ConfigDict(from_attributes=True)
