import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import { fetchWorkouts, startWorkout } from '../lib/api';

export default function Workouts() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      setLoading(true);
      const data = await fetchWorkouts();
      setItems(data);
      setLoading(false);
    })();
  }, []);

  const onStart = async (id) => {
    setBusyId(id);
    await startWorkout(id);
    setBusyId(null);
    navigate('/workout/active');
  };

  return (
    <div className="px-4 pt-4 pb-24">
      <h2 className="text-xl font-bold mb-3">Workouts</h2>
      {loading ? (
        <div className="flex items-center gap-2 text-slate-600"><Spinner /> <span>Loading workouts…</span></div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {items.map((w) => (
            <Card key={w.id}>
              <img src={w.image} alt="" className="w-full h-28 object-cover rounded-t-xl" />
              <div className="p-3">
                <div className="font-semibold">{w.title}</div>
                <div className="text-xs text-slate-500">{w.duration} min · {w.exercises} exercises</div>
                <Button className="mt-2" onClick={() => onStart(w.id)} disabled={busyId === w.id}>
                  {busyId === w.id ? 'Starting…' : 'Start'}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
