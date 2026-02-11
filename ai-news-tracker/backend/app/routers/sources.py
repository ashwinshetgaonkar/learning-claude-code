import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from typing import Optional

from ..database import get_db
from ..models import Article
from ..services.fetchers import ArxivFetcher, HuggingFaceFetcher, BlogFetcher, AggregatorFetcher
from ..utils.categorizer import auto_categorize, deduplicate_articles
from ..config import settings

router = APIRouter(prefix="/api/sources", tags=["sources"])


async def save_articles(db: AsyncSession, articles: list[dict]) -> int:
    """Save articles to database, skipping duplicates."""
    saved_count = 0

    for article_data in articles:
        # Check if article already exists
        result = await db.execute(
            select(Article).where(Article.source_id == article_data["source_id"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            continue

        # Auto-categorize if no categories
        if not article_data.get("categories"):
            article_data["categories"] = auto_categorize(
                article_data.get("title", ""),
                article_data.get("abstract", "")
            )

        # Create new article
        article = Article(
            source=article_data["source"],
            source_id=article_data["source_id"],
            title=article_data["title"],
            authors=article_data.get("authors", []),
            abstract=article_data.get("abstract"),
            content=article_data.get("content"),
            summary=article_data.get("summary"),
            url=article_data["url"],
            pdf_url=article_data.get("pdf_url"),
            categories=article_data.get("categories", []),
            published_at=article_data.get("published_at"),
        )

        db.add(article)
        saved_count += 1

    await db.commit()
    return saved_count


@router.post("/refresh")
async def refresh_all_sources(
    db: AsyncSession = Depends(get_db),
    max_per_source: int = 30,
):
    """Fetch new articles from all sources."""
    results = {}
    all_articles = []

    async def _fetch_source(name, fetcher_factory, **kwargs):
        try:
            fetcher = fetcher_factory(**kwargs)
            articles = await fetcher.fetch(max_results=max_per_source)
            await fetcher.close()
            return name, articles, {"fetched": len(articles), "status": "success"}
        except Exception as e:
            return name, [], {"fetched": 0, "status": "error", "error": str(e)}

    # Fetch all sources in parallel
    fetch_results = await asyncio.gather(
        _fetch_source("arxiv", ArxivFetcher),
        _fetch_source("huggingface", HuggingFaceFetcher),
        _fetch_source("blogs", BlogFetcher),
        _fetch_source("aggregators", AggregatorFetcher,
                      reddit_client_id=settings.reddit_client_id,
                      reddit_client_secret=settings.reddit_client_secret),
    )

    for name, articles, result in fetch_results:
        results[name] = result
        all_articles.extend(articles)

    # Deduplicate
    unique_articles = deduplicate_articles(all_articles)

    # Save to database
    saved_count = await save_articles(db, unique_articles)

    return {
        "sources": results,
        "total_fetched": len(all_articles),
        "unique_articles": len(unique_articles),
        "saved": saved_count,
    }


@router.post("/refresh/{source}")
async def refresh_source(
    source: str,
    db: AsyncSession = Depends(get_db),
    max_results: int = 50,
):
    """Refresh a specific source."""
    articles = []

    if source == "arxiv":
        fetcher = ArxivFetcher()
        articles = await fetcher.fetch(max_results=max_results)
        await fetcher.close()
    elif source == "huggingface":
        fetcher = HuggingFaceFetcher()
        articles = await fetcher.fetch(max_results=max_results)
        await fetcher.close()
    elif source == "blogs":
        fetcher = BlogFetcher()
        articles = await fetcher.fetch(max_results=max_results)
        await fetcher.close()
    elif source == "aggregators":
        fetcher = AggregatorFetcher(
            reddit_client_id=settings.reddit_client_id,
            reddit_client_secret=settings.reddit_client_secret,
        )
        articles = await fetcher.fetch(max_results=max_results)
        await fetcher.close()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown source: {source}")

    # Deduplicate and save
    unique_articles = deduplicate_articles(articles)
    saved_count = await save_articles(db, unique_articles)

    return {
        "source": source,
        "fetched": len(articles),
        "unique": len(unique_articles),
        "saved": saved_count,
    }
