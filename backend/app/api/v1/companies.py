from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.company import Company
from app.models.contact import Contact

router = APIRouter(prefix="/companies", tags=["Companies Directory"])


@router.get("")
async def list_companies(
    search: Optional[str] = None,
    country: Optional[str] = None,
    industry: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    db: AsyncSession = Depends(get_db),
):
    """
    Lightweight Module 1 Company Directory:
    Returns Company Name, Country, Industry, Website, Contact Count, Lead Score.
    """
    query = select(Company).options(selectinload(Company.contacts))

    conditions = []
    if search:
        s = f"%{search.strip()}%"
        conditions.append(Company.name.ilike(s) | Company.domain.ilike(s))
    if country:
        conditions.append(Company.country.ilike(country.strip()))
    if industry:
        conditions.append(Company.industry.ilike(industry.strip()))

    if conditions:
        query = query.where(*conditions)

    count_query = select(func.count(Company.id))
    if conditions:
        count_query = count_query.where(*conditions)

    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(desc(Company.created_at)).offset(offset).limit(page_size)

    res = await db.execute(query)
    companies = res.scalars().all()

    items = []
    for c in companies:
        items.append({
            "id": c.id,
            "name": c.name,
            "domain": c.domain,
            "website": c.website,
            "country": c.country,
            "region": c.region,
            "city": c.city,
            "industry": c.industry,
            "contact_count": len(c.contacts),
            "lead_score": 75,
            "is_synthetic": c.is_synthetic,
            "created_at": c.created_at.isoformat(),
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
