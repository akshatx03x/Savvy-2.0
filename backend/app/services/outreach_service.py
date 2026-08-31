from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.offer import OfferProfile
from app.models.outreach import OutreachDraft, OutreachDraftVersion
from app.models.outreach_job import OutreachJob, OutreachJobLog
from app.schemas.outreach import (
    OutreachGenerationRequest,
    OutreachRewriteRequest,
    OutreachJobCreate,
    Module4OutreachContract,
)
from app.services.personalization_engine import PersonalizationEngine
from app.services.research_service import ResearchService
from app.core.config import settings


class OutreachService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_draft_by_id(self, draft_id: str) -> Optional[OutreachDraft]:
        stmt = (
            select(OutreachDraft)
            .options(
                selectinload(OutreachDraft.versions),
                selectinload(OutreachDraft.lead).selectinload(Lead.company),
                selectinload(OutreachDraft.lead).selectinload(Lead.contact),
            )
            .where(OutreachDraft.id == draft_id)
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_draft_by_lead_id(self, lead_id: str) -> Optional[OutreachDraft]:
        stmt = (
            select(OutreachDraft)
            .options(selectinload(OutreachDraft.versions))
            .where(OutreachDraft.lead_id == lead_id)
            .order_by(desc(OutreachDraft.created_at))
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def generate_outreach_draft(self, req: OutreachGenerationRequest) -> OutreachDraft:
        # Fetch lead
        stmt_lead = (
            select(Lead)
            .options(selectinload(Lead.company), selectinload(Lead.contact))
            .where(Lead.id == req.lead_id)
        )
        res_lead = await self.db.execute(stmt_lead)
        lead = res_lead.scalars().first()
        if not lead:
            raise ValueError(f"Lead {req.lead_id} not found")

        # Fetch Offer if provided
        offer_info = None
        if req.offer_id:
            stmt_offer = select(OfferProfile).where(OfferProfile.id == req.offer_id)
            res_offer = await self.db.execute(stmt_offer)
            offer_obj = res_offer.scalars().first()
            if offer_obj:
                offer_info = {
                    "id": offer_obj.id,
                    "name": offer_obj.name,
                    "description": offer_obj.description,
                    "value_proposition": offer_obj.value_proposition,
                    "cta": offer_obj.cta,
                }

        # Fetch Module 2 Research Profile
        research_svc = ResearchService(self.db)
        profile_obj = await research_svc.get_profile_by_lead_id(req.lead_id)
        research_profile = None
        if profile_obj:
            research_profile = {
                "summary": profile_obj.summary,
                "company_overview": profile_obj.company_overview,
                "evidence_items": [
                    {
                        "source_name": e.source_name,
                        "source_url": e.source_url,
                        "supporting_snippet": e.supporting_snippet,
                        "confidence": e.confidence,
                        "recency_tier": e.recency_tier,
                    }
                    for e in profile_obj.evidence_items
                ],
            }

        lead_info = {
            "company_name": lead.company.name,
            "contact_name": lead.contact.full_name,
            "contact_title": lead.contact.job_title,
            "country": lead.country,
            "industry": lead.industry,
        }

        # Personalization Engine Execution
        draft_content, validation, message_plan = await PersonalizationEngine.generate_draft(
            lead_info,
            research_profile,
            offer_info,
            req.custom_objective or req.objective,
            req.tone,
            req.length,
            req.cta_type,
            req.personalization_level,
        )

        status_val = draft_content.get("status", "DRAFT")

        # Check existing draft
        existing = await self.get_draft_by_lead_id(req.lead_id)
        if existing:
            draft = existing
            draft.offer_id = req.offer_id
            draft.objective = req.custom_objective or req.objective
            draft.tone = req.tone
            draft.length = req.length
            draft.personalization_level = req.personalization_level
            draft.cta_type = req.cta_type
            draft.subject = draft_content["subject"]
            draft.subject_options = draft_content.get("subject_options", [])
            draft.preview_text = draft_content.get("preview_text")
            draft.body = draft_content["body"]
            draft.ps_text = draft_content.get("ps_text")
            draft.personalization_score = draft_content.get("personalization_score", 90)
            draft.evidence_score = draft_content.get("evidence_score", 92)
            draft.relevance_score = draft_content.get("relevance_score", 90)
            draft.naturalness_score = draft_content.get("naturalness_score", 88)
            draft.status = status_val
            draft.unsupported_claims = validation.unsupported_claims
            draft.message_plan = message_plan
            draft.evidence_used = draft_content.get("evidence_used", [])
        else:
            draft = OutreachDraft(
                lead_id=lead.id,
                contact_id=lead.contact_id,
                offer_id=req.offer_id,
                objective=req.custom_objective or req.objective,
                tone=req.tone,
                length=req.length,
                personalization_level=req.personalization_level,
                cta_type=req.cta_type,
                subject=draft_content["subject"],
                subject_options=draft_content.get("subject_options", []),
                preview_text=draft_content.get("preview_text"),
                body=draft_content["body"],
                ps_text=draft_content.get("ps_text"),
                personalization_score=draft_content.get("personalization_score", 90),
                evidence_score=draft_content.get("evidence_score", 92),
                relevance_score=draft_content.get("relevance_score", 90),
                naturalness_score=draft_content.get("naturalness_score", 88),
                status=status_val,
                unsupported_claims=validation.unsupported_claims,
                message_plan=message_plan,
                evidence_used=draft_content.get("evidence_used", []),
                is_synthetic=settings.ENABLE_SYNTHETIC_DATA,
            )
            self.db.add(draft)

        await self.db.commit()
        await self.db.refresh(draft)

        # Record Version 1
        ver_stmt = select(OutreachDraftVersion).where(OutreachDraftVersion.draft_id == draft.id)
        ver_res = await self.db.execute(ver_stmt)
        vers = list(ver_res.scalars().all())
        new_version_num = len(vers) + 1

        version = OutreachDraftVersion(
            draft_id=draft.id,
            version_number=new_version_num,
            subject=draft.subject,
            body=draft.body,
            personalization_score=draft.personalization_score,
            change_description=f"Generated draft (Version {new_version_num})",
        )
        self.db.add(version)
        await self.db.commit()

        return draft

    async def rewrite_draft(self, draft_id: str, req: OutreachRewriteRequest) -> OutreachDraft:
        draft = await self.get_draft_by_id(draft_id)
        if not draft:
            raise ValueError(f"OutreachDraft {draft_id} not found")

        rewritten, validation = await PersonalizationEngine.rewrite_draft(
            draft.subject, draft.body, req.prompt, draft.evidence_used or []
        )

        draft.subject = rewritten["subject"]
        draft.body = rewritten["body"]
        draft.unsupported_claims = validation.unsupported_claims
        if not validation.is_valid:
            draft.status = "DRAFT" # Cannot be approved if unsupported claims introduced

        await self.db.commit()

        # Add Version
        ver_stmt = select(OutreachDraftVersion).where(OutreachDraftVersion.draft_id == draft.id)
        ver_res = await self.db.execute(ver_stmt)
        vers = list(ver_res.scalars().all())
        new_version_num = len(vers) + 1

        version = OutreachDraftVersion(
            draft_id=draft.id,
            version_number=new_version_num,
            subject=draft.subject,
            body=draft.body,
            personalization_score=draft.personalization_score,
            change_description=rewritten.get("change_description", f"AI Rewrite: {req.prompt}"),
        )
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(draft)

        return draft

    async def approve_draft(self, draft_id: str) -> OutreachDraft:
        draft = await self.get_draft_by_id(draft_id)
        if not draft:
            raise ValueError(f"OutreachDraft {draft_id} not found")

        if draft.unsupported_claims and len(draft.unsupported_claims) > 0:
            raise ValueError("Cannot approve draft while unsupported claims remain. Please fix claims first.")

        draft.status = "APPROVED"
        await self.db.commit()
        await self.db.refresh(draft)
        return draft

    async def archive_draft(self, draft_id: str) -> OutreachDraft:
        draft = await self.get_draft_by_id(draft_id)
        if not draft:
            raise ValueError(f"OutreachDraft {draft_id} not found")

        draft.status = "ARCHIVED"
        await self.db.commit()
        await self.db.refresh(draft)
        return draft

    async def update_draft(self, draft_id: str, updates: Dict[str, Any]) -> OutreachDraft:
        draft = await self.get_draft_by_id(draft_id)
        if not draft:
            raise ValueError(f"OutreachDraft {draft_id} not found")

        for k, v in updates.items():
            if hasattr(draft, k) and v is not None:
                setattr(draft, k, v)

        await self.db.commit()
        await self.db.refresh(draft)
        return draft

    async def get_drafts(self, status: Optional[str] = None, limit: int = 50) -> List[OutreachDraft]:
        stmt = select(OutreachDraft).options(selectinload(OutreachDraft.versions)).order_by(desc(OutreachDraft.created_at)).limit(limit)
        if status:
            stmt = stmt.where(OutreachDraft.status == status)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # Bulk Outreach Jobs
    async def create_outreach_job(self, req: OutreachJobCreate) -> OutreachJob:
        job = OutreachJob(
            name=req.name or f"Bulk Outreach ({len(req.lead_ids)} leads)",
            status="QUEUED",
            total_leads=len(req.lead_ids),
            target_lead_ids={"lead_ids": req.lead_ids},
            config_json=req.model_dump(),
            is_synthetic=settings.ENABLE_SYNTHETIC_DATA,
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        self.db.add(OutreachJobLog(job_id=job.id, level="INFO", message="Outreach job queued", step="QUEUED"))
        await self.db.commit()

        return job

    async def get_outreach_jobs(self, limit: int = 50) -> List[OutreachJob]:
        stmt = select(OutreachJob).options(selectinload(OutreachJob.logs)).order_by(desc(OutreachJob.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_outreach_job_by_id(self, job_id: str) -> Optional[OutreachJob]:
        stmt = select(OutreachJob).options(selectinload(OutreachJob.logs)).where(OutreachJob.id == job_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    # Module 4 Contract Interface
    async def get_module4_contract(self, draft_id: str) -> Module4OutreachContract:
        draft = await self.get_draft_by_id(draft_id)
        if not draft:
            raise ValueError(f"Draft {draft_id} not found")

        stmt_lead = select(Lead).options(selectinload(Lead.company), selectinload(Lead.contact)).where(Lead.id == draft.lead_id)
        res_lead = await self.db.execute(stmt_lead)
        lead = res_lead.scalars().first()

        stmt_offer = select(OfferProfile).where(OfferProfile.id == draft.offer_id) if draft.offer_id else None
        offer_name = None
        if stmt_offer:
            res_offer = await self.db.execute(stmt_offer)
            offer_obj = res_offer.scalars().first()
            if offer_obj:
                offer_name = offer_obj.name

        return Module4OutreachContract(
            draft_id=draft.id,
            lead_id=draft.lead_id,
            contact_id=draft.contact_id,
            recipient_email=lead.contact.email if lead else None,
            recipient_name=lead.contact.full_name if lead else "Prospect",
            recipient_title=lead.contact.job_title if lead else None,
            company_name=lead.company.name if lead else "Company",
            subject=draft.subject,
            body=draft.body,
            preview_text=draft.preview_text,
            ps_text=draft.ps_text,
            offer_name=offer_name,
            personalization_score=draft.personalization_score,
            status=draft.status,
            approved_at=draft.updated_at,
        )
