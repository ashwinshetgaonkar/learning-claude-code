import httpx
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from email.utils import parsedate_to_datetime


class BlogFetcher:
    BLOG_SOURCES = {
        "openai": {
            "name": "OpenAI",
            "rss": "https://openai.com/news/rss.xml",
            "categories": ["AI", "Generative AI", "LLM"],
        },
        "anthropic": {
            "name": "Anthropic",
            "url": "https://www.anthropic.com/research",
            "categories": ["AI", "LLM", "AI Safety"],
        },
        "deepmind": {
            "name": "Google DeepMind",
            "rss": "https://deepmind.google/blog/rss.xml",
            "categories": ["AI", "Machine Learning", "Research"],
        },
        "meta": {
            "name": "Meta AI",
            "url": "https://ai.meta.com/blog/",
            "categories": ["AI", "Machine Learning"],
        },
    }

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    async def fetch(self, max_results: int = 30) -> List[Dict[str, Any]]:
        """Fetch posts from AI company blogs."""
        articles = []

        for source_id, source_info in self.BLOG_SOURCES.items():
            try:
                if "rss" in source_info:
                    source_articles = await self._fetch_rss(source_id, source_info)
                else:
                    source_articles = await self._scrape_blog(source_id, source_info)

                articles.extend(source_articles[:max_results // len(self.BLOG_SOURCES)])
            except Exception as e:
                print(f"Error fetching from {source_info['name']}: {e}")
                continue

        return articles

    async def _fetch_rss(self, source_id: str, source_info: Dict) -> List[Dict[str, Any]]:
        """Fetch blog posts via RSS feed."""
        articles = []

        try:
            response = await self.client.get(source_info["rss"])
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
                    elif hasattr(entry, "updated"):
                        try:
                            published_at = parsedate_to_datetime(entry.updated)
                        except:
                            pass

                    # Extract content
                    content = ""
                    if hasattr(entry, "content"):
                        content = entry.content[0].get("value", "") if entry.content else ""
                    elif hasattr(entry, "summary"):
                        content = entry.summary

                    # Clean HTML from content for abstract
                    abstract = ""
                    if content:
                        soup = BeautifulSoup(content, "html.parser")
                        abstract = soup.get_text()[:500] + "..." if len(soup.get_text()) > 500 else soup.get_text()

                    article = {
                        "source": "blog",
                        "source_id": f"blog:{source_id}:{entry.get('id', entry.link)}",
                        "title": entry.get("title", ""),
                        "authors": [source_info["name"]],
                        "abstract": abstract,
                        "content": content,
                        "url": entry.get("link", ""),
                        "pdf_url": None,
                        "categories": source_info["categories"],
                        "published_at": published_at,
                    }
                    articles.append(article)
                except Exception as e:
                    print(f"Error parsing RSS entry from {source_info['name']}: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching RSS from {source_info['name']}: {e}")

        return articles

    async def _scrape_blog(self, source_id: str, source_info: Dict) -> List[Dict[str, Any]]:
        """Scrape blog posts when RSS is not available."""
        articles = []

        try:
            response = await self.client.get(source_info["url"])
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Generic blog post detection - this may need adjustment per site
            post_selectors = [
                "article",
                ".blog-post",
                ".post-item",
                "[data-testid='blog-post']",
            ]

            posts = []
            for selector in post_selectors:
                posts = soup.select(selector)
                if posts:
                    break

            for post in posts[:10]:
                try:
                    # Try to find title
                    title_elem = post.select_one("h1, h2, h3, .title, [data-testid='title']")
                    title = title_elem.get_text(strip=True) if title_elem else ""

                    # Try to find link
                    link_elem = post.select_one("a[href]")
                    url = link_elem.get("href", "") if link_elem else ""
                    if url and not url.startswith("http"):
                        url = source_info["url"].rstrip("/") + "/" + url.lstrip("/")

                    # Try to find description
                    desc_elem = post.select_one("p, .description, .excerpt")
                    abstract = desc_elem.get_text(strip=True)[:500] if desc_elem else ""

                    if title and url:
                        article = {
                            "source": "blog",
                            "source_id": f"blog:{source_id}:{url}",
                            "title": title,
                            "authors": [source_info["name"]],
                            "abstract": abstract,
                            "content": None,
                            "url": url,
                            "pdf_url": None,
                            "categories": source_info["categories"],
                            "published_at": None,
                        }
                        articles.append(article)
                except Exception as e:
                    print(f"Error parsing scraped post from {source_info['name']}: {e}")
                    continue

        except Exception as e:
            print(f"Error scraping {source_info['name']}: {e}")

        return articles

    async def close(self):
        await self.client.aclose()
