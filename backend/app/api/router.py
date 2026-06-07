from fastapi import APIRouter
from app.api.routes import analysis, articles, scraper, topics

api_router = APIRouter()
api_router.include_router(analysis.router)
api_router.include_router(articles.router)
api_router.include_router(scraper.router)
api_router.include_router(topics.router)
