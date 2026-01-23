import httpx
import feedparser
from datetime import datetime
from typing import List, Dict, Any
from email.utils import parsedate_to_datetime


class HuggingFaceFetcher:
    BLOG_RSS = "https://huggingface.co/blog/feed.xml"
    PAPERS_API = "https://huggingface.co/api/daily_papers"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, max_results: int = 30) -> List[Dict[str, Any]]:
        """Fetch content from HuggingFace blog and papers."""
        articles = []

        # Fetch blog posts
        blog_articles = await self._fetch_blog()
        articles.extend(blog_articles[:max_results // 2])

        # Fetch daily papers
        papers = await self._fetch_papers()
        articles.extend(papers[:max_results // 2])

        return articles

    async def _fetch_blog(self) -> List[Dict[str, Any]]:
        """Fetch HuggingFace blog posts via RSS."""
        articles = []

        try:
            response = await self.client.get(self.BLOG_RSS)
            response.raise_for_status()

            feed = feedparser.parse(response.text)

            for entry in feed.entries:
                try:
                    published_at = None
                    if hasattr(entry, "published"):
                        try:
                            published_at = parsedate_to_datetime(entry.published)
                        except:
                            pass

                    article = {
                        "source": "huggingface",
                        "source_id": f"hf:blog:{entry.get('id', entry.link)}",
                        "title": entry.get("title", ""),
                        "authors": [author.get("name", "") for author in entry.get("authors", [])],
                        "abstract": entry.get("summary", ""),
                        "content": entry.get("content", [{}])[0].get("value", "") if entry.get("content") else None,
                        "url": entry.get("link", ""),
                        "pdf_url": None,
                        "categories": ["AI", "Generative AI"],
                        "published_at": published_at,
                    }
                    articles.append(article)
                except Exception as e:
                    print(f"Error parsing HuggingFace blog entry: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching HuggingFace blog: {e}")

        return articles

    async def _fetch_papers(self) -> List[Dict[str, Any]]:
        """Fetch daily papers from HuggingFace."""
        articles = []

        try:
            response = await self.client.get(self.PAPERS_API)
            response.raise_for_status()

            papers = response.json()

            for paper in papers:
                try:
                    paper_info = paper.get("paper", {})

                    published_at = None
                    if paper_info.get("publishedAt"):
                        try:
                            published_at = datetime.fromisoformat(paper_info["publishedAt"].replace("Z", "+00:00"))
                        except:
                            pass

                    arxiv_id = paper_info.get("id", "")

                    article = {
                        "source": "huggingface",
                        "source_id": f"hf:paper:{arxiv_id}",
                        "title": paper_info.get("title", ""),
                        "authors": [author.get("name", "") for author in paper_info.get("authors", [])],
                        "abstract": paper_info.get("summary", ""),
                        "content": None,
                        "url": f"https://huggingface.co/papers/{arxiv_id}" if arxiv_id else "",
                        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else None,
                        "categories": ["AI", "Machine Learning"],
                        "published_at": published_at,
                    }
                    articles.append(article)
                except Exception as e:
                    print(f"Error parsing HuggingFace paper: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching HuggingFace papers: {e}")

        return articles

    async def close(self):
        await self.client.aclose()
