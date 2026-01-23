# AI News Tracker - Product Requirements Document

## Overview
A personal web application to aggregate, summarize, and organize AI news from multiple sources with easy access to original papers and articles.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+ with FastAPI |
| Frontend | React 18 + TypeScript + Vite |
| Database | SQLite with SQLAlchemy ORM |
| Styling | Tailwind CSS |
| LLM | Claude API (Anthropic) |
| PDF Generation | WeasyPrint or pdfkit |
| Deployment | Local/Self-hosted |

---

## Data Sources & Integration

### 1. arXiv Papers
- **API**: arXiv API (REST)
- **Categories**: cs.AI, cs.LG, cs.CL, cs.CV, cs.NE
- **Data**: Title, authors, abstract, PDF link, categories, published date

### 2. HuggingFace
- **API**: HuggingFace Hub API + RSS feeds
- **Content**: New model releases, papers, blog posts
- **Data**: Title, description, link, tags, date

### 3. AI Company Blogs
- **Sources**: OpenAI, Anthropic, Google DeepMind, Meta AI
- **Method**: RSS feeds + web scraping (BeautifulSoup)
- **Data**: Title, excerpt, full content, link, date

### 4. News Aggregators
- **Sources**: Hacker News (AI tagged), Reddit r/MachineLearning
- **API**: HN Algolia API, Reddit JSON API
- **Data**: Title, score, comments, link, date

---

## Core Features

### 1. Article Aggregation
- Fetch articles from all sources on-demand (manual refresh)
- Deduplicate articles across sources
- Store metadata and content in SQLite

### 2. AI Summarization
- Generate concise summaries using Claude API
- Summary fields: key findings, methodology, implications
- Cache summaries to avoid redundant API calls

### 3. Category Filtering
- Auto-categorize by domain: NLP, Computer Vision, RL, Generative AI, etc.
- Filter by source (arXiv, HuggingFace, Blogs, etc.)
- Filter by date range

### 4. Search
- Full-text search across titles, abstracts, summaries
- SQLite FTS5 for fast search

### 5. Bookmarks
- Save articles for later reading
- Bookmark list view with quick access

### 6. Download & Export
- Download original PDF (arXiv papers)
- Convert web articles to PDF for download
- Export summaries as Markdown
- Share links functionality

---

## Project Structure

```
ai-news-tracker/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings & env vars
│   │   ├── database.py          # SQLite + SQLAlchemy setup
│   │   ├── models/
│   │   │   ├── article.py       # Article SQLAlchemy model
│   │   │   └── bookmark.py      # Bookmark model
│   │   ├── routers/
│   │   │   ├── articles.py      # Article CRUD endpoints
│   │   │   ├── sources.py       # Source refresh endpoints
│   │   │   ├── bookmarks.py     # Bookmark endpoints
│   │   │   └── export.py        # PDF/Markdown export
│   │   ├── services/
│   │   │   ├── summarizer.py    # Claude API integration
│   │   │   ├── pdf_generator.py # Article to PDF
│   │   │   └── fetchers/
│   │   │       ├── arxiv.py
│   │   │       ├── huggingface.py
│   │   │       ├── blogs.py
│   │   │       └── aggregators.py
│   │   └── utils/
│   │       └── categorizer.py   # Auto-categorization
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ArticleCard.tsx
│   │   │   ├── ArticleList.tsx
│   │   │   ├── FilterBar.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Bookmarks.tsx
│   │   │   └── ArticleDetail.tsx
│   │   ├── hooks/
│   │   │   └── useArticles.ts
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── README.md
└── docker-compose.yml (optional)
```

---

## Database Schema

```sql
-- Articles table
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,           -- 'arxiv', 'huggingface', 'blog', 'aggregator'
    source_id TEXT UNIQUE,          -- Original ID from source
    title TEXT NOT NULL,
    authors TEXT,                   -- JSON array
    abstract TEXT,
    content TEXT,                   -- Full content if available
    summary TEXT,                   -- AI-generated summary
    url TEXT NOT NULL,
    pdf_url TEXT,                   -- Direct PDF link if available
    categories TEXT,                -- JSON array: ['NLP', 'LLM']
    published_at DATETIME,
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_bookmarked BOOLEAN DEFAULT FALSE
);

-- Full-text search
CREATE VIRTUAL TABLE articles_fts USING fts5(
    title, abstract, summary, content,
    content='articles'
);

-- Bookmarks (alternative approach if needed)
CREATE TABLE bookmarks (
    id INTEGER PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/articles` | List articles with filters |
