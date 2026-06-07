import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import type { SentimentTrendPoint } from "../../types";

interface Props {
  data: SentimentTrendPoint[];
}

export default function TrendLineChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey="date"
          tick={{ fill: "#64748b", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v: string) => v.slice(5)}
        />
        <YAxis
          domain={[0, 1]}
          tick={{ fill: "#64748b", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v: number) => v.toFixed(1)}
        />
        <Tooltip
          contentStyle={{
            background: "#1e293b",
            border: "1px solid #334155",
            borderRadius: 8,
            fontSize: 12,
          }}
          formatter={(val: number) => [val.toFixed(3), "情緒分數"]}
          labelFormatter={(l: string) => `日期：${l}`}
        />
        <ReferenceLine y={0.6} stroke="#34d399" strokeDasharray="4 2" strokeOpacity={0.4} />
        <ReferenceLine y={0.4} stroke="#f87171" strokeDasharray="4 2" strokeOpacity={0.4} />
        <Line
          type="monotone"
          dataKey="avg_score"
          stroke="#38bdf8"
          strokeWidth={2}
          dot={{ r: 3, fill: "#38bdf8" }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
