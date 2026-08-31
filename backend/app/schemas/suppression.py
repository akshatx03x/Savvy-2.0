from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SuppressionCreate(BaseModel):
    email: str
    contact_id: Optional[str] = None
    reason: str = "OPT_OUT" # OPT_OUT, HARD_BOUNCE, COMPLAINT, MANUAL, INVALID_ADDRESS
    source: str = "user_manual"


class SuppressionResponse(BaseModel):
    id: str
    email: str
    contact_id: Optional[str] = None
    reason: str
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
