"""
Resolve startup/product names to canonical (standard) names.
Example: "Open AI", "OpenAI Inc" -> "OpenAI"
"""

import re
import pandas as pd
from rapidfuzz import process, fuzz

# Seed list: 50 known AI startups canonical names
CANONICAL_STARTUPS = [
    "OpenAI", "Anthropic", "Google DeepMind", "Meta AI", "Microsoft AI",
    "Cohere", "Mistral AI", "Stability AI", "Hugging Face", "Scale AI",
    "Perplexity AI", "Runway", "Midjourney", "Character.AI", "Inflection AI",
    "Adept AI", "AI21 Labs", "Together AI", "Databricks", "Snowflake",
    "Nvidia", "IBM Watson", "Amazon AWS AI", "Salesforce AI", "Adobe AI",
    "xAI", "DeepL", "ElevenLabs", "Synthesia", "Jasper AI",
    "Copy.ai", "Writesonic", "Grammarly", "Notion AI", "Replit",
    "GitHub Copilot", "Cursor", "Vercel", "LangChain", "Pinecone",
    "Weights & Biases", "Palantir", "C3 AI", "UiPath", "Automation Anywhere",
    "Glean", "Harvey AI", "Sierra", "Speak", "Suno AI",
]

# Strict Threshold: Score must be 90+ to avoid false positives
MATCH_THRESHOLD = 92.0


def clean_name(name: str) -> str:
    """Removes suffixes and special characters for a fair base comparison."""
    if not name or pd.isna(name):
        return ""
    name = str(name).lower()
    # Strip common corporate/tech suffixes
    # name = re.sub(r'\b(inc|corp|corporation|llc|ltd|labs|ai|io|app)\b', '', name)
    name = re.sub(r'\b(inc|corp|corporation|llc|ltd)\b', '', name)
    # Remove special symbols and extra spaces
    name = re.sub(r'[^a-z0-9]', '', name)
    return name.strip()


def resolve_name(raw_name: str) -> tuple[str, float]:
    """
    Takes a raw name and finds the best match in the seed list.
    Return: (canonical_name or original_name, score)
    """
    if not raw_name or pd.isna(raw_name):
        return raw_name, 0.0

    raw_cleaned = clean_name(raw_name)
    if not raw_cleaned:
        return raw_name, 0.0

    best_match = None
    best_score = 0.0

    # Comparison between cleaned base names
    for canonical in CANONICAL_STARTUPS:
        canonical_cleaned = clean_name(canonical)

        # 1. Exact cleaned match (e.g., "writesonic" == "writesonic")
        if raw_cleaned == canonical_cleaned:
            return canonical, 100.0

        # 2. Calculate Token Set Ratio score (performs better than WRatio)
        # score = fuzz.token_set_ratio(raw_name.lower(), canonical.lower())
        score = fuzz.ratio(raw_cleaned, canonical_cleaned)

        if score > best_score:
            best_score = score
            best_match = canonical

    # Verification threshold check
    if best_score >= MATCH_THRESHOLD and best_match:
        return best_match, best_score
    else:
        return raw_name, best_score


def build_mapping_log(names: list[str]) -> pd.DataFrame:
    """Creates a mapping row for each unique name."""
    rows = []
    seen = set()

    for raw_name in names:
        if raw_name in seen or pd.isna(raw_name):
            continue
        seen.add(raw_name)

        canonical, score = resolve_name(raw_name)
        rows.append({
            "raw_name": raw_name,
            "canonical_name": canonical,
            "match_score": round(score, 1),
            "was_matched": score >= MATCH_THRESHOLD,
        })

    return pd.DataFrame(rows)


def main():
    startups_df = pd.read_csv("../output/startups.csv")
    products_df = pd.read_csv("../output/products.csv")

    all_names = list(startups_df["entityName"]) + list(products_df["startupName"])

    print(f"Total names to resolve: {len(all_names)}")
    mapping_log = build_mapping_log(all_names)

    matched_count = mapping_log["was_matched"].sum()
    print(f"Matched to canonical names: {matched_count}")
    print(f"Unmatched (kept as-is, likely new/unique companies): {len(mapping_log) - matched_count}")

    mapping_log.to_csv("../output/entity_mapping_log.csv", index=False)
    print(f"\nSaved to output/entity_mapping_log.csv ({len(mapping_log)} rows)")

    print("\nSample matches:")
    print(mapping_log[mapping_log["was_matched"]].head(10))


if __name__ == "__main__":
    main()