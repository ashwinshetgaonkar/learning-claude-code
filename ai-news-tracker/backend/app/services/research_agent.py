"""
Research Agent Service using Groq Agentic Tool-Use Loop

Uses an agentic loop where the LLM decides which tools to call,
executes them, and iterates until it has enough information to
synthesize a response. Tools available:
- arXiv: Academic papers
- Wikipedia: General knowledge
- Tavily: Web search
- YouTube: Video search
- Semantic Scholar: Papers with citation data
- HuggingFace: ML models
- GitHub: Repositories
- Papers With Code: Papers with implementations
- Anthropic: Research articles
"""

import asyncio
import json
import sys
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import httpx
from bs4 import BeautifulSoup
from groq import AsyncGroq
from ..config import settings

# Import optional tool dependencies with fallback
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


# AI/ML domain context for searches
AI_ML_CONTEXT = "AI machine learning deep learning"
YOUTUBE_AI_ML_CONTEXT = "AI machine learning tutorial deep learning neural network"


def _add_ai_ml_context(query: str, source: str = "general") -> str:
    """Add AI/ML domain context to search query for more relevant results."""
    if source == "youtube":
        return f"{query} {YOUTUBE_AI_ML_CONTEXT}"
    return f"{query} {AI_ML_CONTEXT}"


# ---------- Tool functions (unchanged) ----------

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


def _search_semantic_scholar(query: str, max_results: int = 5) -> List[Dict]:
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


