import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.database import Base
from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.offer import OfferProfile
from app.schemas.offer import OfferCreate
from app.schemas.outreach import OutreachGenerationRequest, OutreachRewriteRequest
from app.services.offer_service import OfferService
from app.services.outreach_service import OutreachService
from app.core.ai_provider import ai_provider


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionTest = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionTest() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_offer_crud(db_session):
    service = OfferService(db_session)
    offer_data = OfferCreate(
        name="Website Conversion Optimization",
        description="Improve real estate site conversion",
        target_customer="Real Estate Businesses",
        value_proposition="Turn site visitors into inquiries",
        cta="Would you be open to a 15-minute audit?",
    )
    created = await service.create_offer(offer_data)
    assert created.id is not None
    assert created.name == "Website Conversion Optimization"

    offers = await service.get_offers()
    assert len(offers) == 1


@pytest.mark.asyncio
async def test_research_readiness_enforcement(db_session):
    # Setup company, contact, lead without research profile
    co = Company(name="Test Realty", normalized_name="test realty", country="United States", industry="Real Estate")
    db_session.add(co)
    await db_session.flush()

    ct = Contact(company_id=co.id, full_name="Jane Doe", email="jane@test.com", country="United States")
    db_session.add(ct)
    await db_session.flush()

    lead = Lead(company_id=co.id, contact_id=ct.id, country="United States", industry="Real Estate")
    db_session.add(lead)
    await db_session.commit()

    service = OutreachService(db_session)
    req = OutreachGenerationRequest(lead_id=lead.id, personalization_level="DEEP")
    draft = await service.generate_outreach_draft(req)

    # Should enforce NEEDS_RESEARCH state instead of fake deep personalization
    assert draft.status == "NEEDS_RESEARCH"


@pytest.mark.asyncio
async def test_unsupported_claim_rejection():
    body_with_unsupported = "Hi John, I saw your recent expansion into Texas and your latest Instagram post!"
    evidence = [{"source_name": "Company Site", "snippet": "Company offers broker services in Seattle."}]

    validation = await ai_provider.validate_claims(body_with_unsupported, evidence)
    assert validation["is_valid"] is False
    assert len(validation["unsupported_claims"]) > 0
