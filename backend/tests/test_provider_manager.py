import pytest
from app.sources.provider_manager import LeadSourceProviderManager
from app.sources.adapters.osm import OpenStreetMapAdapter
from app.core.ai_provider_manager import ai_provider_manager
from app.schemas.ai import SearchPlanResponse
from app.core.config import settings


@pytest.mark.asyncio
async def test_provider_manager_eligibility():
    mgr = LeadSourceProviderManager()
    eligible = mgr.get_eligible_providers(cost_mode="free_only")
    
    names = [a.name for a in eligible]
    assert "OpenStreetMap" in names
    assert "Web Business Registry" in names
    # Quota/Paid providers should be omitted in free_only if unconfigured
    assert "B2B Directory Provider" not in names


@pytest.mark.asyncio
async def test_osm_adapter_structure():
    adapter = OpenStreetMapAdapter()
    assert adapter.name == "OpenStreetMap"
    assert adapter.is_synthetic_adapter is False
    assert adapter.credentials_present is True


@pytest.mark.asyncio
async def test_ai_provider_manager_health():
    health = ai_provider_manager.get_ai_provider_health()
    assert len(health) >= 2
    names = [h["name"] for h in health]
    assert "Gemini" in names
    assert "OpenAI" in names


@pytest.mark.asyncio
async def test_lead_search_execution_zero_cost():
    mgr = LeadSourceProviderManager()
    plan = SearchPlanResponse(
        niche="Real Estate",
        country="India",
        region="Uttar Pradesh",
        city="Ghaziabad",
        quantity=5,
    )
    
    discovered, attempted, used, diag = await mgr.execute_search(plan, limit=5)
    assert isinstance(discovered, list)
    assert isinstance(attempted, list)
    assert "OpenStreetMap" in attempted or "Web Business Registry" in attempted