def _search_huggingface(query: str, max_results: int = 5) -> List[Dict]:
    """Search HuggingFace Hub for models."""
    try:
        resp = httpx.get(
            "https://huggingface.co/api/models",
            params={
                "search": query,
                "sort": "downloads",
                "direction": "-1",
                "limit": max_results,
            },
            timeout=15,
        )
        resp.raise_for_status()
        models = resp.json()
        results = []
        for model in models[:max_results]:
            model_id = model.get("modelId", model.get("id", ""))
            results.append({
                "model_id": model_id,
                "author": model_id.split("/")[0] if "/" in model_id else "",
                "downloads": model.get("downloads", 0),
                "likes": model.get("likes", 0),
                "tags": model.get("tags", [])[:5],
                "url": f"https://huggingface.co/{model_id}",
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def _search_github(query: str, max_results: int = 5) -> List[Dict]:
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


def _search_papers_with_code(query: str, max_results: int = 5) -> List[Dict]:
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
                authors = [a.get("name", "") for a in paper.get("authors", [])[:3]]
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


def _search_anthropic(query: str, max_results: int = 5) -> List[Dict]:
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


# ---------- Tool schemas for Groq function calling ----------

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_arxiv",
            "description": "Search arXiv for academic papers and preprints about AI, machine learning, and related topics. Use for research, algorithms, models, or technical concepts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for arXiv. Include relevant technical terms."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of papers to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search Wikipedia for general knowledge articles. Use for background information, definitions, history, or broader context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Wikipedia."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of articles to return (1-5, default 3)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for recent news, blog posts, tutorials, and general content. Use for current events, recent developments, or practical information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Web search query."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_youtube",
            "description": "Search YouTube for educational videos, tutorials, and presentations. Use when visual explanations or conference talks would be helpful.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "YouTube search query. Include terms like 'tutorial', 'explained' for better results."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of videos to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_semantic_scholar",
            "description": "Search Semantic Scholar for academic papers with citation counts. Use for finding highly-cited or recent research papers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Semantic Scholar."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of papers to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_huggingface",
            "description": "Search HuggingFace Hub for ML models. Use when looking for pre-trained models, fine-tuned models, or model architectures.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for HuggingFace models."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of models to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_github",
            "description": "Search GitHub for ML/AI repositories. Use for finding open-source implementations, libraries, and tools.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for GitHub repositories."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of repos to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_papers_with_code",
            "description": "Search Papers With Code for papers that have code implementations. Use when looking for reproducible research with code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Papers With Code."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_anthropic",
            "description": "Search Anthropic's research page for articles about Claude, constitutional AI, and AI safety. Use for Anthropic-specific research.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Anthropic research."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of articles to return (1-5, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
]

# Map tool names to functions
TOOL_FUNCTIONS = {
    "search_arxiv": _search_arxiv,
    "search_wikipedia": _search_wikipedia,
    "search_web": _search_tavily,
    "search_youtube": _search_youtube,
    "search_semantic_scholar": _search_semantic_scholar,
    "search_huggingface": _search_huggingface,
    "search_github": _search_github,
    "search_papers_with_code": _search_papers_with_code,
    "search_anthropic": _search_anthropic,
}

# Map tool names to source keys expected by the frontend
TOOL_TO_SOURCE_KEY = {
    "search_arxiv": "arxiv",
    "search_wikipedia": "wikipedia",
    "search_web": "tavily",
    "search_youtube": "youtube",
    "search_semantic_scholar": "semantic_scholar",
    "search_huggingface": "huggingface",
    "search_github": "github",
    "search_papers_with_code": "papers_with_code",
    "search_anthropic": "anthropic",
}

MAX_ITERATIONS = 5
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = (
    "You are a research assistant specializing in AI and machine learning. "
    "You have access to tools for searching academic papers (arXiv, Semantic Scholar, Papers With Code), "
    "Wikipedia, the web (Tavily), YouTube, HuggingFace models, GitHub repositories, "
    "and Anthropic research articles. Use the most relevant tools to find information "
    "about the user's query. You can call multiple tools and refine your searches. "
    "After gathering enough information, provide a comprehensive 2-3 paragraph summary "
    "that synthesizes findings and cites which sources the information comes from."
)


class ResearchAgentService:
    """Service for searching research data using a Groq agentic tool-use loop."""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)
        self._client = None
        self._initialized = False

    @property
    def client(self):
        """Lazy initialization of Groq client."""
        if not self._initialized:
            if settings.groq_api_key:
                self._client = AsyncGroq(api_key=settings.groq_api_key)
            else:
                print("Warning: GROQ_API_KEY not configured. Research agent will use fallback mode.", file=sys.stderr)
            self._initialized = True
        return self._client

    def _get_available_tools(self) -> tuple:
        """Return (tool_schemas, func_map) for currently available tools."""
        # Tools that require availability checks
        skip = set()
        if not ARXIV_AVAILABLE:
            skip.add("search_arxiv")
        if not WIKIPEDIA_AVAILABLE:
            skip.add("search_wikipedia")
        if not (TAVILY_AVAILABLE and settings.tavily_api_key):
            skip.add("search_web")
        if not (YOUTUBE_AVAILABLE and settings.youtube_api_key):
            skip.add("search_youtube")

        tools = []
        func_map = {}
        for schema in TOOL_SCHEMAS:
            name = schema["function"]["name"]
            if name not in skip and name in TOOL_FUNCTIONS:
                tools.append(schema)
                func_map[name] = TOOL_FUNCTIONS[name]

        return tools, func_map

    def _collect_source(self, all_sources: Dict, fn_name: str, result: Any):
        """Map tool results into the sources dict the frontend expects."""
        key = TOOL_TO_SOURCE_KEY.get(fn_name)
        if key:
            all_sources[key] = result

    async def search(self, query: str) -> Dict[str, Any]:
        """
        Search using an agentic tool-use loop.

        The LLM decides which tools to call, executes them, reads the results,
        and iterates until it has enough information to provide a synthesis.
        Falls back to parallel search if no Groq API key is configured.
        """
        if not self.client:
            return await self._fallback_search(query)

        tools, func_map = self._get_available_tools()
        if not tools:
            return await self._fallback_search(query)

        # Collected source results across all iterations
        all_sources: Dict[str, Any] = {
            "arxiv": [], "wikipedia": [], "tavily": None, "youtube": [],
            "semantic_scholar": [], "huggingface": [], "github": [],
            "papers_with_code": [], "anthropic": [],
        }

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Research the following topic in the context of AI and machine learning: {query}"},
        ]

        loop = asyncio.get_event_loop()

        for _ in range(MAX_ITERATIONS):
            try:
                response = await self.client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0,
                    max_tokens=1024,
                )
            except Exception as e:
                print(f"Groq API error: {e}", file=sys.stderr)
                return await self._fallback_search(query)

            msg = response.choices[0].message

            # No tool calls — LLM returned its final text response
            if not msg.tool_calls:
                return {
                    "query": query,
                    "response": msg.content,
                    "sources": all_sources,
                    "success": True,
                }

            # Append assistant message (with tool_calls) to conversation
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            })

            # Execute each tool call
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name

                try:
                    fn_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {"query": query}

                if fn_name in func_map:
                    result = await loop.run_in_executor(
                        self.executor,
                        partial(func_map[fn_name], **fn_args),
                    )
                    self._collect_source(all_sources, fn_name, result)
                else:
                    result = {"error": f"Unknown tool: {fn_name}"}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str),
                })

        # Exhausted iterations — force a final synthesis
        messages.append({
            "role": "user",
            "content": "Please provide your final summary now based on all the information gathered.",
        })
        try:
            final = await self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0,
                max_tokens=1024,
            )
            return {
                "query": query,
                "response": final.choices[0].message.content,
                "sources": all_sources,
                "success": True,
            }
        except Exception as e:
            print(f"Groq API error on final synthesis: {e}", file=sys.stderr)
            return {
                "query": query,
                "sources": all_sources,
                "success": True,
            }

    async def _fallback_search(self, query: str) -> Dict[str, Any]:
        """Run all available tools in parallel without LLM synthesis."""
        loop = asyncio.get_event_loop()
        enhanced_query = _add_ai_ml_context(query)

        tasks = []
        task_names = []

        # Always-available sources
        tasks.append(loop.run_in_executor(self.executor, _search_arxiv, enhanced_query))
        task_names.append("arxiv")
        tasks.append(loop.run_in_executor(self.executor, _search_wikipedia, enhanced_query))
        task_names.append("wikipedia")
        tasks.append(loop.run_in_executor(self.executor, _search_semantic_scholar, enhanced_query))
        task_names.append("semantic_scholar")
        tasks.append(loop.run_in_executor(self.executor, _search_huggingface, enhanced_query))
        task_names.append("huggingface")
        tasks.append(loop.run_in_executor(self.executor, _search_github, enhanced_query))
        task_names.append("github")
        tasks.append(loop.run_in_executor(self.executor, _search_papers_with_code, enhanced_query))
        task_names.append("papers_with_code")
        tasks.append(loop.run_in_executor(self.executor, _search_anthropic, query))
        task_names.append("anthropic")

        # Optional sources (need API keys)
        if settings.tavily_api_key:
            tasks.append(loop.run_in_executor(self.executor, _search_tavily, enhanced_query))
            task_names.append("tavily")
        if settings.youtube_api_key:
            youtube_query = _add_ai_ml_context(query, "youtube")
            tasks.append(loop.run_in_executor(self.executor, _search_youtube, youtube_query))
            task_names.append("youtube")

        results = await asyncio.gather(*tasks, return_exceptions=True)

        sources = {
            "arxiv": [], "wikipedia": [], "tavily": None, "youtube": [],
            "semantic_scholar": [], "huggingface": [], "github": [],
            "papers_with_code": [], "anthropic": [],
        }
        for name, result in zip(task_names, results):
            if not isinstance(result, Exception):
                sources[name] = result

        return {
            "query": query,
            "sources": sources,
            "success": True,
        }

    async def search_source(self, query: str, source: str) -> Dict[str, Any]:
        """Search a specific source."""
        loop = asyncio.get_event_loop()

        # Add AI/ML context for more relevant results
        enhanced_query = _add_ai_ml_context(query)

        if source == "arxiv":
            results = await loop.run_in_executor(self.executor, _search_arxiv, enhanced_query)
        elif source == "wikipedia":
            results = await loop.run_in_executor(self.executor, _search_wikipedia, enhanced_query)
        elif source == "tavily":
            results = await loop.run_in_executor(self.executor, _search_tavily, enhanced_query)
        elif source == "youtube":
            youtube_query = _add_ai_ml_context(query, "youtube")
            results = await loop.run_in_executor(self.executor, _search_youtube, youtube_query)
        elif source == "semantic_scholar":
            results = await loop.run_in_executor(self.executor, _search_semantic_scholar, enhanced_query)
        elif source == "huggingface":
            results = await loop.run_in_executor(self.executor, _search_huggingface, enhanced_query)
        elif source == "github":
            results = await loop.run_in_executor(self.executor, _search_github, enhanced_query)
        elif source == "papers_with_code":
            results = await loop.run_in_executor(self.executor, _search_papers_with_code, enhanced_query)
        elif source == "anthropic":
            results = await loop.run_in_executor(self.executor, _search_anthropic, query)
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
