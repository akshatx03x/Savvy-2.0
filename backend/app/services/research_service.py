from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.research import (
    ResearchProfile,
    ResearchFinding,
    ResearchEvidence,
    ResearchSignal,
    ResearchOpportunity,
    PersonalizationAngle,
)
from app.models.research_job import ResearchJob, ResearchJobLog
from app.schemas.research import (
    ResearchProfileResponse,
    Module3ResearchContract,
    ResearchJobCreate,
    FindingSchema,
    EvidenceSchema,
    SignalSchema,
    OpportunitySchema,
    PersonalizationAngleSchema,
)
from app.core.config import settings


class ResearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile_by_lead_id(self, lead_id: str) -> Optional[ResearchProfile]:
        stmt = (
            select(ResearchProfile)
            .options(
                selectinload(ResearchProfile.findings).selectinload(ResearchFinding.evidence),
                selectinload(ResearchProfile.evidence_items),
                selectinload(ResearchProfile.signals),
                selectinload(ResearchProfile.opportunities),
                selectinload(ResearchProfile.personalization_angles),
            )
            .where(ResearchProfile.lead_id == lead_id)
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create_research_job(self, data: ResearchJobCreate) -> ResearchJob:
        job_name = data.name or f"AI Research ({len(data.lead_ids)} leads) - {data.research_depth.capitalize()}"

        job = ResearchJob(
            name=job_name,
            research_depth=data.research_depth,
            status="QUEUED",
            total_leads=len(data.lead_ids),
            target_lead_ids={"lead_ids": data.lead_ids},
            is_synthetic=settings.ENABLE_SYNTHETIC_DATA,
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        self.db.add(ResearchJobLog(job_id=job.id, level="INFO", message="Research job queued", step="QUEUED"))
        await self.db.commit()

        return job

    async def get_research_jobs(self, limit: int = 50) -> List[ResearchJob]:
        stmt = select(ResearchJob).options(selectinload(ResearchJob.logs)).order_by(desc(ResearchJob.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_research_job_by_id(self, job_id: str) -> Optional[ResearchJob]:
        stmt = select(ResearchJob).options(selectinload(ResearchJob.logs)).where(ResearchJob.id == job_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def cancel_research_job(self, job_id: str) -> Optional[ResearchJob]:
        job = await self.get_research_job_by_id(job_id)
        if job and job.status in ["QUEUED", "IDENTIFYING", "DISCOVERING", "FETCHING", "ANALYZING"]:
            job.status = "CANCELLED"
            job.completed_at = datetime.now(timezone.utc)
            self.db.add(ResearchJobLog(job_id=job.id, level="WARNING", message="User requested job cancellation", step="CANCELLED"))
            await self.db.commit()
            await self.db.refresh(job)
        return job

    async def get_module3_contract(self, lead_id: str) -> Module3ResearchContract:
        """
        MODULE 3 CONTRACT:
        Provides structured prospect intelligence payload specifically formatted for
        Module 3's personalized outreach email generation engine.
        """
        stmt_lead = select(Lead).options(selectinload(Lead.company), selectinload(Lead.contact)).where(Lead.id == lead_id)
        res_lead = await self.db.execute(stmt_lead)
        lead = res_lead.scalars().first()

        if not lead:
            raise ValueError("Lead not found")

        profile = await self.get_profile_by_lead_id(lead_id)

        if not profile:
            # Fallback placeholder contract if not researched yet
            return Module3ResearchContract(
                lead_id=lead_id,
                company_name=lead.company.name,
                contact_name=lead.contact.full_name,
                contact_title=lead.contact.job_title,
                company_summary=f"{lead.company.name} is a {lead.industry} business operating in {lead.country}.",
                contact_summary=f"{lead.contact.full_name} is {lead.contact.job_title or 'Executive'} at {lead.company.name}.",
                key_findings=[],
                signals=[],
                opportunities=[],
                personalization_angles=[],
                confidence=0.50,
                last_researched_at=datetime.now(timezone.utc),
            )

        return Module3ResearchContract(
            lead_id=lead_id,
            company_name=lead.company.name,
            contact_name=lead.contact.full_name,
            contact_title=lead.contact.job_title,
            company_summary=profile.company_overview or f"{lead.company.name} is a {lead.industry} company.",
            contact_summary=f"{lead.contact.full_name} ({lead.contact.job_title or 'Executive'}) at {lead.company.name}.",
            key_findings=[{"category": f.category, "title": f.title, "summary": f.summary} for f in profile.findings],
            signals=[{"signal_type": s.signal_type, "title": s.title, "description": s.description} for s in profile.signals],
            opportunities=[{"title": o.title, "reason": o.reason, "observation": o.observation_text, "inference": o.inference_text} for o in profile.opportunities],
            personalization_angles=[{"angle": a.angle_title, "reason": a.angle_reason, "confidence": a.confidence} for a in profile.personalization_angles],
            confidence=profile.confidence_score,
            last_researched_at=profile.last_researched_at,
        )
