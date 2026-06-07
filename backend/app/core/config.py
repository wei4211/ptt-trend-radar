from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://ptt:pttpassword@localhost:5432/ptt_radar"
    GEMINI_API_KEY: str = ""
    SCRAPE_INTERVAL_MINUTES: int = 60

    SUPPORTED_BOARDS: List[str] = ["Gossiping", "Stock", "NBA", "Tech_Job"]
    ARTICLES_PER_BOARD: int = 100

    PTT_BASE_URL: str = "https://www.ptt.cc"
    PTT_HEADERS: dict = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Cookie": "over18=1",
    }

    SENTIMENT_POSITIVE_THRESHOLD: float = 0.6
    SENTIMENT_NEGATIVE_THRESHOLD: float = 0.4

    # BERTopic
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    TOPIC_MIN_CLUSTER_SIZE: int = 5
    TOPIC_TOP_N: int = 10

    # Gemini
    GEMINI_MODEL: str = "gemini-2.5-flash"
    AI_SUMMARY_MAX_ARTICLES: int = 20

    class Config:
        env_file = ".env"


settings = Settings()
