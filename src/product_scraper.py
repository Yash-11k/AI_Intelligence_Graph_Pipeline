"""
tools.json se products leta hai, LLM se pricing model nikaalta hai,
aur output CSV mein save karta hai.
"""

import json
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime
from llm_extractor import extract_pricing_model

TOOLS_JSON_URL = "https://raw.githubusercontent.com/lakey009/AI-Tools-List/main/AIToolsList.json"

# Max 10 LLM calls ek saath - isse zyada rate-limit mein phasenge, isse kam slow hoga
CONCURRENCY_LIMIT = 10


async def fetch_tools_list(session: aiohttp.ClientSession) -> list[dict]:
    async with session.get(TOOLS_JSON_URL) as resp:
        return await resp.json(content_type=None)


async def process_one_product(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, tool: dict, index: int, total: int) -> dict:
    """
    Semaphore ka matlab: ek time pe max CONCURRENCY_LIMIT products hi process honge,
    baaki queue mein wait karenge apni baari ka.
    """
    async with semaphore:
        pricing = await extract_pricing_model(session, tool.get("description", ""))
        print(f"  [{index+1}/{total}] {tool.get('handle')} -> {pricing}")

        return {
            "schemaVersion": "1.0",
            "recordType": "PRODUCT",
            "startupName": tool.get("handle"),
            "pricingModel": pricing,
            "source_name": "AI-Tools-List (github)",
            "source_url": tool.get("website"),
            "collectedAt": datetime.utcnow().isoformat() + "Z",
        }


async def scrape_products(target_count: int = 1000) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        print("Fetching tools list...")
        all_tools = await fetch_tools_list(session)
        print(f"Total tools available: {len(all_tools)}")

        selected = all_tools[:target_count]
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

        tasks = [
            process_one_product(session, semaphore, tool, i, len(selected))
            for i, tool in enumerate(selected)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Koi ek product fail ho jaye to poora batch crash na ho, usse skip kar do
    clean_results = [r for r in results if not isinstance(r, Exception)]
    return clean_results


async def main():
    products = await scrape_products(target_count=1000)

    df = pd.DataFrame(products)
    df.to_csv("../output/products.csv", index=False)

    print(f"\nDone! {len(df)} products saved to output/products.csv")
    print("\nPricing distribution:")
    print(df["pricingModel"].value_counts())


if __name__ == "__main__":
    asyncio.run(main())