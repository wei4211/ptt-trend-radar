import { useState } from "react";
import { Brain, RefreshCw, Sparkles } from "lucide-react";
import clsx from "clsx";
import BoardSelector from "../components/UI/BoardSelector";
import Spinner from "../components/UI/Spinner";
import TopicTrendChart from "../components/Charts/TopicTrendChart";
import { useTopics, useTopicTrend, useTopicArticles, useComputeTopics, useGenerateSummary } from "../hooks/useTopics";
import type { Board, Topic } from "../types";

const SENTIMENT_BAR_COLORS = {
  positive: "bg-emerald-500",
  neutral: "bg-slate-500",
  negative: "bg-rose-500",
};

const TOPIC_COLORS = [
  "#38bdf8", "#818cf8", "#34d399", "#fb923c", "#f472b6",
  "#a78bfa", "#22d3ee", "#86efac", "#fde68a", "#fca5a5",
];

function SentimentBar({ positive, neutral, negative }: { positive: number; neutral: number; negative: number }) {
  return (
    <div className="flex h-1.5 rounded-full overflow-hidden w-full gap-px">
      <div className={SENTIMENT_BAR_COLORS.positive} style={{ width: `${positive}%` }} />
      <div className={SENTIMENT_BAR_COLORS.neutral} style={{ width: `${neutral}%` }} />
      <div className={SENTIMENT_BAR_COLORS.negative} style={{ width: `${negative}%` }} />
    </div>
  );
}

function TopicCard({ topic, isSelected, color, onClick }: {
  topic: Topic; isSelected: boolean; color: string; onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        "text-left w-full glass rounded-xl p-4 transition-all border",
        isSelected ? "border-sky-500/60 bg-sky-500/10" : "border-slate-700/50 hover:border-slate-600"
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <p className="text-sm font-semibold text-slate-200 leading-snug">{topic.name}</p>
        <span className="shrink-0 text-xs text-slate-500">{topic.article_count} 篇</span>
      </div>
      <div className="flex flex-wrap gap-1 mb-3">
        {topic.keywords.slice(0, 5).map((kw) => (
          <span key={kw} className="px-1.5 py-0.5 text-xs rounded" style={{ background: `${color}20`, color }}>
            {kw}
          </span>
        ))}
      </div>
      <SentimentBar positive={topic.sentiment.positive} neutral={topic.sentiment.neutral} negative={topic.sentiment.negative} />
      <div className="flex justify-between text-xs text-slate-600 mt-1">
        <span className="text-emerald-500">+{topic.sentiment.positive}%</span>
        <span className="text-rose-500">-{topic.sentiment.negative}%</span>
      </div>
    </button>
  );
}

