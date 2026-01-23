import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any
import asyncio


class ArxivFetcher:
    BASE_URL = "http://export.arxiv.org/api/query"
    CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE"]

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent AI papers from arXiv."""
        articles = []

        # Build category query
        cat_query = " OR ".join([f"cat:{cat}" for cat in self.CATEGORIES])

        params = {
            "search_query": cat_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            articles = self._parse_response(response.text)
        except Exception as e:
            print(f"Error fetching from arXiv: {e}")

        return articles

    def _parse_response(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse arXiv API XML response."""
        articles = []

        # Define namespaces
        namespaces = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        root = ET.fromstring(xml_content)

        for entry in root.findall("atom:entry", namespaces):
            try:
                # Extract arXiv ID from the id URL
                id_elem = entry.find("atom:id", namespaces)
                arxiv_url = id_elem.text if id_elem is not None else ""
                arxiv_id = arxiv_url.split("/abs/")[-1] if "/abs/" in arxiv_url else ""

                # Get title
                title_elem = entry.find("atom:title", namespaces)
                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else ""

                # Get authors
                authors = []
                for author in entry.findall("atom:author", namespaces):
                    name_elem = author.find("atom:name", namespaces)
                    if name_elem is not None:
                        authors.append(name_elem.text)

                # Get abstract
                summary_elem = entry.find("atom:summary", namespaces)
                abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""

                # Get categories
                categories = []
                for category in entry.findall("arxiv:primary_category", namespaces):
                    cat_term = category.get("term")
                    if cat_term:
                        categories.append(cat_term)
                for category in entry.findall("atom:category", namespaces):
                    cat_term = category.get("term")
                    if cat_term and cat_term not in categories:
                        categories.append(cat_term)

                # Get published date
                published_elem = entry.find("atom:published", namespaces)
                published_at = None
                if published_elem is not None:
                    try:
                        published_at = datetime.fromisoformat(published_elem.text.replace("Z", "+00:00"))
                    except:
                        pass

                # Get PDF link
                pdf_url = None
                for link in entry.findall("atom:link", namespaces):
                    if link.get("title") == "pdf":
                        pdf_url = link.get("href")
                        break

                if not pdf_url and arxiv_id:
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

                article = {
                    "source": "arxiv",
                    "source_id": f"arxiv:{arxiv_id}",
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "content": None,
                    "url": arxiv_url,
                    "pdf_url": pdf_url,
                    "categories": self._map_categories(categories),
                    "published_at": published_at,
                }

                articles.append(article)

            except Exception as e:
                print(f"Error parsing arXiv entry: {e}")
                continue

        return articles

    def _map_categories(self, arxiv_categories: List[str]) -> List[str]:
        """Map arXiv categories to our simplified categories."""
        category_map = {
            "cs.CL": "NLP",
            "cs.CV": "Computer Vision",
            "cs.LG": "Machine Learning",
            "cs.AI": "AI",
            "cs.NE": "Neural Networks",
            "stat.ML": "Machine Learning",
        }

        mapped = set()
        for cat in arxiv_categories:
            if cat in category_map:
                mapped.add(category_map[cat])
            else:
                # Keep first part of category as fallback
                mapped.add(cat.split(".")[0].upper())

        return list(mapped)

    async def close(self):
        await self.client.aclose()
