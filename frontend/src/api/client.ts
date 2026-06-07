import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
});

export const fetchOverview = (board?: string, days = 1) =>
  api.get("/analysis/overview", { params: { board: board === "all" ? undefined : board, days } });

export const fetchKeywords = (board?: string, days = 7, top_n = 20) =>
  api.get("/analysis/keywords", { params: { board: board === "all" ? undefined : board, days, top_n } });

export const fetchSentiment = (board?: string, days = 7) =>
  api.get("/analysis/sentiment", { params: { board: board === "all" ? undefined : board, days } });

export const fetchSentimentTrend = (board?: string, days = 14) =>
  api.get("/analysis/sentiment/trend", {
    params: { board: board === "all" ? undefined : board, days },
  });

export const fetchWordcloud = (board?: string, days = 7) =>
  api.get("/analysis/wordcloud", { params: { board: board === "all" ? undefined : board, days } });

export const fetchArticles = (board?: string, days = 7, limit = 50) =>
  api.get("/articles/", { params: { board: board === "all" ? undefined : board, days, limit } });

export const triggerScrape = (board?: string) =>
  api.post("/scraper/trigger/sync", null, {
    params: { board: board === "all" ? undefined : board },
    timeout: 120000,
  });

// V2 — Topics
export const fetchTopics = (board?: string) =>
  api.get("/topics/", { params: { board: board === "all" ? undefined : board } });

export const computeTopics = (board?: string, days = 30) =>
  api.post("/topics/compute/sync", null, {
    params: { board: board === "all" ? undefined : board, days },
    timeout: 300000,
  });

export const fetchTopicTrend = (topicId: number, days = 14) =>
  api.get(`/topics/${topicId}/trend`, { params: { days } });

export const fetchTopicArticles = (topicId: number, limit = 20) =>
  api.get(`/topics/${topicId}/articles`, { params: { limit } });

export const generateTopicSummary = (topicId: number, board: string) =>
  api.post(`/topics/${topicId}/summary`, null, {
    params: { board },
    timeout: 60000,
  });
