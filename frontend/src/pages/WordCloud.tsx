import { useState } from "react";
import { Cloud } from "lucide-react";
import { useWordcloud } from "../hooks/useAnalysis";
import BoardSelector from "../components/UI/BoardSelector";
import Spinner from "../components/UI/Spinner";
import type { Board } from "../types";

export default function WordCloud() {
  const [board, setBoard] = useState<Board>("all");
  const [days, setDays] = useState(7);
  const { image, loading } = useWordcloud(board, days);

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">文字雲</h1>
        <p className="text-slate-400 text-sm mt-1">依詞頻生成文字雲，字體越大代表出現次數越多</p>
      </div>

      <div className="flex flex-wrap gap-4 items-center">
        <BoardSelector value={board} onChange={setBoard} />
        <div className="flex gap-2">
          {[1, 3, 7, 14, 30].map((d) => (
            <button key={d} onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                days === d ? "bg-indigo-500 text-white" : "bg-slate-800 text-slate-400 hover:text-slate-200"
              }`}>
              {d === 1 ? "今日" : `${d} 天`}
            </button>
          ))}
        </div>
      </div>

      <div className="glass rounded-xl p-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <Spinner size="lg" />
            <p className="text-slate-500 text-sm">生成文字雲中，請稍候...</p>
          </div>
        ) : image ? (
          <img src={`data:image/png;base64,${image}`} alt="word cloud" className="w-full rounded-lg" />
        ) : (
          <div className="flex flex-col items-center justify-center py-24 gap-3">
            <Cloud size={40} className="text-slate-600" />
            <p className="text-slate-500 text-sm">暫無資料，請先爬取文章</p>
          </div>
        )}
      </div>
    </div>
  );
}
