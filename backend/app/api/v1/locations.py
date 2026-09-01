import re
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/locations", tags=["Locations"])


class CountryItem(BaseModel):
    code: str
    name: str
    official_name: Optional[str] = None
    iso_code: str


class RegionItem(BaseModel):
    id: str
    country_code: str
    name: str
    code: str


class CityItem(BaseModel):
    id: str
    country_code: str
    region_code: str
    region_name: str
    name: str


# Comprehensive ISO 3166-1 country dataset
COUNTRIES_DB: List[CountryItem] = [
    CountryItem(code="US", name="United States", official_name="United States of America", iso_code="USA"),
    CountryItem(code="CA", name="Canada", official_name="Canada", iso_code="CAN"),
    CountryItem(code="GB", name="United Kingdom", official_name="United Kingdom of Great Britain and Northern Ireland", iso_code="GBR"),
    CountryItem(code="IN", name="India", official_name="Republic of India", iso_code="IND"),
    CountryItem(code="AU", name="Australia", official_name="Commonwealth of Australia", iso_code="AUS"),
    CountryItem(code="DE", name="Germany", official_name="Federal Republic of Germany", iso_code="DEU"),
    CountryItem(code="FR", name="France", official_name="French Republic", iso_code="FRA"),
    CountryItem(code="JP", name="Japan", official_name="Japan", iso_code="JPN"),
    CountryItem(code="BR", name="Brazil", official_name="Federative Republic of Brazil", iso_code="BRA"),
    CountryItem(code="SG", name="Singapore", official_name="Republic of Singapore", iso_code="SGP"),
    CountryItem(code="AE", name="United Arab Emirates", official_name="United Arab Emirates", iso_code="ARE"),
    CountryItem(code="ID", name="Indonesia", official_name="Republic of Indonesia", iso_code="IDN"),
    CountryItem(code="NL", name="Netherlands", official_name="Kingdom of the Netherlands", iso_code="NLD"),
    CountryItem(code="ES", name="Spain", official_name="Kingdom of Spain", iso_code="ESP"),
    CountryItem(code="IT", name="Italy", official_name="Italian Republic", iso_code="ITA"),
    CountryItem(code="MX", name="Mexico", official_name="United Mexican States", iso_code="MEX"),
    CountryItem(code="ZA", name="South Africa", official_name="Republic of South Africa", iso_code="ZAF"),
    CountryItem(code="NZ", name="New Zealand", official_name="New Zealand", iso_code="NZL"),
    CountryItem(code="IE", name="Ireland", official_name="Republic of Ireland", iso_code="IRL"),
    CountryItem(code="SE", name="Sweden", official_name="Kingdom of Sweden", iso_code="SWE"),
    CountryItem(code="CH", name="Switzerland", official_name="Swiss Confederation", iso_code="CHE"),
]

