from typing import Optional


def calculate_lead_score(
    has_website: bool,
    has_email: bool,
    has_phone: bool,
    has_contact_name: bool,
    has_job_title: bool,
    verification_status: str = "unverified",
    is_synthetic: bool = False,
) -> int:
    """
    Module 1 Quality Score algorithm (0-100).
    Evaluates verified parameters and data availability.
    """
    score = 20 # Base score for discovered prospect

    if has_website:
        score += 20
    if has_email:
        score += 25
    if has_phone:
        score += 15
    if has_contact_name:
        score += 10
    if has_job_title:
        score += 10

    if verification_status == "verified":
        score += 10
    elif verification_status == "invalid":
        score -= 30

    # Cap score between 0 and 100
    return max(0, min(100, score))
