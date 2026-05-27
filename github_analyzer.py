import httpx
from typing import Any
import re

GITHUB_API = "https://api.github.com"


def parse_repo_url(url: str) -> tuple[str, str] | None:
    """Extract owner/repo from a GitHub URL."""
    pattern = r"github\.com[:/]([^/]+)/([^/\s#]+?)(?:\.git)?$"
    m = re.search(pattern, url.rstrip("/"))
    if not m:
        return None
    return m.group(1), m.group(2)


async def fetch_json(client: httpx.AsyncClient, url: str) -> dict[str, Any] | None:
    resp = await client.get(url)
    if resp.status_code == 404:
        return None
    if resp.status_code == 403 and "rate limit" in (resp.text or "").lower():
        raise RuntimeError("GitHub API rate limit exceeded (60 requests/hour). "
                           "Set GITHUB_TOKEN in .env for 5000 requests/hour.")
    resp.raise_for_status()
    return resp.json()


async def analyze_repo(owner: str, repo: str) -> dict[str, Any]:
    """Fetch comprehensive repository data from GitHub API."""
    async with httpx.AsyncClient(
        base_url=GITHUB_API,
        headers={"Accept": "application/vnd.github.v3+json",
                  "User-Agent": "git-exam-analyzer/1.0"},
        timeout=30,
    ) as client:
        # Fetch primary repo info
        repo_data = await fetch_json(client, f"/repos/{owner}/{repo}")
        if repo_data is None:
            raise ValueError(f"Repository {owner}/{repo} not found")

        # Fetch in parallel
        langs, contribs, releases, commits_30d, issues_all, pulls_all = await _fetch_parallel(
            client, owner, repo
        )

    return _build_result(repo_data, langs, contribs, releases,
                         commits_30d, issues_all, pulls_all)


async def _fetch_parallel(
    client: httpx.AsyncClient, owner: str, repo: str
) -> tuple:
    """Fetch subsidiary data in parallel."""
    base = f"/repos/{owner}/{repo}"

    langs_r = await fetch_json(client, f"{base}/languages")
    contribs_r = await fetch_json(client, f"{base}/contributors?per_page=10")
    releases_r = await fetch_json(client, f"{base}/releases?per_page=1")

    # Recent activity — count commits in last 30 days via commits endpoint
    since = _iso_30d_ago()
    commits_r = await fetch_json(client, f"{base}/commits?since={since}&per_page=1")
    # Total issues (open+closed)
    issues_r = await fetch_json(client, f"{base}/issues?state=all&per_page=1")
    pulls_r = await fetch_json(client, f"{base}/pulls?state=all&per_page=1")

    return langs_r, contribs_r, releases_r, commits_r, issues_r, pulls_r


def _iso_30d_ago() -> str:
    from datetime import datetime, timezone, timedelta
    return (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()


def _build_result(
    repo_data: dict,
    langs: dict | None,
    contribs: list | None,
    releases: list | None,
    commits_30d: list | None,
    issues_all: list | None,
    pulls_all: list | None,
) -> dict[str, Any]:
    # Recent commit count via Link header trick isn't great; fall back to
    # pushed_at as a freshness indicator and count what we can from commits
    recent_commit_count = len(commits_30d) if commits_30d else 0

    # Extract link header totals (GitHub returns total count in edge case)
    open_issues_count = repo_data.get("open_issues_count", 0)

    return {
        "name": repo_data.get("full_name"),
        "description": repo_data.get("description") or "",
        "url": repo_data.get("html_url"),
        "stars": repo_data.get("stargazers_count", 0),
        "forks": repo_data.get("forks_count", 0),
        "watchers": repo_data.get("subscribers_count", 0),
        "open_issues": open_issues_count,
        "language": repo_data.get("language") or "",
        "topics": repo_data.get("topics") or [],
        "license": (repo_data.get("license") or {}).get("spdx_id") or "Unknown",
        "created_at": repo_data.get("created_at"),
        "updated_at": repo_data.get("updated_at"),
        "pushed_at": repo_data.get("pushed_at"),
        "size_kb": repo_data.get("size", 0),
        "has_wiki": repo_data.get("has_wiki", False),
        "has_pages": repo_data.get("has_pages", False),
        "has_issues": repo_data.get("has_issues", False),
        "archived": repo_data.get("archived", False),
        "language_distribution": langs or {},
        "contributors_count": len(contribs) if contribs else 0,
        "top_contributors": _top_contributors(contribs or []),
        "latest_release": _latest_release_info(releases or []),
        "recent_commits_30d": recent_commit_count,
        "owner_type": repo_data.get("owner", {}).get("type", "User"),
    }


def _top_contributors(contribs: list) -> list[dict]:
    return [
        {"login": c["login"], "contributions": c["contributions"],
         "avatar": c.get("avatar_url", "")}
        for c in contribs[:5]
    ]


def _latest_release_info(releases: list) -> dict | None:
    if not releases:
        return None
    r = releases[0]
    return {"tag": r.get("tag_name"), "name": r.get("name"),
            "published_at": r.get("published_at")}
