from typing import List, Optional
from app.research.base import BaseResearchSource, RawResearchResult


class WebsiteCrawlerAdapter(BaseResearchSource):
    """
    Public Company Website Analyzer.
    Respects page priorities, page limits, and HTTP timeouts.
    """

    def __init__(self):
        super().__init__(name="Company Website Analyzer", is_synthetic=False)

    async def discover_and_fetch(
        self, company_name: str, domain: Optional[str], country: str, depth: str
    ) -> List[RawResearchResult]:
        # Production crawler connector placeholder — ready for HTTPX async crawler
        return []


class WebSearchResearchAdapter(BaseResearchSource):
    """
    Intelligent Web Search & News Research Connector.
    """

    def __init__(self):
        super().__init__(name="Public Web Search & News", is_synthetic=False)

    async def discover_and_fetch(
        self, company_name: str, domain: Optional[str], country: str, depth: str
    ) -> List[RawResearchResult]:
        # Production web search connector placeholder
        return []
