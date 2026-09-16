"""
YC (Y Combinator) ke public company directory se AI startups nikaalta hai.
Data source: https://github.com/yc-oss/api (free, no auth needed, real data)
"""

import aiohttp
import asyncio
import pandas as pd
from datetime import datetime

YC_DATA_URL = "https://raw.githubusercontent.com/yc-oss/api/main/companies/all.json"


async def fetch_yc_companies() -> list[dict]:
    async with aiohttp.ClientSession() as session:
            async with session.get(YC_DATA_URL) as resp:
                return await resp.json(content_type=None)


def is_ai_related(company: dict) -> bool:
    """Company AI-related hai ya nahi, tags aur industries check karke."""
    tags = company.get("tags") or []
    industries = company.get("industries") or []
    combined = [str(t) for t in tags + industries]
    return any("AI" in t or "Artificial Intelligence" in t for t in combined)


def normalize_startup(raw: dict) -> dict:
    return {
        "schemaVersion": "1.0",
        "recordType": "STARTUP",
        "content": {
            "entityName": raw.get("name"),
            "data": {
                "employeeCount": raw.get("team_size"),
            },
        },
        "source": {
            "name": "ycombinator.com",
            "url": f"https://www.ycombinator.com/companies/{raw.get('slug')}",
        },
        "collectedAt": datetime.utcnow().isoformat() + "Z",
    }


async def scrape_startups(target_count: int = 1000) -> list[dict]:
    print("Fetching YC companies data...")
    all_companies = await fetch_yc_companies()
    print(f"Total companies in dataset: {len(all_companies)}")

    ai_companies = [c for c in all_companies if is_ai_related(c)]
    print(f"AI-related companies found: {len(ai_companies)}")

    selected = ai_companies[:target_count]
    return [normalize_startup(c) for c in selected]


async def main():
    startups = await scrape_startups(target_count=1000)

    rows = []
    for s in startups:
        rows.append({
            "schemaVersion": s["schemaVersion"],
            "recordType": s["recordType"],
            "entityName": s["content"]["entityName"],
            "employeeCount": s["content"]["data"]["employeeCount"],
            "source_name": s["source"]["name"],
            "source_url": s["source"]["url"],
            "collectedAt": s["collectedAt"],
        })

    df = pd.DataFrame(rows)
    df.to_csv("../output/startups.csv", index=False)
    print(f"\nDone! {len(df)} startups saved to output/startups.csv")


if __name__ == "__main__":
    asyncio.run(main())