# Region/Subdivision mapping per country code
REGIONS_DB = {
    "US": [
        RegionItem(id="US-AL", country_code="US", name="Alabama", code="AL"),
        RegionItem(id="US-AK", country_code="US", name="Alaska", code="AK"),
        RegionItem(id="US-AZ", country_code="US", name="Arizona", code="AZ"),
        RegionItem(id="US-AR", country_code="US", name="Arkansas", code="AR"),
        RegionItem(id="US-CA", country_code="US", name="California", code="CA"),
        RegionItem(id="US-CO", country_code="US", name="Colorado", code="CO"),
        RegionItem(id="US-CT", country_code="US", name="Connecticut", code="CT"),
        RegionItem(id="US-FL", country_code="US", name="Florida", code="FL"),
        RegionItem(id="US-GA", country_code="US", name="Georgia", code="GA"),
        RegionItem(id="US-IL", country_code="US", name="Illinois", code="IL"),
        RegionItem(id="US-MA", country_code="US", name="Massachusetts", code="MA"),
        RegionItem(id="US-NY", country_code="US", name="New York", code="NY"),
        RegionItem(id="US-TX", country_code="US", name="Texas", code="TX"),
        RegionItem(id="US-WA", country_code="US", name="Washington", code="WA"),
    ],
    "CA": [
        RegionItem(id="CA-AB", country_code="CA", name="Alberta", code="AB"),
        RegionItem(id="CA-BC", country_code="CA", name="British Columbia", code="BC"),
        RegionItem(id="CA-ON", country_code="CA", name="Ontario", code="ON"),
        RegionItem(id="CA-QC", country_code="CA", name="Quebec", code="QC"),
    ],
    "IN": [
        RegionItem(id="IN-DL", country_code="IN", name="Delhi", code="DL"),
        RegionItem(id="IN-UP", country_code="IN", name="Uttar Pradesh", code="UP"),
        RegionItem(id="IN-KA", country_code="IN", name="Karnataka", code="KA"),
        RegionItem(id="IN-MH", country_code="IN", name="Maharashtra", code="MH"),
        RegionItem(id="IN-TN", country_code="IN", name="Tamil Nadu", code="TN"),
        RegionItem(id="IN-TG", country_code="IN", name="Telangana", code="TG"),
        RegionItem(id="IN-GJ", country_code="IN", name="Gujarat", code="GJ"),
        RegionItem(id="IN-HR", country_code="IN", name="Haryana", code="HR"),
        RegionItem(id="IN-WB", country_code="IN", name="West Bengal", code="WB"),
        RegionItem(id="IN-PB", country_code="IN", name="Punjab", code="PB"),
        RegionItem(id="IN-RJ", country_code="IN", name="Rajasthan", code="RJ"),
        RegionItem(id="IN-KL", country_code="IN", name="Kerala", code="KL"),
    ],
    "AU": [
        RegionItem(id="AU-NSW", country_code="AU", name="New South Wales", code="NSW"),
        RegionItem(id="AU-VIC", country_code="AU", name="Victoria", code="VIC"),
        RegionItem(id="AU-QLD", country_code="AU", name="Queensland", code="QLD"),
    ],
    "GB": [
        RegionItem(id="GB-ENG", country_code="GB", name="England", code="ENG"),
        RegionItem(id="GB-SCT", country_code="GB", name="Scotland", code="SCT"),
        RegionItem(id="GB-WLS", country_code="GB", name="Wales", code="WLS"),
    ]
}

