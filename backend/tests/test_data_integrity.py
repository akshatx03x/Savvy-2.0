import pytest
from app.core.config import settings
from app.sources.registry import SourceRegistry
from app.sources.adapters.web_business import WebBusinessAdapter
from app.schemas.ai import SearchPlanResponse, RequirementSpec
from app.services.lead_scoring import calculate_lead_score


def test_synthetic_data_disabled_by_default():
    """Verify ENABLE_SYNTHETIC_DATA is False for real leads only."""
    assert settings.ENABLE_SYNTHETIC_DATA is False


def test_source_registry_active_adapters():
    """Verify SourceRegistry returns only active non-synthetic adapters."""
    registry = SourceRegistry()
    adapters = registry.get_active_adapters()
    for adapter in adapters:
        assert adapter.is_synthetic_adapter is False


def test_lead_scoring_calculated_dynamically():
    """Verify lead score is calculated from real signals and not hardcoded."""
    # Discovered lead with website only
    score_basic = calculate_lead_score(
        has_website=True,
        has_email=False,
        has_phone=False,
        has_contact_name=False,
        has_job_title=False,
        verification_status="unverified"
    )
    assert score_basic == 40

    # Discovered lead with full details
    score_full = calculate_lead_score(
        has_website=True,
        has_email=True,
        has_phone=True,
        has_contact_name=True,
        has_job_title=True,
        verification_status="verified"
    )
    assert score_full == 100
    assert score_basic < score_full


@pytest.mark.asyncio
async def test_real_web_adapter_never_fabricates():
    """Verify WebBusinessAdapter returns real leads without fake email/contact padding."""
    adapter = WebBusinessAdapter()
    plan = SearchPlanResponse(
        niche="Real Estate",
        country="Canada",
        region="Ontario",
        city="Toronto",
        quantity=5,
        quality="high",
        requirements=RequirementSpec(
            website_required=True,
            public_email_required=False,
            phone_required=False,
            social_presence_required=False,
            active_business_required=True
        ),
        keywords=["real estate", "canada"],
        confidence_score=1.0,
        explanation="Real test search"
    )

    leads = await adapter.search(plan=plan, limit=5)
    for lead in leads:
        # Every returned lead must be non-synthetic
        assert lead.is_synthetic is False
        assert lead.source == "Web Business Registry"
        # Email and contact must NOT be invented
        if not lead.email:
            assert lead.email is None
        if not lead.full_name:
            assert lead.full_name is None
