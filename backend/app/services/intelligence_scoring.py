from typing import List
from app.schemas.research import FindingSchema, EvidenceSchema, SignalSchema, OpportunitySchema


def calculate_intelligence_score(
    evidence_items: List[EvidenceSchema],
    findings: List[FindingSchema],
    signals: List[SignalSchema],
    opportunities: List[OpportunitySchema],
    has_contact: bool = True,
) -> int:
    """
    Transparent Lead Intelligence Scoring Algorithm (0-100).
    Evaluates evidence quality, source diversity, recency, signals, and opportunity clarity.
    """
    score = 25 # Base intelligence score for initiated research

    # 1. Evidence Quality & Count (up to +25)
    evidence_count = len(evidence_items)
    if evidence_count >= 5:
        score += 25
    elif evidence_count >= 3:
        score += 18
    elif evidence_count >= 1:
        score += 10

    # 2. Source Diversity (up to +20)
    distinct_sources = len(set([e.source_name for e in evidence_items]))
    if distinct_sources >= 3:
        score += 20
    elif distinct_sources >= 2:
        score += 12
    elif distinct_sources >= 1:
        score += 6

    # 3. Content Recency (up to +20)
    recent_items = [e for e in evidence_items if e.recency_tier in ["recent", "fresh"]]
    if len(recent_items) >= 2:
        score += 20
    elif len(recent_items) >= 1:
        score += 10

    # 4. Business Signals Strength (up to +15)
    signal_count = len(signals)
    if signal_count >= 2:
        score += 15
    elif signal_count >= 1:
        score += 8

    # 5. Opportunities Clarity (up to +10)
    if len(opportunities) >= 2:
        score += 10
    elif len(opportunities) >= 1:
        score += 5

    # Cap score between 0 and 100
    return max(0, min(100, score))
