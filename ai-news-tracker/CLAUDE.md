# AI News Tracker - Project Context

## Overview
AI News Tracker is a full-stack web application that aggregates, summarizes, and organizes AI-related news from multiple sources (arXiv, HuggingFace, AI company blogs, Hacker News, Reddit). It also includes a Research Agent for searching external sources (arXiv, Wikipedia, Tavily, YouTube) using LangChain with Groq LLM.

## Live URL
https://ai-news-tracker-859111833133.us-central1.run.app/

## Tech Stack

### Backend
- **Framework**: FastAPI (async)
- **Database**: SQLite with aiosqlite (async) + FTS5 for full-text search
- **ORM**: SQLAlchemy 2.0
- **AI/LLM**: Groq API with Llama-3.1-8b-instant model
- **Research Agent**: LangChain + LangChain-Groq for multi-source search orchestration
- **HTTP Client**: httpx (async)
- **Parsing**: BeautifulSoup4, feedparser
- **External APIs**: arxiv, wikipedia, tavily-python, google-api-python-client (YouTube)

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Build**: Vite 5
- **Routing**: React Router v6
- **HTTP**: Axios

## Project Structure

```
ai-news-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point (debug logging on imports)
│   │   ├── config.py            # Pydantic settings (env vars)
│   │   ├── database.py          # SQLAlchemy async engine + FTS5 setup
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── article.py       # Article model with to_dict()
│   │   │   └── bookmark.py      # Bookmark model
│   │   ├── routers/             # API route handlers
│   │   │   ├── __init__.py      # Router barrel exports (agents has try/except fallback)
│   │   │   ├── articles.py      # /api/articles routes (with JSON category filtering)
│   │   │   ├── agents.py        # /api/agents routes (research agent)
│   │   │   ├── bookmarks.py     # /api/bookmarks routes
│   │   │   ├── sources.py       # /api/sources routes (refresh fetchers)
│   │   │   └── export.py        # PDF/Markdown export
│   │   ├── services/
│   │   │   ├── summarizer.py    # Groq LLM summarization (lazy init)
│   │   │   ├── research_agent.py # LangChain multi-source search (lazy init)
│   │   │   ├── pdf_generator.py # PDF generation
│   │   │   └── fetchers/        # Source-specific article fetchers
│   │   │       ├── arxiv.py
│   │   │       ├── huggingface.py
│   │   │       ├── blogs.py
│   │   │       └── aggregators.py
│   │   └── utils/
│   │       └── categorizer.py   # Auto-categorization
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.tsx             # React entry point
│   │   ├── App.tsx              # Main router + state (selectedArticle, selectedCategory)
│   │   ├── pages/
│   │   │   ├── Home.tsx         # Main article list with FilterBar
│   │   │   ├── Bookmarks.tsx    # Bookmarked articles
│   │   │   ├── Research.tsx     # Research Agent page (multi-source search with tabs)
│   │   │   └── ArticleDetail.tsx # Article detail modal
│   │   ├── components/
│   │   │   ├── Sidebar.tsx      # Nav: All Articles, Bookmarks, Research Agent
│   │   │   ├── FilterBar.tsx    # Source/Category/Time filters + Refresh button
│   │   │   ├── ArticleCard.tsx  # Individual article display
│   │   │   ├── ArticleList.tsx  # Article list container with pagination
│   │   │   └── Pagination.tsx   # Pagination controls
│   │   ├── hooks/
│   │   │   └── useArticles.ts   # Article state management hook
│   │   └── api/
│   │       └── client.ts        # Axios API wrapper (all endpoints)
│   ├── package.json
│   └── vite.config.ts
├── Dockerfile                    # Multi-stage: node build + python + nginx + supervisor
└── .github/workflows/deploy-gcp.yml  # CI/CD to Cloud Run
```

## API Endpoints

### Articles
- `GET /api/articles` - List articles (filters: source, category, days, bookmarked, limit, offset)
- `GET /api/articles/search?q=` - Full-text search (FTS5)
- `GET /api/articles/{id}` - Get single article
- `POST /api/articles/{id}/summarize` - Generate AI summary (cached)
- `GET /api/articles/categories/list` - List categories with counts

### Bookmarks
- `GET /api/bookmarks` - List bookmarked articles
- `POST /api/bookmarks/{id}` - Add bookmark
- `DELETE /api/bookmarks/{id}` - Remove bookmark

### Sources
- `POST /api/sources/refresh` - Refresh all sources (fetches new articles)
- `POST /api/sources/refresh/{source}` - Refresh specific source

### Research Agents
- `GET /api/agents/search?q=&source=` - Search across multiple sources (arXiv, Wikipedia, Tavily, YouTube). Without source param, AI agent searches all and synthesizes.
- `GET /api/agents/sources` - List available research sources and their status

### Export
- `GET /api/articles/{id}/pdf` - Download as PDF
- `GET /api/articles/{id}/markdown` - Export as Markdown

## Database Models

### Article
- id, source, source_id (unique), title, authors (JSON)
- abstract, content, summary (AI-generated, cached)
- url, pdf_url, categories (JSON)
- published_at, fetched_at, is_bookmarked

### Bookmark
- id, article_id (FK), created_at

## Environment Variables
- `GROQ_API_KEY` - Groq API key for LLM summarization + research agent
- `TAVILY_API_KEY` - Tavily API key for web search in research agent
- `YOUTUBE_API_KEY` - YouTube Data API key for video search
- `DATABASE_URL` - SQLite connection string (default: sqlite+aiosqlite:////app/data/ai_news.db)
- `CORS_ORIGINS` - Allowed CORS origins
- `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` - Reddit API (optional)

## Development Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev  # runs on http://localhost:5173
```

## Deployment

### GCP Cloud Run
- **Project ID**: vast-pad-485307-g8
- **Service**: ai-news-tracker
- **Region**: us-central1
- **URL**: https://ai-news-tracker-859111833133.us-central1.run.app/
- **Container**: Multi-stage Docker (node build -> python:3.11-slim + nginx + supervisor)
- **Architecture**: nginx on port 8080 (Cloud Run PORT), proxies /api to uvicorn on 8000
- **CI/CD**: GitHub Actions on push to master, auto-deploys to Cloud Run
- **GitHub Secrets**: GCP_SA_KEY, GROQ_API_KEY, TAVILY_API_KEY
- **Resources**: 1Gi memory, 1 CPU, 0-3 instances

### Known Issues
- **SQLite is ephemeral on Cloud Run**: Each deployment resets the database. Users must click "Refresh" to populate articles after deploy.
- **Cold starts**: Backend takes a few seconds to initialize on first request after scale-to-zero.

## Key Patterns
- **Lazy initialization**: Services (SummarizerService, ResearchAgentService) use lazy property initialization to avoid blocking imports at startup. This was critical for Cloud Run where import-time blocking caused 502 errors.
- Async/await throughout (FastAPI, SQLAlchemy, httpx)
- FTS5 virtual table with triggers for full-text search
- LLM-based categorization with rule-based fallback
- Article deduplication by source_id and title similarity
- Pagination with 10 items per page
- Research Agent adds AI/ML context to search queries for relevance
- Router imports wrapped in try/except with fallback stubs

## Git Info
- **Repo**: https://github.com/ashwinshetgaonkar/learning-claude-code.git
- **Branch**: master
- **User**: ashwin.shetgaonkar / shetgaonkarash18@gmail.com
