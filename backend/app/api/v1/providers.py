from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.sources.provider_manager import LeadSourceProviderManager
from app.core.ai_provider_manager import ai_provider_manager

router = APIRouter(prefix="/providers", tags=["Providers & Integrations"])


class ProviderItemStatus(BaseModel):
    name: str
    status: str  # Connected, Available, Not Configured, Limit Reached, Error
    enabled: bool
    credentials_present: bool
    cost_type: Optional[str] = "free"
    model: Optional[str] = None
    last_checked: str
    error: str = ""


class ProviderHealthResponse(BaseModel):
    lead_sources: List[ProviderItemStatus]
    ai_providers: List[ProviderItemStatus]
    cost_mode: Dict[str, str]


@router.get("/status")
async def get_provider_statuses():
    """
    Returns health diagnostic status for lead discovery sources and AI providers,
    including cost control modes (free_only vs free_first).
    """
    lead_mgr = LeadSourceProviderManager()
    lead_health = lead_mgr.get_provider_health()
    ai_health = ai_provider_manager.get_ai_provider_health()

    return {
        "lead_sources": lead_health,
        "ai_providers": ai_health,
        "cost_mode": {
            "lead_cost_mode": settings.LEAD_COST_MODE,
            "ai_cost_mode": settings.AI_COST_MODE,
        },
    }
