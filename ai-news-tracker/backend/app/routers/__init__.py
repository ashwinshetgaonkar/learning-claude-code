from .articles import router as articles_router
from .sources import router as sources_router
from .bookmarks import router as bookmarks_router
from .export import router as export_router

# Import agents router with fallback if dependencies are missing
try:
    from .agents import router as agents_router
except ImportError as e:
    import sys
    print(f"Warning: Could not import agents router: {e}", file=sys.stderr)
    from fastapi import APIRouter
    agents_router = APIRouter(prefix="/api/agents", tags=["agents"])

    @agents_router.get("/sources")
    async def sources_unavailable():
        return {"error": "Research agents unavailable - missing dependencies", "sources": []}

    @agents_router.get("/search")
    async def search_unavailable():
        return {"error": "Research agents unavailable - missing dependencies"}

__all__ = ["articles_router", "sources_router", "bookmarks_router", "export_router", "agents_router"]
