import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import Chip from '../components/ui/Chip';
import { fetchWorkouts, startWorkout, getSuggestedWorkout, acceptSuggestedWorkout } from '../lib/api';

export default function Workouts() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const [savingId, setSavingId] = useState(null);
  const categories = ['cardio', 'strength', 'mobility'];
  const [cat, setCat] = useState('cardio');
  const [suggested, setSuggested] = useState(null);
  const [suggestLoading, setSuggestLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      setLoading(true);
      const data = await fetchWorkouts();
      setItems(data);
      setLoading(false);
    })();
  }, []);

  useEffect(() => {
    (async () => {
      setSuggestLoading(true);
      const s = await getSuggestedWorkout(cat);
      setSuggested(s);
      setSuggestLoading(false);
    })();
  }, [cat]);

  const onStart = async (id) => {
    setBusyId(id);
    await startWorkout(id);
    setBusyId(null);
    navigate('/workout/active');
  };

  const onOk = async () => {
    if (!suggested) return;
    setSavingId(suggested.id);
    await acceptSuggestedWorkout(cat, suggested.id);
    await onStart(suggested.id);
    setSavingId(null);
  };

  const onNo = async () => {
    if (!suggested) return;
    setSuggestLoading(true);
    const next = await getSuggestedWorkout(cat, suggested.id);
    setSuggested(next);
    setSuggestLoading(false);
  };

  return (
    <div className="px-4 pt-4 pb-24">
      <h2 className="text-xl font-bold mb-3">Workouts</h2>

      <div className="mb-3">
        {categories.map((c) => (
          <Chip key={c} label={c} selected={c===cat} onClick={()=>setCat(c)} />
        ))}
      </div>

      <Card className="p-3 mb-4">
        <div className="font-semibold mb-2">Suggested {cat}</div>
        {suggestLoading || !suggested ? (
          <div className="flex items-center gap-2 text-slate-600"><Spinner /> <span>Finding workout…</span></div>
        ) : (
          <div className="flex gap-3 items-center">
            <img src={suggested.image} alt="" className="w-20 h-20 rounded-xl object-cover" />
            <div className="flex-1">
              <div className="font-semibold">{suggested.title}</div>
              <div className="text-xs text-slate-500">{suggested.duration} min · {suggested.exercises} exercises</div>
            </div>
            <div className="grid grid-cols-2 gap-2 w-40">
              <Button variant="outline" onClick={onNo}>No</Button>
              <Button onClick={onOk} disabled={savingId===suggested.id || busyId===suggested.id}>{savingId===suggested.id || busyId===suggested.id ? 'Starting…' : 'OK'}</Button>
            </div>
          </div>
        )}
      </Card>
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
