import base64
import io
from typing import Dict, Optional
from wordcloud import WordCloud
import logging

logger = logging.getLogger(__name__)

# Common Chinese fonts on Linux/Docker
FONT_PATHS = [
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/System/Library/Fonts/PingFang.ttc",  # macOS
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]


def _get_font_path() -> Optional[str]:
    import os
    for path in FONT_PATHS:
        if os.path.exists(path):
            return path
    return None


def generate_wordcloud(
    word_frequencies: Dict[str, float],
    width: int = 800,
    height: int = 400,
    background_color: str = "#0f172a",
    colormap: str = "cool",
) -> str:
    """Generate word cloud and return as base64-encoded PNG."""
    if not word_frequencies:
        return ""

    font_path = _get_font_path()
    try:
        wc = WordCloud(
            font_path=font_path,
            width=width,
            height=height,
            background_color=background_color,
            colormap=colormap,
            max_words=100,
            prefer_horizontal=0.7,
            min_font_size=12,
            max_font_size=80,
        )
        wc.generate_from_frequencies(word_frequencies)

        img_bytes = io.BytesIO()
        wc.to_image().save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return base64.b64encode(img_bytes.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"Word cloud generation failed: {e}")
        return ""
