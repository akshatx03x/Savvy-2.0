import json
import re
from typing import Optional, Tuple
from app.schemas.ai import SearchPlanResponse, SearchRequirements
from app.core.config import settings
from app.core.logging import logger

try:
    import httpx
except ImportError:
    httpx = None


class AIPlannerService:
    """
    AI Search Planner Service: Converts natural language prospect requests into
    structured, validated SearchPlan Response objects with structured ISO geographic codes.
    """

    @staticmethod
    async def analyze_prompt(prompt: str) -> SearchPlanResponse:
        from app.core.ai_provider_manager import ai_provider_manager
        plan = await ai_provider_manager.analyze_prompt(prompt)
        if plan:
            return plan
        return AIPlannerService._parse_rule_based(prompt, prompt.lower().strip())


    @staticmethod
    def _parse_rule_based(prompt: str, prompt_lower: str) -> SearchPlanResponse:
        quantity = 100
        qty_match = re.search(r"\b(\d{1,5})\b", prompt)
        if qty_match:
            try:
                parsed_qty = int(qty_match.group(1))
                if 1 <= parsed_qty <= 5000:
                    quantity = parsed_qty
            except ValueError:
                pass

        # City Mapping: (City, Region, RegionCode, Country, CountryCode)
        cities_map = {
            "toronto": ("Toronto", "Ontario", "CA-ON", "Canada", "CA"),
            "vancouver": ("Vancouver", "British Columbia", "CA-BC", "Canada", "CA"),
            "montreal": ("Montreal", "Quebec", "CA-QC", "Canada", "CA"),
            "seattle": ("Seattle", "Washington", "US-WA", "United States", "US"),
            "san francisco": ("San Francisco", "California", "US-CA", "United States", "US"),
            "los angeles": ("Los Angeles", "California", "US-CA", "United States", "US"),
            "austin": ("Austin", "Texas", "US-TX", "United States", "US"),
            "new york": ("New York", "New York", "US-NY", "United States", "US"),
            "chicago": ("Chicago", "Illinois", "US-IL", "United States", "US"),
            "miami": ("Miami", "Florida", "US-FL", "United States", "US"),
            "sydney": ("Sydney", "New South Wales", "AU-NSW", "Australia", "AU"),
            "melbourne": ("Melbourne", "Victoria", "AU-VIC", "Australia", "AU"),
            "berlin": ("Berlin", "Berlin", "DE-BE", "Germany", "DE"),
            "munich": ("Munich", "Bavaria", "DE-BY", "Germany", "DE"),
            "paris": ("Paris", "Ile-de-France", "FR-IDF", "France", "FR"),
            "london": ("London", "Greater London", "GB-LND", "United Kingdom", "GB"),
            "delhi": ("Delhi", "Delhi", "IN-DL", "India", "IN"),
            "mumbai": ("Mumbai", "Maharashtra", "IN-MH", "India", "IN"),
            "tokyo": ("Tokyo", "Tokyo", "JP-13", "Japan", "JP"),
        }

        city = None
        region = None
        region_code = None
        country = None
        country_code = None

        for c_key, (c_name, r_name, r_code, ct_name, ct_code) in cities_map.items():
            if c_key in prompt_lower:
                city = c_name
                region = r_name
                region_code = r_code
                country = ct_name
                country_code = ct_code
                break

        if not country:
            countries_map = {
                "canada": ("Canada", "CA"), "canadian": ("Canada", "CA"),
                "united kingdom": ("United Kingdom", "GB"), "uk": ("United Kingdom", "GB"), "britain": ("United Kingdom", "GB"),
                "australia": ("Australia", "AU"), "australian": ("Australia", "AU"),
                "germany": ("Germany", "DE"), "german": ("Germany", "DE"),
                "france": ("France", "FR"), "french": ("France", "FR"),
                "india": ("India", "IN"), "indian": ("India", "IN"),
                "singapore": ("Singapore", "SG"),
                "japan": ("Japan", "JP"),
                "brazil": ("Brazil", "BR"),
                "united states": ("United States", "US"), "usa": ("United States", "US"), "american": ("United States", "US"),
            }
            for k, (c_name, c_code) in countries_map.items():
                if re.search(r"\b" + k + r"\b", prompt_lower):
                    country = c_name
                    country_code = c_code
                    break

        if not country:
            country = "United States"
            country_code = "US"

        if not region:
            regions_map = {
                "ontario": ("Ontario", "CA-ON"),
                "quebec": ("Quebec", "CA-QC"),
                "british columbia": ("British Columbia", "CA-BC"),
                "california": ("California", "US-CA"),
                "texas": ("Texas", "US-TX"),
                "new york": ("New York", "US-NY"),
                "florida": ("Florida", "US-FL"),
                "illinois": ("Illinois", "US-IL"),
                "pennsylvania": ("Pennsylvania", "US-PA"),
                "ohio": ("Ohio", "US-OH"),
                "georgia": ("Georgia", "US-GA"),
                "north carolina": ("North Carolina", "US-NC"),
                "washington": ("Washington", "US-WA"),
                "bavaria": ("Bavaria", "DE-BY"),
            }
            for k, (r_name, r_code) in regions_map.items():
                if k in prompt_lower:
                    region = r_name
                    region_code = r_code
                    break

        niche = "Business Services"
        niches_map = {
            "real estate": "Real Estate",
            "realty": "Real Estate",
            "broker": "Real Estate",
            "dentist": "Healthcare & Dental",
            "dental": "Healthcare & Dental",
            "saas": "Software & Technology",
            "software": "Software & Technology",
            "tech": "Software & Technology",
            "technology": "Software & Technology",
            "e-commerce": "E-Commerce & Retail",
            "ecommerce": "E-Commerce & Retail",
            "retail": "E-Commerce & Retail",
            "healthcare": "Healthcare & Medical",
            "medical": "Healthcare & Medical",
            "clinic": "Healthcare & Medical",
            "construction": "Construction & Engineering",
            "builder": "Construction & Engineering",
            "marketing": "Marketing & Advertising",
            "agency": "Marketing & Advertising",
            "finance": "Financial Services",
            "financial": "Financial Services",
            "legal": "Legal Services",
            "law": "Legal Services",
            "consulting": "Management Consulting",
            "restaurant": "Hospitality & Dining",
            "hotel": "Hospitality & Dining",
        }
        for k, v in niches_map.items():
            if k in prompt_lower:
                niche = v
                break

        quality = "high"
        if "premium" in prompt_lower or "verified" in prompt_lower:
            quality = "premium"
        elif "basic" in prompt_lower:
            quality = "basic"

        reqs = SearchRequirements(
            website_required="website" in prompt_lower,
            public_email_required="email" in prompt_lower or "contact" in prompt_lower,
            phone_required="phone" in prompt_lower,
            social_presence_required="linkedin" in prompt_lower,
            active_business_required=True,
        )


        keywords = [
            word for word in prompt.split()
            if len(word) > 3 and word.lower() not in ["find", "leads", "business", "businesses", "companies", "in", "with", "active"]
        ]

        return SearchPlanResponse(
            niche=niche,
            country=country,
            country_code=country_code,
            region=region,
            region_code=region_code,
            city=city,
            quantity=quantity,
            quality=quality,
            requirements=reqs,
            keywords=keywords[:5],
            confidence_score=0.95,
            explanation=f"Targeting {niche} in {country}" + (f" ({region})" if region else "") + f" requesting {quantity} verified business leads.",
        )

    @staticmethod
    async def _call_llm(prompt: str) -> Optional[SearchPlanResponse]:
        system_prompt = (
            "You are an expert B2B Prospecting Search AI. Analyze the user request and return STRICT JSON matching the SearchPlan schema, including ISO country_code and region_code."
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.AI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed_json = json.loads(content)
                return SearchPlanResponse(**parsed_json)
        return None
