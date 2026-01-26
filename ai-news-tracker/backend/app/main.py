import sys
print("Loading main.py...", file=sys.stderr, flush=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

print("Importing config...", file=sys.stderr, flush=True)
from .config import settings

print("Importing database...", file=sys.stderr, flush=True)
from .database import init_db

print("Importing routers...", file=sys.stderr, flush=True)
try:
    from .routers import articles_router, sources_router, bookmarks_router, export_router, agents_router
    print("Routers imported successfully", file=sys.stderr, flush=True)
except Exception as e:
    print(f"ERROR importing routers: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc()
    raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    import sys
    print("Starting application...", file=sys.stderr, flush=True)
    try:
        await init_db()
        print("Database initialized successfully", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"ERROR initializing database: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        raise
    yield
    # Shutdown
    pass


app = FastAPI(
    title="AI News Tracker",
    description="Aggregate, summarize, and organize AI news from multiple sources",
    version="1.0.0",
    lifespan=lifespan,
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
