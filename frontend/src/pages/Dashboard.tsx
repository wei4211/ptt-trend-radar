import { useState } from "react";
import { triggerScrape } from "../api/client";
import { useOverview, useSentiment, useSentimentTrend, useKeywords } from "../hooks/useAnalysis";
import BoardSelector from "../components/UI/BoardSelector";
import StatCard from "../components/Cards/StatCard";
import SentimentPieChart from "../components/Charts/SentimentPieChart";
import TrendLineChart from "../components/Charts/TrendLineChart";
import KeywordBarChart from "../components/Charts/KeywordBarChart";
import Spinner from "../components/UI/Spinner";
import type { Board } from "../types";

export default function Dashboard() {
  const [board, setBoard] = useState<Board>("all");
  const [scraping, setScraping] = useState(false);
  const [scrapeMsg, setScrapeMsg] = useState("");

  const { data: overview, loading: ovLoading, refetch } = useOverview(board, 7);
  const { data: sentiment, loading: sentLoading } = useSentiment(board, 7);
  const { data: trend, loading: trendLoading } = useSentimentTrend(board, 14);
  const { data: keywords, loading: kwLoading } = useKeywords(board, 7, 15);

  const handleScrape = async () => {
    setScraping(true);
    setScrapeMsg("");
    try {
      const res = await triggerScrape(board);
      const results = res.data.results || [res.data];
      const total = results.reduce((s: number, r: { inserted?: number }) => s + (r.inserted || 0), 0);
      setScrapeMsg(`✅ 新增 ${total} 篇文章`);
      refetch();
    } catch {
      setScrapeMsg("❌ 爬取失敗，請確認 API 是否啟動");
    } finally {
      setScraping(false);
    }
  };

  const sentimentLabel = (score?: number) => {
    if (!score) return "—";
    if (score >= 0.6) return "😊 偏正面";
    if (score <= 0.4) return "😟 偏負面";
    return "😐 中性";
  };

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-white">總覽 Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">過去 7 天 PTT 熱門話題分析</p>
        </div>
        <div className="flex items-center gap-3">
          {scrapeMsg && <span className="text-sm text-slate-400">{scrapeMsg}</span>}
          <button
            onClick={handleScrape}
            disabled={scraping}
            className="flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
          >
            {scraping ? <Spinner size="sm" /> : "🔄"}
            {scraping ? "爬取中..." : "立即爬取"}
          </button>
        </div>
      </div>

      {/* Board Selector */}
      <BoardSelector value={board} onChange={setBoard} />

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {ovLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="glass rounded-xl p-5 flex items-center justify-center h-24">
              <Spinner size="sm" />
            </div>
          ))
        ) : (
          <>
            <StatCard
              title="文章總數 (7天)"
              value={overview?.total_articles ?? 0}
              icon="📰"
              accent="sky"
            />
            <StatCard
              title="平均情緒"
              value={sentimentLabel(overview?.avg_sentiment_score)}
              icon="💬"
              subtitle={`分數 ${overview?.avg_sentiment_score?.toFixed(3) ?? "—"}`}
              accent="emerald"
            />
            <StatCard
              title="正面文章"
              value={`${overview?.sentiment_distribution?.positive ?? 0} 篇`}
              icon="😊"
              accent="emerald"
            />
            <StatCard
              title="負面文章"
              value={`${overview?.sentiment_distribution?.negative ?? 0} 篇`}
              icon="😟"
              accent="rose"
            />
          </>
        )}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Pie */}
        <div className="glass rounded-xl p-6">
          <h2 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wide">
            情緒分布
          </h2>
          {sentLoading || !sentiment ? (
            <div className="flex justify-center py-16"><Spinner /></div>
          ) : (
            <SentimentPieChart data={sentiment} />
          )}
        </div>

        {/* Trend Line */}
        <div className="glass rounded-xl p-6">
          <h2 className="text-sm font-semibold text-slate-300 mb-1 uppercase tracking-wide">
            情緒趨勢（14 天）
          </h2>
          <p className="text-xs text-slate-500 mb-4">綠線=正面門檻(0.6)　紅線=負面門檻(0.4)</p>
          {trendLoading ? (
            <div className="flex justify-center py-16"><Spinner /></div>
          ) : trend.length === 0 ? (
            <p className="text-slate-500 text-center py-16 text-sm">暫無資料，請先爬取文章</p>
          ) : (
            <TrendLineChart data={trend} />
          )}
        </div>
      </div>

      {/* Keyword Bar */}
      <div className="glass rounded-xl p-6">
        <h2 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wide">
          熱門關鍵字 Top 15
        </h2>
        {kwLoading ? (
          <div className="flex justify-center py-16"><Spinner /></div>
        ) : keywords.length === 0 ? (
          <p className="text-slate-500 text-center py-10 text-sm">暫無關鍵字資料</p>
        ) : (
          <KeywordBarChart data={keywords} />
        )}
      </div>
    </div>
  );
}
