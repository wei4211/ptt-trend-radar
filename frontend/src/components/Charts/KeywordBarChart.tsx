import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { Keyword } from "../../types";

interface Props {
  data: Keyword[];
}

const COLORS = [
  "#38bdf8", "#818cf8", "#34d399", "#fb923c", "#f472b6",
  "#a78bfa", "#22d3ee", "#86efac", "#fde68a", "#fca5a5",
];

export default function KeywordBarChart({ data }: Props) {
  const sliced = data.slice(0, 15);
  return (
    <ResponsiveContainer width="100%" height={360}>
      <BarChart
        data={sliced}
        layout="vertical"
        margin={{ top: 0, right: 24, bottom: 0, left: 8 }}
      >
        <XAxis type="number" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis
          type="category"
          dataKey="keyword"
          width={72}
          tick={{ fill: "#94a3b8", fontSize: 12 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          cursor={{ fill: "rgba(148,163,184,0.05)" }}
          contentStyle={{
            background: "#1e293b",
            border: "1px solid #334155",
            borderRadius: 8,
            fontSize: 12,
          }}
          formatter={(val: number) => [val, "出現次數"]}
        />
        <Bar dataKey="count" radius={[0, 4, 4, 0]}>
          {sliced.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
