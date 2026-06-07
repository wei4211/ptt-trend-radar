from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Index
from datetime import datetime
from app.db.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    board = Column(String(50), nullable=False, index=True)
    topic_idx = Column(Integer, nullable=False)       # BERTopic internal index
    name = Column(String(200), nullable=False)        # Auto-generated from keywords
    keywords = Column(JSON, nullable=False, default=list)  # List[str]
    article_count = Column(Integer, default=0)
    sentiment_positive = Column(Float, default=0.0)
    sentiment_neutral = Column(Float, default=0.0)
    sentiment_negative = Column(Float, default=0.0)
    ai_summary = Column(Text, nullable=True)
    computed_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_topics_board_computed", "board", "computed_at"),
    )


class ArticleTopic(Base):
    __tablename__ = "article_topics"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, nullable=False, index=True)
    topic_id = Column(Integer, nullable=False, index=True)  # FK to topics.id
    topic_idx = Column(Integer, nullable=False)
    probability = Column(Float, default=0.0)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_article_topics_article", "article_id"),
        Index("ix_article_topics_topic", "topic_id"),
    )
