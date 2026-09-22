"""
Papers scrape and save it to CSV file 
paper_scraper.py import from this file 
"""

import asyncio
import pandas as pd
from paper_scraper import scrape_papers


async def main():
    print("Scraping started, this will take some time...")
    papers = await scrape_papers(query="artificial intelligence", target_count=1000)

    # Convert nested dictionary (content.title, content.authors, etc.)
    # into a flat table for CSV export
    rows = []
    for p in papers:
        rows.append({
            "schemaVersion": p["schemaVersion"],
            "recordType": p["recordType"],
            "title": p["content"]["title"],
            "authors": "; ".join(p["content"]["authors"]),  # Join list into text
            "paper_url": p["content"]["paper_url"],
            "github_url": p["content"]["github_url"],
            "github_stars": p["content"]["github_stars"],
            "published_date": p["content"]["published_date"],
            "source_name": p["source"]["name"],
            "collectedAt": p["collectedAt"],
        })

    df = pd.DataFrame(rows)
    df.to_csv("../output/papers.csv", index=False)

    print(f"\nDone! {len(df)} papers saved to output/papers.csv")
    github_count = df["github_url"].notna().sum()
    print(f"Out of these, {github_count} papers have a GitHub link.")


if __name__ == "__main__":
    asyncio.run(main())