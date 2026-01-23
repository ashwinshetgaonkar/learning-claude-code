from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, text, or_
from typing import Optional, List
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Article
from ..services.summarizer import summarizer_service

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("")
async def list_articles(
    db: AsyncSession = Depends(get_db),
    source: Optional[str] = Query(None, description="Filter by source"),
    category: Optional[str] = Query(None, description="Filter by category"),
    days: Optional[int] = Query(None, description="Filter by days ago"),
    bookmarked: Optional[bool] = Query(None, description="Filter bookmarked only"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List articles with optional filters."""
    query = select(Article).order_by(desc(Article.published_at), desc(Article.fetched_at))

    # Apply filters
    if source:
        query = query.where(Article.source == source)

    if bookmarked is not None:
        query = query.where(Article.is_bookmarked == bookmarked)

    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.where(Article.published_at >= cutoff_date)

    # Apply pagination
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    articles = result.scalars().all()

    # Filter by category in Python (since it's stored as JSON)
    if category:
        articles = [
            a for a in articles
            if a.categories and category in a.categories
        ]

    return {
        "articles": [a.to_dict() for a in articles],
        "total": len(articles),
        "limit": limit,
        "offset": offset,
    }


@router.get("/search")
async def search_articles(
    q: str = Query(..., min_length=2, description="Search query"),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
):
    """Full-text search across articles."""
    # Use FTS5 for search
    fts_query = text("""
        SELECT articles.*
        FROM articles
        JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit
    """)

    result = await db.execute(fts_query, {"query": q, "limit": limit})
    rows = result.fetchall()

    # Convert rows to Article objects
    articles = []
    for row in rows:
        article = Article(
            id=row.id,
            source=row.source,
            source_id=row.source_id,
            title=row.title,
            authors=row.authors,
            abstract=row.abstract,
            content=row.content,
            summary=row.summary,
            url=row.url,
            pdf_url=row.pdf_url,
            categories=row.categories,
            published_at=row.published_at,
            fetched_at=row.fetched_at,
            is_bookmarked=row.is_bookmarked,
        )
        articles.append(article.to_dict())

    return {
        "articles": articles,
        "query": q,
        "total": len(articles),
    }


@router.get("/{article_id}")
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single article by ID."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return article.to_dict()


@router.post("/{article_id}/summarize")
async def summarize_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Generate AI summary for an article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Return cached summary if exists
    if article.summary:
        return {"summary": article.summary, "cached": True}

    # Generate new summary
    summary = await summarizer_service.summarize(
        title=article.title,
        abstract=article.abstract or "",
        content=article.content,
    )

    if summary:
        article.summary = summary
        await db.commit()
        return {"summary": summary, "cached": False}

    raise HTTPException(status_code=500, detail="Failed to generate summary")


@router.get("/categories/list")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Get list of all categories with counts."""
    result = await db.execute(select(Article.categories))
    all_categories = result.scalars().all()

    category_counts = {}
    for cats in all_categories:
        if cats:
            for cat in cats:
                category_counts[cat] = category_counts.get(cat, 0) + 1

    return {
        "categories": [
            {"name": name, "count": count}
            for name, count in sorted(category_counts.items(), key=lambda x: -x[1])
        ]
    }
