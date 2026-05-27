"""Web app: GitHub repository analyzer with AI scoring and visualization."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path

from github_analyzer import analyze_repo, parse_repo_url
from scorer import score_repo
from visualizer import language_pie, score_radar, score_gauge, dimension_bars

app = FastAPI(title="GitExam — GitHub Repo Analyzer")

INDEX_HTML = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")


class AnalyzeRequest(BaseModel):
    url: str


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(INDEX_HTML)


@app.post("/api/analyze")
async def api_analyze(req: AnalyzeRequest):
    parsed = parse_repo_url(req.url)
    if not parsed:
        raise HTTPException(400, "Invalid GitHub URL. "
                                 "Example: https://github.com/owner/repo")

    owner, repo = parsed

    try:
        data = await analyze_repo(owner, repo)
    except ValueError as e:
        raise HTTPException(404, str(e))

    ai_score = score_repo(data)

    charts = {
        "lang_pie": language_pie(data["language_distribution"]),
        "score_radar": score_radar(ai_score["dimensions"]),
        "score_gauge": score_gauge(ai_score["total"]),
        "dim_bars": dimension_bars(ai_score["dimensions"]),
    }

    return {
        "repo": data,
        "score": ai_score,
        "charts": charts,
    }
