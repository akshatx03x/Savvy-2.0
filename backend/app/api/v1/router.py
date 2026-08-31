from fastapi import APIRouter
from app.api.v1 import (
    leads,
    countries,
    jobs,
    ai,
    stats,
    companies,
    contacts,
    research,
    offers,
    outreach,
    mailboxes,
    campaigns,
    suppression,
    deliverability,
    analytics,
)

api_router = APIRouter()
api_router.include_router(leads.router)
api_router.include_router(countries.router)
api_router.include_router(jobs.router)
api_router.include_router(ai.router)
api_router.include_router(stats.router)
api_router.include_router(companies.router)
api_router.include_router(contacts.router)
api_router.include_router(research.router)
api_router.include_router(offers.router)
api_router.include_router(outreach.router)
api_router.include_router(mailboxes.router)
api_router.include_router(campaigns.router)
api_router.include_router(suppression.router)
api_router.include_router(deliverability.router)
api_router.include_router(analytics.router)
