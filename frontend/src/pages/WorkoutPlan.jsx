import { useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import { demoImages } from '../data/demo';

export default function WorkoutPlan() {
  const navigate = useNavigate();
  const items = [
    { name: 'Sun Salutations', minutes: 5 },
    { name: 'Warrior Poses', minutes: 10 },
    { name: 'Balancing Poses', minutes: 10 },
    { name: 'Cool Down', minutes: 5 },
  ];
  return (
    <div className="px-4 pt-4 pb-24">
      <button onClick={() => navigate(-1)} className="text-xl">←</button>
      <div className="mt-2">
        <img src={demoImages.yoga} alt="Yoga" className="w-full h-40 object-cover rounded-2xl shadow-card" />
      </div>
      <h2 className="text-2xl font-bold mt-4">Morning Yoga Flow</h2>
      <p className="text-slate-600 mt-2">
        Start your day with a gentle yoga flow to awaken your body and mind. This session focuses on stretching and
        mindfulness.
      </p>

      <h3 className="font-semibold mt-4 mb-2">Exercises</h3>
      <div className="space-y-2">
        {items.map((it) => (
          <Card key={it.name} className="p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span>🧘</span>
              <span>{it.name}</span>
            </div>
            <span className="text-slate-500 text-sm">{it.minutes} minutes</span>
          </Card>
        ))}
      </div>

      <div className="fixed bottom-20 left-0 right-0 mobile-shell mx-auto px-4">
        <Button onClick={() => navigate('/workout/active')}>Start Workout</Button>
      </div>
    </div>
  );
}