function TopicDetail({ topic, board, color }: { topic: Topic; board: Board; color: string }) {
  const { data: trend, loading: trendLoading } = useTopicTrend(topic.id, 14);
  const { data: articles, loading: artsLoading } = useTopicArticles(topic.id);
  const { generate, loading: summaryLoading } = useGenerateSummary();
  const [summary, setSummary] = useState<string | null>(topic.ai_summary);

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-lg font-bold text-white">{topic.name}</h3>
        <div className="flex flex-wrap gap-1.5 mt-2">
          {topic.keywords.map((kw) => (
            <span key={kw} className="px-2 py-1 text-xs rounded-full border" style={{ borderColor: `${color}50`, color }}>
              {kw}
            </span>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="glass rounded-lg p-3 text-center">
          <p className="text-xl font-bold text-white">{topic.article_count}</p>
          <p className="text-xs text-slate-500 mt-0.5">文章數</p>
        </div>
        <div className="glass rounded-lg p-3 text-center">
          <p className="text-xl font-bold text-emerald-400">{topic.sentiment.positive}%</p>
          <p className="text-xs text-slate-500 mt-0.5">正面</p>
        </div>
        <div className="glass rounded-lg p-3 text-center">
          <p className="text-xl font-bold text-rose-400">{topic.sentiment.negative}%</p>
          <p className="text-xs text-slate-500 mt-0.5">負面</p>
        </div>
      </div>

      <div className="glass rounded-xl p-4">
        <p className="text-xs text-slate-400 font-semibold uppercase tracking-wide mb-3">熱度趨勢（14 天）</p>
        {trendLoading ? (
          <div className="flex justify-center py-8"><Spinner size="sm" /></div>
        ) : (
          <TopicTrendChart data={trend} color={color} />
        )}
      </div>

      <div className="glass rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs text-slate-400 font-semibold uppercase tracking-wide">AI 摘要</p>
          <button
            onClick={() => generate(topic.id, board === "all" ? "Gossiping" : board, setSummary)}
            disabled={summaryLoading}
            className="flex items-center gap-1.5 px-3 py-1 text-xs rounded-lg bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white transition-colors"
          >
            {summaryLoading ? <Spinner size="sm" /> : <Sparkles size={12} />}
            {summaryLoading ? "生成中..." : summary ? "重新生成" : "Gemini 生成摘要"}
          </button>
        </div>
        {summary ? (
          <p className="text-sm text-slate-300 leading-relaxed">{summary}</p>
        ) : (
          <p className="text-sm text-slate-500">點擊右上角按鈕，讓 Gemini 自動摘要這個主題的討論內容</p>
        )}
      </div>

      <div className="glass rounded-xl overflow-hidden">
        <p className="text-xs text-slate-400 font-semibold uppercase tracking-wide px-4 py-3 border-b border-slate-800">
          代表文章
        </p>
        {artsLoading ? (
          <div className="flex justify-center py-6"><Spinner size="sm" /></div>
        ) : (
          <ul className="divide-y divide-slate-800/50">
            {articles.map((a) => (
              <li key={a.id} className="px-4 py-2.5 hover:bg-slate-800/30 transition-colors">
                <a href={a.url} target="_blank" rel="noopener noreferrer"
                  className="text-sm text-slate-300 hover:text-sky-400 transition-colors line-clamp-1">
                  {a.title}
                </a>
                <div className="flex gap-3 mt-0.5 text-xs text-slate-600">
                  <span>{a.push_count} 推</span>
                  <span>{a.author}</span>
                  <span className="ml-auto">相關度 {(a.probability * 100).toFixed(0)}%</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default function Topics() {
  const [board, setBoard] = useState<Board>("all");
  const [days, setDays] = useState(30);
  const [selected, setSelected] = useState<Topic | null>(null);
  const { data: topics, loading, error, refetch } = useTopics(board);
  const { compute, computing, msg } = useComputeTopics();

  const handleCompute = () => {
    compute(board, days, () => { refetch(); setSelected(null); });
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-white">主題分析</h1>
          <p className="text-slate-400 text-sm mt-1">BERTopic 自動發現主題，Gemini AI 生成摘要</p>
        </div>
        <div className="flex items-center gap-3">
          {msg && <span className="text-sm text-slate-400">{msg}</span>}
          <button
            onClick={handleCompute}
            disabled={computing}
            className="flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
          >
            {computing ? <Spinner size="sm" /> : <Brain size={14} />}
            {computing ? "分析中..." : "執行主題分析"}
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-4 items-center">
        <BoardSelector value={board} onChange={(b) => { setBoard(b); setSelected(null); }} />
        <div className="flex gap-2">
          {[7, 14, 30, 60].map((d) => (
            <button key={d} onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                days === d ? "bg-violet-600 text-white" : "bg-slate-800 text-slate-400 hover:text-slate-200"
              }`}>
              {d} 天
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-24"><Spinner size="lg" /></div>
      ) : error ? (
        <div className="glass rounded-xl p-10 text-center text-slate-500">{error}</div>
      ) : topics.length === 0 ? (
        <div className="glass rounded-xl p-16 text-center space-y-3">
          <Brain size={40} className="mx-auto text-slate-600" />
          <p className="text-slate-400">尚未執行主題分析</p>
          <p className="text-slate-600 text-sm">請先爬取文章（建議 ≥ 50 篇），再點「執行主題分析」</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          <div className="lg:col-span-2 space-y-3">
            <p className="text-xs text-slate-500 uppercase tracking-wide font-medium">{topics.length} 個主題</p>
            {topics.map((t, i) => (
              <TopicCard key={t.id} topic={t} isSelected={selected?.id === t.id}
                color={TOPIC_COLORS[i % TOPIC_COLORS.length]} onClick={() => setSelected(t)} />
            ))}
          </div>
          <div className="lg:col-span-3">
            {selected ? (
              <TopicDetail topic={selected} board={board}
                color={TOPIC_COLORS[topics.findIndex((t) => t.id === selected.id) % TOPIC_COLORS.length]} />
            ) : (
              <div className="glass rounded-xl h-full flex items-center justify-center py-24">
                <div className="text-center space-y-2">
                  <RefreshCw size={24} className="mx-auto text-slate-600" />
                  <p className="text-slate-500 text-sm mt-2">點選左側主題查看詳情</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
