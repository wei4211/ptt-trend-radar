from collections import Counter
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.article import Article, KeywordStat
from app.nlp.tokenizer import tokenize, tokenize_batch, extract_keywords_tfidf
from app.nlp.keyword_extractor import extract_keywords_fast, count_tokens
from app.nlp.sentiment_analyzer import analyze_text, aggregate_sentiment
from app.nlp.wordcloud_generator import generate_wordcloud
from app.scraper.ptt_scraper import scrape_board
import logging

logger = logging.getLogger(__name__)

# Simple TTL cache: key → (result, expires_at)
_cache: dict = {}
_CACHE_TTL = 300  # 5 minutes


def _cache_get(key: str):
    entry = _cache.get(key)
    if entry and time.time() < entry[1]:
        return entry[0]
    return None


def _cache_set(key: str, value):
    _cache[key] = (value, time.time() + _CACHE_TTL)


async def upsert_articles(db: AsyncSession, articles: List[dict]) -> int:
    """Insert new articles, skip duplicates by URL."""
    inserted = 0
    for data in articles:
        existing = await db.execute(select(Article).where(Article.url == data["url"]))
        if existing.scalar_one_or_none():
            continue

        sentiment = analyze_text(f"{data['title']} {data['content']}")
        article = Article(
            board=data["board"],
            title=data["title"],
            content=data["content"],
            author=data["author"],
            push_count=data["push_count"],
            boo_count=data["boo_count"],
            url=data["url"],
            published_at=data["published_at"],
            sentiment_label=sentiment["label"],
            sentiment_score=sentiment["score"],
        )
        db.add(article)
        inserted += 1

    await db.commit()
    return inserted


async def run_scrape_and_analyze(db: AsyncSession, board: str, pages: int = 3) -> dict:
    """Scrape board and store results."""
    logger.info(f"Scraping board: {board}")
    articles = await scrape_board(board, pages=pages)
    inserted = await upsert_articles(db, articles)
    logger.info(f"Inserted {inserted} new articles from {board}")
    return {"board": board, "scraped": len(articles), "inserted": inserted}


async def get_overview_stats(db: AsyncSession, board: Optional[str] = None, days: int = 1) -> dict:
    since = datetime.utcnow() - timedelta(days=days)
    query = select(func.count(Article.id), func.avg(Article.sentiment_score))

    if board:
        query = query.where(and_(Article.board == board, Article.created_at >= since))
    else:
        query = query.where(Article.created_at >= since)

    result = await db.execute(query)
    row = result.one()
    total = row[0] or 0
    avg_score = round(row[1] or 0.5, 4)

    # Sentiment distribution
    sent_query = select(Article.sentiment_label, func.count(Article.id)).group_by(Article.sentiment_label)
    if board:
        sent_query = sent_query.where(and_(Article.board == board, Article.created_at >= since))
    else:
        sent_query = sent_query.where(Article.created_at >= since)

    sent_result = await db.execute(sent_query)
    sent_dist = {row[0]: row[1] for row in sent_result.all() if row[0]}

    return {
        "total_articles": total,
        "avg_sentiment_score": avg_score,
        "sentiment_distribution": sent_dist,
        "period_days": days,
        "board": board or "all",
    }


