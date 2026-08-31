import pytest
from app.services.normalization import (
    normalize_email,
    normalize_domain,
    normalize_phone,
    normalize_company_name,
    split_full_name,
)


def test_normalize_email():
    assert normalize_email("  John.Doe+test@Gmail.com ") == "johndoe@gmail.com"
    assert normalize_email("sarah@company.co.uk") == "sarah@company.co.uk"
    assert normalize_email("invalid-email") is None


def test_normalize_domain():
    assert normalize_domain("https://www.ApexRealty.com/about?ref=123") == "apexrealty.com"
    assert normalize_domain("http://sub.domain.co.uk/") == "sub.domain.co.uk"
    assert normalize_domain(None) is None


def test_normalize_phone():
    assert normalize_phone("+1 (555) 234-5678") == "+15552345678"
    assert normalize_phone("123") is None # Too short


def test_normalize_company_name():
    assert normalize_company_name("Apex Realty, Inc.") == "apex realty"
    assert normalize_company_name("Vanguard Solutions LLC") == "vanguard solutions"
    assert normalize_company_name("Global Tech Group Ltd") == "global tech"


def test_split_full_name():
    assert split_full_name("John Smith") == ("John", "Smith")
    assert split_full_name("Dr. Sarah Jane Connor") == ("Dr.", "Sarah Jane Connor")
    assert split_full_name("Cher") == ("Cher", None)
