"""
Research Agent Service using Groq Agentic Tool-Use Loop

Uses an agentic loop where the LLM decides which tools to call,
executes them, and iterates until it has enough information to
synthesize a response. Tools available:
- arXiv: Academic papers
- Wikipedia: General knowledge
- Tavily: Web search
- YouTube: Video search
"""

import asyncio
import json
import sys
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from functools import partial

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
]

# Map tool names to functions
TOOL_FUNCTIONS = {
    "search_arxiv": _search_arxiv,
    "search_wikipedia": _search_wikipedia,
    "search_web": _search_tavily,
    "search_youtube": _search_youtube,
}

# Map tool names to source keys expected by the frontend
TOOL_TO_SOURCE_KEY = {
    "search_arxiv": "arxiv",
    "search_wikipedia": "wikipedia",
    "search_web": "tavily",
    "search_youtube": "youtube",
}

MAX_ITERATIONS = 5
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = (
    "You are a research assistant specializing in AI and machine learning. "
    "You have access to tools for searching academic papers (arXiv), Wikipedia, "
    "the web (Tavily), and YouTube. Use the most relevant tools to find information "
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
        tools = []
        func_map = {}

        if ARXIV_AVAILABLE:
            tools.append(TOOL_SCHEMAS[0])
            func_map["search_arxiv"] = _search_arxiv

        if WIKIPEDIA_AVAILABLE:
            tools.append(TOOL_SCHEMAS[1])
            func_map["search_wikipedia"] = _search_wikipedia

        if TAVILY_AVAILABLE and settings.tavily_api_key:
            tools.append(TOOL_SCHEMAS[2])
            func_map["search_web"] = _search_tavily

        if YOUTUBE_AVAILABLE and settings.youtube_api_key:
            tools.append(TOOL_SCHEMAS[3])
            func_map["search_youtube"] = _search_youtube

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
            "arxiv": [], "wikipedia": [], "tavily": None, "youtube": []
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

        # Run all searches concurrently
        arxiv_task = loop.run_in_executor(self.executor, _search_arxiv, enhanced_query)
        wiki_task = loop.run_in_executor(self.executor, _search_wikipedia, enhanced_query)

        tasks = [arxiv_task, wiki_task]
        task_names = ['arxiv', 'wiki']

        if settings.tavily_api_key:
            tavily_task = loop.run_in_executor(self.executor, _search_tavily, enhanced_query)
            tasks.append(tavily_task)
            task_names.append('tavily')

        if settings.youtube_api_key:
            youtube_query = _add_ai_ml_context(query, "youtube")
            youtube_task = loop.run_in_executor(self.executor, _search_youtube, youtube_query)
            tasks.append(youtube_task)
            task_names.append('youtube')

        results = await asyncio.gather(*tasks, return_exceptions=True)

        arxiv_results = results[0] if not isinstance(results[0], Exception) else []
        wiki_results = results[1] if not isinstance(results[1], Exception) else []

        tavily_idx = task_names.index('tavily') if 'tavily' in task_names else -1
        youtube_idx = task_names.index('youtube') if 'youtube' in task_names else -1

        tavily_results = results[tavily_idx] if tavily_idx >= 0 and not isinstance(results[tavily_idx], Exception) else None
        youtube_results = results[youtube_idx] if youtube_idx >= 0 and not isinstance(results[youtube_idx], Exception) else None

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
