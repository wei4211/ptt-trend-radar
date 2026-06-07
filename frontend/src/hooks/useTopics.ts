import { useState, useEffect, useCallback } from "react";
import {
  fetchTopics,
  fetchTopicTrend,
  fetchTopicArticles,
  generateTopicSummary,
  computeTopics,
} from "../api/client";
import type { Topic, TopicArticle, TopicTrendPoint, Board } from "../types";

export function useTopics(board: Board) {
  const [data, setData] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchTopics(board);
      setData(res.data.topics || []);
    } catch {
      setError("無法載入主題資料");
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [board]);

  useEffect(() => { load(); }, [load]);
  return { data, loading, error, refetch: load };
}

export function useTopicTrend(topicId: number | null, days = 14) {
  const [data, setData] = useState<TopicTrendPoint[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!topicId) return;
    setLoading(true);
    fetchTopicTrend(topicId, days)
      .then((res) => setData(res.data.trend || []))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [topicId, days]);

  return { data, loading };
}

export function useTopicArticles(topicId: number | null) {
  const [data, setData] = useState<TopicArticle[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!topicId) return;
    setLoading(true);
    fetchTopicArticles(topicId, 20)
      .then((res) => setData(res.data.articles || []))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [topicId]);

  return { data, loading };
}

export function useComputeTopics() {
  const [computing, setComputing] = useState(false);
  const [msg, setMsg] = useState("");

  const compute = async (board: Board, days: number, onDone: () => void) => {
    setComputing(true);
    setMsg("");
    try {
      const res = await computeTopics(board, days);
      const count = res.data.count ?? 0;
      setMsg(`✅ 發現 ${count} 個主題`);
      onDone();
    } catch {
      setMsg("❌ 主題分析失敗，請確認 API 是否啟動且已有足夠文章");
    } finally {
      setComputing(false);
    }
  };

  return { compute, computing, msg };
}

export function useGenerateSummary() {
  const [loading, setLoading] = useState(false);

  const generate = async (
    topicId: number,
    board: string,
    onSuccess: (summary: string) => void,
  ) => {
    setLoading(true);
    try {
      const res = await generateTopicSummary(topicId, board);
      onSuccess(res.data.summary);
    } catch {
      onSuccess("（需設定 GEMINI_API_KEY 才能生成 AI 摘要）");
    } finally {
      setLoading(false);
    }
  };

  return { generate, loading };
}
