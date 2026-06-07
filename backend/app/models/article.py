from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    board = Column(String(50), nullable=False, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, default="")
    author = Column(String(100), default="")
    push_count = Column(Integer, default=0)
    boo_count = Column(Integer, default=0)
    url = Column(String(500), unique=True, nullable=False)
    published_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sentiment_label = Column(String(20), nullable=True)
    sentiment_score = Column(Float, nullable=True)

    __table_args__ = (
        Index("ix_articles_board_published", "board", "published_at"),
    )


class KeywordStat(Base):
    __tablename__ = "keyword_stats"

    id = Column(Integer, primary_key=True, index=True)
    board = Column(String(50), nullable=False, index=True)
    keyword = Column(String(100), nullable=False)
    count = Column(Integer, default=0)
    tfidf_score = Column(Float, default=0.0)
    date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_keyword_board_date", "board", "date"),
    )
