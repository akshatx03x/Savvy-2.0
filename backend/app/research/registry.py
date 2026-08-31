from typing import List
from app.research.base import BaseResearchSource
from app.research.adapters.website_crawler import WebsiteCrawlerAdapter, WebSearchResearchAdapter
from app.research.adapters.simulated_research import SimulatedResearchAdapter
from app.core.config import settings


class ResearchSourceRegistry:
    def __init__(self):
        self.adapters: List[BaseResearchSource] = [
            WebsiteCrawlerAdapter(),
            WebSearchResearchAdapter(),
        ]
        if settings.ENABLE_SYNTHETIC_DATA:
            self.adapters.append(SimulatedResearchAdapter())

    def get_active_adapters(self) -> List[BaseResearchSource]:
        active = [a for a in self.adapters if not a.is_synthetic]
        if settings.ENABLE_SYNTHETIC_DATA:
            synthetic = [a for a in self.adapters if a.is_synthetic]
            return active + synthetic
        return active
