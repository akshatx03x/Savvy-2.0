import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base
from app.services.deduplication import DeduplicationService, RawLeadData


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
async def test_two_level_deduplication_multiple_contacts(db_session):
    dedup = DeduplicationService(db_session)

    # Lead 1: CEO at ABC Realty
    raw1 = RawLeadData(
        company_name="ABC Realty Inc",
        domain="abcrealty.com",
        country="United States",
        industry="Real Estate",
        full_name="John Smith",
        job_title="CEO",
        email="john@abcrealty.com",
        phone="+1 555 111 2222",
        is_synthetic=True,
    )

    # Lead 2: Marketing Director at ABC Realty (Same company, DIFFERENT contact)
    raw2 = RawLeadData(
        company_name="ABC Realty",
        domain="abcrealty.com",
        country="United States",
        industry="Real Estate",
        full_name="Sarah Smith",
        job_title="Marketing Director",
        email="sarah@abcrealty.com",
        phone="+1 555 333 4444",
        is_synthetic=True,
    )

    lead1, is_new_co1, is_new_ct1 = await dedup.process_raw_lead(raw1)
    lead2, is_new_co2, is_new_ct2 = await dedup.process_raw_lead(raw2)

    # Company 1 created
    assert is_new_co1 is True
    assert is_new_ct1 is True

    # Company 2 reused existing company! But contact 2 is NEW!
    assert is_new_co2 is False
    assert is_new_ct2 is True
    assert lead1.company_id == lead2.company_id
    assert lead1.contact_id != lead2.contact_id

    # Lead 3: Duplicate of John Smith (Same email) -> Should NOT create new contact or lead!
    raw3 = RawLeadData(
        company_name="ABC Realty LLC",
        domain="abcrealty.com",
        country="United States",
        industry="Real Estate",
        full_name="John Smith",
        job_title="CEO & Founder",
        email="john@abcrealty.com",
        phone="+1 555 111 2222",
        is_synthetic=True,
    )

    lead3, is_new_co3, is_new_ct3 = await dedup.process_raw_lead(raw3)
    assert is_new_co3 is False
    assert is_new_ct3 is False
    assert lead3.id == lead1.id
