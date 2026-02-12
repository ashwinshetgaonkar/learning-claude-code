from typing import List, Dict

import httpx


def search_papers_with_code(query: str, max_results: int = 5) -> List[Dict]:
    """Search HuggingFace papers (formerly Papers With Code) for trending research."""
    try:
        resp = httpx.get(
            "https://huggingface.co/api/daily_papers",
            params={"limit": 50},
            timeout=15,
        )
        resp.raise_for_status()
        papers = resp.json()
        query_terms = query.lower().split()
        results = []
        for item in papers:
            paper = item.get("paper", {})
            title = paper.get("title", "")
            summary = paper.get("summary", "")
            text = f"{title} {summary}".lower()
            if any(term in text for term in query_terms):
                results.append({
                    "title": title,
                    "abstract": summary[:500] + "..." if len(summary) > 500 else summary,
                    "url": f"https://huggingface.co/papers/{paper.get('id', '')}",
                    "repository_url": None,
                })
            if len(results) >= max_results:
                break
        return results
    except Exception as e:
        return [{"error": str(e)}]
