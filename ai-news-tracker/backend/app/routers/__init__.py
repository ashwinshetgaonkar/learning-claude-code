import logging

from .articles import router as articles_router
from .sources import router as sources_router
from .bookmarks import router as bookmarks_router
from .export import router as export_router

logger = logging.getLogger(__name__)

# Import agents router with fallback if dependencies are missing
try:
    from .agents import router as agents_router
except Exception as e:
    logger.warning("Could not import agents router: %s: %s", type(e).__name__, e, exc_info=True)
    from fastapi import APIRouter
    agents_router = APIRouter(prefix="/api/agents", tags=["agents"])

    @agents_router.get("/sources")
    async def sources_unavailable():
        return {"error": "Research agents unavailable - missing dependencies", "sources": []}

    @agents_router.get("/search")
    async def search_unavailable():
        return {"error": "Research agents unavailable - missing dependencies"}

__all__ = ["articles_router", "sources_router", "bookmarks_router", "export_router", "agents_router"]
