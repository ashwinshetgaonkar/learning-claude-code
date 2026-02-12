import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError as e:
    logger.warning("wikipedia not available: %s", e)
    WIKIPEDIA_AVAILABLE = False
    wikipedia = None


def search_wikipedia(query: str, max_results: int = 3) -> List[Dict]:
    """Search Wikipedia for articles."""
    if not WIKIPEDIA_AVAILABLE:
        return [{"error": "wikipedia package not installed"}]
    try:
        search_results = wikipedia.search(query, results=max_results)
        results = []
        for title in search_results:
            try:
                summary = wikipedia.summary(title, sentences=3, auto_suggest=False)
                page = wikipedia.page(title, auto_suggest=False)
                results.append({
                    "title": page.title,
                    "summary": summary,
                    "url": page.url,
                })
            except (wikipedia.DisambiguationError, wikipedia.PageError):
                continue
        return results
    except Exception as e:
        return [{"error": str(e)}]
