export default function Spinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const s = { sm: "h-4 w-4 border", md: "h-8 w-8 border-2", lg: "h-12 w-12 border-2" }[size];
  return (
    <div className={`animate-spin rounded-full border-slate-700 border-t-sky-500 ${s}`} />
  );
}
