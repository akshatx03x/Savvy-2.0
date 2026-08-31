from typing import List, Dict, Any, Tuple, Optional
from app.schemas.outreach import ClaimValidationResult, MessagePlan
from app.core.ai_provider import ai_provider
from app.core.logging import logger

MAX_EVIDENCE_ITEMS = 5


class PersonalizationEngine:
    """
    Module 3 AI Personalization Engine:
    Ranks evidence, constructs message plans, generates evidence-backed drafts,
    and performs claim validation & quality scoring.
    """

    @staticmethod
    def check_research_readiness(
        research_profile: Optional[Dict[str, Any]], personalization_level: str
    ) -> Tuple[bool, str]:
        """
        Enforces STRICT Requirement #46:
        If DEEP personalization is requested and research is missing/empty,
        reject fake deep personalization and return NEEDS_RESEARCH status.
        """
        has_profile = research_profile is not None and len(research_profile.get("evidence_items", [])) > 0

        if personalization_level == "DEEP" and not has_profile:
            return False, "NEEDS_RESEARCH"
        return True, "READY"

    @staticmethod
    def rank_evidence(
        evidence_items: List[Dict[str, Any]], offer_info: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Ranks research evidence items based on relevance to offer, confidence, and recency.
        """
        if not evidence_items:
            return []

        offer_keywords = []
        if offer_info:
            offer_keywords = (offer_info.get("name", "") + " " + offer_info.get("description", "")).lower().split()

        scored = []
        for ev in evidence_items:
            score = ev.get("confidence", 0.85) * 40 # Up to 40 pts

            snippet = ev.get("supporting_snippet", "").lower()
            rel_matches = sum(1 for kw in offer_keywords if len(kw) > 3 and kw in snippet)
            score += min(30, rel_matches * 10) # Up to 30 pts

            if ev.get("recency_tier") in ["recent", "fresh"]:
                score += 20
            else:
                score += 10

            scored.append((score, ev))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:MAX_EVIDENCE_ITEMS]]

    @classmethod
    async def generate_draft(
        cls,
        lead_info: Dict[str, Any],
        research_profile: Optional[Dict[str, Any]],
        offer_info: Optional[Dict[str, Any]],
        objective: str,
        tone: str,
        length: str,
        cta_type: str,
        personalization_level: str,
    ) -> Tuple[Dict[str, Any], ClaimValidationResult, Dict[str, Any]]:
        # 1. Check research readiness
        ready, status_code = cls.check_research_readiness(research_profile, personalization_level)
        if not ready:
            return (
                {
                    "subject": f"Research required for {lead_info.get('company_name', 'lead')}",
                    "body": "Deep research has not been completed for this prospect. Please run AI Research before generating deep personalized outreach.",
                    "status": "NEEDS_RESEARCH",
                    "personalization_score": 0,
                    "evidence_used": [],
                },
                ClaimValidationResult(is_valid=False, unsupported_claims=[], quality_score=0),
                {},
            )

        # 2. Context Selection & Ranking
        raw_evidence = research_profile.get("evidence_items", []) if research_profile else []
        ranked_evidence = cls.rank_evidence(raw_evidence, offer_info)

        compact_profile = {}
        if research_profile:
            compact_profile = {
                "summary": research_profile.get("summary"),
                "company_overview": research_profile.get("company_overview"),
                "evidence_items": ranked_evidence,
            }

        # 3. Generate Message Plan
        message_plan = await ai_provider.generate_message_plan(lead_info, compact_profile, offer_info or {}, objective)

        # 4. Generate Outreach Email
        draft_content = await ai_provider.generate_outreach(
            lead_info, compact_profile, offer_info, objective, tone, length, cta_type, personalization_level
        )

        # 5. Claim Validation
        validation = await ai_provider.validate_claims(draft_content["body"], draft_content["evidence_used"])

        return draft_content, validation, message_plan

    @classmethod
    async def rewrite_draft(
        cls, current_subject: str, current_body: str, prompt: str, evidence_used: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], ClaimValidationResult]:
        rewritten = await ai_provider.rewrite_outreach(current_subject, current_body, prompt, evidence_used)
        validation = await ai_provider.validate_claims(rewritten["body"], evidence_used)
        return rewritten, validation
