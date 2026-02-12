from .arxiv import search_arxiv, ARXIV_AVAILABLE
from .wikipedia import search_wikipedia, WIKIPEDIA_AVAILABLE
from .tavily import search_tavily, TAVILY_AVAILABLE
from .youtube import search_youtube, YOUTUBE_AVAILABLE
from .semantic_scholar import search_semantic_scholar
from .huggingface import search_huggingface
from .github import search_github
from .papers_with_code import search_papers_with_code
from .anthropic import search_anthropic

# AI/ML domain context for searches
AI_ML_CONTEXT = "AI machine learning deep learning"
YOUTUBE_AI_ML_CONTEXT = "AI machine learning tutorial deep learning neural network"


def add_ai_ml_context(query: str, source: str = "general") -> str:
    """Add AI/ML domain context to search query for more relevant results."""
    if source == "youtube":
        return f"{query} {YOUTUBE_AI_ML_CONTEXT}"
    return f"{query} {AI_ML_CONTEXT}"


# Map tool names to functions
TOOL_FUNCTIONS = {
    "search_arxiv": search_arxiv,
    "search_wikipedia": search_wikipedia,
    "search_web": search_tavily,
    "search_youtube": search_youtube,
    "search_semantic_scholar": search_semantic_scholar,
    "search_huggingface": search_huggingface,
    "search_github": search_github,
    "search_papers_with_code": search_papers_with_code,
    "search_anthropic": search_anthropic,
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

# All source keys for initializing empty results
ALL_SOURCE_KEYS = list(TOOL_TO_SOURCE_KEY.values())
