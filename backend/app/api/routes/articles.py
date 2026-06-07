from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.database import get_db
from app.services import analysis_service as svc

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/")
async def list_articles(
    board: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    articles = await svc.get_articles(db, board=board, days=days, limit=limit, offset=offset)
    return {"articles": articles, "count": len(articles)}
