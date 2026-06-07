import clsx from "clsx";
import { LucideIcon } from "lucide-react";

interface Props {
  title: string;
  value: string | number;
  icon: LucideIcon;
  subtitle?: string;
  accent?: "sky" | "emerald" | "rose" | "amber";
}

const accentMap = {
  sky: "text-sky-400 bg-sky-500/10 border-sky-500/20",
  emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  rose: "text-rose-400 bg-rose-500/10 border-rose-500/20",
  amber: "text-amber-400 bg-amber-500/10 border-amber-500/20",
};

export default function StatCard({ title, value, icon: Icon, subtitle, accent = "sky" }: Props) {
  return (
    <div className="glass rounded-xl p-5 flex items-start gap-4">
      <div className={clsx("p-2.5 rounded-lg border", accentMap[accent])}>
        <Icon size={18} strokeWidth={1.8} />
      </div>
      <div className="min-w-0">
        <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{title}</p>
        <p className="text-2xl font-bold text-white mt-0.5 truncate">{value}</p>
        {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
      </div>
    </div>
  );
}
