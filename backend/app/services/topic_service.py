"""
Topic modeling service: runs BERTopic on stored articles,
persists results, computes trend data.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, delete

from app.models.article import Article
from app.models.topic import Topic, ArticleTopic
from app.nlp.topic_modeler import run_topic_modeling, get_topic_info
from app.nlp.tokenizer import tokenize
from app.nlp.sentiment_analyzer import aggregate_sentiment
from app.services.ai_service import generate_topic_summary
from app.core.config import settings

logger = logging.getLogger(__name__)


async def compute_topics(
    db: AsyncSession,
    board: Optional[str] = None,
    days: int = 30,
    top_n: int = 10,
) -> List[dict]:
    """
    Main entry: fetch recent articles, run BERTopic, persist topics & assignments.
    Returns list of topic dicts.
    """
    since = datetime.utcnow() - timedelta(days=days)
    query = select(Article).where(Article.created_at >= since)
    if board:
        query = query.where(Article.board == board)
    query = query.limit(800)

    result = await db.execute(query)
    articles = result.scalars().all()

    if len(articles) < 10:
        logger.warning(f"Not enough articles ({len(articles)}) to run topic modeling")
        return []

    # Tokenize titles+content for BERTopic
    texts = []
    for a in articles:
        tokens = tokenize(f"{a.title} {a.content}", min_length=2)
        texts.append(" ".join(tokens) if tokens else a.title)

    logger.info(f"Running BERTopic on {len(texts)} documents (board={board})")
    topic_assignments, probs, topic_model = run_topic_modeling(
        texts, settings.EMBEDDING_MODEL
    )

    if topic_model is None:
        return []

    topic_infos = get_topic_info(topic_model, top_n=top_n)

    # Map articles to topics
    article_topic_map: dict[int, list] = defaultdict(list)
    for i, (art, t_idx, prob) in enumerate(zip(articles, topic_assignments, probs)):
        if t_idx >= 0:
            article_topic_map[t_idx].append({
                "article": art,
                "prob": float(prob[t_idx]) if hasattr(prob, '__len__') else (float(prob) if prob else 0.0),
            })

    # Delete old topic assignments for this board
    board_filter = board or "all"
    old_topics = await db.execute(
        select(Topic.id).where(Topic.board == board_filter)
    )
    old_ids = [r[0] for r in old_topics.all()]
    if old_ids:
        await db.execute(
            delete(ArticleTopic).where(ArticleTopic.topic_id.in_(old_ids))
        )
        await db.execute(delete(Topic).where(Topic.id.in_(old_ids)))
        await db.commit()

    # Persist topics
    saved_topics = []
    for info in topic_infos:
        t_idx = info["topic_idx"]
        arts_in_topic = article_topic_map.get(t_idx, [])

        # Sentiment for this topic
        sentiment_inputs = [
            {"label": a["article"].sentiment_label or "neutral",
             "score": a["article"].sentiment_score or 0.5}
            for a in arts_in_topic
        ]
        sent = aggregate_sentiment(sentiment_inputs) if sentiment_inputs else {
            "positive": 0, "neutral": 100, "negative": 0
        }

        topic = Topic(
            board=board_filter,
            topic_idx=t_idx,
            name=info["name"],
            keywords=info["keywords"],
            article_count=info["count"],
            sentiment_positive=sent["positive"],
            sentiment_neutral=sent["neutral"],
            sentiment_negative=sent["negative"],
            computed_at=datetime.utcnow(),
        )
        db.add(topic)
        await db.flush()  # get topic.id

        # Persist article-topic assignments
        for entry in arts_in_topic:
            at = ArticleTopic(
                article_id=entry["article"].id,
                topic_id=topic.id,
                topic_idx=t_idx,
                probability=entry["prob"],
            )
            db.add(at)

        saved_topics.append({
            "id": topic.id,
            "topic_idx": t_idx,
            "name": info["name"],
            "keywords": info["keywords"],
            "article_count": info["count"],
            "sentiment": {
                "positive": sent["positive"],
                "neutral": sent["neutral"],
                "negative": sent["negative"],
            },
            "ai_summary": None,
        })

    await db.commit()
    logger.info(f"Saved {len(saved_topics)} topics for board={board_filter}")
    return saved_topics


async def get_topics(
    db: AsyncSession,
    board: Optional[str] = None,
) -> List[dict]:
    """Fetch latest computed topics from DB."""
    board_filter = board or "all"
    result = await db.execute(
        select(Topic)
        .where(Topic.board == board_filter)
        .order_by(Topic.article_count.desc())
    )
    topics = result.scalars().all()
    return [
        {
            "id": t.id,
            "topic_idx": t.topic_idx,
            "name": t.name,
            "keywords": t.keywords,
            "article_count": t.article_count,
            "sentiment": {
                "positive": t.sentiment_positive,
                "neutral": t.sentiment_neutral,
                "negative": t.sentiment_negative,
            },
            "ai_summary": t.ai_summary,
            "computed_at": t.computed_at.isoformat() if t.computed_at else None,
        }
        for t in topics
    ]


async def get_topic_trend(
    db: AsyncSession,
    topic_id: int,
    days: int = 14,
) -> List[dict]:
    """Daily article count for a topic (trend data)."""
    since = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(Article.created_at).label("date"),
            func.count(Article.id).label("count"),
        )
        .join(ArticleTopic, ArticleTopic.article_id == Article.id)
        .where(
            and_(
                ArticleTopic.topic_id == topic_id,
                Article.created_at >= since,
            )
        )
        .group_by(func.date(Article.created_at))
        .order_by(func.date(Article.created_at))
    )
    return [{"date": str(r[0]), "count": r[1]} for r in result.all()]


async def get_topic_articles(
    db: AsyncSession,
    topic_id: int,
    limit: int = 20,
) -> List[dict]:
    """Top articles for a topic (by probability)."""
    result = await db.execute(
        select(Article, ArticleTopic.probability)
        .join(ArticleTopic, ArticleTopic.article_id == Article.id)
        .where(ArticleTopic.topic_id == topic_id)
        .order_by(ArticleTopic.probability.desc(), Article.push_count.desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "author": a.author,
            "push_count": a.push_count,
            "url": a.url,
            "sentiment_label": a.sentiment_label,
            "probability": round(prob, 4),
        }
        for a, prob in rows
    ]


async def generate_and_save_summary(
    db: AsyncSession,
    topic_id: int,
    board: str,
) -> str:
    """Generate Gemini summary for a topic and persist it."""
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        return ""

    # Get sample titles
    arts = await get_topic_articles(db, topic_id, limit=20)
    titles = [a["title"] for a in arts]

    summary = await generate_topic_summary(
        topic_name=topic.name,
        keywords=topic.keywords,
        sample_titles=titles,
        board=board,
    )

    topic.ai_summary = summary
    await db.commit()
    return summary
