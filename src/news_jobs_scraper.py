"""
Phase II: High-Fidelity Signal Ingestion (News & Jobs)
Strict 24-Hour Freshness Filter to extract only the most recent AI/ML/Tech news and job postings.
This module scrapes multiple sources for news and job postings, filters them based on relevance to AI
"""

import datetime
import dateparser
import feedparser
import pandas as pd
import requests
from bs4 import BeautifulSoup

NOW = datetime.datetime.now(datetime.timezone.utc)
CUTOFF_TIME = NOW - datetime.timedelta(hours=24)


def parse_to_utc_datetime(date_str: str) -> datetime.datetime:
    if not date_str:
        return None
    dt = dateparser.parse(
        str(date_str),
        settings={"RELATIVE_BASE": NOW, "RETURN_AS_TIMEZONE_AWARE": True},
    )
    if dt:
        return dt.astimezone(datetime.timezone.utc)
    return None


def is_within_24_hours(dt: datetime.datetime) -> bool:
    if not dt:
        return False
    return dt >= CUTOFF_TIME


# --- 1. NEWS SCRAPER ---
NEWS_FEEDS = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "VentureBeat AI", "url": "https://feeds.feedburner.com/venturebeat/SGBU"},
    {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed"},
    {"name": "Ars Technica AI", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab"},
    {"name": "HackerNews AI", "url": "https://hnrss.org/newest?q=AI"},
]


def scrape_news() -> pd.DataFrame:
    print("Scraping AI News (24-hr fresh)...")
    articles = []

    for feed_info in NEWS_FEEDS:
        try:
            parsed_feed = feedparser.parse(feed_info["url"])
            for entry in parsed_feed.entries:
                title = entry.get("title", "")
                url = entry.get("link", "")
                raw_date = entry.get("published", entry.get("updated", ""))

                pub_dt = parse_to_utc_datetime(raw_date)

                if pub_dt and is_within_24_hours(pub_dt):
                    summary_raw = entry.get("summary", "")
                    summary_clean = (
                        BeautifulSoup(summary_raw, "html.parser").get_text()
                        if summary_raw
                        else ""
                    )

                    articles.append(
                        {
                            "schemaVersion": "1.0",
                            "recordType": "NEWS",
                            "source_name": feed_info["name"],
                            "source_url": url,
                            "title": title,
                            "content_text": summary_clean[:500],
                            "published_date": pub_dt.isoformat(),
                            "collectedAt": NOW.isoformat(),
                        }
                    )
        except Exception as e:
            print(f"Error fetching news feed {feed_info['name']}: {e}")

    df = pd.DataFrame(articles)
    print(f"Total Fresh News Articles Found: {len(df)}")
    return df


# --- 2. JOBS SCRAPER (Multi-source Fallback) ---
JOB_FEEDS = [
    {"name": "WeWorkRemotely AI", "url": "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss"},
    {"name": "HackerNews Jobs", "url": "https://hnrss.org/jobs"},
    {"name": "Remotive AI Jobs", "url": "https://remotive.com/remote-jobs/feed"},
]


def scrape_jobs() -> pd.DataFrame:
    print("Scraping AI Jobs (24-hr fresh)...")
    jobs = []

    # 1. RSS Job Feeds
    for feed_info in JOB_FEEDS:
        try:
            parsed_feed = feedparser.parse(feed_info["url"])
            for entry in parsed_feed.entries:
                title = entry.get("title", "")
                url = entry.get("link", "")
                raw_date = entry.get("published", entry.get("updated", ""))

                # Filter AI/Data/ML related roles
                title_lower = title.lower()
                if any(kw in title_lower for kw in ["ai", "machine learning", "data", "python", "backend", "engineer", "model"]):
                    pub_dt = parse_to_utc_datetime(raw_date)

                    if pub_dt and is_within_24_hours(pub_dt):
                        jobs.append(
                            {
                                "schemaVersion": "1.0",
                                "recordType": "JOB",
                                "source_name": feed_info["name"],
                                "source_url": url,
                                "company": title.split("at")[1].strip() if "at" in title else "Tech Startup",
                                "role": title,
                                "role_family": "Engineering",
                                "is_remote": True,
                                "published_date": pub_dt.isoformat(),
                                "collectedAt": NOW.isoformat(),
                            }
                        )
        except Exception as e:
            print(f"Error fetching job feed {feed_info['name']}: {e}")

    # 2. RemoteOK API Fallback
    try:
        url = "https://remoteok.com/api"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=25)
        if response.status_code == 200:
            data = response.json()
            for item in data[1:]:
                position = item.get("position", "")
                if any(kw in position.lower() for kw in ["ai", "ml", "data", "python", "developer", "engineer"]):
                    pub_dt = parse_to_utc_datetime(item.get("date", ""))
                    if pub_dt and is_within_24_hours(pub_dt):
                        jobs.append(
                            {
                                "schemaVersion": "1.0",
                                "recordType": "JOB",
                                "source_name": "RemoteOK",
                                "source_url": item.get("url", ""),
                                "company": item.get("company", "Unknown"),
                                "role": position,
                                "role_family": "Engineering",
                                "is_remote": True,
                                "published_date": pub_dt.isoformat(),
                                "collectedAt": NOW.isoformat(),
                            }
                        )
    except Exception as e:
        print(f"RemoteOK API backup error: {e}")

    df = pd.DataFrame(jobs)
    # Deduplicate job entries by role/url
    if not df.empty:
        df = df.drop_duplicates(subset=["source_url"])

    print(f"Total Fresh Jobs Found: {len(df)}")
    return df


def main():
    news_df = scrape_news()
    news_df.to_csv("../output/news.csv", index=False)
    print("Saved to output/news.csv")

    jobs_df = scrape_jobs()
    jobs_df.to_csv("../output/jobs.csv", index=False)
    print("Saved to output/jobs.csv")


if __name__ == "__main__":
    main()