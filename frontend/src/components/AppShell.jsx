import TabBar from './TabBar';

export default function AppShell({ children }) {
  return (
    <div className="mobile-shell min-h-screen flex flex-col bg-soft text-ink">
      <div className="flex-1 overflow-y-auto no-scrollbar pb-20">{children}</div>
      <TabBar />
    </div>
  );
}
