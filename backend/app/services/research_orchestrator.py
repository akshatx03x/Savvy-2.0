import asyncio
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.company import Company
from app.models.contact import Contact
from app.models.research import (
    ResearchProfile,
    ResearchFinding,
    ResearchEvidence,
    ResearchSignal,
    ResearchOpportunity,
    PersonalizationAngle,
)
from app.models.research_job import ResearchJob, ResearchJobLog
from app.research.registry import ResearchSourceRegistry
from app.services.research_pipeline import ResearchPipelineService
from app.core.database import AsyncSessionLocal
from app.core.logging import logger


class ResearchOrchestrator:
    """
    Asynchronous Lead Intelligence Research Job Orchestrator.
    Executes source discovery, content retrieval, evidence extraction,
    and updates real-time job progress.
    """

    @staticmethod
    async def run_job(job_id: str):
        async with AsyncSessionLocal() as db:
            try:
                stmt = select(ResearchJob).where(ResearchJob.id == job_id)
                res = await db.execute(stmt)
                job: Optional[ResearchJob] = res.scalars().first()

                if not job:
                    logger.error(f"ResearchJob {job_id} not found")
                    return

                if job.status == "CANCELLED":
                    return

                # State: IDENTIFYING
                job.status = "IDENTIFYING"
                job.started_at = datetime.now(timezone.utc)
                job.progress_percentage = 10
                db.add(ResearchJobLog(job_id=job.id, level="INFO", message="Identifying target leads and company profiles", step="IDENTIFYING"))
                await db.commit()

                target_lead_ids: List[str] = job.target_lead_ids.get("lead_ids", [])
                total_leads = len(target_lead_ids)
                job.total_leads = total_leads

                # Fetch leads from DB
                stmt_leads = (
                    select(Lead)
                    .options(selectinload(Lead.company), selectinload(Lead.contact))
                    .where(Lead.id.in_(target_lead_ids))
                )
                res_leads = await db.execute(stmt_leads)
                leads = list(res_leads.scalars().all())

                registry = ResearchSourceRegistry()
                adapters = registry.get_active_adapters()

                processed = 0
                successful = 0
                partial = 0
                failed = 0

                for i, lead in enumerate(leads):
                    # Check cancellation
                    stmt_check = select(ResearchJob.status).where(ResearchJob.id == job_id)
                    check_res = await db.execute(stmt_check)
                    current_status = check_res.scalar()
                    if current_status == "CANCELLED":
                        break

                    # State: DISCOVERING / FETCHING
                    job.status = "DISCOVERING"
                    job.progress_percentage = 20 + int((i / max(1, total_leads)) * 70)
                    db.add(ResearchJobLog(job_id=job.id, level="INFO", message=f"Researching lead {i+1}/{total_leads}: {lead.company.name}", step="DISCOVERING", lead_id=lead.id))
                    await db.commit()

                    raw_results = []
                    for adapter in adapters:
                        try:
                            results = await adapter.discover_and_fetch(
                                company_name=lead.company.name,
                                domain=lead.company.domain,
                                country=lead.country,
                                depth=job.research_depth,
                            )
                            raw_results.extend(results)
                        except Exception as e:
                            logger.warning(f"Research adapter {adapter.name} error for lead {lead.id}: {e}")

                    # State: ANALYZING / EXTRACTING
                    job.status = "ANALYZING"
                    await db.commit()

                    try:
                        (
                            overview,
                            findings,
                            evidence_items,
                            signals,
                            opportunities,
                            angles,
                            intel_score,
                            conf_score,
                        ) = await ResearchPipelineService.process_research(
                            company_name=lead.company.name,
                            domain=lead.company.domain,
                            country=lead.country,
                            industry=lead.industry,
                            contact_name=lead.contact.full_name,
                            contact_title=lead.contact.job_title,
                            depth=job.research_depth,
                            raw_results=raw_results,
                            is_synthetic=job.is_synthetic,
                        )

                        # Delete existing ResearchProfile for this lead if re-researching
                        stmt_old = select(ResearchProfile).where(ResearchProfile.lead_id == lead.id)
                        res_old = await db.execute(stmt_old)
                        old_profile = res_old.scalars().first()
                        if old_profile:
                            await db.delete(old_profile)
                            await db.flush()

                        # Save new ResearchProfile
                        profile = ResearchProfile(
                            company_id=lead.company_id,
                            contact_id=lead.contact_id,
                            lead_id=lead.id,
                            research_depth=job.research_depth,
                            intelligence_score=intel_score,
                            confidence_score=conf_score,
                            summary=overview["summary"],
                            company_overview=overview["company_overview"],
                            business_model=overview["business_model"],
                            industry=overview["industry"],
                            products_services=overview["products_services"],
                            recent_activity=overview["recent_activity"],
                            last_researched_at=datetime.now(timezone.utc),
                            is_synthetic=job.is_synthetic,
                        )
                        db.add(profile)
                        await db.flush()

                        # Save Findings & Evidence
                        for f_schema in findings:
                            finding = ResearchFinding(
                                profile_id=profile.id,
                                category=f_schema.category,
                                title=f_schema.title,
                                summary=f_schema.summary,
                                importance=f_schema.importance,
                                confidence=f_schema.confidence,
                            )
                            db.add(finding)
                            await db.flush()

                            for ev_schema in f_schema.evidence:
                                evidence = ResearchEvidence(
                                    profile_id=profile.id,
                                    finding_id=finding.id,
                                    source_name=ev_schema.source_name,
                                    source_url=ev_schema.source_url,
                                    source_type=ev_schema.source_type,
                                    supporting_snippet=ev_schema.supporting_snippet,
                                    published_date=ev_schema.published_date,
                                    recency_tier=ev_schema.recency_tier,
                                    confidence=ev_schema.confidence,
                                    is_observation_vs_inference=ev_schema.is_observation_vs_inference,
                                    is_synthetic=job.is_synthetic,
                                )
                                db.add(evidence)

                        # Save Signals
                        for sig_schema in signals:
                            db.add(
                                ResearchSignal(
                                    profile_id=profile.id,
                                    signal_type=sig_schema.signal_type,
                                    title=sig_schema.title,
                                    description=sig_schema.description,
                                    source_name=sig_schema.source_name,
                                    confidence=sig_schema.confidence,
                                    recency_tier=sig_schema.recency_tier,
                                    importance=sig_schema.importance,
                                )
                            )

                        # Save Opportunities
                        for opp_schema in opportunities:
                            db.add(
                                ResearchOpportunity(
                                    profile_id=profile.id,
                                    title=opp_schema.title,
                                    reason=opp_schema.reason,
                                    potential_offer=opp_schema.potential_offer,
                                    confidence=opp_schema.confidence,
                                    observation_text=opp_schema.observation_text,
                                    inference_text=opp_schema.inference_text,
                                )
                            )

                        # Save Personalization Angles
                        for ang_schema in angles:
                            db.add(
                                PersonalizationAngle(
                                    profile_id=profile.id,
                                    angle_title=ang_schema.angle_title,
                                    angle_reason=ang_schema.angle_reason,
                                    evidence_ids=ang_schema.evidence_ids,
                                    confidence=ang_schema.confidence,
                                )
                            )

                        # Update lead status
                        lead.last_verified_at = datetime.now(timezone.utc)
                        self_add = db.add(lead)

                        processed += 1
                        if len(evidence_items) >= 2:
                            successful += 1
                        else:
                            partial += 1

                    except Exception as lead_err:
                        logger.error(f"Error researching lead {lead.id}: {lead_err}", exc_info=True)
                        processed += 1
                        failed += 1

                    job.processed_count = processed
                    job.successful_count = successful
                    job.partial_count = partial
                    job.failed_count = failed
                    await db.commit()

                # State: COMPLETED
                job.status = "COMPLETED" if failed == 0 else "PARTIAL"
                job.progress_percentage = 100
                job.completed_at = datetime.now(timezone.utc)
                db.add(ResearchJobLog(job_id=job.id, level="INFO", message=f"Research complete: {successful} successful, {partial} partial, {failed} failed.", step="COMPLETED"))
                await db.commit()

            except Exception as outer_err:
                logger.error(f"Research job {job_id} failed: {outer_err}", exc_info=True)
                stmt = select(ResearchJob).where(ResearchJob.id == job_id)
                res = await db.execute(stmt)
                job = res.scalars().first()
                if job:
                    job.status = "FAILED"
                    job.error_message = str(outer_err)
                    db.add(ResearchJobLog(job_id=job.id, level="ERROR", message=f"Job failed: {outer_err}", step="FAILED"))
                    await db.commit()
