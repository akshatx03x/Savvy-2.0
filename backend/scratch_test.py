import asyncio
import httpx
import urllib.parse
import re

async def test_ddg():
    search_query = "Real Estate businesses in Ghaziabad Delhi India"
    encoded_query = urllib.parse.quote_plus(search_query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        resp = await client.get(url, headers=headers)
        print("HTTP STATUS:", resp.status_code)
        if resp.status_code == 200:
            print("HTML LEN:", len(resp.text))

            # Test regex in web_business.py
            result_blocks = re.findall(
                r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
                resp.text,
                re.IGNORECASE | re.DOTALL
            )
            print(f"Total <a href> tags matched: {len(result_blocks)}")

            # Test result__a or result__url or uddg
            uddg_matches = re.findall(r'uddg=([^&"]+)', resp.text)
            print(f"uddg redirect matches found: {len(uddg_matches)}")
            for u in uddg_matches[:10]:
                dec = urllib.parse.unquote(u)
                print(" - DECODED URL:", dec)

asyncio.run(test_ddg())
