from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.services.analysis_service import run_scrape_and_analyze
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def scheduled_scrape():
    logger.info("Scheduled scrape starting...")
    async with AsyncSessionLocal() as db:
        for board in settings.SUPPORTED_BOARDS:
            try:
                result = await run_scrape_and_analyze(db, board, pages=10)
                logger.info(f"Scheduled scrape {board}: {result}")
            except Exception as e:
                logger.error(f"Scheduled scrape failed for {board}: {e}")


def start_scheduler():
    scheduler.add_job(
        scheduled_scrape,
        trigger=IntervalTrigger(minutes=settings.SCRAPE_INTERVAL_MINUTES),
        id="ptt_scrape",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started, interval={settings.SCRAPE_INTERVAL_MINUTES}m")


def stop_scheduler():
    scheduler.shutdown(wait=False)
