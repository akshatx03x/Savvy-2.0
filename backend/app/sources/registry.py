from typing import List
from app.sources.base import BaseSourceAdapter
from app.sources.adapters.web_business import WebBusinessAdapter, B2BDirectoryAdapter
from app.sources.adapters.simulated_live import SimulatedLiveAdapter
from app.core.config import settings


class SourceRegistry:
    def __init__(self):
        self.adapters: List[BaseSourceAdapter] = [
            WebBusinessAdapter(),
            B2BDirectoryAdapter(),
        ]
        if settings.ENABLE_SYNTHETIC_DATA:
            self.adapters.append(SimulatedLiveAdapter())

    def get_active_adapters(self) -> List[BaseSourceAdapter]:
        active = [a for a in self.adapters if not a.is_synthetic_adapter]
        if settings.ENABLE_SYNTHETIC_DATA:
            synthetic = [a for a in self.adapters if a.is_synthetic_adapter]
            return active + synthetic
        return active
