import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError as e:
    logger.warning("arxiv not available: %s", e)
    ARXIV_AVAILABLE = False
    arxiv = None


def search_arxiv(query: str, max_results: int = 5) -> List[Dict]:
    """Search arXiv for academic papers."""
    if not ARXIV_AVAILABLE:
        return [{"error": "arxiv package not installed"}]
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = []
        for paper in client.results(search):
            results.append({
                "title": paper.title,
                "authors": [author.name for author in paper.authors][:3],
                "abstract": paper.summary[:500] + "..." if len(paper.summary) > 500 else paper.summary,
                "url": paper.entry_id,
                "pdf_url": paper.pdf_url,
                "published": paper.published.strftime("%Y-%m-%d") if paper.published else None,
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]
