from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, text
from .config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.database_url,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Create FTS5 virtual table for full-text search
        await conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
                title, abstract, summary, content,
                content='articles',
                content_rowid='id'
            )
        """))
        # Create triggers to keep FTS in sync
        await conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS articles_ai AFTER INSERT ON articles BEGIN
                INSERT INTO articles_fts(rowid, title, abstract, summary, content)
                VALUES (new.id, new.title, new.abstract, new.summary, new.content);
            END
        """))
        await conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS articles_ad AFTER DELETE ON articles BEGIN
                INSERT INTO articles_fts(articles_fts, rowid, title, abstract, summary, content)
                VALUES ('delete', old.id, old.title, old.abstract, old.summary, old.content);
            END
        """))
        await conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS articles_au AFTER UPDATE ON articles BEGIN
                INSERT INTO articles_fts(articles_fts, rowid, title, abstract, summary, content)
                VALUES ('delete', old.id, old.title, old.abstract, old.summary, old.content);
                INSERT INTO articles_fts(rowid, title, abstract, summary, content)
                VALUES (new.id, new.title, new.abstract, new.summary, new.content);
            END
        """))
