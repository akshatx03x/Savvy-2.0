import re
from typing import Optional, Tuple


def normalize_email(email: Optional[str]) -> Optional[str]:
    if not email or not isinstance(email, str):
        return None
    email = email.strip().lower()
    if "@" not in email:
        return None
    
    parts = email.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None
        
    local, domain = parts
    # Handle Gmail subaddressing (user+tag@gmail.com -> user@gmail.com)
    if domain in ["gmail.com", "googlemail.com"]:
        local = local.split("+")[0].replace(".", "")
    return f"{local}@{domain}"


def normalize_domain(domain_or_url: Optional[str]) -> Optional[str]:
    if not domain_or_url or not isinstance(domain_or_url, str):
        return None
    url = domain_or_url.strip().lower()
    # Strip protocol
    url = re.sub(r"^https?://", "", url)
    # Strip www.
    url = re.sub(r"^www\.", "", url)
    # Strip path & query params
    url = url.split("/")[0].split("?")[0].split(":")[0]
    return url if url else None


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone or not isinstance(phone, str):
        return None
    # Strip non-digits except leading plus
    cleaned = re.sub(r"[^\d+]", "", phone.strip())
    if len(cleaned) < 7: # Too short to be valid phone
        return None
    return cleaned


def normalize_company_name(name: Optional[str]) -> str:
    if not name or not isinstance(name, str):
        return ""
    cleaned = name.strip().lower()
    # Strip legal entity suffixes
    suffixes = [
        r"\binc\.?\b", r"\bllc\.?\b", r"\bltd\.?\b", r"\bcorp\.?\b",
        r"\bcorporation\b", r"\bco\.?\b", r"\bcompany\b", r"\bgroup\b",
        r"\benterprises\b", r"\bholdings\b", r"\bplc\b", r"\bgmbh\b",
        r"\bpte\b", r"\bpvt\b", r"\bprivate\b", r"\blimited\b"
    ]
    for s in suffixes:
        cleaned = re.sub(s, "", cleaned)
    
    # Strip punctuation and multiple spaces
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if cleaned else name.strip().lower()


def split_full_name(full_name: str) -> Tuple[Optional[str], Optional[str]]:
    if not full_name:
        return None, None
    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0], None
    return parts[0], " ".join(parts[1:])
