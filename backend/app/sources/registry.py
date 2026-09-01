from typing import List
from app.sources.base import BaseSourceAdapter
from app.sources.adapters.google_places import GooglePlacesAdapter
from app.sources.adapters.web_business import WebBusinessAdapter, B2BDirectoryAdapter
from app.sources.adapters.yelp import YelpAdapter
from app.sources.adapters.simulated_live import SimulatedLiveAdapter
from app.core.config import settings


class SourceRegistry:
    """
    Source Registry for Lead Generation Adapters.
    Registers and provides active live search adapters.
    Synthetic adapters are strictly excluded from standard user search flows.
    """

    def __init__(self):
        self.adapters: List[BaseSourceAdapter] = [
            GooglePlacesAdapter(),
            WebBusinessAdapter(),
            YelpAdapter(),
            B2BDirectoryAdapter(),
        ]

    def get_active_adapters(self) -> List[BaseSourceAdapter]:
        """
        Returns only real, live source adapters for user searches.
        Synthetic adapters are never used in standard lead discovery flows.
        """
        return [a for a in self.adapters if not a.is_synthetic_adapter]

