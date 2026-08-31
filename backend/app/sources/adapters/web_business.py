from typing import List
from app.sources.base import BaseSourceAdapter
from app.schemas.ai import SearchPlanResponse
from app.services.deduplication import RawLeadData


class WebBusinessAdapter(BaseSourceAdapter):
    """
    Public Business Registry Connector Interface.
    Integrates with public business registers and web indexes.
    """

    def __init__(self):
        super().__init__(name="Web Business Registry", is_synthetic_adapter=False)

    async def search(self, plan: SearchPlanResponse, limit: int) -> List[RawLeadData]:
        # Production connector placeholder — ready for licensed API keys
        return []

    async def validate(self, raw_lead: RawLeadData) -> bool:
        return bool(raw_lead.company_name and raw_lead.country)


class B2BDirectoryAdapter(BaseSourceAdapter):
    """
    Licensed B2B Directory Connector Interface.
    Integrates with B2B data providers (Apollo/ZoomInfo licensed API endpoints).
    """

    def __init__(self):
        super().__init__(name="B2B Directory Provider", is_synthetic_adapter=False)

    async def search(self, plan: SearchPlanResponse, limit: int) -> List[RawLeadData]:
        # Production connector placeholder — ready for licensed API keys
        return []

    async def validate(self, raw_lead: RawLeadData) -> bool:
        return bool(raw_lead.email or raw_lead.domain)
