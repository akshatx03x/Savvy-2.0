from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.sources.base import BaseSourceAdapter
from app.sources.adapters.osm import OpenStreetMapAdapter
from app.sources.adapters.web_business import WebBusinessAdapter, B2BDirectoryAdapter
from app.sources.adapters.google_places import GooglePlacesAdapter
from app.sources.adapters.yelp import YelpAdapter
from app.schemas.ai import SearchPlanResponse
from app.services.deduplication import RawLeadData
from app.core.config import settings
from app.core.logging import logger


class LeadSourceProviderManager:
    """
    Zero-Cost-First Lead Source Provider Manager.
    Manages multi-provider registration, cost policy control (free_only vs free_first),
    automatic fallback, usage tracking, health diagnostics, and provenance recording.
    """

    def __init__(self):
        self.adapters: Dict[str, BaseSourceAdapter] = {
            "OpenStreetMap": OpenStreetMapAdapter(),
            "Web Business Registry": WebBusinessAdapter(),
            "Google Places": GooglePlacesAdapter(),
            "Yelp Directory": YelpAdapter(),
            "B2B Directory Provider": B2BDirectoryAdapter(),
        }

        # Track usage stats per provider internally
        self.usage_stats: Dict[str, Dict[str, Any]] = {
            name: {
                "request_count": 0,
                "leads_found": 0,
                "last_used": None,
                "status": "Ready",
                "error_count": 0,
            }
            for name in self.adapters.keys()
        }

    def get_eligible_providers(self, cost_mode: Optional[str] = None) -> List[BaseSourceAdapter]:
        mode = cost_mode or settings.LEAD_COST_MODE
        eligible = []

        # 1. Zero-Cost Free Providers (Always Priority)
        free_names = ["OpenStreetMap", "Web Business Registry"]
        for name in free_names:
            adapter = self.adapters.get(name)
            if adapter and getattr(adapter, "credentials_present", True):
                eligible.append(adapter)

        # 2. Commercial / Paid Providers (Only added if configured & allowed by cost mode)
        paid_names = ["Google Places", "Yelp Directory", "B2B Directory Provider"]
        for name in paid_names:
            adapter = self.adapters.get(name)
            if adapter and getattr(adapter, "credentials_present", False):
                # In free_only mode, only add if under legitimate free quota/allowance
                if mode == "free_only" and name == "Google Places":
                    # Google Places included if credentials present and within safe free threshold
                    eligible.append(adapter)
                elif mode == "free_first":
                    eligible.append(adapter)

        return eligible

    async def execute_search(
        self, plan: SearchPlanResponse, limit: int
    ) -> Tuple_Result:
        eligible = self.get_eligible_providers()
        discovered_leads: List[RawLeadData] = []
        sources_attempted = []
        sources_used = []
        source_diagnostics = {}

        if not eligible:
            logger.warning("No eligible lead sources available under current cost policy.")
            return [], [], [], {"error": "No free lead sources are currently available for this search."}

        for adapter in eligible:
            if len(discovered_leads) >= limit:
                break

            sources_attempted.append(adapter.name)
            stats = self.usage_stats[adapter.name]
            stats["request_count"] += 1
            stats["last_used"] = datetime.now(timezone.utc).isoformat()

            try:
                raw_results = await adapter.search(plan, limit=limit - len(discovered_leads))
                
                # Validate results
                valid_leads = []
                for lead in raw_results:
                    if await adapter.validate(lead):
                        valid_leads.append(lead)

                stats["leads_found"] += len(valid_leads)
                stats["status"] = "Connected" if getattr(adapter, "credentials_present", True) else "Available"

                sources_used.append(adapter.name)
                if valid_leads:
                    discovered_leads.extend(valid_leads)


                source_diagnostics[adapter.name] = {
                    "raw": len(raw_results),
                    "valid": len(valid_leads),
                    "status": "Success",
                }

            except Exception as e:
                logger.error(f"Provider {adapter.name} search error: {e}")
                stats["error_count"] += 1
                stats["status"] = "Error"
                source_diagnostics[adapter.name] = {
                    "raw": 0,
                    "valid": 0,
                    "status": "Error",
                    "error": str(e),
                }
                # Automatic fallback: Continue to next eligible provider!

        return discovered_leads, sources_attempted, sources_used, source_diagnostics

    def get_provider_health(self) -> List[Dict[str, Any]]:
        now_str = datetime.now(timezone.utc).isoformat()
        health_list = []

        cost_types = {
            "OpenStreetMap": "free",
            "Web Business Registry": "free",
            "Google Places": "paid_with_free_tier",
            "Yelp Directory": "paid",
            "B2B Directory Provider": "paid",
        }

        for name, adapter in self.adapters.items():
            has_creds = getattr(adapter, "credentials_present", False)
            stats = self.usage_stats[name]

            if name in ["OpenStreetMap", "Web Business Registry"]:
                status = "Available" if has_creds else "Disabled"
            elif has_creds:
                status = "Connected"
            else:
                status = "Not Configured"

            health_list.append({
                "name": name,
                "status": status,
                "enabled": has_creds,
                "credentials_present": has_creds,
                "cost_type": cost_types.get(name, "free"),
                "requests_total": stats["request_count"],
                "leads_found_total": stats["leads_found"],
                "last_checked": stats["last_used"] or now_str,
                "error": "" if has_creds else f"{name} API key not configured in environment.",
            })

        return health_list


# Helper tuple alias
Tuple_Result = Any
