"""
Research Agents API Router

Provides endpoints for searching research data across multiple sources
using LangChain-integrated tools.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List

from ..services.research_agent import research_agent

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/search")
async def search_research(
    q: str = Query(..., min_length=2, description="Search query"),
    sources: Optional[str] = Query(
        None,
        description="Comma-separated list of sources (arxiv,wikipedia,tavily). Default: all"
    ),
    max_results: int = Query(5, ge=1, le=20, description="Max results per source"),
):
    """
    Search across multiple research sources.

    Returns aggregated results from:
    - **arXiv**: Academic papers and preprints
    - **Wikipedia**: General knowledge articles
    - **Tavily**: Web search with AI-generated answer

    Example:
    ```
    GET /api/agents/search?q=transformer+architecture&sources=arxiv,wikipedia&max_results=5
    ```
    """
    # Parse sources
    source_list = None
    if sources:
        source_list = [s.strip().lower() for s in sources.split(",")]
        valid_sources = {"arxiv", "wikipedia", "tavily"}
        invalid = set(source_list) - valid_sources
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sources: {invalid}. Valid sources: {valid_sources}"
            )

    results = await research_agent.search_all(
        query=q,
        sources=source_list,
        max_results_per_source=max_results
    )

    return results


@router.get("/sources")
async def list_sources():
    """
    List available research sources and their status.
    """
    from ..config import settings

    return {
        "sources": [
            {
                "name": "arxiv",
                "description": "Academic papers and preprints from arXiv.org",
                "available": True,
                "requires_api_key": False,
            },
            {
                "name": "wikipedia",
                "description": "General knowledge articles from Wikipedia",
                "available": True,
                "requires_api_key": False,
            },
            {
                "name": "tavily",
                "description": "Web search with AI-generated answers",
                "available": bool(settings.tavily_api_key),
                "requires_api_key": True,
            },
        ]
    }
