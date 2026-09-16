"""
Ye file GitHub se kisi repo ke stars nikaalne ka kaam karti hai.
Agar rate-limit (403/429) mile, to automatic retry karega, wait karke.
"""

import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class RateLimitError(Exception):
    """Jab GitHub 'too many requests' bole, ye error uthayenge."""
    pass


# @retry decorator ka matlab: neeche wala function fail ho to
# automatic dobara chalao, har baar zyada wait karke.
@retry(
    stop=stop_after_attempt(5),              # max 5 baar try karo, fir haar maan lo
    wait=wait_exponential(multiplier=1, min=2, max=60),  # 2s, 4s, 8s... max 60s wait
    retry=retry_if_exception_type(RateLimitError),
)
async def fetch_github_stars(session: aiohttp.ClientSession, owner: str, repo: str) -> dict:
    """
    owner="openai", repo="whisper" jaisa input dedo,
    ye function stars, description, aur repo URL wapas dega.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-intelligence-pipeline",  # GitHub ko user-agent chahiye hota hai
    }

    async with session.get(url, headers=headers) as resp:
        if resp.status in (403, 429):
            # Rate limit lag gaya -> exception uthao, @retry isko pakad ke wait karega
            print(f"  [rate limited] {owner}/{repo} -> retrying with backoff...")
            raise RateLimitError(f"Rate limited on {owner}/{repo}")

        if resp.status == 404:
            # Repo exist hi nahi karta, retry karne ka matlab nahi
            return {"owner": owner, "repo": repo, "stars": None, "error": "not_found"}

        data = await resp.json()
        return {
            "owner": owner,
            "repo": repo,
            "stars": data.get("stargazers_count"),
            "description": data.get("description"),
            "url": data.get("html_url"),
        }


async def fetch_many_repos(repo_list: list[tuple[str, str]]) -> list[dict]:
    """
    repo_list = [("openai", "whisper"), ("meta-llama", "llama"), ...]
    Ye sabko EK SAATH (concurrently) fetch karega, sequentially nahi.
    Isliye 1000 repos bhi jaldi ho jaayenge, ek-ek karke nahi karna padega.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_github_stars(session, owner, repo) for owner, repo in repo_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Agar kisi ek mein 5 retry ke baad bhi fail ho gaya, use skip karo, crash mat ho
    clean_results = []
    for r in results:
        if isinstance(r, Exception):
            print(f"  [failed permanently] {r}")
        else:
            clean_results.append(r)
    return clean_results


if __name__ == "__main__":
    # Chhota test: 3 famous AI repos ke stars nikaalo
    sample_repos = [
        ("openai", "whisper"),
        ("huggingface", "transformers"),
        ("meta-llama", "llama"),
    ]
    results = asyncio.run(fetch_many_repos(sample_repos))
    for r in results:
        print(r)