from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.schemas.research import FindingSchema, EvidenceSchema, SignalSchema, OpportunitySchema, PersonalizationAngleSchema


class RawResearchResult:
    def __init__(
        self,
        source_name: str,
        source_url: str,
        source_type: str,
        raw_text: str,
        title: Optional[str] = None,
        snippets: Optional[List[str]] = None,
    ):
        self.source_name = source_name
        self.source_url = source_url
        self.source_type = source_type
        self.raw_text = raw_text
        self.title = title or source_name
        self.snippets = snippets or [raw_text[:300]]


class BaseResearchSource(ABC):
    """
    Abstract Base Class for Lead Intelligence Research Sources.
    """

    def __init__(self, name: str, is_synthetic: bool = False):
        self.name = name
        self.is_synthetic = is_synthetic

    @abstractmethod
    async def discover_and_fetch(
        self, company_name: str, domain: Optional[str], country: str, depth: str
    ) -> List[RawResearchResult]:
        pass
