"""
Research Agents API Router

Provides endpoints for searching research data using an agentic tool-use
loop with Groq LLM. The LLM decides which tools to call (arXiv, Wikipedia,
Tavily, YouTube), executes them, and iterates until it can synthesize a response.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from ..services.research_agent import research_agent
from ..config import settings

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/search")
async def search_research(
    q: str = Query(..., min_length=2, description="Search query"),
    source: Optional[str] = Query(
        None,
        description="Specific source to search (arxiv, wikipedia, tavily). If not specified, uses AI agent to search all."
    ),
):
    """
    Search across multiple research sources using an AI agent.

    The agent uses Groq LLM (llama-3.1-8b-instant) to intelligently search:
    - **arXiv**: Academic papers and preprints
    - **Wikipedia**: General knowledge articles
    - **Tavily**: Web search (if API key configured)

    The AI will decide which sources are most relevant and synthesize the results.

    Example:
    ```
    GET /api/agents/search?q=transformer+architecture
    GET /api/agents/search?q=neural+networks&source=arxiv
    ```
    """
    if source:
        # Search specific source
        valid_sources = {"arxiv", "wikipedia", "tavily", "youtube", "semantic_scholar", "huggingface", "github", "papers_with_code", "anthropic"}
        if source.lower() not in valid_sources:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source: {source}. Valid sources: {valid_sources}"
            )
        results = await research_agent.search_source(q, source.lower())
    else:
        # Use AI agent to search all sources
        results = await research_agent.search(q)

    return results


@router.get("/sources")
async def list_sources():
    """
    List available research sources and their status.
    """
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
            {
                "name": "youtube",
                "description": "Educational videos and tutorials from YouTube",
                "available": bool(settings.youtube_api_key),
                "requires_api_key": True,
            },
            {
                "name": "semantic_scholar",
                "description": "Academic papers with citation data from Semantic Scholar",
                "available": True,
                "requires_api_key": False,
            },
            {
                "name": "huggingface",
                "description": "ML models from HuggingFace Hub",
                "available": True,
                "requires_api_key": False,
            },
            {
                "name": "github",
                "description": "AI/ML repositories from GitHub",
                "available": True,
                "requires_api_key": False,
            },
            {
                "name": "papers_with_code",
                "description": "Papers with code implementations from Papers With Code",
                "available": True,
                "requires_api_key": False,
            },
            {
                "name": "anthropic",
                "description": "Research articles from Anthropic",
                "available": True,
                "requires_api_key": False,
            },
        ],
        "llm": {
            "provider": "groq",
            "model": "llama-3.1-8b-instant",
            "configured": bool(settings.groq_api_key),
        }
    }
