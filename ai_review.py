"""AI-powered repository review using 火山引擎 Ark API."""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

ARK_API_KEY = os.getenv("ARK_API_KEY", "")
ARK_MODEL = os.getenv("ARK_MODEL", "ep-20260527120021-h77hm")
ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

SYSTEM_PROMPT = """You are an expert software engineer reviewing GitHub repositories.
Given repository metadata, write a concise review in Chinese covering:

1. Project Overview (1 sentence — what it does, who it's for)
2. Strengths (2-3 bullet points — what stands out from the data)
3. Weaknesses / Risks (1-2 bullet points — what could be improved)
4. Recommendation (1 sentence — should someone use/contribute/star this?)

Reply in plain text, no markdown headings. Keep the total under 200 characters."""


def _build_user_prompt(data: dict, score: dict) -> str:
    r = data
    return f"""Analyze this GitHub repository:

Name: {r.get('name')}
Description: {r.get('description') or 'None'}
Language: {r.get('language') or 'N/A'}
Topics: {', '.join(r.get('topics', [])) or 'None'}
License: {r.get('license')}
Stars: {r.get('stars')}
Forks: {r.get('forks')}
Open Issues: {r.get('open_issues')}
Contributors (top sample): {len(r.get('top_contributors', []))}
Created: {r.get('created_at')}
Last Push: {r.get('pushed_at')}
Latest Release: {r.get('latest_release')}
Owner Type: {r.get('owner_type')}
Archived: {r.get('archived')}
Score (out of 100): {score.get('total')}
Grade: {score.get('grade')}
Score dimensions: {score.get('dimensions')}"""


async def generate_review(repo_data: dict, score_data: dict) -> str | None:
    """Call Ark API to generate an AI review. Returns None if API key is not set or call fails."""
    if not ARK_API_KEY or ARK_API_KEY == "your-api-key-here":
        return None

    user_prompt = _build_user_prompt(repo_data, score_data)

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(
                f"{ARK_BASE_URL}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {ARK_API_KEY}",
                },
                json={
                    "model": ARK_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                },
            )
            resp.raise_for_status()
            body = resp.json()
            return body["choices"][0]["message"]["content"].strip()
        except Exception:
            return None