# Cities database mapping
CITIES_DB: List[CityItem] = [
    # India - Uttar Pradesh
    CityItem(id="IN-UP-GZB", country_code="IN", region_code="UP", region_name="Uttar Pradesh", name="Ghaziabad"),
    CityItem(id="IN-UP-NOIDA", country_code="IN", region_code="UP", region_name="Uttar Pradesh", name="Noida"),
    CityItem(id="IN-UP-LKO", country_code="IN", region_code="UP", region_name="Uttar Pradesh", name="Lucknow"),
    CityItem(id="IN-UP-AGR", country_code="IN", region_code="UP", region_name="Uttar Pradesh", name="Agra"),
    CityItem(id="IN-UP-KNP", country_code="IN", region_code="UP", region_name="Uttar Pradesh", name="Kanpur"),
    CityItem(id="IN-UP-VNS", country_code="IN", region_code="UP", region_name="Uttar Pradesh", name="Varanasi"),
    CityItem(id="IN-UP-MTR", country_code="IN", region_code="UP", region_name="Uttar Pradesh", name="Meerut"),
    # India - Delhi
    CityItem(id="IN-DL-DEL", country_code="IN", region_code="DL", region_name="Delhi", name="Delhi"),
    CityItem(id="IN-DL-NDL", country_code="IN", region_code="DL", region_name="Delhi", name="New Delhi"),
    # India - Maharashtra
    CityItem(id="IN-MH-BOM", country_code="IN", region_code="MH", region_name="Maharashtra", name="Mumbai"),
    CityItem(id="IN-MH-PNE", country_code="IN", region_code="MH", region_name="Maharashtra", name="Pune"),
    CityItem(id="IN-MH-NAG", country_code="IN", region_code="MH", region_name="Maharashtra", name="Nagpur"),
    # India - Karnataka
    CityItem(id="IN-KA-BLR", country_code="IN", region_code="KA", region_name="Karnataka", name="Bengaluru"),
    CityItem(id="IN-KA-MYS", country_code="IN", region_code="KA", region_name="Karnataka", name="Mysore"),
    # US - Washington
    CityItem(id="US-WA-SEA", country_code="US", region_code="WA", region_name="Washington", name="Seattle"),
    CityItem(id="US-WA-SPO", country_code="US", region_code="WA", region_name="Washington", name="Spokane"),
    CityItem(id="US-WA-TAC", country_code="US", region_code="WA", region_name="Washington", name="Tacoma"),
    # US - California
    CityItem(id="US-CA-LAX", country_code="US", region_code="CA", region_name="California", name="Los Angeles"),
    CityItem(id="US-CA-SFO", country_code="US", region_code="CA", region_name="California", name="San Francisco"),
    CityItem(id="US-CA-SAN", country_code="US", region_code="CA", region_name="California", name="San Diego"),
    # Canada - Ontario
    CityItem(id="CA-ON-TOR", country_code="CA", region_code="ON", region_name="Ontario", name="Toronto"),
    CityItem(id="CA-ON-OTT", country_code="CA", region_code="ON", region_name="Ontario", name="Ottawa"),
    # UK - England
    CityItem(id="GB-ENG-LON", country_code="GB", region_code="ENG", region_name="England", name="London"),
    CityItem(id="GB-ENG-MAN", country_code="GB", region_code="ENG", region_name="England", name="Manchester"),
]


@router.get("/countries", response_model=List[CountryItem])
async def search_countries(q: Optional[str] = Query(None, description="Search term for country name or ISO code")):
    if not q:
        return COUNTRIES_DB
    
    query_lower = q.lower().strip()
    results = [
        c for c in COUNTRIES_DB
        if query_lower in c.name.lower() or
           query_lower in c.code.lower() or
           query_lower in c.iso_code.lower() or
           (c.official_name and query_lower in c.official_name.lower())
    ]
    return results


@router.get("/countries/{country_code}/regions", response_model=List[RegionItem])
async def get_regions_by_country(country_code: str, q: Optional[str] = Query(None)):
    code_upper = country_code.upper()
    regions = REGIONS_DB.get(code_upper, [])
    
    if not q:
        return regions
    
    query_lower = q.lower().strip()
    return [r for r in regions if query_lower in r.name.lower() or query_lower in r.code.lower()]


@router.get("/countries/{country_code}/regions/{region_code}/cities", response_model=List[CityItem])
async def get_cities_by_region(country_code: str, region_code: str, q: Optional[str] = Query(None)):
    c_code = country_code.upper()
    r_code = region_code.upper()

    cities = [
        c for c in CITIES_DB
        if c.country_code == c_code and (c.region_code.upper() == r_code or c.region_name.lower() == r_code.lower())
    ]

    if not q:
        return cities

    query_lower = q.lower().strip()
    return [c for c in cities if query_lower in c.name.lower()]


@router.post("/validate")
async def validate_location_integrity(country: str, region: Optional[str] = None, city: Optional[str] = None):
    """
    Validates location hierarchy (Country -> Region -> City).
    Blocks invalid combinations (e.g. Region: Delhi + City: Ghaziabad).
    """
    if not country:
        return {"valid": False, "reason": "Country is required."}

    if region and city:
        # Check if city is known to belong to a different region
        for c in CITIES_DB:
            if c.name.lower() == city.lower():
                if c.region_name.lower() != region.lower() and c.region_code.lower() != region.lower():
                    return {
                        "valid": False,
                        "reason": f"Location mismatch: {city} belongs to {c.region_name}, not {region}."
                    }

    return {"valid": True, "reason": "Location hierarchy is valid."}

