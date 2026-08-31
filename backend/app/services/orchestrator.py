import asyncio
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import GenerationJob, JobLog
from app.schemas.ai import SearchPlanResponse
from app.sources.registry import SourceRegistry
from app.services.deduplication import DeduplicationService
from app.core.database import AsyncSessionLocal
from app.core.logging import logger


class JobOrchestrator:
    """
    Asynchronous Lead Generation Search Job Orchestrator.
    Manages job state transitions, source querying, 2-level deduplication,
    lead scoring, and PostgreSQL database persistence.
    """

    @staticmethod
    async def run_job(job_id: str):
        """
        Background worker task executing the generation pipeline.
        """
        async with AsyncSessionLocal() as db:
            try:
                stmt = select(GenerationJob).where(GenerationJob.id == job_id)
                res = await db.execute(stmt)
                job: Optional[GenerationJob] = res.scalars().first()

                if not job:
                    logger.error(f"Job {job_id} not found")
                    return

                if job.status == "CANCELLED":
                    logger.info(f"Job {job_id} was cancelled before start")
                    return

                # State: PLANNING
                job.status = "PLANNING"
                job.started_at = datetime.now(timezone.utc)
                job.progress_percentage = 10
                db.add(JobLog(job_id=job.id, level="INFO", message="Initializing search plan and adapters", step="PLANNING"))
                await db.commit()

                # Reconstruct SearchPlan from query_params
                plan = SearchPlanResponse(**job.query_params)
                target_qty = plan.quantity

                # State: SEARCHING
                job.status = "SEARCHING"
                job.progress_percentage = 30
                db.add(JobLog(job_id=job.id, level="INFO", message=f"Searching sources for {plan.niche} in {plan.country}", step="SEARCHING"))
                await db.commit()

                registry = SourceRegistry()
                adapters = registry.adapters

                discovered_raw_leads = []

                for adapter in adapters:
                    if job.status == "CANCELLED":
                        break

                    db.add(JobLog(job_id=job.id, level="INFO", message=f"Executing source: {adapter.name}", step="SEARCHING"))
                    await db.commit()

                    try:
                        results = await adapter.search(plan, limit=target_qty)
                        discovered_raw_leads.extend(results)
                    except Exception as adapter_err:
                        logger.error(f"Adapter {adapter.name} error: {adapter_err}")
                        db.add(JobLog(job_id=job.id, level="WARNING", message=f"Source {adapter.name} returned error: {adapter_err}", step="SEARCHING"))
                        await db.commit()

                # Refresh job status in case cancelled
                stmt = select(GenerationJob).where(GenerationJob.id == job_id)
                res = await db.execute(stmt)
                job = res.scalars().first()

                if job.status == "CANCELLED":
                    db.add(JobLog(job_id=job.id, level="INFO", message="Job cancelled by user", step="CANCELLED"))
                    await db.commit()
                    return

                job.discovered_count = len(discovered_raw_leads)
                job.progress_percentage = 60

                # State: DEDUPLICATING
                job.status = "DEDUPLICATING"
                db.add(JobLog(job_id=job.id, level="INFO", message=f"Discovered {len(discovered_raw_leads)} prospects. Running 2-level deduplication.", step="DEDUPLICATING"))
                await db.commit()

                dedup_service = DeduplicationService(db)

                new_companies_count = 0
                new_contacts_count = 0
                duplicates_count = 0

                # State: SAVING
                job.status = "SAVING"
                job.progress_percentage = 80
                await db.commit()

                for raw_lead in discovered_raw_leads:
                    # Check requirements
                    if plan.requirements.website_required and not (raw_lead.domain or raw_lead.website):
                        continue
                    if plan.requirements.public_email_required and not raw_lead.email:
                        continue
                    if plan.requirements.phone_required and not raw_lead.phone:
                        continue

                    lead, is_new_company, is_new_contact = await dedup_service.process_raw_lead(raw_lead, generation_job_id=job.id)

                    if is_new_company:
                        new_companies_count += 1
                    if is_new_contact:
                        new_contacts_count += 1
                    else:
                        duplicates_count += 1

                job.duplicates_count = duplicates_count
                job.saved_count = new_contacts_count
                job.valid_count = len(discovered_raw_leads) - duplicates_count
                job.progress_percentage = 100
                job.completed_at = datetime.now(timezone.utc)

                if job.saved_count >= target_qty or job.saved_count > 0:
                    job.status = "COMPLETED" if job.saved_count >= target_qty else "PARTIAL"
                else:
                    job.status = "COMPLETED" if len(discovered_raw_leads) == 0 else "PARTIAL"

                db.add(JobLog(job_id=job.id, level="INFO", message=f"Job complete! Saved {job.saved_count} unique leads ({duplicates_count} duplicates merged).", step="COMPLETED"))
                await db.commit()

            except Exception as e:
                logger.error(f"Job execution failed: {e}", exc_info=True)
                stmt = select(GenerationJob).where(GenerationJob.id == job_id)
                res = await db.execute(stmt)
                job = res.scalars().first()
                if job:
                    job.status = "FAILED"
                    job.error_message = str(e)
                    db.add(JobLog(job_id=job.id, level="ERROR", message=f"Job failed: {e}", step="FAILED"))
                    await db.commit()
