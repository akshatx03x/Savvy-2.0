from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactResponse

router = APIRouter(prefix="/contacts", tags=["Contacts Directory"])


@router.get("", response_model=List[ContactResponse])
async def list_contacts(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Contact).options(selectinload(Contact.company)).order_by(desc(Contact.created_at)).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars().all())
