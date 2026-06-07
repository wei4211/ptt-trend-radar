import { NavLink } from "react-router-dom";
import { LayoutDashboard, Brain, KeyRound, MessageSquare, Cloud, Newspaper } from "lucide-react";
import clsx from "clsx";

const NAV_ITEMS = [
  { to: "/", label: "總覽", icon: LayoutDashboard },
  { to: "/topics", label: "主題分析", icon: Brain, badge: "V2" },
  { to: "/keywords", label: "關鍵字", icon: KeyRound },
  { to: "/sentiment", label: "情緒分析", icon: MessageSquare },
  { to: "/wordcloud", label: "文字雲", icon: Cloud },
  { to: "/articles", label: "文章列表", icon: Newspaper },
];

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 flex flex-col bg-slate-900 border-r border-slate-800 h-screen sticky top-0">
      <div className="px-6 py-5 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-sky-500 flex items-center justify-center shrink-0">
            <span className="text-white text-xs font-bold">P</span>
          </div>
          <div>
            <p className="font-bold text-white text-sm leading-tight">PTT Trend</p>
            <p className="text-xs text-sky-400 leading-tight">Radar</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sky-500/20 text-sky-400 border border-sky-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                )
              }
            >
              <Icon size={16} strokeWidth={1.8} />
              <span className="flex-1">{item.label}</span>
              {"badge" in item && (
                <span className="text-xs px-1.5 py-0.5 rounded bg-violet-500/20 text-violet-400 font-mono">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      <div className="px-4 py-3 border-t border-slate-800 text-xs text-slate-500">
        PTT Trend Radar v2.0
      </div>
    </aside>
  );
}
