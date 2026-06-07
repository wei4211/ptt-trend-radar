import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import type { SentimentOverview } from "../../types";

const COLORS = { positive: "#34d399", neutral: "#94a3b8", negative: "#f87171" };
const LABELS = { positive: "正面", neutral: "中性", negative: "負面" };

interface Props {
  data: SentimentOverview;
}

export default function SentimentPieChart({ data }: Props) {
  const chartData = [
    { name: LABELS.positive, value: data.positive, key: "positive" },
    { name: LABELS.neutral, value: data.neutral, key: "neutral" },
    { name: LABELS.negative, value: data.negative, key: "negative" },
  ].filter((d) => d.value > 0);

  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={70}
          outerRadius={110}
          paddingAngle={3}
          dataKey="value"
          label={({ name, value }) => `${name} ${value}%`}
          labelLine={false}
        >
          {chartData.map((entry) => (
            <Cell
              key={entry.key}
              fill={COLORS[entry.key as keyof typeof COLORS]}
            />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background: "#1e293b",
            border: "1px solid #334155",
            borderRadius: 8,
            fontSize: 12,
          }}
          formatter={(val: number) => [`${val}%`]}
        />
        <Legend
          formatter={(value) => (
            <span style={{ color: "#94a3b8", fontSize: 12 }}>{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
