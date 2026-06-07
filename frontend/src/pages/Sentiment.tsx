import { useState } from "react";
import { TrendingUp, TrendingDown, Minus, BarChart2 } from "lucide-react";
import { useSentiment, useSentimentTrend } from "../hooks/useAnalysis";
import BoardSelector from "../components/UI/BoardSelector";
import SentimentPieChart from "../components/Charts/SentimentPieChart";
import TrendLineChart from "../components/Charts/TrendLineChart";
import StatCard from "../components/Cards/StatCard";
import Spinner from "../components/UI/Spinner";
import type { Board } from "../types";

export default function Sentiment() {
  const [board, setBoard] = useState<Board>("all");
  const [days, setDays] = useState(7);
  const { data: sentiment, loading: sentLoading } = useSentiment(board, days);
  const { data: trend, loading: trendLoading } = useSentimentTrend(board, days * 2);

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">情緒分析</h1>
        <p className="text-slate-400 text-sm mt-1">使用 SnowNLP 進行中文情緒分類，分為正面 / 中性 / 負面</p>
      </div>

      <div className="flex flex-wrap gap-4 items-center">
        <BoardSelector value={board} onChange={setBoard} />
        <div className="flex gap-2">
          {[3, 7, 14, 30].map((d) => (
            <button key={d} onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                days === d ? "bg-indigo-500 text-white" : "bg-slate-800 text-slate-400 hover:text-slate-200"
              }`}>
              {d} 天
            </button>
          ))}
        </div>
      </div>

      {!sentLoading && sentiment && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="正面" value={`${sentiment.positive}%`} icon={TrendingUp} accent="emerald" />
          <StatCard title="中性" value={`${sentiment.neutral}%`} icon={Minus} accent="sky" />
          <StatCard title="負面" value={`${sentiment.negative}%`} icon={TrendingDown} accent="rose" />
          <StatCard title="平均分數" value={sentiment.avg_score.toFixed(3)} icon={BarChart2}
            subtitle={`共 ${sentiment.total} 篇`} accent="amber" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass rounded-xl p-6">
          <h2 className="text-xs font-semibold text-slate-400 mb-4 uppercase tracking-wide">情緒分布</h2>
          {sentLoading || !sentiment ? (
            <div className="flex justify-center py-16"><Spinner /></div>
          ) : (
            <SentimentPieChart data={sentiment} />
          )}
        </div>

        <div className="glass rounded-xl p-6">
          <h2 className="text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wide">情緒趨勢</h2>
          <p className="text-xs text-slate-600 mb-4">綠線 = 正面門檻 (0.6)　紅線 = 負面門檻 (0.4)</p>
          {trendLoading ? (
            <div className="flex justify-center py-16"><Spinner /></div>
          ) : trend.length === 0 ? (
            <p className="text-slate-500 text-center py-16 text-sm">暫無資料</p>
          ) : (
            <TrendLineChart data={trend} />
          )}
        </div>
      </div>

      <div className="glass rounded-xl p-6">
        <h2 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wide">情緒分類說明</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-400">
          <div className="flex gap-3">
            <span className="w-3 h-3 rounded-full bg-emerald-400 mt-1 shrink-0" />
            <div>
              <p className="text-emerald-400 font-medium">正面（score ≥ 0.6）</p>
              <p>內容傾向正向、讚美、支持等情緒</p>
            </div>
          </div>
          <div className="flex gap-3">
            <span className="w-3 h-3 rounded-full bg-slate-400 mt-1 shrink-0" />
            <div>
              <p className="text-slate-300 font-medium">中性（0.4 – 0.6）</p>
              <p>情緒偏中立，難以明確分類</p>
            </div>
          </div>
          <div className="flex gap-3">
            <span className="w-3 h-3 rounded-full bg-rose-400 mt-1 shrink-0" />
            <div>
              <p className="text-rose-400 font-medium">負面（score ≤ 0.4）</p>
              <p>內容傾向批評、抱怨、悲觀等情緒</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
