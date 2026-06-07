"""
BERTopic-based topic modeling for Chinese PTT articles.
Uses multilingual sentence embeddings + HDBSCAN clustering.
"""
from __future__ import annotations

import logging
from typing import List, Tuple
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_models(embedding_model_name: str):
    """Lazy-load heavy models once and cache in process."""
    from sentence_transformers import SentenceTransformer
    from bertopic import BERTopic
    from umap import UMAP
    from hdbscan import HDBSCAN
    from sklearn.feature_extraction.text import CountVectorizer

    logger.info(f"Loading embedding model: {embedding_model_name}")
    embedding_model = SentenceTransformer(embedding_model_name)

    umap_model = UMAP(
        n_neighbors=5,
        n_components=3,
        min_dist=0.0,
        metric="cosine",
        random_state=42,
    )
    hdbscan_model = HDBSCAN(
        min_cluster_size=3,
        min_samples=1,
        metric="euclidean",
        cluster_selection_method="eom",
        prediction_data=True,
    )
    vectorizer_model = CountVectorizer(
        analyzer="word",
        token_pattern=r"[一-鿿]{2,}",  # Chinese chars only, min 2
        max_features=3000,
        min_df=1,  # allow rare terms in small datasets
    )
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        language="multilingual",
        top_n_words=8,
        nr_topics="auto",
        verbose=False,
        calculate_probabilities=True,
    )
    return embedding_model, topic_model


def run_topic_modeling(
    texts: List[str],
    embedding_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
) -> Tuple[List[int], List[float], object]:
    if len(texts) < 10:
        logger.warning(f"Too few documents ({len(texts)}) for topic modeling")
        return [-1] * len(texts), [0.0] * len(texts), None

    try:
        _, topic_model = _load_models(embedding_model_name)
        # Always re-fit (don't reuse state from previous run)
        from bertopic import BERTopic
        from umap import UMAP
        from hdbscan import HDBSCAN
        from sklearn.feature_extraction.text import CountVectorizer
        from sentence_transformers import SentenceTransformer

        embedding_model = SentenceTransformer(embedding_model_name)
        n_neighbors = min(5, len(texts) - 1)
        umap_model = UMAP(n_neighbors=n_neighbors, n_components=3, min_dist=0.0,
                          metric="cosine", random_state=42)
        hdbscan_model = HDBSCAN(min_cluster_size=3, min_samples=1,
                                metric="euclidean", cluster_selection_method="eom",
                                prediction_data=True)
        vectorizer_model = CountVectorizer(
            token_pattern=r"[一-鿿]{2,}", max_features=3000, min_df=1)

        fresh_model = BERTopic(
            embedding_model=embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            vectorizer_model=vectorizer_model,
            language="multilingual",
            top_n_words=8,
            nr_topics="auto",
            verbose=False,
            calculate_probabilities=True,
        )
        topics, probs = fresh_model.fit_transform(texts)
        return topics, list(probs) if hasattr(probs, '__iter__') else [float(probs)] * len(texts), fresh_model
    except Exception as e:
        logger.error(f"BERTopic failed: {e}")
        return [-1] * len(texts), [0.0] * len(texts), None


def get_topic_info(topic_model, top_n: int = 10) -> List[dict]:
    if topic_model is None:
        return []
    try:
        info = topic_model.get_topic_info()
        results = []
        for _, row in info.iterrows():
            idx = int(row["Topic"])
            if idx == -1:
                continue
            words = topic_model.get_topic(idx)
            keywords = [w for w, _ in words[:8]] if words else []
            name = "、".join(keywords[:3]) if keywords else f"主題{idx}"
            results.append({
                "topic_idx": idx,
                "name": name,
                "keywords": keywords,
                "count": int(row["Count"]),
            })
            if len(results) >= top_n:
                break
        return results
    except Exception as e:
        logger.error(f"Failed to get topic info: {e}")
        return []
