import { useState } from "react";
import { useKeywords } from "../hooks/useAnalysis";
import BoardSelector from "../components/UI/BoardSelector";
import KeywordBarChart from "../components/Charts/KeywordBarChart";
import Spinner from "../components/UI/Spinner";
import type { Board } from "../types";

export default function Keywords() {
  const [board, setBoard] = useState<Board>("all");
  const [days, setDays] = useState(7);
  const { data, loading } = useKeywords(board, days, 20);

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">關鍵字分析</h1>
        <p className="text-slate-400 text-sm mt-1">TF-IDF 關鍵字萃取，過濾停用詞後呈現最具代表性詞彙</p>
      </div>

      <div className="flex flex-wrap gap-4 items-center">
        <BoardSelector value={board} onChange={setBoard} />
        <div className="flex gap-2">
          {[{ label: "今日", value: 1 }, { label: "3 天", value: 3 }, { label: "7 天", value: 7 },
            { label: "14 天", value: 14 }, { label: "30 天", value: 30 }].map((opt) => (
            <button key={opt.value} onClick={() => setDays(opt.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                days === opt.value ? "bg-indigo-500 text-white" : "bg-slate-800 text-slate-400 hover:text-slate-200"
              }`}>
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="glass rounded-xl p-6">
        <h2 className="text-xs font-semibold text-slate-400 mb-4 uppercase tracking-wide">Top 20 關鍵字</h2>
        {loading ? (
          <div className="flex justify-center py-20"><Spinner /></div>
        ) : data.length === 0 ? (
          <p className="text-slate-500 text-center py-20 text-sm">暫無資料</p>
        ) : (
          <KeywordBarChart data={data} />
        )}
      </div>

      {!loading && data.length > 0 && (
        <div className="glass rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-xs uppercase tracking-wide text-slate-500">
                <th className="px-6 py-3 text-left">#</th>
                <th className="px-6 py-3 text-left">關鍵字</th>
                <th className="px-6 py-3 text-right">出現次數</th>
                <th className="px-6 py-3 text-right">TF-IDF 分數</th>
              </tr>
            </thead>
            <tbody>
              {data.map((kw, i) => (
                <tr key={kw.keyword} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-3 text-slate-500">{i + 1}</td>
                  <td className="px-6 py-3 font-medium text-slate-200">{kw.keyword}</td>
                  <td className="px-6 py-3 text-right text-sky-400">{kw.count}</td>
                  <td className="px-6 py-3 text-right text-slate-400">{kw.tfidf_score.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
