"""
Research Agent Service using LangChain with Groq LLM

Uses the same Groq LLM as the summarizer to orchestrate research tools:
- arXiv: Academic papers
- Wikipedia: General knowledge
- Tavily: Web search
"""

import asyncio
import sys
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from ..config import settings

# Import optional dependencies with fallback
try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: LangChain not available: {e}", file=sys.stderr)
    LANGCHAIN_AVAILABLE = False
    ChatGroq = None
    HumanMessage = None
    SystemMessage = None

try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError as e:
    print(f"Warning: arxiv not available: {e}", file=sys.stderr)
    ARXIV_AVAILABLE = False
    arxiv = None

try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError as e:
    print(f"Warning: wikipedia not available: {e}", file=sys.stderr)
    WIKIPEDIA_AVAILABLE = False
    wikipedia = None

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: tavily not available: {e}", file=sys.stderr)
    TAVILY_AVAILABLE = False
    TavilyClient = None

try:
    from googleapiclient.discovery import build
    YOUTUBE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: YouTube API not available: {e}", file=sys.stderr)
    YOUTUBE_AVAILABLE = False


# Define tools as simple functions
def _search_arxiv(query: str, max_results: int = 5) -> List[Dict]:
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


def _search_wikipedia(query: str, max_results: int = 3) -> List[Dict]:
    """Search Wikipedia for articles."""
    if not WIKIPEDIA_AVAILABLE:
        return [{"error": "wikipedia package not installed"}]
    try:
        search_results = wikipedia.search(query, results=max_results)
        results = []
        for title in search_results:
            try:
                summary = wikipedia.summary(title, sentences=3, auto_suggest=False)
                page = wikipedia.page(title, auto_suggest=False)
                results.append({
                    "title": page.title,
                    "summary": summary,
                    "url": page.url,
                })
            except (wikipedia.DisambiguationError, wikipedia.PageError):
                continue
        return results
    except Exception as e:
        return [{"error": str(e)}]


def _search_tavily(query: str, max_results: int = 5) -> Dict:
    """Search web using Tavily."""
    if not TAVILY_AVAILABLE:
        return {"error": "tavily package not installed"}
    if not settings.tavily_api_key:
        return {"error": "Tavily API key not configured"}
    try:
        client = TavilyClient(api_key=settings.tavily_api_key)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=True,
        )
        return {
            "answer": response.get("answer"),
            "results": [
                {
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:300],
                    "url": r.get("url", ""),
                }
                for r in response.get("results", [])[:max_results]
            ]
        }
    except Exception as e:
        return {"error": str(e)}


