import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db

logger = logging.getLogger(__name__)

try:
    from .routers import articles_router, sources_router, bookmarks_router, export_router, agents_router
except Exception as e:
    logger.exception("Failed to import routers")
    raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.exception("Failed to initialize database")
        raise
    yield


app = FastAPI(
    title="AI News Tracker",
    description="Aggregate, summarize, and organize AI news from multiple sources",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(articles_router)
app.include_router(sources_router)
app.include_router(bookmarks_router)
app.include_router(export_router)
app.include_router(agents_router)


@app.get("/")
async def root():
    return {
        "name": "AI News Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
