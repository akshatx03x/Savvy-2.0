import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import GenerationJob, JobLog
from app.schemas.ai import SearchPlanResponse
from app.sources.registry import SourceRegistry
from app.services.deduplication import DeduplicationService, RawLeadData
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.core.logging import logger


class JobOrchestrator:
    """
    Asynchronous Lead Generation Search Job Orchestrator.
    Manages job state transitions, live source querying, 2-level deduplication,
    lead scoring, structured diagnostic logging, and database persistence.
    """

    @staticmethod
    async def run_job(job_id: str):
        """
        Background worker task executing the live lead generation search pipeline.
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

                # Reconstruct SearchPlan from query_params
                plan = SearchPlanResponse(**job.query_params)
                target_qty = plan.quantity

                # Stage 1: Log Search Request & Plan Diagnostics
                logger.info(
                    f"SEARCH_REQUEST: niche='{plan.niche}', country='{plan.country}', "
                    f"country_code='{plan.country_code}', region='{plan.region}', "
                    f"region_code='{plan.region_code}', city='{plan.city}', quantity={plan.quantity}"
                )

                # State: PLANNING
                job.status = "PLANNING"
                job.started_at = datetime.now(timezone.utc)
                job.progress_percentage = 10
                db.add(JobLog(job_id=job.id, level="INFO", message=f"Search plan initialized for {plan.niche} in {plan.country}", step="PLANNING"))
                await db.commit()

                # State: SEARCHING
                job.status = "SEARCHING"
                job.progress_percentage = 30
                db.add(JobLog(job_id=job.id, level="INFO", message=f"Searching sources for {plan.niche} in {plan.country}", step="SEARCHING"))
                await db.commit()

                from app.sources.provider_manager import LeadSourceProviderManager
                provider_mgr = LeadSourceProviderManager()

                discovered_raw_leads, sources_attempted_list, sources_used, source_diagnostics = await provider_mgr.execute_search(
                    plan, limit=target_qty
                )

                sources_attempted = len(sources_attempted_list)
                sources_successful = len(sources_used)

                for src_name in sources_attempted_list:
                    db.add(JobLog(job_id=job.id, level="INFO", message=f"Executed source provider: {src_name}", step="SEARCHING"))
                await db.commit()


                # Refresh job status in case cancelled
                stmt = select(GenerationJob).where(GenerationJob.id == job_id)
                res = await db.execute(stmt)
                job = res.scalars().first()

                if job.status == "CANCELLED":
                    db.add(JobLog(job_id=job.id, level="INFO", message="Job cancelled by user", step="CANCELLED"))
                    await db.commit()
                    return

                # If no sources were successfully queried or none configured
                if sources_attempted == 0:
                    job.status = "FAILED"
                    job.error_message = "No live lead sources are configured. Please connect a lead source in Settings."
                    job.completed_at = datetime.now(timezone.utc)
                    db.add(JobLog(job_id=job.id, level="ERROR", message="No live lead sources are configured.", step="FAILED"))
                    await db.commit()
                    return

                if sources_successful == 0 and sources_attempted > 0:
                    job.status = "FAILED"
                    job.error_message = "Lead sources could not be reached or authentication failed."
                    job.completed_at = datetime.now(timezone.utc)
                    db.add(JobLog(job_id=job.id, level="ERROR", message="All attempted lead sources failed.", step="FAILED"))
                    await db.commit()
                    return

                job.discovered_count = len(discovered_raw_leads)
                job.progress_percentage = 50

                # State: PROCESSING
                job.status = "PROCESSING"
                db.add(JobLog(job_id=job.id, level="INFO", message=f"Processing {len(discovered_raw_leads)} raw prospect records.", step="PROCESSING"))
                await db.commit()

                # State: DEDUPLICATING
                job.status = "DEDUPLICATING"
                job.progress_percentage = 70
                db.add(JobLog(job_id=job.id, level="INFO", message=f"Discovered {len(discovered_raw_leads)} prospects. Running 2-level deduplication.", step="DEDUPLICATING"))
                await db.commit()

                dedup_service = DeduplicationService(db)

                new_companies_count = 0
                new_contacts_count = 0
                duplicates_count = 0
                validation_rejected_count = 0
                validation_reasons: Dict[str, int] = {}

                # State: SAVING
                job.status = "SAVING"
                job.progress_percentage = 85
                await db.commit()

                for raw_lead in discovered_raw_leads:
                    # Requirements check: website / phone / email
                    if plan.requirements.website_required and not (raw_lead.domain or raw_lead.website):
                        validation_rejected_count += 1
                        validation_reasons["website_missing"] = validation_reasons.get("website_missing", 0) + 1
                        continue
                    if plan.requirements.public_email_required and not raw_lead.email:
                        validation_rejected_count += 1
                        validation_reasons["email_missing"] = validation_reasons.get("email_missing", 0) + 1
                        continue
                    if plan.requirements.phone_required and not raw_lead.phone:
                        validation_rejected_count += 1
                        validation_reasons["phone_missing"] = validation_reasons.get("phone_missing", 0) + 1
                        continue

                    # Minimum validation: Company Name + Country + Source
                    if not (raw_lead.company_name and raw_lead.country):
                        validation_rejected_count += 1
                        validation_reasons["invalid_company_or_country"] = validation_reasons.get("invalid_company_or_country", 0) + 1
                        continue

                    lead, is_new_company, is_new_lead = await dedup_service.process_raw_lead(raw_lead, generation_job_id=job.id)

                    if is_new_company:
                        new_companies_count += 1
                    if is_new_lead:
                        new_contacts_count += 1
                    else:
                        duplicates_count += 1

                job.duplicates_count = duplicates_count
                job.saved_count = new_contacts_count
                job.valid_count = len(discovered_raw_leads) - validation_rejected_count
                job.requested_count = target_qty
                job.progress_percentage = 100
                job.completed_at = datetime.now(timezone.utc)

                registry_diag = provider_mgr.get_provider_health()
                missing_credentials = [p["name"] for p in registry_diag if not p["credentials_present"]]

                # Internal diagnostic summary tracking requested, raw, normalized, valid, duplicates, saved
                diagnostic_summary = {
                    "requested": target_qty,
                    "sources_attempted": sources_attempted,
                    "sources_successful": sources_successful,
                    "sources_used": sources_used,
                    "raw_results": len(discovered_raw_leads),
                    "normalized": len(discovered_raw_leads),
                    "validated": job.valid_count,
                    "validation_rejected": validation_rejected_count,
                    "validation_reasons": validation_reasons,
                    "duplicates": duplicates_count,
                    "saved": job.saved_count,
                    "missing_credentials": missing_credentials,
                    "source_breakdown": source_diagnostics,
                    "registry_status": registry_diag,
                }
                job.diagnostic = diagnostic_summary


                # Determine final status (COMPLETED vs PARTIAL)
                if sources_successful < sources_attempted:
                    job.status = "PARTIAL"
                    job.error_message = "Some lead sources were unavailable."
                    db.add(JobLog(job_id=job.id, level="WARNING", message=f"Search finished as PARTIAL: {job.saved_count} saved, some sources failed.", step="PARTIAL"))
                else:
                    job.status = "COMPLETED"
                    db.add(JobLog(job_id=job.id, level="INFO", message=f"Job complete! Saved {job.saved_count} verified unique leads.", step="COMPLETED"))

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

