from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.db.database import init_db
from app.api.router import api_router
from app.core.scheduler import start_scheduler, stop_scheduler
# Import models so SQLAlchemy discovers them for create_all
from app.models import article, topic  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _warmup_nlp():
    """Pre-load jieba dict in background so first API call isn't slow."""
    import asyncio
    loop = asyncio.get_running_loop()
    def _init():
        import jieba
        jieba.initialize()
        logger.info("jieba warmup done")
    await loop.run_in_executor(None, _init)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database initialized")
    import asyncio
    asyncio.create_task(_warmup_nlp())  # fire-and-forget
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="PTT Trend Radar API",
    version="1.0.0",
    description="PTT 熱門話題與情緒分析平台",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
