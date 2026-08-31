from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.company import Company
from app.models.contact import Contact
from app.schemas.lead import LeadFilter
from app.schemas.stats import CountryStat, DashboardStatsResponse


class LeadService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_leads(self, filters: LeadFilter) -> Tuple[List[Lead], int]:
        """
        Get leads with filtering, sorting, and pagination.
        """
        query = select(Lead).options(
            selectinload(Lead.company),
            selectinload(Lead.contact)
        )

        conditions = []

        if filters.search:
            s = f"%{filters.search.strip()}%"
            query = query.join(Lead.company).join(Lead.contact)
            conditions.append(
                or_(
                    Company.name.ilike(s),
                    Company.domain.ilike(s),
                    Contact.full_name.ilike(s),
                    Contact.email.ilike(s),
                    Contact.job_title.ilike(s),
                )
            )

        if filters.country:
            conditions.append(Lead.country.ilike(filters.country.strip()))

        if filters.region:
            conditions.append(Lead.region.ilike(filters.region.strip()))

        if filters.city:
            conditions.append(Lead.city.ilike(filters.city.strip()))

        if filters.industry:
            conditions.append(Lead.industry.ilike(filters.industry.strip()))

        if filters.min_score is not None:
            conditions.append(Lead.lead_score >= filters.min_score)

        if filters.status:
            conditions.append(Lead.status == filters.status)

        if filters.has_email is True:
            query = query.join(Lead.contact) if not filters.search else query
            conditions.append(Contact.email.isnot(None))

        if filters.has_phone is True:
            query = query.join(Lead.contact) if not filters.search else query
            conditions.append(Contact.phone.isnot(None))

        if filters.has_website is True:
            query = query.join(Lead.company) if not filters.search else query
            conditions.append(Company.website.isnot(None))

        if filters.source:
            conditions.append(Lead.source == filters.source)

        if conditions:
            query = query.where(and_(*conditions))

        # Total count query
        count_query = select(func.count(Lead.id))
        if conditions:
            if filters.search or filters.has_email or filters.has_phone or filters.has_website:
                # Need joins for count
                count_query = count_query.select_from(Lead).join(Lead.company).join(Lead.contact).where(and_(*conditions))
            else:
                count_query = count_query.select_from(Lead).where(and_(*conditions))

        total_res = await self.db.execute(count_query)
        total = total_res.scalar() or 0

        # Sorting
        sort_attr = getattr(Lead, filters.sort_by, Lead.created_at)
        if filters.sort_order.lower() == "asc":
            query = query.order_by(asc(sort_attr))
        else:
            query = query.order_by(desc(sort_attr))

        # Pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        res = await self.db.execute(query)
        leads = res.scalars().all()

        return list(leads), total

    async def get_lead_by_id(self, lead_id: str) -> Optional[Lead]:
        stmt = (
            select(Lead)
            .options(
                selectinload(Lead.company),
                selectinload(Lead.contact).selectinload(Contact.sources),
                selectinload(Lead.generation_job)
            )
            .where(Lead.id == lead_id)
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_country_stats(self) -> List[CountryStat]:
        """
        Geographic categorization: COUNTRY ONLY.
        Aggregates leads, companies, and quality scores by Country.
        """
        stmt = (
            select(
                Lead.country,
                func.count(Lead.id).label("lead_count"),
                func.count(func.distinct(Lead.company_id)).label("company_count"),
                func.avg(Lead.lead_score).label("avg_score")
            )
            .group_by(Lead.country)
            .order_by(desc("lead_count"))
        )
        res = await self.db.execute(stmt)
        rows = res.all()

        total_leads_stmt = select(func.count(Lead.id))
        total_res = await self.db.execute(total_leads_stmt)
        total_leads = total_res.scalar() or 1

        country_stats = []
        for r in rows:
            cnt = r.lead_count
            pct = round((cnt / total_leads) * 100, 1)
            country_stats.append(
                CountryStat(
                    country=r.country,
                    code=r.country[:2].upper(),
                    lead_count=cnt,
                    company_count=r.company_count,
                    avg_score=round(float(r.avg_score or 0), 1),
                    percentage=pct,
                )
            )
        return country_stats

    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        total_leads_res = await self.db.execute(select(func.count(Lead.id)))
        total_leads = total_leads_res.scalar() or 0

        total_comp_res = await self.db.execute(select(func.count(Company.id)))
        total_companies = total_comp_res.scalar() or 0

        total_contacts_res = await self.db.execute(select(func.count(Contact.id)))
        total_contacts = total_contacts_res.scalar() or 0

        avg_score_res = await self.db.execute(select(func.avg(Lead.lead_score)))
        avg_score = avg_score_res.scalar() or 0.0

        country_stats = await self.get_country_stats()

        return DashboardStatsResponse(
            total_leads=total_leads,
            unique_leads=total_leads,
            leads_generated_today=total_leads,
            total_companies=total_companies,
            total_contacts=total_contacts,
            generation_jobs_count=0,
            avg_quality_score=round(float(avg_score), 1),
            top_countries=country_stats,
            recent_jobs=[],
        )
