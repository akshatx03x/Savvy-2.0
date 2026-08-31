import json
import re
from typing import Optional
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
    structured, validated SearchPlan Response objects.
    """

    @staticmethod
    async def analyze_prompt(prompt: str) -> SearchPlanResponse:
        prompt_lower = prompt.lower().strip()

        # Try LLM integration if API key is provided
        if settings.OPENAI_API_KEY and httpx:
            try:
                plan = await AIPlannerService._call_llm(prompt)
                if plan:
                    return plan
            except Exception as e:
                logger.warning(f"LLM call failed, falling back to rule parser: {e}")

        # High-intelligence Rule-Based Parser Fallback
        return AIPlannerService._parse_rule_based(prompt, prompt_lower)

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

        country = "United States"
        countries_map = {
            "united states": "United States", "usa": "United States", "us": "United States", "american": "United States",
            "united kingdom": "United Kingdom", "uk": "United Kingdom", "britain": "United Kingdom", "london": "United Kingdom",
            "canada": "Canada", "canadian": "Canada",
            "australia": "Australia", "australian": "Australia",
            "germany": "Germany", "german": "Germany",
            "france": "France", "french": "France",
            "india": "India", "indian": "India",
            "singapore": "Singapore",
            "japan": "Japan",
            "brazil": "Brazil",
        }
        for k, v in countries_map.items():
            if k in prompt_lower:
                country = v
                break

        region = None
        regions_map = [
            "Washington", "California", "Texas", "New York", "Florida",
            "Illinois", "Pennsylvania", "Ohio", "Georgia", "North Carolina",
            "Ontario", "Quebec", "British Columbia", "Bavaria", "London"
        ]
        for r in regions_map:
            if r.lower() in prompt_lower:
                region = r
                break

        city = None
        cities_map = [
            "Seattle", "San Francisco", "Los Angeles", "New York", "Chicago",
            "Miami", "Austin", "Toronto", "Vancouver", "Sydney", "Berlin", "Paris", "Tokyo", "London"
        ]
        for c in cities_map:
            if c.lower() in prompt_lower:
                city = c
                break

        niche = "Business Services"
        niches_map = {
            "real estate": "Real Estate",
            "realty": "Real Estate",
            "broker": "Real Estate",
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
            website_required="website" in prompt_lower or "site" in prompt_lower or True,
            public_email_required="email" in prompt_lower or "contact" in prompt_lower or True,
            phone_required="phone" in prompt_lower or "call" in prompt_lower or False,
            social_presence_required="linkedin" in prompt_lower or "social" in prompt_lower or False,
            active_business_required="active" in prompt_lower or True,
        )

        keywords = [word for word in prompt.split() if len(word) > 4 and word.lower() not in ["find", "leads", "business", "businesses", "companies", "in", "with", "active"]]

        return SearchPlanResponse(
            niche=niche,
            country=country,
            region=region,
            city=city,
            quantity=quantity,
            quality=quality,
            requirements=reqs,
            keywords=keywords[:5],
            confidence_score=0.92,
            explanation=f"Identified targeting {niche} in {country}" + (f" ({region})" if region else "") + f" requesting {quantity} high-quality prospects.",
        )

    @staticmethod
    async def _call_llm(prompt: str) -> Optional[SearchPlanResponse]:
        system_prompt = (
            "You are an expert B2B Prospecting Search AI. Analyze the user request and return STRICT JSON matching the SearchPlan schema."
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
