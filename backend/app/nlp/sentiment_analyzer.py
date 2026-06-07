from snownlp import SnowNLP
from typing import Literal
import re
import logging

logger = logging.getLogger(__name__)

SentimentLabel = Literal["positive", "neutral", "negative"]

# PTT-specific sentiment keywords for better accuracy
POSITIVE_WORDS = {"推", "讚", "棒", "厲害", "強", "神", "好", "優", "佳", "愛", "支持", "賺", "漲", "買"}
NEGATIVE_WORDS = {"爛", "差", "糟", "廢", "蠢", "噓", "跌", "虧", "賠", "醜", "爛", "垃圾", "悲"}

POSITIVE_THRESHOLD = 0.6
NEGATIVE_THRESHOLD = 0.4


def _ptt_sentiment_adjustment(text: str, base_score: float) -> float:
    """Adjust score based on PTT-specific sentiment words."""
    pos_hits = sum(1 for w in POSITIVE_WORDS if w in text)
    neg_hits = sum(1 for w in NEGATIVE_WORDS if w in text)
    adjustment = (pos_hits - neg_hits) * 0.05
    return max(0.0, min(1.0, base_score + adjustment))


def analyze_text(text: str) -> dict:
    """Analyze sentiment of a single text. Returns label and score (0-1)."""
    if not text or len(text.strip()) < 5:
        return {"label": "neutral", "score": 0.5}

    # Clean text for snownlp
    clean = re.sub(r"https?://\S+", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()

    # Chunk text if too long (snownlp works better on shorter texts)
    if len(clean) > 500:
        chunks = [clean[i:i+500] for i in range(0, min(len(clean), 1500), 500)]
        scores = []
        for chunk in chunks:
            try:
                s = SnowNLP(chunk)
                scores.append(s.sentiments)
            except Exception:
                scores.append(0.5)
        base_score = sum(scores) / len(scores)
    else:
        try:
            base_score = SnowNLP(clean).sentiments
        except Exception:
            base_score = 0.5

    score = _ptt_sentiment_adjustment(text, base_score)

    if score >= POSITIVE_THRESHOLD:
        label = "positive"
    elif score <= NEGATIVE_THRESHOLD:
        label = "negative"
    else:
        label = "neutral"

    return {"label": label, "score": round(score, 4)}


def analyze_batch(texts: list[str]) -> list[dict]:
    return [analyze_text(t) for t in texts]


def aggregate_sentiment(results: list[dict]) -> dict:
    """Aggregate multiple sentiment results into summary stats."""
    if not results:
        return {"positive": 0, "neutral": 0, "negative": 0, "avg_score": 0.5}

    counts = {"positive": 0, "neutral": 0, "negative": 0}
    total_score = 0.0

    for r in results:
        counts[r["label"]] += 1
        total_score += r["score"]

    total = len(results)
    return {
        "positive": round(counts["positive"] / total * 100, 1),
        "neutral": round(counts["neutral"] / total * 100, 1),
        "negative": round(counts["negative"] / total * 100, 1),
        "avg_score": round(total_score / total, 4),
        "total": total,
    }
