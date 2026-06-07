import { useState } from "react";
import { useArticles } from "../hooks/useAnalysis";
import BoardSelector from "../components/UI/BoardSelector";
import Spinner from "../components/UI/Spinner";
import type { Board, Article } from "../types";
import clsx from "clsx";

const SENTIMENT_STYLE = {
  positive: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  neutral: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  negative: "bg-rose-500/10 text-rose-400 border-rose-500/20",
};
const SENTIMENT_LABEL = { positive: "😊 正面", neutral: "😐 中性", negative: "😟 負面" };

function ArticleRow({ article }: { article: Article }) {
  const label = article.sentiment_label as keyof typeof SENTIMENT_LABEL;
  return (
    <tr className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
      <td className="px-4 py-3">
        <span className="inline-block px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-400">
          {article.board}
        </span>
      </td>
      <td className="px-4 py-3">
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-200 hover:text-sky-400 transition-colors text-sm line-clamp-1"
        >
          {article.title}
        </a>
      </td>
      <td className="px-4 py-3 text-slate-500 text-xs">{article.author}</td>
      <td className="px-4 py-3 text-right">
        <span className="text-emerald-400 text-sm font-medium">↑{article.push_count}</span>
        {article.boo_count > 0 && (
          <span className="text-rose-400 text-sm font-medium ml-1">↓{article.boo_count}</span>
        )}
      </td>
      <td className="px-4 py-3">
        {label && (
          <span className={clsx("inline-block px-2 py-0.5 rounded-full text-xs border", SENTIMENT_STYLE[label])}>
            {SENTIMENT_LABEL[label]}
          </span>
        )}
      </td>
      <td className="px-4 py-3 text-slate-500 text-xs whitespace-nowrap">
        {article.published_at ? article.published_at.slice(0, 10) : "—"}
      </td>
    </tr>
  );
}

export default function Articles() {
  const [board, setBoard] = useState<Board>("all");
  const [days, setDays] = useState(7);
  const [search, setSearch] = useState("");
  const { data, loading } = useArticles(board, days);

  const filtered = search
    ? data.filter((a) => a.title.toLowerCase().includes(search.toLowerCase()))
    : data;

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">文章列表</h1>
        <p className="text-slate-400 text-sm mt-1">依推文數排序，含情緒分析結果</p>
      </div>

      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex flex-wrap gap-3 items-center">
          <BoardSelector value={board} onChange={setBoard} />
          <div className="flex gap-2">
            {[1, 3, 7, 14].map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  days === d
                    ? "bg-indigo-500 text-white"
                    : "bg-slate-800 text-slate-400 hover:text-slate-200"
                }`}
              >
                {d === 1 ? "今日" : `${d} 天`}
              </button>
            ))}
          </div>
        </div>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="搜尋標題..."
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 w-52"
        />
      </div>

      <div className="glass rounded-xl overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-20"><Spinner /></div>
        ) : filtered.length === 0 ? (
          <p className="text-center py-20 text-slate-500 text-sm">暫無文章</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700 text-xs uppercase tracking-wide text-slate-500">
                  <th className="px-4 py-3 text-left">看板</th>
                  <th className="px-4 py-3 text-left">標題</th>
                  <th className="px-4 py-3 text-left">作者</th>
                  <th className="px-4 py-3 text-right">推/噓</th>
                  <th className="px-4 py-3 text-left">情緒</th>
                  <th className="px-4 py-3 text-left">日期</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((a) => (
                  <ArticleRow key={a.id} article={a} />
                ))}
              </tbody>
            </table>
            <div className="px-4 py-3 border-t border-slate-800 text-xs text-slate-500">
              共 {filtered.length} 篇
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
