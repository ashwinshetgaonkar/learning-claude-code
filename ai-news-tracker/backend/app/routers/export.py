from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from io import BytesIO

from ..database import get_db
from ..models import Article
from ..services.pdf_generator import pdf_generator

router = APIRouter(prefix="/api/articles", tags=["export"])


@router.get("/{article_id}/pdf")
async def download_pdf(
    article_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Download article as PDF."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # If article has a PDF URL (arXiv), try to download it
    if article.pdf_url:
        pdf_bytes = await pdf_generator.download_pdf(article.pdf_url)
        if pdf_bytes:
            filename = f"{article.source_id.replace(':', '_')}.pdf"
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                },
            )

    # Otherwise, generate PDF from content
    pdf_bytes = await pdf_generator.generate_from_article(
        title=article.title,
        authors=article.authors or [],
        abstract=article.abstract or "",
        content=article.content,
        url=article.url,
        summary=article.summary,
    )

    if not pdf_bytes:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate PDF. WeasyPrint may not be installed."
        )

    filename = f"article_{article_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@router.get("/{article_id}/markdown")
async def export_markdown(
    article_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Export article as Markdown."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Build markdown content
    authors_str = ", ".join(article.authors) if article.authors else "Unknown"
    categories_str = ", ".join(article.categories) if article.categories else "Uncategorized"

    markdown = f"""# {article.title}

**Authors:** {authors_str}

**Source:** {article.source} | **Categories:** {categories_str}

**URL:** [{article.url}]({article.url})

"""

    if article.published_at:
        markdown += f"**Published:** {article.published_at.strftime('%Y-%m-%d')}\n\n"

    if article.summary:
        markdown += f"""## AI Summary

{article.summary}

"""

    if article.abstract:
        markdown += f"""## Abstract

{article.abstract}

"""

    if article.content:
        markdown += f"""## Content

{article.content}

"""

    markdown += """---

*Exported from AI News Tracker*
"""

    filename = f"article_{article_id}.md"
    return Response(
        content=markdown.encode("utf-8"),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )
