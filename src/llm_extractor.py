"""
Product descriptions ko LLM se structured JSON mein convert karta hai.
Fallback: agar pehla model fail ho (rate limit/error/bad JSON), dusra model try karta hai.
"""

import os
import re
import json
import aiohttp
import asyncio
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()  # .env file se GROQ_API_KEY uthata hai

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Fallback chain: pehla model fail ho to dusra try hoga
MODEL_CHAIN = ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]

VALID_PRICING = {"FREE", "FREEMIUM", "PAID", "ENTERPRISE"}


class LLMRetryError(Exception):
    pass


def build_prompt(description: str) -> str:
    return f"""Classify the pricing model of this AI tool into EXACTLY one of: FREE, FREEMIUM, PAID, ENTERPRISE.
Respond with ONLY a JSON object, nothing else, no explanation, no markdown.
Format: {{"pricingModel": "FREE"}}

Description: "{description}"
"""


def extract_json_object(text: str) -> dict:
    """
    LLM kabhi kabhi JSON ke aage-peeche extra text ya markdown fences bhej deta hai.
    Ye function pehla valid-looking '{...}' block dhund ke nikaal leta hai.
    """
    cleaned = text.strip()
    cleaned = re.sub(r"```json|```", "", cleaned).strip()

    match = re.search(r"\{[^{}]*\}", cleaned)
    if not match:
        raise json.JSONDecodeError("No JSON object found in response", cleaned, 0)

    return json.loads(match.group(0))


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=20),
    retry=retry_if_exception_type(LLMRetryError),
)
async def call_groq(session: aiohttp.ClientSession, prompt: str, model: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 300,
        "reasoning_effort": "low"
    }

    async with session.post(GROQ_URL, headers=headers, json=payload) as resp:
        if resp.status == 429:
            print(f"  [{model}] rate limited, retrying...")
            raise LLMRetryError("429 from Groq")

        if resp.status != 200:
            text = await resp.text()
            print(f"  [{model}] error {resp.status}: {text[:150]}")
            raise LLMRetryError(f"Status {resp.status}")

        data = await resp.json()
        return data["choices"][0]["message"]["content"]


async def extract_pricing_model(session: aiohttp.ClientSession, description: str) -> str:
    """
    Fallback chain: pehle model try karta hai, fail ho (retries ke baad bhi ya bad JSON)
    to agla model try karta hai. Sab fail ho to 'FREEMIUM' default deta hai (safe fallback,
    kabhi crash nahi hota).
    """
    prompt = build_prompt(description[:500])  # 500 chars tak truncate - 413 se bachne ke liye

    for model in MODEL_CHAIN:
        try:
            raw_response = await call_groq(session, prompt, model)
            print(f"  [{model}] raw response: {raw_response[:150]!r}")  # DEBUG line

            parsed = extract_json_object(raw_response)
            pricing = parsed.get("pricingModel", "").upper()

            if pricing in VALID_PRICING:
                return pricing
            else:
                print(f"  [{model}] invalid value '{pricing}', trying next model...")
                continue

        except Exception as e:
            print(f"  [{model}] failed permanently ({e}), trying next model in chain...")
            continue

    return "FREEMIUM"


if __name__ == "__main__":
    async def test():
        async with aiohttp.ClientSession() as session:
            samples = [
                "Free AI writer for creating viral short video scripts and AI content.",
                "Enterprise-grade AI security platform for Fortune 500 companies, custom pricing.",
                "AI chatbot builder, $29/month for pro features, free trial available.",
            ]
            for desc in samples:
                result = await extract_pricing_model(session, desc)
                print(f"'{desc[:50]}...' -> {result}")

    asyncio.run(test())