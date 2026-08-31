import pytest
from app.services.ai_planner import AIPlannerService


@pytest.mark.asyncio
async def test_ai_planner_parsing():
    prompt = "Find 500 real estate businesses in Washington with active websites and public business contact information."
    plan = await AIPlannerService.analyze_prompt(prompt)

    assert plan.niche == "Real Estate"
    assert plan.country == "United States"
    assert plan.region == "Washington"
    assert plan.quantity == 500
    assert plan.requirements.website_required is True
    assert plan.requirements.public_email_required is True
    assert plan.confidence_score > 0.8
