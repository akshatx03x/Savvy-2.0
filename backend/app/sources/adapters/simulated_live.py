import random
from typing import List
from app.sources.base import BaseSourceAdapter
from app.schemas.ai import SearchPlanResponse
from app.services.deduplication import RawLeadData
from app.core.config import settings


FIRST_NAMES = [
    "Alex", "Sarah", "Michael", "David", "Emma", "James", "Sophia", "Daniel",
    "Emily", "Chris", "Olivia", "Robert", "Jessica", "William", "Amanda", "Brian",
    "Rachel", "Matthew", "Ashley", "Andrew", "Stephanie", "Joshua", "Lauren", "Kevin"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"
]

TITLES_BY_NICHE = {
    "Real Estate": ["Founder & Principal Broker", "Managing Director", "Senior Real Estate Agent", "Commercial Broker", "VP of Sales", "Acquisitions Director"],
    "Software & Technology": ["Chief Executive Officer", "CTO & Co-Founder", "VP of Engineering", "Head of Product", "Director of Growth", "Sales Director"],
    "E-Commerce & Retail": ["E-Commerce Director", "Founder & CEO", "Head of Marketing", "Brand Director", "Operations Manager", "VP of Merchandising"],
    "Healthcare & Medical": ["Medical Director", "Practice Manager", "Chief Executive Officer", "Head of Operations", "Clinic Owner", "VP of Patient Care"],
    "Construction & Engineering": ["President & Founder", "Managing Director", "Chief Operating Officer", "VP of Construction", "Project Executive", "Director of Estimating"],
    "Marketing & Advertising": ["Agency Founder & CEO", "Chief Marketing Officer", "VP of Client Services", "Head of Performance Marketing", "Managing Director"],
}

DEFAULT_TITLES = ["Founder & CEO", "Managing Director", "VP of Sales", "Director of Operations", "Chief Executive Officer"]

COMPANY_PREFIXES = ["Apex", "Vanguard", "Summit", "Beacon", "Pinnacle", "Crest", "Horizon", "Sterling", "Nexus", "Atlas", "Omega", "Velocity", "Synergy", "Meridian"]
COMPANY_SUFFIXES = ["Group", "Solutions", "Capital", "Partners", "Holdings", "Ventures", "Services", "Media", "Properties", "Technologies", "Global"]


class SimulatedLiveAdapter(BaseSourceAdapter):
    """
    Simulated Live Source Adapter for Development & Testing.
    STRICT SAFETY RULES:
    1. Disabled if ENABLE_SYNTHETIC_DATA is False.
    2. Explicitly tags ALL records with is_synthetic = True.
    """

    def __init__(self):
        super().__init__(name="Simulated Live Discovery", is_synthetic_adapter=True)

    async def search(self, plan: SearchPlanResponse, limit: int) -> List[RawLeadData]:
        if not settings.ENABLE_SYNTHETIC_DATA:
            return []

        leads: List[RawLeadData] = []
        titles = TITLES_BY_NICHE.get(plan.niche, DEFAULT_TITLES)

        country = plan.country
        region = plan.region
        city = plan.city
        niche = plan.niche

        # Generate realistic companies with 1 to 3 contacts per company to test 2-level deduplication
        num_companies = max(1, limit // 2)

        for i in range(num_companies):
            prefix = random.choice(COMPANY_PREFIXES)
            suffix = random.choice(COMPANY_SUFFIXES)
            company_name = f"{prefix} {niche} {suffix}"
            domain = f"{prefix.lower()}{niche.lower().replace(' ', '')}{i+10}.com"
            website = f"https://www.{domain}"

            # 1 to 2 contacts per company
            num_contacts = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]

            for c in range(num_contacts):
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                full_name = f"{first_name} {last_name}"
                job_title = random.choice(titles)

                email_domain = domain if plan.requirements.website_required else "gmail.com"
                email = f"{first_name.lower()}.{last_name.lower()}@{email_domain}"

                phone_area = random.randint(200, 999)
                phone_prefix = random.randint(200, 999)
                phone_line = random.randint(1000, 9999)
                phone = f"+1 ({phone_area}) {phone_prefix}-{phone_line}" if country in ["United States", "Canada"] else f"+44 20 {phone_area} {phone_line}"

                raw_lead = RawLeadData(
                    company_name=company_name,
                    domain=domain,
                    website=website,
                    country=country,
                    region=region,
                    city=city,
                    industry=niche,
                    full_name=full_name,
                    first_name=first_name,
                    last_name=last_name,
                    job_title=job_title,
                    email=email,
                    phone=phone if plan.requirements.phone_required or random.random() > 0.3 else None,
                    source="simulated_live",
                    source_url=f"https://directory.leadgen.example.com/company/{domain}",
                    verification_status="verified" if random.random() > 0.2 else "unverified",
                    description=f"Leading {niche} provider operating in {country}.",
                    employee_count_range=random.choice(["11-50", "51-200", "201-500", "501-1000"]),
                    linkedin_url=f"https://linkedin.com/company/{domain.replace('.com', '')}",
                    is_synthetic=True, # MANDATORY SAFETY TAG
                )

                leads.append(raw_lead)

                if len(leads) >= limit:
                    break

            if len(leads) >= limit:
                break

        return leads

    async def validate(self, raw_lead: RawLeadData) -> bool:
        return True
