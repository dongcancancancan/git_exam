# GitExam — GitHub Repository Analyzer

输入任意公开 GitHub 仓库 URL，一键分析并可视化 Star 数、Fork 数、语言分布等核心指标，结合 AI 给出项目评分与评价。

## 功能

- **仓库指标采集** — Star / Fork / Watcher / Open Issues / 贡献者 / License / 语言分布
- **AI 智能评分** — 5 维度加权评分（Popularity / Activity / Community / Maturity / Quality），输出 S~E 等级
- **LLM 评价** — 接入火山引擎 Ark API，生成中文项目点评（未配置 Key 时自动跳过）
- **可视化仪表盘** — Plotly 交互图表（语言饼图、评分仪表盘、雷达图、维度条形图）
- **深色主题 UI** — 单页应用，输入 URL 即刻分析

## 快速开始

### 环境要求

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) 包管理器

### 安装与启动

```bash
# 1. 克隆仓库
git clone https://github.com/dongcancancancan/git_exam.git
cd git_exam

# 2. 安装依赖
uv sync

# 3. 配置 API Key（可选，不配则跳过 AI 评价 + 受 GitHub 限速影响）
cp .env.example .env   # 或直接编辑 .env，填入 ARK_API_KEY 和可选的 GITHUB_TOKEN

# 4. 启动服务
uv run uvicorn main:app --host 127.0.0.1 --port 8901
```

浏览器访问 `http://127.0.0.1:8901/`，输入 GitHub 仓库 URL 即可。

### 环境变量（.env）

| 变量 | 必填 | 说明 |
|------|------|------|
| `ARK_API_KEY` | 否 | 火山引擎 Ark API Key，用于 AI 评价 |
| `ARK_MODEL` | 否 | 模型 endpoint，默认已填 |
| `ARK_BASE_URL` | 否 | API 地址，默认已填 |
| `GITHUB_TOKEN` | 否 | GitHub Personal Access Token，可提升限速至 5000 次/小时 |

> 未配置 `ARK_API_KEY` 时，AI 评价功能静默跳过，评分和图表功能不受影响。
> 未配置 `GITHUB_TOKEN` 时，GitHub API 限速为 60 次/小时。

## 项目结构

```
git_exam/
├── main.py               # FastAPI 入口，路由 + API
├── github_analyzer.py    # GitHub API 数据采集
├── scorer.py             # 规则引擎评分（5 维度）
├── ai_review.py          # 火山引擎 Ark LLM 评价
├── visualizer.py         # Plotly 图表生成
├── templates/
│   └── index.html        # 前端单页应用
├── .env                  # 环境变量（不提交 git）
├── pyproject.toml        # 项目配置与依赖
└── uv.lock               # 依赖锁定
```

## API

### POST /api/analyze

```json
// Request
{ "url": "https://github.com/psf/requests" }

// Response
{
  "repo": {
    "name": "psf/requests",
    "stars": 53998,
    "forks": 8892,
    "language_distribution": { "Python": 123456, "HTML": 1234 },
    ...
  },
  "score": {
    "total": 85.0,
    "grade": "A",
    "dimensions": {
      "popularity": { "score": 92.5, "max": 25 },
      ...
    },
    "verdict": "psf/requests is an excellent project..."
  },
  "charts": {
    "lang_pie": "<html>...",
    "score_radar": "<html>...",
    "score_gauge": "<html>...",
    "dim_bars": "<html>..."
  },
  "ai_review": "1. Project Overview: ..."
}
```

## 技术栈

- [FastAPI](https://fastapi.tiangolo.com/) — Web 框架
- [httpx](https://www.python-httpx.org/) — 异步 HTTP 客户端
- [Plotly](https://plotly.com/python/) — 交互式图表
- [Jinja2](https://jinja.palletsprojects.com/) — 模板引擎
- [uv](https://docs.astral.sh/uv/) — Python 包管理
