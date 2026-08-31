import random
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from app.research.base import BaseResearchSource, RawResearchResult
from app.core.config import settings


class SimulatedResearchAdapter(BaseResearchSource):
    """
    Simulated Lead Research Adapter for Development & Testing.
    STRICT SAFETY RULES:
    1. Disabled if ENABLE_SYNTHETIC_DATA is False.
    2. Explicitly tags ALL evidence with is_synthetic = True.
    """

    def __init__(self):
        super().__init__(name="Simulated Web Intelligence", is_synthetic=True)

    async def discover_and_fetch(
        self, company_name: str, domain: Optional[str], country: str, depth: str
    ) -> List[RawResearchResult]:
        if not settings.ENABLE_SYNTHETIC_DATA:
            return []

        base_domain = domain or "example.com"
        results: List[RawResearchResult] = []

        # 1. Homepage & About Page
        results.append(
            RawResearchResult(
                source_name="Company Website - Homepage",
                source_url=f"https://www.{base_domain}",
                source_type="website",
                title=f"{company_name} | Official Website",
                raw_text=f"{company_name} is an industry-leading provider operating in {country}. We specialize in high-end commercial services, customer relationship management, and technology optimization.",
                snippets=[f"{company_name} provides comprehensive solutions across {country}."]
            )
        )

        results.append(
            RawResearchResult(
                source_name="Company Website - About Us",
                source_url=f"https://www.{base_domain}/about",
                source_type="website",
                title=f"About {company_name}",
                raw_text=f"Founded over a decade ago, {company_name} has grown its operational footprint in {country}. Our executive leadership team brings over 25 years of combined domain expertise.",
                snippets=[f"{company_name} has expanded operations in {country}."]
            )
        )

        if depth in ["standard", "deep"]:
            # 2. Services & Press Releases
            results.append(
                RawResearchResult(
                    source_name="Company Website - Press Release",
                    source_url=f"https://www.{base_domain}/news/expansion-announcement",
                    source_type="news",
                    title=f"{company_name} Announces Regional Expansion",
                    raw_text=f"{company_name} recently announced a major expansion of its service capabilities and team in {country}, increasing client onboarding capacity by 40%.",
                    snippets=[f"{company_name} expanded its service capabilities and client capacity by 40%."]
                )
            )

        if depth == "deep":
            # 3. Careers & Tech Stack Signals
            results.append(
                RawResearchResult(
                    source_name="Company Website - Careers",
                    source_url=f"https://www.{base_domain}/careers",
                    source_type="website",
                    title=f"Careers at {company_name}",
                    raw_text=f"We are actively hiring Senior Account Executives, Operations Leads, and Software Engineers to support our rapid growth in {country}.",
                    snippets=[f"Actively hiring Senior Account Executives and Operations Leads."]
                )
            )

        return results
