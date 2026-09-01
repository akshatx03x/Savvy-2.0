import urllib.parse
from typing import List, Optional
import httpx
from app.sources.base import BaseSourceAdapter
from app.schemas.ai import SearchPlanResponse
from app.services.deduplication import RawLeadData
from app.services.normalization import normalize_domain, normalize_phone, normalize_company_name
from app.core.config import settings
from app.core.logging import logger


class GooglePlacesAdapter(BaseSourceAdapter):
    """
    Google Places API Source Adapter (Places API - Text Search).
    Fetches real business locations and verified place details.
    NEVER generates synthetic or invented leads.
    """

    def __init__(self):
        super().__init__(name="Google Places", is_synthetic_adapter=False)

    @property
    def credentials_present(self) -> bool:
        return bool(settings.GOOGLE_MAPS_API_KEY and settings.GOOGLE_MAPS_API_KEY.strip())

    async def search(self, plan: SearchPlanResponse, limit: int) -> List[RawLeadData]:
        if not self.credentials_present:
            logger.info("Google Places API Key not configured. Skipping Google Places search.")
            return []

        api_key = settings.GOOGLE_MAPS_API_KEY.strip()
        niche = plan.niche
        country = plan.country
        region = plan.region or ""
        city = plan.city or ""

        # Build clean geographic query string
        location_parts = [p for p in [city, region, country] if p]
        location_str = ", ".join(location_parts)
        text_query = f"{niche} in {location_str}"

        discovered_leads: List[RawLeadData] = []

        # Try Google Places API (New Text Search Endpoint) first
        new_places_url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,places.internationalPhoneNumber,places.primaryType,places.types",
        }
        body = {
            "textQuery": text_query,
            "pageSize": min(limit, 20),
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.post(new_places_url, headers=headers, json=body)
                if resp.status_code == 200:
                    data = resp.json()
                    places = data.get("places", [])
                    for place in places:
                        raw_lead = self._parse_new_place(place, plan)
                        if raw_lead:
                            discovered_leads.append(raw_lead)
                elif resp.status_code in [400, 403, 404]:
                    # Fallback to Legacy Google Places Text Search API
                    legacy_leads = await self._search_legacy_places(client, api_key, text_query, plan, limit)
                    discovered_leads.extend(legacy_leads)
                else:
                    logger.error(f"Google Places API error {resp.status_code}: {resp.text}")

        except Exception as e:
            logger.error(f"Google Places API request failed: {e}")

        return discovered_leads

    def _parse_new_place(self, place: dict, plan: SearchPlanResponse) -> Optional[RawLeadData]:
        place_id = place.get("id")
        display_name_obj = place.get("displayName", {})
        company_name = display_name_obj.get("text") if isinstance(display_name_obj, dict) else str(display_name_obj)

        if not company_name or len(company_name.strip()) < 2:
            return None

        website_uri = place.get("websiteUri")
        domain = normalize_domain(website_uri) if website_uri else None
        phone = place.get("internationalPhoneNumber") or place.get("nationalPhoneNumber")
        norm_phone = normalize_phone(phone) if phone else None

        return RawLeadData(
            company_name=company_name.strip(),
            domain=domain,
            website=website_uri,
            country=plan.country,
            region=plan.region,
            city=plan.city,
            industry=plan.niche,
            full_name=None,  # Real business discovery: no contact invented
            first_name=None,
            last_name=None,
            job_title=None,
            email=None,      # Real business discovery: email left None if not on place record
            phone=norm_phone or phone,
            source="Google Places",
            source_url=website_uri or f"https://www.google.com/maps/place/?q=place_id:{place_id}",
            verification_status="verified",
            description=f"Verified business listing from Google Places in {plan.country}.",
            is_synthetic=False,
        )

    async def _search_legacy_places(
        self, client: httpx.AsyncClient, api_key: str, text_query: str, plan: SearchPlanResponse, limit: int
    ) -> List[RawLeadData]:
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={urllib.parse.quote(text_query)}&key={api_key}"
        leads = []
        resp = await client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            for res in results[:limit]:
                name = res.get("name")
                if not name:
                    continue
                place_id = res.get("place_id")
                # Get place details for website & phone
                detail_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,website,formatted_phone_number,international_phone_number&key={api_key}"
                d_resp = await client.get(detail_url)
                website = None
                phone = None
                if d_resp.status_code == 200:
                    d_data = d_resp.json().get("result", {})
                    website = d_data.get("website")
                    phone = d_data.get("international_phone_number") or d_data.get("formatted_phone_number")

                domain = normalize_domain(website) if website else None

                leads.append(
                    RawLeadData(
                        company_name=name,
                        domain=domain,
                        website=website,
                        country=plan.country,
                        region=plan.region,
                        city=plan.city,
                        industry=plan.niche,
                        full_name=None,
                        email=None,
                        phone=phone,
                        source="Google Places",
                        source_url=website or f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                        verification_status="verified",
                        is_synthetic=False,
                    )
                )
        return leads

    async def validate(self, raw_lead: RawLeadData) -> bool:
        return bool(raw_lead.company_name and raw_lead.country and raw_lead.is_synthetic is False)
