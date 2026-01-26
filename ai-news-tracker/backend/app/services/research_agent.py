"""
Research Agent Service using LangChain

Integrates multiple tools to search and aggregate research data:
- arXiv: Academic papers
- Wikipedia: General knowledge
- Tavily: Web search
"""

import asyncio
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import arxiv
import wikipedia
from tavily import TavilyClient

from ..config import settings


class ResearchAgentService:
    """Service for searching research data across multiple sources."""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.tavily_client = None
        if settings.tavily_api_key:
            self.tavily_client = TavilyClient(api_key=settings.tavily_api_key)

    async def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search arXiv for academic papers."""
        try:
            def _search():
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
                        "authors": [author.name for author in paper.authors],
                        "abstract": paper.summary,
                        "url": paper.entry_id,
                        "pdf_url": paper.pdf_url,
                        "published": paper.published.isoformat() if paper.published else None,
                        "categories": paper.categories,
                    })
                return results

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(self.executor, _search)
            return results
        except Exception as e:
            print(f"arXiv search error: {e}")
            return []

    async def search_wikipedia(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search Wikipedia for general knowledge."""
        try:
            def _search():
                results = []
                # Search for pages
                search_results = wikipedia.search(query, results=max_results)

                for title in search_results:
                    try:
                        page = wikipedia.page(title, auto_suggest=False)
                        results.append({
                            "title": page.title,
                            "summary": wikipedia.summary(title, sentences=3, auto_suggest=False),
                            "url": page.url,
                            "categories": page.categories[:5] if page.categories else [],
                        })
                    except (wikipedia.DisambiguationError, wikipedia.PageError):
                        continue
                return results

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(self.executor, _search)
            return results
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return []

    async def search_tavily(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web using Tavily."""
        if not self.tavily_client:
            return []

        try:
            def _search():
                response = self.tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=max_results,
                    include_answer=True,
                )
                results = []

                # Include the AI-generated answer if available
                answer = response.get("answer")

                for result in response.get("results", []):
                    results.append({
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "url": result.get("url", ""),
                        "score": result.get("score", 0),
                    })

                return {"answer": answer, "results": results}

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(self.executor, _search)
            return results
        except Exception as e:
            print(f"Tavily search error: {e}")
            return {"answer": None, "results": []}

    async def search_all(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        max_results_per_source: int = 5
    ) -> Dict[str, Any]:
        """
        Search across all configured sources.

        Args:
            query: Search query
            sources: List of sources to search (arxiv, wikipedia, tavily).
                    If None, searches all available sources.
            max_results_per_source: Maximum results per source

        Returns:
            Dictionary with results from each source
        """
        if sources is None:
            sources = ["arxiv", "wikipedia", "tavily"]

        tasks = []
        source_names = []

        if "arxiv" in sources:
            tasks.append(self.search_arxiv(query, max_results_per_source))
            source_names.append("arxiv")

        if "wikipedia" in sources:
            tasks.append(self.search_wikipedia(query, min(max_results_per_source, 3)))
            source_names.append("wikipedia")

        if "tavily" in sources and self.tavily_client:
            tasks.append(self.search_tavily(query, max_results_per_source))
            source_names.append("tavily")

        # Execute all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build response
        response = {
            "query": query,
            "sources": {}
        }

        for i, source_name in enumerate(source_names):
            if isinstance(results[i], Exception):
                response["sources"][source_name] = {
                    "error": str(results[i]),
                    "results": []
                }
            else:
                if source_name == "tavily":
                    response["sources"][source_name] = results[i]
                else:
                    response["sources"][source_name] = {
                        "results": results[i],
                        "count": len(results[i])
                    }

        return response


# Singleton instance
research_agent = ResearchAgentService()
