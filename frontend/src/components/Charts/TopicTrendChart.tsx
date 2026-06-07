import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { TopicTrendPoint } from "../../types";

interface Props {
  data: TopicTrendPoint[];
  color?: string;
}

export default function TopicTrendChart({ data, color = "#38bdf8" }: Props) {
  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
        暫無趨勢資料
      </div>
    );
  }
  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id={`grad-${color.replace("#", "")}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey="date"
          tick={{ fill: "#64748b", fontSize: 10 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v: string) => v.slice(5)}
        />
        <YAxis
          tick={{ fill: "#64748b", fontSize: 10 }}
          axisLine={false}
          tickLine={false}
          allowDecimals={false}
        />
        <Tooltip
          contentStyle={{
            background: "#1e293b",
            border: "1px solid #334155",
            borderRadius: 8,
            fontSize: 12,
          }}
          formatter={(val: number) => [val, "文章數"]}
          labelFormatter={(l: string) => `日期：${l}`}
        />
        <Area
          type="monotone"
          dataKey="count"
          stroke={color}
          strokeWidth={2}
          fill={`url(#grad-${color.replace("#", "")})`}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
