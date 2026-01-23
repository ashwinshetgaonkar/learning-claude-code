from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from ..database import get_db
from ..models import Article, Bookmark

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


@router.get("")
async def list_bookmarks(
    db: AsyncSession = Depends(get_db),
):
    """List all bookmarked articles."""
    result = await db.execute(
        select(Article)
        .where(Article.is_bookmarked == True)
        .order_by(desc(Article.fetched_at))
    )
    articles = result.scalars().all()

    return {
        "bookmarks": [a.to_dict() for a in articles],
        "total": len(articles),
    }


@router.post("/{article_id}")
async def add_bookmark(
    article_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Bookmark an article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if article.is_bookmarked:
        return {"message": "Article already bookmarked", "article": article.to_dict()}

    article.is_bookmarked = True

    # Also add to bookmarks table
    bookmark = Bookmark(article_id=article_id)
    db.add(bookmark)

    await db.commit()

    return {"message": "Article bookmarked", "article": article.to_dict()}


@router.delete("/{article_id}")
async def remove_bookmark(
    article_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Remove bookmark from an article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if not article.is_bookmarked:
        return {"message": "Article not bookmarked", "article": article.to_dict()}

    article.is_bookmarked = False

    # Remove from bookmarks table
    bookmark_result = await db.execute(
        select(Bookmark).where(Bookmark.article_id == article_id)
    )
    bookmark = bookmark_result.scalar_one_or_none()
    if bookmark:
        await db.delete(bookmark)

    await db.commit()

    return {"message": "Bookmark removed", "article": article.to_dict()}
