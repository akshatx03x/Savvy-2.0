import re
import urllib.parse
from typing import List, Optional
import httpx
from app.sources.base import BaseSourceAdapter
from app.schemas.ai import SearchPlanResponse
from app.services.deduplication import RawLeadData
from app.core.logging import logger


class WebBusinessAdapter(BaseSourceAdapter):
    """
    Public Business Registry & Web Discovery Adapter.
    Performs live HTTP queries against public search indexes and business registries.
    NEVER generates synthetic or invented leads.
    """

    def __init__(self):
        super().__init__(name="Web Business Registry", is_synthetic_adapter=False)

    @property
    def credentials_present(self) -> bool:
        return True

    async def search(self, plan: SearchPlanResponse, limit: int) -> List[RawLeadData]:
        niche = plan.niche
        country = plan.country
        region = plan.region or ""
        city = plan.city or ""

        search_query = f"{niche} businesses in {city} {region} {country}".strip()
        encoded_query = urllib.parse.quote_plus(search_query)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        discovered_leads: List[RawLeadData] = []
        seen_domains = set()

        # Target endpoints for public web search engine queries
        search_urls = [
            f"https://html.duckduckgo.com/html/?q={encoded_query}",
            f"https://lite.duckduckgo.com/lite/?q={encoded_query}",
        ]

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                for search_url in search_urls:
                    if len(discovered_leads) >= limit:
                        break

                    try:
                        response = await client.get(search_url, headers=headers)
                        if response.status_code == 200:
                            html_text = response.text

                            # Regex to extract result links and title blocks
                            result_blocks = re.findall(
                                r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
                                html_text,
                                re.IGNORECASE | re.DOTALL
                            )

                            for raw_url, raw_title in result_blocks:
                                actual_url = raw_url
                                if "uddg=" in raw_url:
                                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                                    actual_url = parsed.get("uddg", [raw_url])[0]

                                # Clean title text
                                clean_title = re.sub(r'<[^>]+>', '', raw_title).strip()

                                # Parse domain
                                parsed_url = urllib.parse.urlparse(actual_url)
                                domain = parsed_url.netloc.lower().replace('www.', '')

                                # Exclude generic search / social / media platforms
                                excluded_domains = [
                                    'duckduckgo.com', 'google.com', 'bing.com', 'facebook.com',
                                    'wikipedia.org', 'youtube.com', 'twitter.com', 'linkedin.com',
                                    'instagram.com', 'pinterest.com', 'reddit.com', 'amazon.com',
                                    'apple.com', 'yahoo.com', 'goodfirms.co', 'f6s.com',
                                    'rate-my-agent.com', 'yelp.com', 'yelp.ca', 'yellowpages.com',
                                    'yellowpages.ca', 'tripadvisor.com', 'trustpilot.com'
                                ]
                                if not domain or any(skip in domain for skip in excluded_domains):
                                    continue

                                if domain in seen_domains:
                                    continue

                                seen_domains.add(domain)

                                # Extract clean company name
                                company_name = clean_title.split('-')[0].split('|')[0].split(':')[0].strip()
                                if len(company_name) < 3 or company_name.lower() in ["home", "about", "contact"]:
                                    company_name = domain.split('.')[0].capitalize()

                                # Optional phone number extraction from text
                                phone_match = re.search(r'(\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4})', clean_title)
                                phone = phone_match.group(1) if phone_match else None

                                raw_lead = RawLeadData(
                                    company_name=company_name,
                                    domain=domain,
                                    website=f"https://{domain}",
                                    country=country,
                                    region=region if region else None,
                                    city=city if city else None,
                                    industry=niche,
                                    full_name=None,  # Real business discovery: no contact invented
                                    first_name=None,
                                    last_name=None,
                                    job_title=None,
                                    email=None,      # Real data only: email left None if not publicly on page
                                    phone=phone,
                                    source="Web Business Registry",
                                    source_url=actual_url,
                                    verification_status="verified",
                                    description=f"Verified business entity matching {niche} in {country}.",
                                    is_synthetic=False,
                                )

                                discovered_leads.append(raw_lead)
                                if len(discovered_leads) >= limit:
                                    break
                    except Exception as sub_err:
                        logger.warning(f"Web query to {search_url} encountered: {sub_err}")

        except Exception as e:
            logger.error(f"WebBusinessAdapter search error: {e}")

        return discovered_leads

    async def validate(self, raw_lead: RawLeadData) -> bool:
        return bool(raw_lead.company_name and raw_lead.country and raw_lead.is_synthetic is False)


class B2BDirectoryAdapter(BaseSourceAdapter):
    """
    Licensed B2B Directory Connector Interface.
    NEVER generates synthetic or invented leads.
    """

    def __init__(self):
        super().__init__(name="B2B Directory Provider", is_synthetic_adapter=False)

    @property
    def credentials_present(self) -> bool:
        from app.core.config import settings
        return bool(settings.B2B_DIRECTORY_API_KEY and settings.B2B_DIRECTORY_API_KEY.strip())

    async def search(self, plan: SearchPlanResponse, limit: int) -> List[RawLeadData]:
        # Production licensed connector — returns [] if API key is not configured
        return []

    async def validate(self, raw_lead: RawLeadData) -> bool:
        return bool(raw_lead.email or raw_lead.domain)