def _search_youtube(query: str, max_results: int = 5) -> List[Dict]:
    """Search YouTube for relevant videos."""
    if not YOUTUBE_AVAILABLE:
        return [{"error": "google-api-python-client not installed"}]
    if not settings.youtube_api_key:
        return [{"error": "YouTube API key not configured"}]
    try:
        youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_results,
            relevanceLanguage='en'
        )
        response = request.execute()

        results = []
        for item in response.get('items', []):
            snippet = item['snippet']
            video_id = item['id']['videoId']
            results.append({
                "title": snippet['title'],
                "channel": snippet['channelTitle'],
                "description": snippet['description'][:200] if snippet['description'] else "",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail_url": snippet['thumbnails']['medium']['url'],
                "published_at": snippet['publishedAt'],
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


class ResearchAgentService:
    """Service for searching research data using Groq LLM."""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.llm = None
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the Groq LLM."""
        if not LANGCHAIN_AVAILABLE:
            print("Warning: LangChain not available. Research agent will use fallback mode.", file=sys.stderr)
            return

        if not settings.groq_api_key:
            print("Warning: GROQ_API_KEY not configured. Research agent will use fallback mode.", file=sys.stderr)
            return

        try:
            self.llm = ChatGroq(
                api_key=settings.groq_api_key,
                model_name="llama-3.1-8b-instant",
                temperature=0,
            )
        except Exception as e:
            print(f"Error initializing Groq LLM: {e}", file=sys.stderr)

    async def search(self, query: str) -> Dict[str, Any]:
        """
        Search across multiple sources and use LLM to synthesize results.
        """
        loop = asyncio.get_event_loop()

        # Run all searches concurrently
        arxiv_task = loop.run_in_executor(self.executor, _search_arxiv, query)
        wiki_task = loop.run_in_executor(self.executor, _search_wikipedia, query)

        tasks = [arxiv_task, wiki_task]
        task_names = ['arxiv', 'wiki']

        if settings.tavily_api_key:
            tavily_task = loop.run_in_executor(self.executor, _search_tavily, query)
            tasks.append(tavily_task)
            task_names.append('tavily')

        if settings.youtube_api_key:
            youtube_task = loop.run_in_executor(self.executor, _search_youtube, query)
            tasks.append(youtube_task)
            task_names.append('youtube')

        results = await asyncio.gather(*tasks, return_exceptions=True)

        arxiv_results = results[0] if not isinstance(results[0], Exception) else []
        wiki_results = results[1] if not isinstance(results[1], Exception) else []

        tavily_idx = task_names.index('tavily') if 'tavily' in task_names else -1
        youtube_idx = task_names.index('youtube') if 'youtube' in task_names else -1

        tavily_results = results[tavily_idx] if tavily_idx >= 0 and not isinstance(results[tavily_idx], Exception) else None
        youtube_results = results[youtube_idx] if youtube_idx >= 0 and not isinstance(results[youtube_idx], Exception) else None

        # Use LLM to synthesize if available
        if self.llm:
            try:
                synthesis = await self._synthesize_results(query, arxiv_results, wiki_results, tavily_results, youtube_results)
                return {
                    "query": query,
                    "response": synthesis,
                    "sources": {
                        "arxiv": arxiv_results,
                        "wikipedia": wiki_results,
                        "tavily": tavily_results,
                        "youtube": youtube_results,
                    },
                    "success": True,
                }
            except Exception as e:
                print(f"LLM synthesis error: {e}")

        # Fallback: return raw results
        return {
            "query": query,
            "sources": {
                "arxiv": arxiv_results,
                "wikipedia": wiki_results,
                "tavily": tavily_results,
                "youtube": youtube_results,
            },
            "success": True,
        }

    async def _synthesize_results(
        self,
        query: str,
        arxiv_results: List[Dict],
        wiki_results: List[Dict],
        tavily_results: Optional[Dict],
        youtube_results: Optional[List[Dict]] = None
    ) -> str:
        """Use LLM to synthesize search results into a coherent response."""

        # Build context from results
        context_parts = []

        if arxiv_results and not any("error" in r for r in arxiv_results):
            arxiv_text = "\n".join([
                f"- {r['title']} by {', '.join(r.get('authors', []))}: {r.get('abstract', '')[:200]}"
                for r in arxiv_results[:3]
            ])
            context_parts.append(f"**Academic Papers (arXiv):**\n{arxiv_text}")

        if wiki_results and not any("error" in r for r in wiki_results):
            wiki_text = "\n".join([
                f"- {r['title']}: {r.get('summary', '')[:200]}"
                for r in wiki_results[:3]
            ])
            context_parts.append(f"**Wikipedia:**\n{wiki_text}")

        if tavily_results and "error" not in tavily_results:
            if tavily_results.get("answer"):
                context_parts.append(f"**Web Search Answer:**\n{tavily_results['answer']}")
            if tavily_results.get("results"):
                web_text = "\n".join([
                    f"- {r['title']}: {r.get('content', '')[:150]}"
                    for r in tavily_results["results"][:3]
                ])
                context_parts.append(f"**Web Results:**\n{web_text}")

        if youtube_results and not any("error" in r for r in youtube_results):
            youtube_text = "\n".join([
                f"- {r['title']} by {r['channel']}: {r.get('description', '')[:100]}"
                for r in youtube_results[:3]
            ])
            context_parts.append(f"**YouTube Videos:**\n{youtube_text}")

        if not context_parts:
            return "No results found from any source."

        context = "\n\n".join(context_parts)

        prompt = f"""Based on the following search results for "{query}", provide a comprehensive summary that combines the key information from all sources. Be concise but informative.

{context}

Provide a 2-3 paragraph summary that answers the query and cites which sources the information comes from."""

        def _call_llm():
            response = self.llm.invoke([
                SystemMessage(content="You are a research assistant that synthesizes information from multiple sources."),
                HumanMessage(content=prompt)
            ])
            return response.content

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _call_llm)

    async def search_source(self, query: str, source: str) -> Dict[str, Any]:
        """Search a specific source."""
        loop = asyncio.get_event_loop()

        if source == "arxiv":
            results = await loop.run_in_executor(self.executor, _search_arxiv, query)
        elif source == "wikipedia":
            results = await loop.run_in_executor(self.executor, _search_wikipedia, query)
        elif source == "tavily":
            results = await loop.run_in_executor(self.executor, _search_tavily, query)
        elif source == "youtube":
            results = await loop.run_in_executor(self.executor, _search_youtube, query)
        else:
            return {"error": f"Unknown source: {source}"}

        return {
            "query": query,
            "source": source,
            "results": results,
            "success": True,
        }


# Singleton instance
research_agent = ResearchAgentService()
