import type { Board } from "../../types";

const BOARDS: { value: Board; label: string }[] = [
  { value: "all", label: "全部看板" },
  { value: "Gossiping", label: "八卦" },
  { value: "Stock", label: "Stock" },
  { value: "NBA", label: "NBA" },
  { value: "Tech_Job", label: "Tech_Job" },
];

interface Props {
  value: Board;
  onChange: (board: Board) => void;
}

export default function BoardSelector({ value, onChange }: Props) {
  return (
    <div className="flex gap-2 flex-wrap">
      {BOARDS.map((b) => (
        <button
          key={b.value}
          onClick={() => onChange(b.value)}
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors border ${
            value === b.value
              ? "bg-sky-500 border-sky-500 text-white"
              : "border-slate-700 text-slate-400 hover:border-slate-500 hover:text-slate-300"
          }`}
        >
          {b.label}
        </button>
      ))}
    </div>
  );
}
