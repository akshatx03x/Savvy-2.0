import urllib.parse
from typing import List, Optional
import httpx
from app.sources.base import BaseSourceAdapter
from app.schemas.ai import SearchPlanResponse
from app.services.deduplication import RawLeadData
from app.services.normalization import normalize_domain, normalize_phone
from app.core.config import settings
from app.core.logging import logger


class YelpAdapter(BaseSourceAdapter):
    """
    Yelp Fusion API Source Adapter.
    Searches Yelp business directory for real, verified local businesses.
    NEVER generates synthetic or invented leads.
    """

    def __init__(self):
        super().__init__(name="Yelp Directory", is_synthetic_adapter=False)

    @property
    def credentials_present(self) -> bool:
        return bool(settings.YELP_API_KEY and settings.YELP_API_KEY.strip())

    async def search(self, plan: SearchPlanResponse, limit: int) -> List[RawLeadData]:
        if not self.credentials_present:
            logger.info("Yelp API Key not configured. Skipping Yelp search.")
            return []

        api_key = settings.YELP_API_KEY.strip()
        niche = plan.niche
        location_parts = [p for p in [plan.city, plan.region, plan.country] if p]
        location_str = ", ".join(location_parts) or "United States"

        url = f"https://api.yelp.com/v3/businesses/search?term={urllib.parse.quote(niche)}&location={urllib.parse.quote(location_str)}&limit={min(limit, 50)}"
        headers = {"Authorization": f"Bearer {api_key}"}

        discovered_leads: List[RawLeadData] = []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    businesses = data.get("businesses", [])
                    for biz in businesses:
                        name = biz.get("name")
                        if not name:
                            continue

                        phone = biz.get("display_phone") or biz.get("phone")
                        yelp_url = biz.get("url")
                        city = biz.get("location", {}).get("city") or plan.city
                        country = biz.get("location", {}).get("country") or plan.country

                        raw_lead = RawLeadData(
                            company_name=name,
                            domain=None,
                            website=yelp_url,
                            country=country,
                            region=plan.region,
                            city=city,
                            industry=niche,
                            full_name=None,
                            email=None,
                            phone=phone,
                            source="Yelp Directory",
                            source_url=yelp_url,
                            verification_status="verified",
                            is_synthetic=False,
                        )
                        discovered_leads.append(raw_lead)
                else:
                    logger.error(f"Yelp API returned HTTP {resp.status_code}: {resp.text}")

        except Exception as e:
            logger.error(f"Yelp API request failed: {e}")

        return discovered_leads

    async def validate(self, raw_lead: RawLeadData) -> bool:
        return bool(raw_lead.company_name and raw_lead.country and raw_lead.is_synthetic is False)
