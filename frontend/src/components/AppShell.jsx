import TabBar from './TabBar';
import TopBar from './TopBar';

export default function AppShell({ children }) {
  return (
    <div className="mobile-shell min-h-screen flex flex-col bg-soft text-ink">
      <TopBar />
      <div className="flex-1 overflow-y-auto no-scrollbar pb-24">{children}</div>
      <TabBar />
    </div>
  );
}
