import asyncio
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outreach import OutreachDraft
from app.models.outreach_job import OutreachJob, OutreachJobLog
from app.schemas.outreach import OutreachGenerationRequest
from app.services.outreach_service import OutreachService
from app.core.database import AsyncSessionLocal
from app.core.logging import logger


class OutreachOrchestrator:
    """
    Asynchronous Bulk Outreach Personalization Job Orchestrator.
    """

    @staticmethod
    async def run_job(job_id: str):
        async with AsyncSessionLocal() as db:
            try:
                stmt = select(OutreachJob).where(OutreachJob.id == job_id)
                res = await db.execute(stmt)
                job: Optional[OutreachJob] = res.scalars().first()

                if not job:
                    logger.error(f"OutreachJob {job_id} not found")
                    return

                if job.status == "CANCELLED":
                    return

                job.status = "PREPARING"
                job.started_at = datetime.now(timezone.utc)
                job.progress_percentage = 10
                db.add(OutreachJobLog(job_id=job.id, level="INFO", message="Preparing lead records and offer context", step="PREPARING"))
                await db.commit()

                target_lead_ids: List[str] = job.target_lead_ids.get("lead_ids", [])
                total_leads = len(target_lead_ids)
                job.total_leads = total_leads

                config = job.config_json or {}
                service = OutreachService(db)

                processed = 0
                successful = 0
                failed = 0
                needs_research = 0

                for i, lead_id in enumerate(target_lead_ids):
                    job.status = "GENERATING"
                    job.progress_percentage = 20 + int((i / max(1, total_leads)) * 75)
                    db.add(OutreachJobLog(job_id=job.id, level="INFO", message=f"Generating outreach for lead {i+1}/{total_leads}", step="GENERATING", lead_id=lead_id))
                    await db.commit()

                    try:
                        req = OutreachGenerationRequest(
                            lead_id=lead_id,
                            offer_id=config.get("offer_id"),
                            objective=config.get("objective", "Book a meeting"),
                            tone=config.get("tone", "Consultative"),
                            length=config.get("length", "Short"),
                            personalization_level=config.get("personalization_level", "DEEP"),
                            cta_type=config.get("cta_type", "Soft CTA"),
                        )
                        draft = await service.generate_outreach_draft(req)

                        processed += 1
                        if draft.status == "NEEDS_RESEARCH":
                            needs_research += 1
                        elif draft.status in ["DRAFT", "APPROVED"]:
                            successful += 1
                        else:
                            failed += 1
                    except Exception as err:
                        logger.error(f"Error generating outreach for lead {lead_id}: {err}", exc_info=True)
                        processed += 1
                        failed += 1

                    job.processed_count = processed
                    job.successful_count = successful
                    job.failed_count = failed
                    job.needs_research_count = needs_research
                    await db.commit()

                job.status = "COMPLETED" if failed == 0 else "PARTIAL"
                job.progress_percentage = 100
                job.completed_at = datetime.now(timezone.utc)
                db.add(OutreachJobLog(job_id=job.id, level="INFO", message=f"Outreach generation complete: {successful} generated, {needs_research} need research, {failed} failed.", step="COMPLETED"))
                await db.commit()

            except Exception as outer_err:
                logger.error(f"OutreachJob {job_id} failed: {outer_err}", exc_info=True)
                stmt = select(OutreachJob).where(OutreachJob.id == job_id)
                res = await db.execute(stmt)
                job = res.scalars().first()
                if job:
                    job.status = "FAILED"
                    job.error_message = str(outer_err)
                    db.add(OutreachJobLog(job_id=job.id, level="ERROR", message=f"Job failed: {outer_err}", step="FAILED"))
                    await db.commit()
