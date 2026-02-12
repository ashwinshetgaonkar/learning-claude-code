"""Core agentic loop for the Research Agent."""

import asyncio
import json
import logging
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from groq import AsyncGroq
from ...config import settings
from .schemas import TOOL_SCHEMAS
from .tools import (
    TOOL_FUNCTIONS, TOOL_TO_SOURCE_KEY, ALL_SOURCE_KEYS,
    add_ai_ml_context,
    ARXIV_AVAILABLE, WIKIPEDIA_AVAILABLE, TAVILY_AVAILABLE, YOUTUBE_AVAILABLE,
    search_arxiv, search_wikipedia, search_tavily, search_youtube,
    search_semantic_scholar, search_huggingface, search_github,
    search_papers_with_code, search_anthropic,
)

logger = logging.getLogger(__name__)

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


def _empty_sources() -> Dict[str, Any]:
    """Return a dict with all source keys initialized to empty values."""
    sources = {key: [] for key in ALL_SOURCE_KEYS}
    sources["tavily"] = None  # tavily returns a dict, not a list
    return sources


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
                logger.warning("GROQ_API_KEY not configured - research agent will use fallback mode")
            self._initialized = True
        return self._client

    def _get_available_tools(self) -> tuple:
        """Return (tool_schemas, func_map) for currently available tools."""
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

        all_sources = _empty_sources()

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
                logger.warning("Groq API error: %s", e)
                return await self._fallback_search(query)

            msg = response.choices[0].message

            # No tool calls -- LLM returned its final text response
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

        # Exhausted iterations -- force a final synthesis
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
            logger.warning("Groq API error on final synthesis: %s", e)
            return {
                "query": query,
                "sources": all_sources,
                "success": True,
            }

    async def _fallback_search(self, query: str) -> Dict[str, Any]:
        """Run all available tools in parallel without LLM synthesis."""
        loop = asyncio.get_event_loop()
        enhanced_query = add_ai_ml_context(query)

        tasks = []
        task_names = []

        # Always-available sources
        for name, fn in [
            ("arxiv", search_arxiv),
            ("wikipedia", search_wikipedia),
            ("semantic_scholar", search_semantic_scholar),
            ("huggingface", search_huggingface),
            ("github", search_github),
            ("papers_with_code", search_papers_with_code),
        ]:
            tasks.append(loop.run_in_executor(self.executor, fn, enhanced_query))
            task_names.append(name)

        # Anthropic doesn't get AI/ML context added (query is specific enough)
        tasks.append(loop.run_in_executor(self.executor, search_anthropic, query))
        task_names.append("anthropic")

        # Optional sources (need API keys)
        if settings.tavily_api_key:
            tasks.append(loop.run_in_executor(self.executor, search_tavily, enhanced_query))
            task_names.append("tavily")
        if settings.youtube_api_key:
            youtube_query = add_ai_ml_context(query, "youtube")
            tasks.append(loop.run_in_executor(self.executor, search_youtube, youtube_query))
            task_names.append("youtube")

        results = await asyncio.gather(*tasks, return_exceptions=True)

        sources = _empty_sources()
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

        # Build a lookup from source key to (function, query)
        enhanced_query = add_ai_ml_context(query)
        source_dispatch = {
            "arxiv": (search_arxiv, enhanced_query),
            "wikipedia": (search_wikipedia, enhanced_query),
            "tavily": (search_tavily, enhanced_query),
            "youtube": (search_youtube, add_ai_ml_context(query, "youtube")),
            "semantic_scholar": (search_semantic_scholar, enhanced_query),
            "huggingface": (search_huggingface, enhanced_query),
            "github": (search_github, enhanced_query),
            "papers_with_code": (search_papers_with_code, enhanced_query),
            "anthropic": (search_anthropic, query),
        }

        entry = source_dispatch.get(source)
        if not entry:
            return {"error": f"Unknown source: {source}"}

        fn, q = entry
        results = await loop.run_in_executor(self.executor, fn, q)

        return {
            "query": query,
            "source": source,
            "results": results,
            "success": True,
        }
