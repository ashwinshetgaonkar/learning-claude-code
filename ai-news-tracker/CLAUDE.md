# AI News Tracker - Project Context

## Overview
AI News Tracker is a full-stack web application that aggregates, summarizes, and organizes AI-related news from multiple sources (arXiv, HuggingFace, AI company blogs, Hacker News, Reddit).

## Tech Stack

### Backend
- **Framework**: FastAPI (async)
- **Database**: SQLite with aiosqlite (async) + FTS5 for full-text search
- **ORM**: SQLAlchemy 2.0
- **AI**: Groq API with Llama-3.1-8b-instant model
- **HTTP Client**: httpx (async)
- **Parsing**: BeautifulSoup4, feedparser

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
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # SQLAlchemy async setup
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── article.py       # Article model
│   │   │   └── bookmark.py      # Bookmark model
│   │   ├── routers/             # API route handlers
│   │   │   ├── articles.py      # /api/articles routes
│   │   │   ├── bookmarks.py     # /api/bookmarks routes
│   │   │   ├── sources.py       # /api/sources routes
│   │   │   └── export.py        # PDF/Markdown export
│   │   ├── services/            # Business logic
│   │   │   ├── summarizer.py    # Groq LLM summarization
│   │   │   ├── pdf_generator.py # PDF generation
│   │   │   └── fetchers/        # Source-specific fetchers
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
│   │   ├── App.tsx              # Main router component
│   │   ├── pages/
│   │   │   ├── Home.tsx         # Main article list
│   │   │   ├── Bookmarks.tsx    # Bookmarked articles
│   │   │   └── ArticleDetail.tsx # Article modal
│   │   ├── components/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── FilterBar.tsx
│   │   │   ├── ArticleCard.tsx
│   │   │   ├── ArticleList.tsx
│   │   │   └── Pagination.tsx
│   │   ├── hooks/
│   │   │   └── useArticles.ts   # Article state management
│   │   └── api/
│   │       └── client.ts        # Axios API wrapper
│   ├── package.json
│   └── vite.config.ts
└── Dockerfile                    # Combined container for Cloud Run
```

## API Endpoints

### Articles
- `GET /api/articles` - List articles (filters: source, category, days, bookmarked, limit, offset)
- `GET /api/articles/search?q=` - Full-text search
- `GET /api/articles/{id}` - Get single article
- `POST /api/articles/{id}/summarize` - Generate AI summary
- `GET /api/articles/categories/list` - List categories with counts

### Bookmarks
- `GET /api/bookmarks` - List bookmarked articles
- `POST /api/bookmarks/{id}` - Add bookmark
- `DELETE /api/bookmarks/{id}` - Remove bookmark

### Sources
- `POST /api/sources/refresh` - Refresh all sources
- `POST /api/sources/refresh/{source}` - Refresh specific source

### Research Agents
- `GET /api/agents/search` - Search across multiple research sources (arXiv, Wikipedia, Tavily)
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
- `GROQ_API_KEY` - Groq API key for LLM summarization
- `DATABASE_URL` - SQLite connection string
- `CORS_ORIGINS` - Allowed CORS origins

## Development Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Deployment
- Deployed to GCP Cloud Run
- Combined Dockerfile with nginx + supervisor
- GitHub Actions CI/CD pipeline

## Key Patterns
- Async/await throughout (FastAPI, SQLAlchemy, httpx)
- FTS5 virtual table with triggers for full-text search
- LLM-based categorization with rule-based fallback
- Article deduplication by source_id and title similarity
- Pagination with 10 items per page
