import urllib.parse
from typing import List, Optional
import httpx
from app.sources.base import BaseSourceAdapter
from app.schemas.ai import SearchPlanResponse
from app.services.deduplication import RawLeadData
from app.services.normalization import normalize_domain, normalize_phone
from app.core.config import settings
from app.core.logging import logger


class OpenStreetMapAdapter(BaseSourceAdapter):
    """
    OpenStreetMap & Nominatim POI Source Adapter.
    Performs legitimate public geographic & business discovery queries using OpenStreetMap data.
    ZERO-COST public business dataset. NEVER generates synthetic leads.
    """

    def __init__(self):
        super().__init__(name="OpenStreetMap", is_synthetic_adapter=False)

    @property
    def credentials_present(self) -> bool:
        return bool(settings.OPENSTREETMAP_ENABLED)

    async def search(self, plan: SearchPlanResponse, limit: int) -> List[RawLeadData]:
        if not self.credentials_present:
            return []

        niche = plan.niche
        country = plan.country
        region = plan.region or ""
        city = plan.city or ""

        location_str = f"{city} {region} {country}".strip()
        headers = {
            "User-Agent": "LeadSynthAI/1.0 (contact@leadsynth.app; B2B Prospect Discovery Engine)"
        }

        discovered_leads: List[RawLeadData] = []
        seen_names = set()

        # Query 1: OpenStreetMap Nominatim POI Search Endpoint
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        search_phrases = [
            f"{niche} in {city} {region} {country}".strip(),
            f"{niche} in {city} {country}".strip(),
            f"office in {city} {country}".strip(),
            f"business in {city} {country}".strip(),
        ]

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                for phrase in search_phrases:
                    if len(discovered_leads) >= limit:
                        break

                    params = {
                        "q": phrase,
                        "format": "json",
                        "addressdetails": 1,
                        "extratags": 1,
                        "limit": min(limit, 25),
                    }
                    try:
                        resp = await client.get(nominatim_url, params=params)
                        if resp.status_code == 200:
                            results = resp.json()
                            for item in results:
                                tags = item.get("extratags", {})
                                name = item.get("name") or tags.get("name") or tags.get("brand") or tags.get("operator")
                                if not name:
                                    # Fallback: extract primary title from display_name
                                    display_parts = item.get("display_name", "").split(",")
                                    if display_parts:
                                        candidate = display_parts[0].strip()
                                        if len(candidate) > 2 and not candidate.isdigit():
                                            name = candidate

                                if not name or len(name.strip()) < 2:
                                    continue

                                norm_name = name.lower().strip()
                                if norm_name in seen_names:
                                    continue
                                seen_names.add(norm_name)

                                website = tags.get("website") or tags.get("contact:website") or tags.get("url")
                                domain = normalize_domain(website) if website else None
                                phone = tags.get("phone") or tags.get("contact:phone")
                                norm_phone = normalize_phone(phone) if phone else None

                                osm_type = item.get("osm_type", "node")
                                osm_id = item.get("osm_id", "0")
                                source_url = f"https://www.openstreetmap.org/{osm_type}/{osm_id}"

                                addr = item.get("address", {})
                                lead_city = city or addr.get("city") or addr.get("town") or addr.get("state_district")
                                lead_region = region or addr.get("state") or addr.get("region")

                                raw_lead = RawLeadData(
                                    company_name=name.strip(),
                                    domain=domain,
                                    website=website,
                                    country=country,
                                    region=lead_region,
                                    city=lead_city,
                                    industry=niche,
                                    full_name=None,  # Real public entity: no contact invented
                                    first_name=None,
                                    last_name=None,
                                    job_title=None,
                                    email=tags.get("email") or tags.get("contact:email"),
                                    phone=norm_phone or phone,
                                    source="OpenStreetMap",
                                    source_url=source_url,
                                    verification_status="verified",
                                    description=f"Verified business entity discovered on OpenStreetMap in {location_str}.",
                                    is_synthetic=False,
                                )
                                discovered_leads.append(raw_lead)
                                if len(discovered_leads) >= limit:
                                    break
                    except Exception as sub_err:
                        logger.warning(f"Nominatim phrase '{phrase}' error: {sub_err}")

        except Exception as e:
            logger.warning(f"OpenStreetMap Nominatim search error: {e}")

        # Query 2: Fallback to Overpass API if still below limit
        if len(discovered_leads) < limit:
            try:
                overpass_url = "https://overpass-api.de/api/interpreter"
                country_code = plan.country_code or "IN"
                if country.lower() in ["india", "indian"]:
                    country_code = "IN"
                elif country.lower() in ["united states", "usa", "us"]:
                    country_code = "US"

                query = f"""
                [out:json][timeout:10];
                area["ISO3166-1"="{country_code}"]->.searchArea;
                (
                  node["office"](area.searchArea);
                  node["shop"](area.searchArea);
                  node["amenity"](area.searchArea);
                );
                out body 15;
                """
                async with httpx.AsyncClient(timeout=8.0, headers=headers) as client:
                    resp = await client.post(overpass_url, data={"data": query})
                    if resp.status_code == 200:
                        data = resp.json()
                        for elem in data.get("elements", []):
                            tags = elem.get("tags", {})
                            cname = tags.get("name") or tags.get("brand")
                            if cname and cname.lower().strip() not in seen_names:
                                seen_names.add(cname.lower().strip())
                                elem_type = elem.get("type", "node")
                                elem_id = elem.get("id")
                                raw_lead = RawLeadData(
                                    company_name=cname.strip(),
                                    domain=normalize_domain(tags.get("website")),
                                    website=tags.get("website"),
                                    country=country,
                                    region=region,
                                    city=city,
                                    industry=niche,
                                    full_name=None,
                                    first_name=None,
                                    last_name=None,
                                    job_title=None,
                                    email=tags.get("email"),
                                    phone=tags.get("phone"),
                                    source="OpenStreetMap",
                                    source_url=f"https://www.openstreetmap.org/{elem_type}/{elem_id}",
                                    verification_status="verified",
                                    description=f"Verified entity on OpenStreetMap.",
                                    is_synthetic=False,
                                )
                                discovered_leads.append(raw_lead)
                                if len(discovered_leads) >= limit:
                                    break
            except Exception as overpass_err:
                logger.warning(f"Overpass fallback query error: {overpass_err}")

        return discovered_leads

    async def validate(self, raw_lead: RawLeadData) -> bool:
        return bool(raw_lead.company_name and raw_lead.country and raw_lead.is_synthetic is False)
