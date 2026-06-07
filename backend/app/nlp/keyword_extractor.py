"""
Fast keyword extraction using sklearn TF-IDF + jieba tokenization.
"""
from __future__ import annotations
import threading
import re
from pathlib import Path
from typing import List, Tuple
from collections import Counter

import jieba
from sklearn.feature_extraction.text import TfidfVectorizer

_lock = threading.Lock()

# Load stopwords
_STOPWORDS_PATH = Path(__file__).parent / "stopwords.txt"
_EXTRA_STOPWORDS = {
    # Generic Chinese expressions that are not meaningful keywords
    "什麼", "如何", "如果", "到底", "開始", "會不會", "這麼", "那麼",
    "怎麼", "為什麼", "一下", "一直", "一定", "一起", "一個", "大家",
    "現在", "時間", "今天", "明天", "昨天", "這樣", "那樣", "可能",
    "感覺", "好像", "其實", "當然", "不過", "雖然", "只是", "只有",
    "所有", "沒有", "有沒有", "這種", "那種", "這些", "那些", "問題",
    "事情", "地方", "方式", "方法", "情況", "結果", "原因", "理由",
    "八卦", "板規", "板板規", "版規", "站規", "補充",
}

_STOPWORDS: set = _EXTRA_STOPWORDS.copy()
if _STOPWORDS_PATH.exists():
    with open(_STOPWORDS_PATH, encoding="utf-8") as f:
        _STOPWORDS.update(line.strip() for line in f if line.strip())

STOP_PATTERN = re.compile(r"^[\d\s\W]+$")


def _is_valid_keyword(word: str) -> bool:
    if len(word) < 2:
        return False
    if word in _STOPWORDS:
        return False
    if STOP_PATTERN.match(word):
        return False
    if not re.search(r"[一-鿿]", word):  # must contain Chinese
        return False
    return True


def _tokenize_for_sklearn(text: str) -> str:
    with _lock:
        tokens = list(jieba.cut(text, cut_all=False))
    result = [t.strip() for t in tokens if _is_valid_keyword(t.strip())]
    return " ".join(result) if result else "無"


def extract_keywords_fast(
    texts: List[str],
    top_n: int = 20,
) -> List[Tuple[str, float]]:
    if not texts:
        return []

    processed = [_tokenize_for_sklearn(t) for t in texts[:100]]

    try:
        vectorizer = TfidfVectorizer(
            max_features=2000,
            min_df=1,
            sublinear_tf=True,
        )
        tfidf_matrix = vectorizer.fit_transform(processed)
        scores = tfidf_matrix.sum(axis=0).A1
        feature_names = vectorizer.get_feature_names_out()

        top_indices = scores.argsort()[-top_n * 3:][::-1]
        results = []
        for i in top_indices:
            word = feature_names[i]
            if _is_valid_keyword(word):
                results.append((word, float(scores[i])))
            if len(results) >= top_n:
                break
        return results
    except Exception:
        return []


def count_tokens(texts: List[str]) -> Counter:
    freq: Counter = Counter()
    with _lock:
        for text in texts[:100]:
            for token in jieba.cut(text, cut_all=False):
                token = token.strip()
                if _is_valid_keyword(token):
                    freq[token] += 1
    return freq
