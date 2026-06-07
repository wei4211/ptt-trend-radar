import jieba
import jieba.analyse
import re
import threading
from typing import List
from pathlib import Path

_jieba_lock = threading.Lock()

# Load custom stopwords
STOPWORDS_PATH = Path(__file__).parent / "stopwords.txt"

STOPWORDS = set()
if STOPWORDS_PATH.exists():
    with open(STOPWORDS_PATH, encoding="utf-8") as f:
        STOPWORDS = {line.strip() for line in f if line.strip()}

# Common Chinese stopwords (built-in)
DEFAULT_STOPWORDS = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
    "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
    "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "他",
    "她", "它", "我们", "你们", "他们", "这个", "那个", "啊", "吗",
    "呢", "吧", "嗎", "啦", "喔", "喽", "嗯", "哦", "哇", "哈",
    "因为", "所以", "但是", "然后", "如果", "就是", "而且", "或者",
    "因為", "所以", "但是", "然後", "如果", "就是", "而且", "或者",
    "可以", "已經", "沒有", "什麼", "這個", "那個", "一些", "一樣",
    "覺得", "知道", "應該", "真的", "還是", "還有", "不是", "不會",
    "http", "https", "www", "com", "net", "tw", "PTT", "Re",
}

STOPWORDS.update(DEFAULT_STOPWORDS)


def tokenize(text: str, min_length: int = 2) -> List[str]:
    """Tokenize Chinese text using jieba, returning meaningful tokens."""
    # Remove URLs, special chars, numbers-only tokens
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^一-鿿㐀-䶿\w]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = jieba.cut(text, cut_all=False)
    result = []
    for token in tokens:
        token = token.strip()
        if (
            len(token) >= min_length
            and token not in STOPWORDS
            and not token.isdigit()
            and re.search(r"[一-鿿]", token)  # must contain Chinese char
        ):
            result.append(token)
    return result


def extract_keywords_tfidf(texts: List[str], top_n: int = 20) -> List[tuple[str, float]]:
    """Extract keywords using jieba TF-IDF. Thread-safe via lock."""
    combined = " ".join(texts)
    with _jieba_lock:
        jieba.analyse.set_stop_words(str(STOPWORDS_PATH) if STOPWORDS_PATH.exists() else "")
        tags = jieba.analyse.extract_tags(
            combined,
            topK=top_n * 2,
            withWeight=True,
            allowPOS=("n", "vn", "eng", "nz", "nr", "ns"),
        )
    filtered = [(word, score) for word, score in tags if word not in STOPWORDS and len(word) >= 2]
    return filtered[:top_n]


def tokenize_batch(texts: List[str], min_length: int = 2) -> List[str]:
    """Thread-safe batch tokenization."""
    tokens = []
    with _jieba_lock:
        for text in texts:
            tokens.extend(tokenize(text, min_length=min_length))
    return tokens
