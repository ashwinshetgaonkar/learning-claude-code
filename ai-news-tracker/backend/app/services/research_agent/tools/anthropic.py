from typing import List, Dict

import httpx
from bs4 import BeautifulSoup


def search_anthropic(query: str, max_results: int = 5) -> List[Dict]:
    """Search Anthropic's research page for articles."""
    try:
        resp = httpx.get(
            "https://www.anthropic.com/research",
            headers={"User-Agent": "AI-News-Tracker/1.0"},
            timeout=15,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        query_terms = query.lower().split()
        results = []
        for link in soup.find_all("a", href=True):
            title_el = link.find(["h2", "h3", "h4", "span"])
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            if not title or len(title) < 10:
                continue
            desc_el = link.find("p")
            description = desc_el.get_text(strip=True) if desc_el else ""
            text = f"{title} {description}".lower()
            if any(term in text for term in query_terms):
                href = link["href"]
                if not href.startswith("http"):
                    href = f"https://www.anthropic.com{href}"
                results.append({
                    "title": title,
                    "description": description[:300],
                    "url": href,
                })
        # Deduplicate by URL
        seen = set()
        unique = []
        for r in results:
            if r["url"] not in seen:
                seen.add(r["url"])
                unique.append(r)
        return unique[:max_results]
    except Exception as e:
        return [{"error": str(e)}]
