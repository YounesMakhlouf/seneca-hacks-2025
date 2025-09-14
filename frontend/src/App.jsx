import { Routes, Route, Navigate } from 'react-router-dom';
import AppShell from './components/AppShell';
import Welcome from './pages/Welcome';
import Login from './pages/Login';
import Preferences from './pages/Preferences';
import Dashboard from './pages/Dashboard';
import WorkoutPlan from './pages/WorkoutPlan';
import Music from './pages/Music';
import WorkoutActive from './pages/WorkoutActive';
import Meals from './pages/Meals';
import Settings from './pages/Settings';

export default function App() {
  return (
    <div className="bg-soft min-h-screen">
      <AppShell>
        <Routes>
          <Route path="/" element={<Welcome />} />
          <Route path="/login" element={<Login />} />
          <Route path="/preferences" element={<Preferences />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/workout/plan" element={<WorkoutPlan />} />
          <Route path="/workout/active" element={<WorkoutActive />} />
          <Route path="/music" element={<Music />} />
          <Route path="/meals" element={<Meals />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </div>
  );
}
