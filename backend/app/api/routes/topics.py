from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.services import topic_service as svc
from app.core.config import settings

router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("/compute")
async def compute_topics(
    background_tasks: BackgroundTasks,
    board: Optional[str] = Query(None),
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger BERTopic computation on stored articles.
    Runs in background — use GET /topics to fetch results after.
    """
    if board and board not in settings.SUPPORTED_BOARDS:
        raise HTTPException(400, f"board must be one of {settings.SUPPORTED_BOARDS}")

    background_tasks.add_task(svc.compute_topics, db, board, days, settings.TOPIC_TOP_N)
    return {"status": "computing", "board": board or "all", "days": days}


@router.post("/compute/sync")
async def compute_topics_sync(
    board: Optional[str] = Query(None),
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Synchronous topic computation (blocks until done)."""
    if board and board not in settings.SUPPORTED_BOARDS:
        raise HTTPException(400, f"board must be one of {settings.SUPPORTED_BOARDS}")

    topics = await svc.compute_topics(db, board, days, settings.TOPIC_TOP_N)
    return {"status": "done", "count": len(topics), "topics": topics}


@router.get("/")
async def list_topics(
    board: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    topics = await svc.get_topics(db, board=board)
    return {"topics": topics, "count": len(topics), "board": board or "all"}


@router.get("/{topic_id}/trend")
async def topic_trend(
    topic_id: int,
    days: int = Query(14, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    trend = await svc.get_topic_trend(db, topic_id=topic_id, days=days)
    return {"topic_id": topic_id, "trend": trend}


@router.get("/{topic_id}/articles")
async def topic_articles(
    topic_id: int,
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    articles = await svc.get_topic_articles(db, topic_id=topic_id, limit=limit)
    return {"topic_id": topic_id, "articles": articles}


@router.post("/{topic_id}/summary")
async def generate_summary(
    topic_id: int,
    board: str = Query("Gossiping"),
    db: AsyncSession = Depends(get_db),
):
    """Generate (or regenerate) AI summary for a topic using Gemini."""
    summary = await svc.generate_and_save_summary(db, topic_id=topic_id, board=board)
    if not summary:
        raise HTTPException(503, "AI summary unavailable — check GEMINI_API_KEY")
    return {"topic_id": topic_id, "summary": summary}
