from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas.ai import SearchPlanResponse
from app.services.deduplication import RawLeadData


class BaseSourceAdapter(ABC):
    """
    Abstract Base Class for Lead Generation Source Adapters.
    Production connectors subclass this adapter interface.
    """

    def __init__(self, name: str, is_synthetic_adapter: bool = False):
        self.name = name
        self.is_synthetic_adapter = is_synthetic_adapter

    @abstractmethod
    async def search(self, plan: SearchPlanResponse, limit: int) -> List[RawLeadData]:
        """
        Execute discovery query against external source/API and return normalized RawLeadData items.
        """
        pass

    @abstractmethod
    async def validate(self, raw_lead: RawLeadData) -> bool:
        """
        Validate source-specific quality requirements.
        """
        pass