| GET | `/api/articles/{id}` | Get article details |
| POST | `/api/articles/{id}/summarize` | Generate AI summary |
| POST | `/api/sources/refresh` | Fetch new articles |
| POST | `/api/sources/refresh/{source}` | Refresh specific source |
| GET | `/api/bookmarks` | List bookmarked articles |
| POST | `/api/bookmarks/{article_id}` | Add bookmark |
| DELETE | `/api/bookmarks/{article_id}` | Remove bookmark |
| GET | `/api/articles/{id}/pdf` | Download as PDF |
| GET | `/api/articles/{id}/markdown` | Export as Markdown |
| GET | `/api/search?q={query}` | Full-text search |

---

## UI Wireframe (Clean Minimal)

```
┌─────────────────────────────────────────────────────────────┐
│  AI News Tracker                    [Search...]  [Refresh]  │
├─────────────────────────────────────────────────────────────┤
│ Filters: [All Sources ▼] [All Categories ▼] [This Week ▼]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📄 Attention Is All You Need (v2)                   │   │
│  │ arXiv • NLP • 2 hours ago                           │   │
│  │ ────────────────────────────────────────────────    │   │
│  │ Summary: Introduces transformer architecture...      │   │
│  │                                                      │   │
│  │ [Read More] [Bookmark] [Download PDF] [Share]       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📰 Claude 3.5 Sonnet Released                       │   │
│  │ Anthropic Blog • Generative AI • 1 day ago          │   │
│  │ ────────────────────────────────────────────────    │   │
│  │ Summary: New model with improved reasoning...        │   │
│  │                                                      │   │
│  │ [Read More] [Bookmark] [Save as PDF] [Share]        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Project Setup & Core Backend
1. Initialize FastAPI project structure
2. Set up SQLite database with SQLAlchemy
3. Create Article model and migrations
4. Implement arXiv fetcher (primary source)
5. Basic CRUD API endpoints

### Phase 2: Additional Sources
1. Implement HuggingFace fetcher
2. Implement blog scrapers (OpenAI, Anthropic, DeepMind, Meta)
3. Implement HN and Reddit fetchers
4. Add deduplication logic

### Phase 3: AI Summarization
1. Claude API integration
2. Summarization service with caching
3. Auto-categorization using LLM

### Phase 4: Frontend
1. Set up React + Vite + TypeScript
2. Implement article list with filtering
3. Search functionality
4. Article detail view
5. Bookmark management

### Phase 5: Export Features
1. PDF generation for web articles
2. arXiv PDF proxy/download
3. Markdown export
4. Share link generation

### Phase 6: Polish & Deploy
1. Error handling and loading states
2. Responsive design
3. Local deployment setup
4. Documentation

---

## Environment Variables

```env
# Backend (.env)
ANTHROPIC_API_KEY=your_claude_api_key
DATABASE_URL=sqlite:///./ai_news.db
CORS_ORIGINS=http://localhost:5173

# Optional
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
```

---

## Verification Plan

1. **Backend Tests**:
   - Test each fetcher independently
   - Verify API endpoints with curl/httpie
   - Test summarization with sample articles

2. **Frontend Tests**:
   - Verify article list renders correctly
   - Test filtering and search
   - Test bookmark add/remove
   - Test PDF download

3. **Integration**:
   - Run full refresh cycle
   - Verify articles appear in UI
   - Test end-to-end summarization flow

---

## Key Files to Create

1. `backend/app/main.py` - FastAPI application entry point
2. `backend/app/models/article.py` - SQLAlchemy Article model
3. `backend/app/services/fetchers/arxiv.py` - arXiv API integration
4. `backend/app/services/summarizer.py` - Claude API summarization
5. `frontend/src/App.tsx` - Main React application
6. `frontend/src/components/ArticleCard.tsx` - Article display component
