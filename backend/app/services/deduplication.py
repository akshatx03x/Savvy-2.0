from typing import Tuple, Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.source import LeadSourceProvenance
from app.services.normalization import (
    normalize_email,
    normalize_domain,
    normalize_phone,
    normalize_company_name,
    split_full_name,
)
from app.services.lead_scoring import calculate_lead_score
from app.core.logging import logger


class RawLeadData:
    def __init__(
        self,
        company_name: str,
        country: str,
        industry: str,
        full_name: str,
        domain: Optional[str] = None,
        website: Optional[str] = None,
        region: Optional[str] = None,
        city: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        job_title: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        source: str = "web",
        source_url: Optional[str] = None,
        verification_status: str = "unverified",
        description: Optional[str] = None,
        employee_count_range: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        is_synthetic: bool = False,
    ):
        self.company_name = company_name
        self.domain = domain
        self.website = website or (f"https://{domain}" if domain else None)
        self.country = country
        self.region = region
        self.city = city
        self.industry = industry
        self.full_name = full_name
        self.first_name = first_name
        self.last_name = last_name
        self.job_title = job_title
        self.email = email
        self.phone = phone
        self.source = source
        self.source_url = source_url
        self.verification_status = verification_status
        self.description = description
        self.employee_count_range = employee_count_range
        self.linkedin_url = linkedin_url
        self.is_synthetic = is_synthetic


