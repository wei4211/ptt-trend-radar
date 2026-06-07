"""
Gemini AI service for topic summarization.
"""
import logging
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)

_gemini_client = None


def _get_client():
    global _gemini_client
    if _gemini_client is None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_client = genai.GenerativeModel(settings.GEMINI_MODEL)
    return _gemini_client


async def generate_topic_summary(
    topic_name: str,
    keywords: List[str],
    sample_titles: List[str],
    board: str,
) -> str:
    """
    Use Gemini to generate a 100-200 word summary of a topic.
    Returns empty string if API key not set.
    """
    if not settings.GEMINI_API_KEY:
        return ""

    try:
        model = _get_client()
        kw_str = "、".join(keywords[:8])
        titles_str = "\n".join(f"- {t}" for t in sample_titles[:15])

        prompt = f"""你是一位 PTT 論壇分析師。請根據以下資訊，用繁體中文撰寫一段 100-200 字的摘要，說明這個主題近期在 PTT {board} 版的討論內容與輿論趨勢。

主題名稱：{topic_name}
關鍵字：{kw_str}
代表性文章標題：
{titles_str}

要求：
- 摘要要具體且有洞察力
- 說明討論的核心議題
- 指出整體輿論偏向（正面/中性/負面）
- 語氣客觀、精簡
- 不要使用條列式，直接用段落文字"""

        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini summary failed: {e}")
        return f"（AI 摘要生成失敗：{str(e)[:100]}）"


async def generate_board_digest(
    board: str,
    top_topics: List[dict],
    sentiment_overview: dict,
) -> str:
    """Generate a daily digest of a board's discussion."""
    if not settings.GEMINI_API_KEY:
        return ""

    try:
        model = _get_client()
        topics_str = "\n".join(
            f"{i+1}. {t['name']}（{t['article_count']} 篇，關鍵字：{'、'.join(t['keywords'][:5])}）"
            for i, t in enumerate(top_topics[:5])
        )

        prompt = f"""請用繁體中文為 PTT {board} 版的近期討論撰寫一份 150-200 字的每日摘要。

熱門主題：
{topics_str}

情緒分布：正面 {sentiment_overview.get('positive', 0)}%、中性 {sentiment_overview.get('neutral', 0)}%、負面 {sentiment_overview.get('negative', 0)}%

請整合以上資訊，說明版面近期整體討論氛圍與熱點，語氣客觀分析，不使用條列式。"""

        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini digest failed: {e}")
        return ""
