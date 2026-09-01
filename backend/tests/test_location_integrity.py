import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_locations_countries_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/locations/countries")
        assert response.status_code == 200
        countries = response.json()
        assert len(countries) >= 10
        codes = [c["code"] for c in countries]
        assert "US" in codes
        assert "CA" in codes
        assert "IN" in codes
        assert "GB" in codes
        assert "AU" in codes


@pytest.mark.asyncio
async def test_locations_country_search():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Search "uni" -> US, UK, UAE
        response = await ac.get("/api/v1/locations/countries?q=uni")
        assert response.status_code == 200
        matches = response.json()
        match_names = [m["name"] for m in matches]
        assert "United States" in match_names
        assert "United Kingdom" in match_names

        # Search "ind" -> India, Indonesia
        response_ind = await ac.get("/api/v1/locations/countries?q=ind")
        assert response_ind.status_code == 200
        matches_ind = [m["name"] for m in response_ind.json()]
        assert "India" in matches_ind
        assert "Indonesia" in matches_ind


@pytest.mark.asyncio
async def test_locations_regions():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # US Regions
        res_us = await ac.get("/api/v1/locations/countries/US/regions")
        assert res_us.status_code == 200
        regions_us = [r["name"] for r in res_us.json()]
        assert "Washington" in regions_us
        assert "California" in regions_us

        # CA Regions
        res_ca = await ac.get("/api/v1/locations/countries/CA/regions")
        assert res_ca.status_code == 200
        regions_ca = [r["name"] for r in res_ca.json()]
        assert "Ontario" in regions_ca
        assert "Washington" not in regions_ca
