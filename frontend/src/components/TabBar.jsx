import { NavLink } from 'react-router-dom';

const tabs = [
  { to: '/dashboard', label: 'Dashboard', icon: '🏠' },
  { to: '/meals', label: 'Meals', icon: '🍽️' },
  { to: '/workout/plan', label: 'Workouts', icon: '🏋️' },
  { to: '/music', label: 'Music', icon: '🎵' },
  { to: '/coach', label: 'Live Coach', icon: '🔴' },
  { to: '/settings', label: 'Settings', icon: '⚙️' },
];

export default function TabBar() {
  return (
    <nav className="mobile-shell fixed bottom-0 left-0 right-0 mx-auto bg-white/95 backdrop-blur border-t border-slate-200 shadow-card">
  <ul className="grid grid-cols-6 text-[11px]">
        {tabs.map((t) => (
          <li key={t.to}>
            <NavLink
              to={t.to}
              className={({ isActive }) =>
                `flex flex-col items-center py-2.5 ${isActive ? 'text-primary' : 'text-slate-600'}`
              }
            >
              <span className="text-lg" aria-hidden>{t.icon}</span>
              <span className="mt-0.5 leading-none">{t.label}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
