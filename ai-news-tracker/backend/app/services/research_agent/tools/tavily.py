import logging
from typing import Dict

from ....config import settings

logger = logging.getLogger(__name__)

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError as e:
    logger.warning("tavily not available: %s", e)
    TAVILY_AVAILABLE = False
    TavilyClient = None


def search_tavily(query: str, max_results: int = 5) -> Dict:
    """Search web using Tavily."""
    if not TAVILY_AVAILABLE:
        return {"error": "tavily package not installed"}
    if not settings.tavily_api_key:
        return {"error": "Tavily API key not configured"}
    try:
        client = TavilyClient(api_key=settings.tavily_api_key)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=True,
        )
        return {
            "answer": response.get("answer"),
            "results": [
                {
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:300],
                    "url": r.get("url", ""),
                }
                for r in response.get("results", [])[:max_results]
            ]
        }
    except Exception as e:
        return {"error": str(e)}
