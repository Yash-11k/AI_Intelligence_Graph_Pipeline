"""
This script fetches star counts for GitHub repositories.
If a rate limit (HTTP 403/429) is encountered, it automatically retries with exponential backoff.
"""

import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class RateLimitError(Exception):
    """Raised when GitHub returns a rate-limit error (too many requests)."""
    pass


# The @retry decorator automatically re-executes the function if it raises RateLimitError,
# increasing the wait time between each attempt.
@retry(
    stop=stop_after_attempt(5),              # Try a maximum of 5 times before failing
    wait=wait_exponential(multiplier=1, min=2, max=60),  # Exponential wait: 2s, 4s, 8s... up to 60s
    retry=retry_if_exception_type(RateLimitError),
)
async def fetch_github_stars(session: aiohttp.ClientSession, owner: str, repo: str) -> dict:
    """
    Fetches repository details including star count, description, and HTML URL.

    Example inputs: owner="openai", repo="whisper"
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-intelligence-pipeline",  # GitHub API requires a User-Agent header
    }

    async with session.get(url, headers=headers) as resp:
        if resp.status in (403, 429):
            # Rate limit reached -> raise RateLimitError to trigger the retry decorator
            print(f"  [rate limited] {owner}/{repo} -> retrying with backoff...")
            raise RateLimitError(f"Rate limited on {owner}/{repo}")

        if resp.status == 404:
            # Repository not found -> retrying will not resolve this, so return immediately
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
    Fetches details for multiple repositories concurrently using asyncio.

    Example input: repo_list = [("openai", "whisper"), ("meta-llama", "llama")]
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_github_stars(session, owner, repo) for owner, repo in repo_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out permanent exceptions (if 5 retries fail) to prevent the application from crashing
    clean_results = []
    for r in results:
        if isinstance(r, Exception):
            print(f"  [failed permanently] {r}")
        else:
            clean_results.append(r)
    return clean_results


if __name__ == "__main__":
    # Test execution using 3 popular repositories
    sample_repos = [
        ("openai", "whisper"),
        ("huggingface", "transformers"),
        ("meta-llama", "llama"),
    ]
    results = asyncio.run(fetch_many_repos(sample_repos))
    for r in results:
        print(r)