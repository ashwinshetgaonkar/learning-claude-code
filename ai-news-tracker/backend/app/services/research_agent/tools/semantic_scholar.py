from typing import List, Dict

import httpx


def search_semantic_scholar(query: str, max_results: int = 5) -> List[Dict]:
    """Search Semantic Scholar for academic papers with citation data."""
    try:
        resp = httpx.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={
                "query": query,
                "limit": max_results,
                "fields": "paperId,title,year,citationCount,url,abstract,authors",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for paper in data.get("data", []):
            authors = [a.get("name", "") for a in (paper.get("authors") or [])[:3]]
            abstract = paper.get("abstract") or ""
            results.append({
                "title": paper.get("title", ""),
                "authors": authors,
                "abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
                "url": paper.get("url") or f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                "year": paper.get("year"),
                "citation_count": paper.get("citationCount", 0),
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]