async def get_keywords(
    db: AsyncSession,
    board: Optional[str] = None,
    days: int = 7,
    top_n: int = 20,
) -> List[dict]:
    cache_key = f"keywords:{board}:{days}:{top_n}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    since = datetime.utcnow() - timedelta(days=days)
    query = select(Article.title, Article.content)
    if board:
        query = query.where(and_(Article.board == board, Article.created_at >= since))
    else:
        query = query.where(Article.created_at >= since)

    result = await db.execute(query)
    rows = result.all()

    import re as _re
    def _clean_title(title: str) -> str:
        # Remove PTT article type tags like [問卦] [公告] Re: Fw:
        t = _re.sub(r"\[.*?\]", "", title)
        t = _re.sub(r"^(Re|Fw|FW|re|fw):\s*", "", t)
        return t.strip()

    # Use content as primary source; title as supplement (without bracket tags)
    texts = [f"{r[1][:600]} {_clean_title(r[0])}" for r in rows]
    if not texts:
        return []

    def _nlp_work():
        kws = extract_keywords_fast(texts, top_n)
        freq = count_tokens(texts)
        return [
            {"keyword": w, "tfidf_score": round(s, 4), "count": freq.get(w, 0)}
            for w, s in kws
        ]

    loop = asyncio.get_running_loop()
    result_data = await loop.run_in_executor(None, _nlp_work)
    _cache_set(cache_key, result_data)
    return result_data


async def get_sentiment_overview(
    db: AsyncSession,
    board: Optional[str] = None,
    days: int = 7,
) -> dict:
    since = datetime.utcnow() - timedelta(days=days)
    query = select(Article.sentiment_label, Article.sentiment_score)
    if board:
        query = query.where(and_(Article.board == board, Article.created_at >= since))
    else:
        query = query.where(Article.created_at >= since)

    result = await db.execute(query)
    rows = result.all()
    results = [{"label": r[0] or "neutral", "score": r[1] or 0.5} for r in rows]
    return aggregate_sentiment(results)


async def get_sentiment_trend(
    db: AsyncSession,
    board: Optional[str] = None,
    days: int = 14,
) -> List[dict]:
    """Daily sentiment averages for trend chart."""
    since = datetime.utcnow() - timedelta(days=days)
    query = (
        select(
            func.date(Article.created_at).label("date"),
            func.avg(Article.sentiment_score).label("avg_score"),
            func.count(Article.id).label("count"),
        )
        .where(Article.created_at >= since)
        .group_by(func.date(Article.created_at))
        .order_by(func.date(Article.created_at))
    )
    if board:
        query = query.where(Article.board == board)

    result = await db.execute(query)
    return [
        {
            "date": str(r[0]),
            "avg_score": round(r[1] or 0.5, 4),
            "article_count": r[2],
        }
        for r in result.all()
    ]


async def get_wordcloud_data(
    db: AsyncSession,
    board: Optional[str] = None,
    days: int = 7,
) -> str:
    """Generate word cloud image as base64."""
    cache_key = f"wordcloud:{board}:{days}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    since = datetime.utcnow() - timedelta(days=days)
    query = select(Article.title, Article.content)
    if board:
        query = query.where(and_(Article.board == board, Article.created_at >= since))
    else:
        query = query.where(Article.created_at >= since)
    query = query.limit(300)

    result = await db.execute(query)
    rows = result.all()
    import re as _re2
    def _clean(t): return _re2.sub(r"\[.*?\]|^(Re|Fw|FW):\s*", "", t).strip()
    texts = [f"{r[1]} {_clean(r[0])}" for r in rows]

    def _build_wordcloud():
        freq = count_tokens(texts)
        return generate_wordcloud(dict(freq.most_common(100)))

    loop = asyncio.get_running_loop()
    img = await loop.run_in_executor(None, _build_wordcloud)
    _cache_set(cache_key, img)
    return img


async def get_articles(
    db: AsyncSession,
    board: Optional[str] = None,
    days: int = 7,
    limit: int = 50,
    offset: int = 0,
) -> List[dict]:
    since = datetime.utcnow() - timedelta(days=days)
    query = select(Article).where(Article.created_at >= since)
    if board:
        query = query.where(Article.board == board)
    query = query.order_by(Article.push_count.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    articles = result.scalars().all()
    return [
        {
            "id": a.id,
            "board": a.board,
            "title": a.title,
            "author": a.author,
            "push_count": a.push_count,
            "boo_count": a.boo_count,
            "url": a.url,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "sentiment_label": a.sentiment_label,
            "sentiment_score": a.sentiment_score,
        }
        for a in articles
    ]
