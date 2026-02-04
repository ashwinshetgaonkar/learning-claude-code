# AI News Tracker

A personal web application to aggregate, summarize, and organize AI news from multiple sources with easy access to original papers and articles. Includes an AI-powered Research Agent for searching across academic papers, Wikipedia, web, and YouTube.

## Features

- **Article Aggregation**: Fetch articles from arXiv, HuggingFace, AI company blogs (OpenAI, Anthropic, DeepMind, Meta), Hacker News, and Reddit r/MachineLearning
- **AI Summarization**: Generate concise summaries using Groq LLM (Llama 3.1)
- **Research Agent**: AI-powered research assistant that searches multiple sources:
  - **arXiv**: Academic papers and preprints
  - **Wikipedia**: General knowledge articles
  - **Tavily**: Web search with AI-generated answers
  - **YouTube**: Educational videos and tutorials (AI/ML focused)
- **Category Filtering**: Filter by domain (NLP, Computer Vision, ML, etc.) and source
- **Full-Text Search**: SQLite FTS5 powered search across titles, abstracts, and summaries
- **Bookmarks**: Save articles for later reading
- **Export**: Download PDFs and export as Markdown

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React 18 + TypeScript + Vite
- **Database**: SQLite with SQLAlchemy ORM
- **Styling**: Tailwind CSS
- **LLM**: Groq API (Llama 3.1-8b-instant)
- **Research Tools**: LangChain, arXiv API, Wikipedia API, Tavily API, YouTube Data API v3
- **PDF Generation**: WeasyPrint

## Project Structure

```
ai-news-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings & env vars
│   │   ├── database.py          # SQLite + SQLAlchemy setup
│   │   ├── models/              # SQLAlchemy models
│   │   ├── routers/             # API endpoints
│   │   │   ├── articles.py      # Article CRUD
│   │   │   ├── bookmarks.py     # Bookmark management
│   │   │   ├── sources.py       # Source refresh
│   │   │   ├── agents.py        # Research Agent API
│   │   │   └── export.py        # PDF/Markdown export
│   │   ├── services/            # Business logic
│   │   │   ├── summarizer.py    # Groq LLM summarization
│   │   │   ├── research_agent.py # Research Agent service
│   │   │   └── fetchers/        # Data source fetchers
│   │   └── utils/               # Utilities
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   │   ├── Home.tsx         # Article list
│   │   │   ├── Bookmarks.tsx    # Saved articles
│   │   │   └── Research.tsx     # Research Agent UI
│   │   ├── hooks/               # Custom hooks
│   │   └── api/                 # API client
│   ├── package.json
│   └── vite.config.ts
├── Dockerfile                   # Combined container for Cloud Run
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd ai-news-tracker/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   YOUTUBE_API_KEY=your_youtube_api_key_here
   DATABASE_URL=sqlite+aiosqlite:///./ai_news.db
   CORS_ORIGINS=http://localhost:5173
   ```

5. Run the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

The API will be available at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ai-news-tracker/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`.

## Usage

### Article Management
1. **Refresh Articles**: Click the "Refresh" button to fetch new articles from all sources
2. **Filter**: Use the dropdown filters to narrow down by source, category, or date range
3. **Search**: Use the search bar to find articles by keywords
4. **Summarize**: Click "Summarize" on any article to generate an AI summary
5. **Bookmark**: Save interesting articles for later
6. **Export**: Download articles as PDF or Markdown

### Research Agent
1. Navigate to the **Research** page
2. Enter a research query (e.g., "transformer architecture", "neural networks")
3. Select a specific source or use "AI Agent (All)" for comprehensive search
4. View results organized by source with tab navigation
5. Click on tabs (arXiv, Wikipedia, Tavily, YouTube) to filter results

## API Endpoints

### Articles
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/articles` | List articles with filters |
| GET | `/api/articles/{id}` | Get article details |
| GET | `/api/articles/search?q=` | Full-text search |
| POST | `/api/articles/{id}/summarize` | Generate AI summary |

### Sources
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sources/refresh` | Fetch new articles |
| POST | `/api/sources/refresh/{source}` | Refresh specific source |

### Bookmarks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bookmarks` | List bookmarked articles |
| POST | `/api/bookmarks/{id}` | Add bookmark |
| DELETE | `/api/bookmarks/{id}` | Remove bookmark |

### Research Agent
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/agents/search?q=` | Search across all sources |
| GET | `/api/agents/search?q=&source=` | Search specific source (arxiv, wikipedia, tavily, youtube) |
| GET | `/api/agents/sources` | List available sources and their status |

### Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/articles/{id}/pdf` | Download as PDF |
| GET | `/api/articles/{id}/markdown` | Export as Markdown |

## Data Sources

### News Aggregation
- **arXiv**: AI/ML papers from cs.AI, cs.LG, cs.CL, cs.CV, cs.NE categories
- **HuggingFace**: Blog posts and daily papers
- **AI Blogs**: OpenAI, Anthropic, Google DeepMind, Meta AI
- **Aggregators**: Hacker News AI stories, Reddit r/MachineLearning

### Research Agent Sources
- **arXiv**: Academic papers and preprints (no API key required)
- **Wikipedia**: General knowledge articles (no API key required)
- **Tavily**: Web search with AI answers (requires TAVILY_API_KEY)
- **YouTube**: Educational videos focused on AI/ML (requires YOUTUBE_API_KEY)

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM summarization | Yes (for AI features) |
| `TAVILY_API_KEY` | Tavily API key for web search | No (Research Agent feature) |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | No (Research Agent feature) |
| `DATABASE_URL` | SQLite database URL | No (defaults to `sqlite+aiosqlite:///./ai_news.db`) |
| `CORS_ORIGINS` | Allowed CORS origins | No (defaults to `http://localhost:5173`) |
| `REDDIT_CLIENT_ID` | Reddit API client ID | No |
| `REDDIT_CLIENT_SECRET` | Reddit API client secret | No |

## Getting API Keys

### Groq API Key
1. Sign up at https://console.groq.com/
2. Create an API key in the dashboard

### Tavily API Key
1. Sign up at https://tavily.com/
2. Get your API key from the dashboard

### YouTube API Key
1. Go to https://console.cloud.google.com/
2. Create or select a project
3. Enable "YouTube Data API v3"
4. Go to Credentials → Create Credentials → API Key
5. (Optional) Restrict key to YouTube Data API v3 only

## Deployment

The application is configured for deployment on GCP Cloud Run using GitHub Actions.

1. Set up secrets in your GitHub repository:
   - `GCP_SA_KEY`: GCP service account JSON key
   - `GROQ_API_KEY`: Groq API key
   - `TAVILY_API_KEY`: Tavily API key
   - `YOUTUBE_API_KEY`: YouTube API key

2. Push to master branch to trigger automatic deployment

## License

MIT
