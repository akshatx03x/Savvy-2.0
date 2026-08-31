import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.database import Base
from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.research import ResearchProfile, ResearchFinding, ResearchEvidence
from app.schemas.research import EvidenceSchema, FindingSchema, SignalSchema, OpportunitySchema
from app.services.intelligence_scoring import calculate_intelligence_score
from app.services.research_service import ResearchService


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionTest = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionTest() as session:
        yield session
    await engine.dispose()


def test_intelligence_scoring_calculation():
    ev1 = EvidenceSchema(
        source_name="Company Website",
        source_url="https://example.com/about",
        supporting_snippet="Leading provider in US",
        recency_tier="recent",
    )
    ev2 = EvidenceSchema(
        source_name="Public Press Release",
        source_url="https://example.com/news/1",
        supporting_snippet="Expanded operations by 40%",
        recency_tier="recent",
    )
    sig1 = SignalSchema(
        signal_type="Expansion",
        title="Regional Expansion",
        description="Expanded operations",
        source_name="Public Press Release",
    )
    opp1 = OpportunitySchema(
        title="Service Modernization",
        reason="Expansion requires CRM scaling",
        observation_text="Observation: Company expanded operations.",
        inference_text="Inference: May require CRM scaling.",
    )

    score = calculate_intelligence_score([ev1, ev2], [], [sig1], [opp1])
    assert 50 <= score <= 100


@pytest.mark.asyncio
async def test_module3_contract_structure(db_session):
    # Setup test company, contact, lead
    co = Company(
        name="Apex Tech Solutions",
        normalized_name="apex tech solutions",
        domain="apextech.com",
        normalized_domain="apextech.com",
        country="United States",
        industry="Software & Technology",
    )
    db_session.add(co)
    await db_session.flush()

    ct = Contact(
        company_id=co.id,
        full_name="Alex Mercer",
        job_title="CEO",
        email="alex@apextech.com",
        country="United States",
    )
    db_session.add(ct)
    await db_session.flush()

    lead = Lead(
        company_id=co.id,
        contact_id=ct.id,
        country="United States",
        industry="Software & Technology",
        lead_score=90,
    )
    db_session.add(lead)
    await db_session.commit()

    service = ResearchService(db_session)
    contract = await service.get_module3_contract(lead.id)

    assert contract.lead_id == lead.id
    assert contract.company_name == "Apex Tech Solutions"
    assert contract.contact_name == "Alex Mercer"
    assert contract.confidence >= 0.50
