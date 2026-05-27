"""AI-powered repository scoring based on multi-dimensional analysis."""

from datetime import datetime, timezone, timedelta


def score_repo(data: dict) -> dict:
    """Score a repository across 5 dimensions, return total score and breakdown."""

    dims = {
        "popularity": _score_popularity(data),
        "activity": _score_activity(data),
        "community": _score_community(data),
        "maturity": _score_maturity(data),
        "quality": _score_quality(data),
    }

    weights = {
        "popularity": 25,
        "activity": 20,
        "community": 20,
        "maturity": 15,
        "quality": 20,
    }

    total = sum(dims[k] * weights[k] / 100 for k in dims)
    total = round(total, 1)

    return {
        "total": total,
        "grade": _letter_grade(total),
        "dimensions": {k: {"score": round(v, 1), "max": weights[k],
                            "label": _dim_label(k)}
                       for k, v in dims.items()},
        "verdict": _verdict(total, data.get("name", "")),
    }


def _score_popularity(data: dict) -> float:
    """Score based on stars and forks (log-scale)."""
    import math
    stars = data.get("stars", 0)
    forks = data.get("forks", 0)

    # Log-scale: 100k stars → 100, 10k → 85, 1k → 65, 100 → 45, 10 → 25
    star_score = min(100, max(0, math.log2(stars + 1) * 7.5))
    fork_score = min(100, max(0, math.log2(forks + 1) * 8))

    return star_score * 0.6 + fork_score * 0.4


def _score_activity(data: dict) -> float:
    """Score based on recency of updates and release presence."""
    pushed = _parse_date(data.get("pushed_at"))
    updated = _parse_date(data.get("updated_at"))

    if not pushed:
        return 30

    days_since_push = (_now() - pushed).days
    # <7d → 100, <30d → 80, <90d → 60, <365d → 30, else 10
    if days_since_push < 7:
        push_score = 100
    elif days_since_push < 30:
        push_score = 85
    elif days_since_push < 90:
        push_score = 60
    elif days_since_push < 365:
        push_score = 30
    else:
        push_score = 10

    # Bonus for releases
    release_bonus = 20 if data.get("latest_release") else 0

    return min(100, push_score * 0.8 + release_bonus)


def _score_community(data: dict) -> float:
    """Score based on contributors and issue health."""
    contribs = data.get("contributors_count", 0)
    open_issues = data.get("open_issues", 0)
    stars = data.get("stars", 1)

    # Contributor diversity
    if contribs >= 50:
        c_score = 100
    elif contribs >= 20:
        c_score = 80
    elif contribs >= 10:
        c_score = 65
    elif contribs >= 5:
        c_score = 45
    elif contribs >= 1:
        c_score = 25
    else:
        c_score = 5

    # Issue health: lower ratio = healthier
    issue_ratio = open_issues / max(stars, 1)
    if issue_ratio < 0.01:
        i_score = 100
    elif issue_ratio < 0.05:
        i_score = 80
    elif issue_ratio < 0.1:
        i_score = 60
    elif issue_ratio < 0.3:
        i_score = 35
    else:
        i_score = 10

    return c_score * 0.5 + i_score * 0.5


def _score_maturity(data: dict) -> float:
    """Score based on repo age, license, and release history."""
    created = _parse_date(data.get("created_at"))
    if not created:
        return 40

    age_days = (_now() - created).days
    # 3+ years → 100, 1-3y → 70, 6m-1y → 45, <6m → 20
    if age_days > 1095:
        age_score = 100
    elif age_days > 365:
        age_score = 70
    elif age_days > 180:
        age_score = 45
    else:
        age_score = 20

    # License
    lic = data.get("license", "Unknown")
    lic_score = 100 if lic != "Unknown" else 20

    has_release = 30 if data.get("latest_release") else 0

    return age_score * 0.4 + lic_score * 0.4 + has_release * 0.2


def _score_quality(data: dict) -> float:
    """Score based on documentation signals and project setup."""
    score = 0.0

    desc = data.get("description", "")
    if len(desc) > 100:
        score += 25
    elif len(desc) > 30:
        score += 15
    elif desc:
        score += 5

    topics = data.get("topics", [])
    if len(topics) >= 10:
        score += 20
    elif len(topics) >= 5:
        score += 15
    elif topics:
        score += 8

    if data.get("has_wiki"):
        score += 15
    if data.get("has_pages"):
        score += 15

    langs = data.get("language_distribution", {})
    if len(langs) >= 3:
        score += 15
    elif len(langs) >= 2:
        score += 10
    elif langs:
        score += 5

    # Bonus: good ratio of stars to size
    size_kb = max(data.get("size_kb", 1), 1)
    stars = data.get("stars", 0)
    if stars / max(size_kb, 1) > 1:
        score += 10

    return min(100, score)


def _letter_grade(score: float) -> str:
    if score >= 90:
        return "S"
    elif score >= 80:
        return "A"
    elif score >= 65:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 35:
        return "D"
    return "E"


def _dim_label(key: str) -> str:
    return {
        "popularity": "Popularity (Stars & Forks)",
        "activity": "Activity (Updates & Releases)",
        "community": "Community (Contributors & Issues)",
        "maturity": "Maturity (Age & License)",
        "quality": "Quality (Docs & Setup)",
    }.get(key, key)


def _verdict(score: float, name: str) -> str:
    if score >= 90:
        return f"{name} is an outstanding project — highly popular, well-maintained, and mature."
    elif score >= 80:
        return f"{name} is an excellent project with strong community and activity."
    elif score >= 65:
        return f"{name} is a solid project worth exploring."
    elif score >= 50:
        return f"{name} shows promise but could improve in some areas."
    elif score >= 35:
        return f"{name} is in early stages or has limited activity."
    return f"{name} appears to be inactive or minimal."


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_date(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    except (ValueError, TypeError):
        return None
