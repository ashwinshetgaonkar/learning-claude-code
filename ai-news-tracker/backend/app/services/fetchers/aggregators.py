import logging

import httpx
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class AggregatorFetcher:
    HN_API = "https://hn.algolia.com/api/v1/search"
    REDDIT_API = "https://www.reddit.com/r/MachineLearning/hot.json"

    def __init__(self, reddit_client_id: str = "", reddit_client_secret: str = ""):
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "AINewsTracker/1.0"
            }
        )

    async def fetch(self, max_results: int = 30) -> List[Dict[str, Any]]:
        """Fetch from Hacker News and Reddit."""
        articles = []

        # Fetch from Hacker News
        hn_articles = await self._fetch_hacker_news()
        articles.extend(hn_articles[:max_results // 2])

        # Fetch from Reddit
        reddit_articles = await self._fetch_reddit()
        articles.extend(reddit_articles[:max_results // 2])

        return articles

    async def _fetch_hacker_news(self) -> List[Dict[str, Any]]:
        """Fetch AI-related stories from Hacker News."""
        articles = []

        # Search for AI/ML related posts
        search_terms = ["AI", "machine learning", "GPT", "LLM", "neural network", "deep learning"]

        for term in search_terms[:3]:  # Limit to avoid too many requests
            try:
                params = {
                    "query": term,
                    "tags": "story",
                    "hitsPerPage": 10,
                }

                response = await self.client.get(self.HN_API, params=params)
                response.raise_for_status()

                data = response.json()

                for hit in data.get("hits", []):
                    try:
                        published_at = None
                        if hit.get("created_at"):
                            try:
                                published_at = datetime.fromisoformat(hit["created_at"].replace("Z", "+00:00"))
                            except:
                                pass

                        # Skip if no URL (self posts)
                        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"

                        article = {
                            "source": "aggregator",
                            "source_id": f"hn:{hit.get('objectID')}",
                            "title": hit.get("title", ""),
                            "authors": [hit.get("author", "")],
                            "abstract": f"Points: {hit.get('points', 0)} | Comments: {hit.get('num_comments', 0)}",
                            "content": None,
                            "url": url,
                            "pdf_url": None,
                            "categories": ["AI", "Tech News"],
                            "published_at": published_at,
                        }

                        # Deduplicate by source_id
                        if not any(a["source_id"] == article["source_id"] for a in articles):
                            articles.append(article)
                    except Exception as e:
                        logger.warning("Error parsing HN hit: %s", e)
                        continue

            except Exception as e:
                logger.warning("Error fetching from HN for term '%s': %s", term, e)
                continue

        return articles

    async def _fetch_reddit(self) -> List[Dict[str, Any]]:
        """Fetch posts from r/MachineLearning."""
        articles = []

        try:
            response = await self.client.get(
                self.REDDIT_API,
                params={"limit": 25}
            )
            response.raise_for_status()

            data = response.json()

            for post in data.get("data", {}).get("children", []):
                try:
                    post_data = post.get("data", {})

                    published_at = None
                    if post_data.get("created_utc"):
                        try:
                            published_at = datetime.fromtimestamp(post_data["created_utc"])
                        except:
                            pass

                    # Get URL - either external link or reddit comments
                    url = post_data.get("url", "")
                    if url.startswith("/r/"):
                        url = f"https://www.reddit.com{url}"

                    # Get flair as category hint
                    flair = post_data.get("link_flair_text", "")
                    categories = ["Machine Learning"]
                    if flair:
                        categories.append(flair)

                    article = {
                        "source": "aggregator",
                        "source_id": f"reddit:{post_data.get('id')}",
                        "title": post_data.get("title", ""),
                        "authors": [post_data.get("author", "")],
                        "abstract": post_data.get("selftext", "")[:500] if post_data.get("selftext") else f"Score: {post_data.get('score', 0)} | Comments: {post_data.get('num_comments', 0)}",
                        "content": post_data.get("selftext"),
                        "url": url,
                        "pdf_url": None,
                        "categories": categories,
                        "published_at": published_at,
                    }
                    articles.append(article)
                except Exception as e:
                    logger.warning("Error parsing Reddit post: %s", e)
                    continue

        except Exception as e:
            logger.warning("Error fetching from Reddit: %s", e)

        return articles

    async def close(self):
        await self.client.aclose()
