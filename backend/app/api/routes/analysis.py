from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.database import get_db
from app.services import analysis_service as svc
from app.core.config import settings

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/overview")
async def overview(
    board: Optional[str] = Query(None),
    days: int = Query(1, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_overview_stats(db, board=board, days=days)


@router.get("/keywords")
async def keywords(
    board: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=90),
    top_n: int = Query(20, ge=5, le=50),
    db: AsyncSession = Depends(get_db),
):
    kws = await svc.get_keywords(db, board=board, days=days, top_n=top_n)
    return {"keywords": kws, "board": board or "all", "days": days}


@router.get("/sentiment")
async def sentiment(
    board: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_sentiment_overview(db, board=board, days=days)


@router.get("/sentiment/trend")
async def sentiment_trend(
    board: Optional[str] = Query(None),
    days: int = Query(14, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    trend = await svc.get_sentiment_trend(db, board=board, days=days)
    return {"trend": trend, "board": board or "all"}


@router.get("/wordcloud")
async def wordcloud(
    board: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    image_b64 = await svc.get_wordcloud_data(db, board=board, days=days)
    return {"image": image_b64, "board": board or "all"}