class DeduplicationService:
    """
    Two-Level Deduplication Engine:
    Level 1: Company Deduplication (Domain, Name+Country)
    Level 2: Contact Deduplication (Email, Phone, Name+Company)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_or_create_company(self, raw: RawLeadData) -> Tuple[Company, bool]:
        """
        Level 1: Company Deduplication
        Returns (Company, is_new)
        """
        norm_domain = normalize_domain(raw.domain or raw.website)
        norm_name = normalize_company_name(raw.company_name)

        existing_company: Optional[Company] = None

        # Strategy 1: Exact normalized domain match
        if norm_domain:
            stmt = select(Company).where(Company.normalized_domain == norm_domain)
            res = await self.db.execute(stmt)
            existing_company = res.scalars().first()

        # Strategy 2: Exact normalized name + country match
        if not existing_company and norm_name:
            stmt = select(Company).where(
                and_(
                    Company.normalized_name == norm_name,
                    Company.country.ilike(raw.country),
                )
            )
            res = await self.db.execute(stmt)
            existing_company = res.scalars().first()

        if existing_company:
            # Enrich existing company with missing fields
            updated = False
            if not existing_company.website and raw.website:
                existing_company.website = raw.website
                updated = True
            if not existing_company.domain and raw.domain:
                existing_company.domain = raw.domain
                existing_company.normalized_domain = norm_domain
                updated = True
            if not existing_company.description and raw.description:
                existing_company.description = raw.description
                updated = True
            if not existing_company.linkedin_url and raw.linkedin_url:
                existing_company.linkedin_url = raw.linkedin_url
                updated = True
            if not existing_company.region and raw.region:
                existing_company.region = raw.region
                updated = True
            if not existing_company.city and raw.city:
                existing_company.city = raw.city
                updated = True

            if updated:
                self.db.add(existing_company)
                await self.db.flush()

            return existing_company, False

        # Create new company
        new_company = Company(
            name=raw.company_name,
            normalized_name=norm_name,
            domain=raw.domain,
            normalized_domain=norm_domain,
            website=raw.website,
            country=raw.country,
            region=raw.region,
            city=raw.city,
            industry=raw.industry,
            description=raw.description,
            employee_count_range=raw.employee_count_range,
            linkedin_url=raw.linkedin_url,
            is_synthetic=raw.is_synthetic,
        )
        self.db.add(new_company)
        await self.db.flush()
        return new_company, True

    async def find_or_create_contact(
        self, company: Company, raw: RawLeadData
    ) -> Tuple[Contact, bool]:
        """
        Level 2: Contact Deduplication
        Returns (Contact, is_new)
        """
        norm_email = normalize_email(raw.email)
        norm_phone = normalize_phone(raw.phone)
        f_name, l_name = raw.first_name, raw.last_name
        if not f_name and raw.full_name:
            f_name, l_name = split_full_name(raw.full_name)

        existing_contact: Optional[Contact] = None

        # Strategy 1: Exact normalized email match
        if norm_email:
            stmt = select(Contact).where(Contact.normalized_email == norm_email)
            res = await self.db.execute(stmt)
            existing_contact = res.scalars().first()

        # Strategy 2: Exact normalized phone match
        if not existing_contact and norm_phone:
            stmt = select(Contact).where(Contact.normalized_phone == norm_phone)
            res = await self.db.execute(stmt)
            existing_contact = res.scalars().first()

        # Strategy 3: Full Name + Company ID match
        if not existing_contact and raw.full_name and company.id:
            stmt = select(Contact).where(
                and_(
                    Contact.company_id == company.id,
                    Contact.full_name.ilike(raw.full_name.strip()),
                )
            )
            res = await self.db.execute(stmt)
            existing_contact = res.scalars().first()

        if existing_contact:
            # Enrich existing contact
            updated = False
            if not existing_contact.email and raw.email:
                existing_contact.email = raw.email
                existing_contact.normalized_email = norm_email
                updated = True
            if not existing_contact.phone and raw.phone:
                existing_contact.phone = raw.phone
                existing_contact.normalized_phone = norm_phone
                updated = True
            if not existing_contact.job_title and raw.job_title:
                existing_contact.job_title = raw.job_title
                updated = True

            # Add source provenance record if new source
            provenance = LeadSourceProvenance(
                contact_id=existing_contact.id,
                source_name=raw.source,
                source_url=raw.source_url,
                verification_status=raw.verification_status,
                is_synthetic=raw.is_synthetic,
            )
            self.db.add(provenance)

            if updated:
                self.db.add(existing_contact)
                await self.db.flush()

            return existing_contact, False

        # Create new contact
        new_contact = Contact(
            company_id=company.id,
            first_name=f_name,
            last_name=l_name,
            full_name=raw.full_name,
            job_title=raw.job_title,
            email=raw.email,
            normalized_email=norm_email,
            phone=raw.phone,
            normalized_phone=norm_phone,
            country=raw.country,
            region=raw.region or company.region,
            city=raw.city or company.city,
            source=raw.source,
            source_url=raw.source_url,
            verification_status=raw.verification_status,
            is_synthetic=raw.is_synthetic,
        )
        self.db.add(new_contact)
        await self.db.flush()

        # Add initial source provenance
        provenance = LeadSourceProvenance(
            contact_id=new_contact.id,
            source_name=raw.source,
            source_url=raw.source_url,
            verification_status=raw.verification_status,
            is_synthetic=raw.is_synthetic,
        )
        self.db.add(provenance)
        await self.db.flush()

        return new_contact, True

    async def process_raw_lead(
        self, raw: RawLeadData, generation_job_id: Optional[str] = None
    ) -> Tuple[Lead, bool, bool]:
        """
        Processes a raw lead through the 2-level deduplication engine.
        Returns (Lead, is_new_company, is_new_contact)
        """
        company, is_new_company = await self.find_or_create_company(raw)
        contact, is_new_contact = await self.find_or_create_contact(company, raw)

        # Check if Lead record already exists linking this contact
        stmt = select(Lead).where(Lead.contact_id == contact.id)
        res = await self.db.execute(stmt)
        existing_lead = res.scalars().first()

        score = calculate_lead_score(
            has_website=bool(company.website),
            has_email=bool(contact.email),
            has_phone=bool(contact.phone),
            has_contact_name=bool(contact.full_name),
            has_job_title=bool(contact.job_title),
            verification_status=contact.verification_status,
            is_synthetic=raw.is_synthetic,
        )

        if existing_lead:
            # Update lead score & last_verified_at
            existing_lead.lead_score = max(existing_lead.lead_score, score)
            existing_lead.last_verified_at = datetime.now(timezone.utc)
            self.db.add(existing_lead)
            await self.db.flush()
            return existing_lead, is_new_company, False

        # Create Lead workflow record
        new_lead = Lead(
            company_id=company.id,
            contact_id=contact.id,
            country=raw.country,
            region=raw.region or company.region,
            city=raw.city or company.city,
            industry=raw.industry,
            lead_score=score,
            status="new",
            source=raw.source,
            source_url=raw.source_url,
            generation_job_id=generation_job_id,
            last_verified_at=datetime.now(timezone.utc),
            is_synthetic=raw.is_synthetic,
        )
        self.db.add(new_lead)
        await self.db.flush()

        return new_lead, is_new_company, True
