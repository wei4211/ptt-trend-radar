from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.analysis_service import run_scrape_and_analyze
from app.core.config import settings

router = APIRouter(prefix="/scraper", tags=["scraper"])


async def _scrape_all(db: AsyncSession):
    results = []
    for board in settings.SUPPORTED_BOARDS:
        try:
            result = await run_scrape_and_analyze(db, board, pages=3)
            results.append(result)
        except Exception as e:
            results.append({"board": board, "error": str(e)})
    return results


@router.post("/trigger")
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    board: str = None,
    pages: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger scraping. If board not specified, scrapes all boards."""
    if board and board not in settings.SUPPORTED_BOARDS:
        raise HTTPException(400, f"Board must be one of {settings.SUPPORTED_BOARDS}")

    async def _scrape_all_pages(db, pages):
        results = []
        for b in settings.SUPPORTED_BOARDS:
            try:
                result = await run_scrape_and_analyze(db, b, pages=pages)
                results.append(result)
            except Exception as e:
                results.append({"board": b, "error": str(e)})
        return results

    if board:
        background_tasks.add_task(run_scrape_and_analyze, db, board, pages)
    else:
        background_tasks.add_task(_scrape_all_pages, db, pages)

    return {"status": "scraping started", "board": board or "all", "pages": pages}


@router.post("/trigger/sync")
async def trigger_scrape_sync(
    board: str = None,
    pages: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Synchronous scrape. pages controls how many index pages per board."""
    if board and board not in settings.SUPPORTED_BOARDS:
        raise HTTPException(400, f"Board must be one of {settings.SUPPORTED_BOARDS}")

    boards = [board] if board else settings.SUPPORTED_BOARDS
    results = []
    for b in boards:
        result = await run_scrape_and_analyze(db, b, pages=pages)
        results.append(result)
    return {"status": "done", "results": results}
