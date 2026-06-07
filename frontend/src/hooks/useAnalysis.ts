import { useState, useEffect, useCallback } from "react";
import {
  fetchOverview,
  fetchKeywords,
  fetchSentiment,
  fetchSentimentTrend,
  fetchWordcloud,
  fetchArticles,
} from "../api/client";
import type {
  OverviewStats,
  Keyword,
  SentimentOverview,
  SentimentTrendPoint,
  Article,
  Board,
} from "../types";

export function useOverview(board: Board, days = 1) {
  const [data, setData] = useState<OverviewStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchOverview(board, days);
      setData(res.data);
    } catch {
      setError("Failed to load overview");
    } finally {
      setLoading(false);
    }
  }, [board, days]);

  useEffect(() => { load(); }, [load]);
  return { data, loading, error, refetch: load };
}

export function useKeywords(board: Board, days = 7, topN = 20) {
  const [data, setData] = useState<Keyword[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchKeywords(board, days, topN)
      .then((res) => setData(res.data.keywords || []))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [board, days, topN]);

  return { data, loading };
}

export function useSentiment(board: Board, days = 7) {
  const [data, setData] = useState<SentimentOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchSentiment(board, days)
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [board, days]);

  return { data, loading };
}

export function useSentimentTrend(board: Board, days = 14) {
  const [data, setData] = useState<SentimentTrendPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchSentimentTrend(board, days)
      .then((res) => setData(res.data.trend || []))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [board, days]);

  return { data, loading };
}

export function useWordcloud(board: Board, days = 7) {
  const [image, setImage] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchWordcloud(board, days)
      .then((res) => setImage(res.data.image || ""))
      .catch(() => setImage(""))
      .finally(() => setLoading(false));
  }, [board, days]);

  return { image, loading };
}

export function useArticles(board: Board, days = 7) {
  const [data, setData] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchArticles(board, days)
      .then((res) => setData(res.data.articles || []))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [board, days]);

  return { data, loading };
}
