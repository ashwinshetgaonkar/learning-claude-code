# Backend Architecture Refactor - Design Document

**Date:** 2026-02-12
**Status:** Approved

## Goal

Refactor 4 backend concerns to improve code organization, performance, and maintainability without changing the API surface.

## Scope

| Item | Problem | Approach |
|------|---------|----------|
| Research agent | 852-line monolith with 9 tools | Split into package with tools/ directory |
| Pagination | Loads all articles into memory | DB-level filtering with SQLite JSON1 |
| Error handling | Inconsistent (HTTPException vs error objects, prints) | HTTPException everywhere + logging |
| Fetcher coupling | Hardcoded if-elif chain per source | Dict-based registry pattern |

**Out of scope:** Frontend changes, new features, database schema changes, API contract changes.

---

## 1. Research Agent Modularization

### Current State

`backend/app/services/research_agent.py` is 852 lines containing:
- 9 search tool functions (arxiv, wikipedia, tavily, youtube, semantic_scholar, huggingface, github, papers_with_code, anthropic)
- Tool JSON schemas
- Agentic loop / LLM orchestration
- Query enhancement logic

### Proposed Structure

```
backend/app/services/research_agent/
├── __init__.py          # Exports ResearchAgentService (public API unchanged)
├── agent.py             # Core agentic loop + LLM orchestration (~150 lines)
├── schemas.py           # Tool schema definitions (~80 lines)
└── tools/
    ├── __init__.py      # Registry: TOOL_MAP = {"search_arxiv": search_arxiv, ...}
    ├── arxiv.py         # search_arxiv()
    ├── wikipedia.py     # search_wikipedia()
    ├── tavily.py        # search_tavily()
    ├── youtube.py       # search_youtube()
    ├── semantic_scholar.py
    ├── huggingface.py
    ├── github.py
    ├── papers_with_code.py
    └── anthropic.py
```

### Key Decisions

- Each tool file exports one async function with the same signature it has today
- `tools/__init__.py` builds a `TOOL_MAP` dict so the agent loop can dispatch by name
- `schemas.py` keeps all tool JSON schemas together (they're small and related)
- `agent.py` contains `ResearchAgentService` class with the agentic loop
- `__init__.py` re-exports so external imports (`from services.research_agent import ResearchAgentService`) still work
- No behavior changes - pure file reorganization

---

## 2. Pagination Fix in articles.py

### Current State (Broken)

```python
result = await db.execute(query)
all_articles = result.scalars().all()  # loads EVERYTHING into memory
if category:
    all_articles = [a for a in all_articles if has_category(a, category)]
total = len(all_articles)
paginated = all_articles[offset:offset + limit]
```

Problems:
- Every request loads the entire articles table into memory
- Category filtering is O(n) in Python
- Total count breaks when filtering reduces results
- Won't scale past a few thousand articles

### Proposed Fix

```python
# Build query with all filters applied at DB level
if category:
    query = query.filter(
        text("EXISTS (SELECT 1 FROM json_each(categories) WHERE json_each.value = :cat)")
    ).params(cat=category)

# Count total BEFORE applying limit/offset
count_query = select(func.count()).select_from(query.subquery())
total = (await db.execute(count_query)).scalar()

# Apply pagination at DB level
query = query.offset(offset).limit(limit)
result = await db.execute(query)
articles = result.scalars().all()
```

Benefits:
- Database does the filtering (indexed, efficient)
- Only fetches the page worth of rows
- Total count is accurate for the filtered set
- Scales to thousands of articles

---

## 3. Standardized Error Handling

### Current State

- Some routes throw `HTTPException` (articles.py)
- Others return `{"error": "..."}` with 200 status (research_agent.py)
- Print statements to stderr instead of logging (main.py, services)
- No global exception handler for unhandled errors

### Proposed Approach

1. **Use `HTTPException` everywhere** - no more returning error objects with 200 status. If something fails, raise an appropriate HTTP status code.

2. **Add a global exception handler** in `main.py`:
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

3. **Replace `print(..., file=sys.stderr)` with Python's `logging` module** across all backend files. Configure a logger in `main.py`.

4. **Keep it simple** - no custom exception classes. Just consistent use of `HTTPException` with clear `detail` messages and proper status codes (400 for bad input, 404 for not found, 500 for server errors).

---

## 4. Fetcher Registry Pattern

### Current State

`sources.py` has a hardcoded if-elif chain:
```python
if source == "arxiv":
    fetcher = ArxivFetcher()
elif source == "huggingface":
    fetcher = HuggingFaceFetcher()
elif source == "blogs":
    fetcher = BlogFetcher()
# ... repeats for each source
```

Adding a new source requires modifying router code.

### Proposed Approach

```python
# services/fetchers/__init__.py
FETCHER_REGISTRY = {
    "arxiv": ArxivFetcher,
    "huggingface": HuggingFaceFetcher,
    "blogs": BlogFetcher,
    "hackernews": AggregatorFetcher,
    "reddit": AggregatorFetcher,
}

def get_fetcher(source: str):
    """Return an instantiated fetcher for the given source."""
    cls = FETCHER_REGISTRY.get(source)
    if not cls:
        raise ValueError(f"Unknown source: {source}")
    if source in ("hackernews", "reddit"):
        return cls(source=source)
    return cls()
```

Then in `sources.py`:
```python
from app.services.fetchers import get_fetcher, FETCHER_REGISTRY

@router.post("/refresh/{source}")
async def refresh_source(source: str, db: AsyncSession = Depends(get_db)):
    fetcher = get_fetcher(source)
    articles = await fetcher.fetch()
    # ... save to db
```

Benefits:
- Adding a new source = add one line to the registry
- Router stays clean
- Easy to list available sources dynamically
- No behavior change

---

## Risk Assessment

| Item | Risk | Mitigation |
|------|------|------------|
| Research agent split | Low - pure file reorganization | Verify imports work after split |
| Pagination | Low - JSON1 well-supported in SQLite | Test with existing data |
| Error handling | Low - simple, consistent pattern | Check frontend handles HTTP errors |
| Fetcher registry | Low - straightforward pattern | Test each source still works |

## Order of Implementation

1. Fetcher registry (smallest, most isolated change)
2. Error handling + logging (touches many files but simple changes)
3. Pagination fix (moderate complexity, important for correctness)
4. Research agent modularization (largest change, most files created)
