from typing import List, Dict

import httpx

from ....config import settings


def search_github(query: str, max_results: int = 5) -> List[Dict]:
    """Search GitHub for repositories related to AI/ML."""
    try:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if settings.github_token:
            headers["Authorization"] = f"token {settings.github_token}"
        resp = httpx.get(
            "https://api.github.com/search/repositories",
            params={
                "q": f"{query} topic:machine-learning",
                "sort": "stars",
                "per_page": max_results,
            },
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for repo in data.get("items", [])[:max_results]:
            results.append({
                "name": repo.get("name", ""),
                "full_name": repo.get("full_name", ""),
                "description": (repo.get("description") or "")[:300],
                "url": repo.get("html_url", ""),
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language"),
                "topics": repo.get("topics", [])[:5],
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]
