import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.database import Base
from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.mailbox import Mailbox
from app.models.campaign import Campaign, CampaignRecipient
from app.models.suppression import SuppressionEntry
from app.models.outreach import OutreachDraft
from app.services.mailbox_selector import MailboxSelector
from app.services.sending_engine import SendingEngine


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
async def test_mailbox_selection(db_session):
    mb1 = Mailbox(provider="gmail", email="sales1@company.com", daily_send_limit=500, current_usage=490, health_score=90)
    mb2 = Mailbox(provider="gmail", email="sales2@company.com", daily_send_limit=500, current_usage=100, health_score=95)
    db_session.add_all([mb1, mb2])
    await db_session.commit()

    selected = await MailboxSelector.select_mailbox(db_session)
    assert selected is not None
    assert selected.email == "sales2@company.com"


@pytest.mark.asyncio
async def test_suppression_check(db_session):
    supp = SuppressionEntry(email="optout@test.com", reason="OPT_OUT")
    db_session.add(supp)
    await db_session.commit()

    is_supp = await SendingEngine.is_suppressed(db_session, "optout@test.com")
    assert is_supp is True

    is_supp_clean = await SendingEngine.is_suppressed(db_session, "clean@test.com")
    assert is_supp_clean is False


@pytest.mark.asyncio
async def test_send_idempotency(db_session):
    # Setup test company, contact, lead, approved draft, mailbox
    co = Company(name="Acme Corp", normalized_name="acme corp", country="United States", industry="SaaS")
    db_session.add(co)
    await db_session.flush()

    ct = Contact(company_id=co.id, full_name="Tom Hanks", email="tom@acme.com", country="United States")
    db_session.add(ct)
    await db_session.flush()

    lead = Lead(company_id=co.id, contact_id=ct.id, country="United States", industry="SaaS")
    db_session.add(lead)
    await db_session.flush()

    draft = OutreachDraft(
        lead_id=lead.id,
        contact_id=ct.id,
        subject="Quick question",
        body="Hi Tom, saw your recent update.",
        status="APPROVED",
    )
    db_session.add(draft)
    await db_session.flush()

    mb = Mailbox(provider="simulated", email="sender@company.com", connection_status="CONNECTED", daily_send_limit=500, current_usage=0)
    db_session.add(mb)
    await db_session.flush()

    camp = Campaign(name="Test Campaign", status="ACTIVE", mailbox_ids=[mb.id])
    db_session.add(camp)
    await db_session.flush()

    rec = CampaignRecipient(campaign_id=camp.id, contact_id=ct.id, status="PENDING")
    db_session.add(rec)
    await db_session.commit()

    # First send attempt
    success, code = await SendingEngine.process_recipient_send(db_session, camp, rec)
    assert success is True
    assert code == "SENT"
    assert rec.status == "SENT"

    # Worker retry attempt — Idempotency check MUST return ALREADY_SENT and 0 duplicate sends!
    retry_success, retry_code = await SendingEngine.process_recipient_send(db_session, camp, rec)
    assert retry_success is True
    assert retry_code == "ALREADY_SENT"
