export default function TopBar() {
  return (
    <header className="mobile-shell sticky top-0 z-20 bg-soft/80 backdrop-blur border-b border-slate-200/60">
      <div className="px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="inline-flex h-7 w-7 items-center justify-center rounded-lg bg-primary/15 text-primary">⚡</span>
          <span className="font-extrabold tracking-tight">FitMix</span>
        </div>
        <div className="text-xs text-slate-500">Beta</div>
      </div>
    </header>
  );
}
