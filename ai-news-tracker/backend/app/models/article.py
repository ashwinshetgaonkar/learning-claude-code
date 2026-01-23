from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from ..database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # 'arxiv', 'huggingface', 'blog', 'aggregator'
    source_id = Column(String(255), unique=True, index=True)  # Original ID from source
    title = Column(String(500), nullable=False)
    authors = Column(JSON, default=list)  # JSON array of author names
    abstract = Column(Text)
    content = Column(Text)  # Full content if available
    summary = Column(Text)  # AI-generated summary
    url = Column(String(1000), nullable=False)
    pdf_url = Column(String(1000))  # Direct PDF link if available
    categories = Column(JSON, default=list)  # JSON array: ['NLP', 'LLM']
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, server_default=func.now())
    is_bookmarked = Column(Boolean, default=False, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "source_id": self.source_id,
            "title": self.title,
            "authors": self.authors or [],
            "abstract": self.abstract,
            "content": self.content,
            "summary": self.summary,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "categories": self.categories or [],
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "is_bookmarked": self.is_bookmarked,
        }
