import { useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';
import { demoImages } from '../data/demo';

export default function Welcome() {
  const navigate = useNavigate();
  return (
    <div className="px-4 pt-6 pb-8">
      <div className="w-full aspect-[3/2] rounded-2xl overflow-hidden shadow-card">
        <img src={demoImages.welcome} alt="Listening" className="w-full h-full object-cover" />
      </div>
  <h1 className="text-2xl font-extrabold mt-6">Welcome to FitMix</h1>
      <p className="text-slate-600 mt-3">
        Discover personalized music, meal, and workout recommendations tailored to your mood and preferences. Let's
        begin your journey to a balanced lifestyle.
      </p>

      <div className="mt-6 space-y-3">
        <Button onClick={() => navigate('/dashboard')}>Start Demo</Button>
        <Button variant="outline" onClick={() => navigate('/login')}>Sign Up</Button>
      </div>
    </div>
  );
}
