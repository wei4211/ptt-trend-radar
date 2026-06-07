export interface Article {
  id: number;
  board: string;
  title: string;
  author: string;
  push_count: number;
  boo_count: number;
  url: string;
  published_at: string | null;
  sentiment_label: "positive" | "neutral" | "negative" | null;
  sentiment_score: number | null;
}

export interface Keyword {
  keyword: string;
  tfidf_score: number;
  count: number;
}

export interface SentimentOverview {
  positive: number;
  neutral: number;
  negative: number;
  avg_score: number;
  total: number;
}

export interface SentimentTrendPoint {
  date: string;
  avg_score: number;
  article_count: number;
}

export interface OverviewStats {
  total_articles: number;
  avg_sentiment_score: number;
  sentiment_distribution: Record<string, number>;
  period_days: number;
  board: string;
}

export interface TopicSentiment {
  positive: number;
  neutral: number;
  negative: number;
}

export interface Topic {
  id: number;
  topic_idx: number;
  name: string;
  keywords: string[];
  article_count: number;
  sentiment: TopicSentiment;
  ai_summary: string | null;
  computed_at: string | null;
}

export interface TopicArticle {
  id: number;
  title: string;
  author: string;
  push_count: number;
  url: string;
  sentiment_label: "positive" | "neutral" | "negative" | null;
  probability: number;
}

export interface TopicTrendPoint {
  date: string;
  count: number;
}

export type Board = "all" | "Gossiping" | "Stock" | "NBA" | "Tech_Job";

export interface ScrapeResult {
  board: string;
  scraped: number;
  inserted: number;
  error?: string;
}
