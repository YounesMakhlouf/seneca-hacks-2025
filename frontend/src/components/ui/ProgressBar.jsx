export default function ProgressBar({ value = 0 }) {
  const pct = Math.max(0, Math.min(100, value));
  return (
    <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
      <div className="h-full bg-primary" style={{ width: `${pct}%` }} />
    </div>
  );
}
