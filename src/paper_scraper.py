"""
This file fetches AI research papers using Semantic Scholar's FREE API.
(More reliable and stable than arXiv's legacy export API)
Handles rate limits (429/503) automatically using retry logic.
"""

import aiohttp
import asyncio
import re
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
GITHUB_PATTERN = re.compile(r"https?://github\.com/[\w\-]+/[\w\-\.]+")


class ApiRetryError(Exception):
    """Raised when the API returns a 429/503 or any server-side error."""
    pass


@retry(
    stop=stop_after_attempt(6),
    wait=wait_exponential(multiplier=2, min=3, max=60),
    retry=retry_if_exception_type(ApiRetryError),
)
async def fetch_batch(session: aiohttp.ClientSession, query: str, token: str | None = None) -> dict:
    params = {
        "query": query,
        "fields": "title,authors,url,publicationDate,abstract,externalIds",
    }
    if token:
        params["token"] = token

    headers = {"User-Agent": "Mozilla/5.0 (ai-pipeline-project)"}

    async with session.get(SEMANTIC_SCHOLAR_API, params=params, headers=headers) as resp:
        if resp.status in (429, 503):
            print(f"  [rate limited/{resp.status}] waiting and retrying...")
            raise ApiRetryError(f"Status {resp.status}")

        if resp.status != 200:
            text = await resp.text()
            print(f"  [ERROR] Status {resp.status}: {text[:200]}")
            raise ApiRetryError(f"Unexpected status {resp.status}")

        return await resp.json()


def normalize_paper(raw: dict) -> dict:
    """Converts the raw response from Semantic Scholar into our standard schema."""
    abstract = raw.get("abstract") or ""
    github_match = GITHUB_PATTERN.search(abstract)
    github_url = github_match.group(0) if github_match else None

    authors = [a.get("name") for a in raw.get("authors", []) if a.get("name")]

    published = raw.get("publicationDate")
    if published:
        published_iso = published + "T00:00:00Z"
    else:
        published_iso = None

    paper_url = raw.get("url") or (
        f"https://arxiv.org/abs/{raw['externalIds']['ArXiv']}"
        if raw.get("externalIds", {}).get("ArXiv") else None
    )

    return {
        "schemaVersion": "1.0",
        "recordType": "RESEARCH_PAPER",
        "content": {
            "title": raw.get("title"),
            "authors": authors,
            "paper_url": paper_url,
            "github_url": github_url,
            "github_stars": None,
            "published_date": published_iso,
        },
        "source": {
            "name": "semanticscholar.org",
            "url": paper_url,
        },
        "collectedAt": datetime.utcnow().isoformat() + "Z",
    }


async def scrape_papers(query: str = "artificial intelligence", target_count: int = 10) -> list[dict]:
    all_papers = []
    token = None

    async with aiohttp.ClientSession() as session:
        while len(all_papers) < target_count:
            print(f"  fetching batch... (have {len(all_papers)} so far)")
            data = await fetch_batch(session, query, token)

            batch = data.get("data", [])
            if not batch:
                break

            for raw in batch:
                if raw.get("title"):
                    all_papers.append(normalize_paper(raw))

            token = data.get("token")
            if not token:
                break

            await asyncio.sleep(1)

    return all_papers[:target_count]


if __name__ == "__main__":
    papers = asyncio.run(scrape_papers(query="artificial intelligence", target_count=1000))
    print(f"\nTotal papers fetched: {len(papers)}\n")
    for p in papers[:5]:
        print("-", p["content"]["title"])
        print("    github:", p["content"]["github_url"])