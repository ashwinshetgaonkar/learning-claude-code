# AI News Tracker

A personal web application to aggregate, summarize, and organize AI news from multiple sources with easy access to original papers and articles.

## Features

- **Article Aggregation**: Fetch articles from arXiv, HuggingFace, AI company blogs (OpenAI, Anthropic, DeepMind, Meta), Hacker News, and Reddit r/MachineLearning
- **AI Summarization**: Generate concise summaries using Claude API
- **Category Filtering**: Filter by domain (NLP, Computer Vision, ML, etc.) and source
- **Full-Text Search**: SQLite FTS5 powered search across titles, abstracts, and summaries
- **Bookmarks**: Save articles for later reading
- **Export**: Download PDFs and export as Markdown

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React 18 + TypeScript + Vite
- **Database**: SQLite with SQLAlchemy ORM
- **Styling**: Tailwind CSS
- **LLM**: Claude API (Anthropic)
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
│   │   ├── services/            # Business logic
│   │   │   └── fetchers/        # Data source fetchers
│   │   └── utils/               # Utilities
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom hooks
│   │   └── api/                 # API client
│   ├── package.json
│   └── vite.config.ts
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

4. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` and add your Anthropic API key:
   ```env
   ANTHROPIC_API_KEY=your_claude_api_key_here
   ```

6. Run the backend server:
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

1. **Refresh Articles**: Click the "Refresh" button to fetch new articles from all sources
2. **Filter**: Use the dropdown filters to narrow down by source, category, or date range
3. **Search**: Use the search bar to find articles by keywords
4. **Summarize**: Click "Summarize" on any article to generate an AI summary (requires Anthropic API key)
5. **Bookmark**: Save interesting articles for later
6. **Export**: Download articles as PDF or Markdown

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/articles` | List articles with filters |
| GET | `/api/articles/{id}` | Get article details |
| GET | `/api/articles/search?q=` | Full-text search |
| POST | `/api/articles/{id}/summarize` | Generate AI summary |
| POST | `/api/sources/refresh` | Fetch new articles |
| POST | `/api/sources/refresh/{source}` | Refresh specific source |
| GET | `/api/bookmarks` | List bookmarked articles |
| POST | `/api/bookmarks/{id}` | Add bookmark |
| DELETE | `/api/bookmarks/{id}` | Remove bookmark |
| GET | `/api/articles/{id}/pdf` | Download as PDF |
| GET | `/api/articles/{id}/markdown` | Export as Markdown |

## Data Sources

- **arXiv**: AI/ML papers from cs.AI, cs.LG, cs.CL, cs.CV, cs.NE categories
- **HuggingFace**: Blog posts and daily papers
- **AI Blogs**: OpenAI, Anthropic, Google DeepMind, Meta AI
- **Aggregators**: Hacker News AI stories, Reddit r/MachineLearning

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key for summarization | Yes (for AI features) |
| `DATABASE_URL` | SQLite database URL | No (defaults to `sqlite+aiosqlite:///./ai_news.db`) |
| `CORS_ORIGINS` | Allowed CORS origins | No (defaults to `http://localhost:5173`) |
| `REDDIT_CLIENT_ID` | Reddit API client ID | No |
| `REDDIT_CLIENT_SECRET` | Reddit API client secret | No |

## License

MIT
