import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Modal from '../components/ui/Modal';
import Spinner from '../components/ui/Spinner';
import { playlists, meals, workouts, recipeDetails } from '../data/demo';
import { getTodaySuggestions, getRecipeDetail, getWorkoutPlan, selectMeal, startWorkout } from '../lib/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [suggest, setSuggest] = useState(null);
  const [recipe, setRecipe] = useState(null);
  const [plan, setPlan] = useState(null);
  const [savingMeal, setSavingMeal] = useState(false);

  useEffect(() => {
    (async () => {
      setLoading(true);
      const s = await getTodaySuggestions();
      setSuggest(s);
      setLoading(false);
    })();
  }, []);

  const onShuffle = async () => {
    setLoading(true);
    const s = await getTodaySuggestions();
    setSuggest(s);
    setLoading(false);
  };

  const onViewRecipe = async () => {
    const r = await getRecipeDetail(suggest.mealId);
    setRecipe(r);
  };

  const onAcceptMeal = async () => {
    setSavingMeal(true);
    await selectMeal(suggest.mealId);
    setSavingMeal(false);
  };

  const onStartWorkout = async () => {
    const p = await getWorkoutPlan(suggest.workoutId);
    setPlan(p);
  };

  const goActive = async () => {
    await startWorkout(suggest.workoutId);
    navigate('/workout/active');
  };

  return (
    <div className="px-4 pt-4 pb-24 space-y-4">
      <section>
        <h3 className="font-bold text-lg mb-2">Today’s Suggestions</h3>
        {loading || !suggest ? (
          <div className="flex items-center gap-2 text-slate-600"><Spinner /> <span>Finding good picks…</span></div>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            <Card className="p-3 flex items-center gap-3">
              <div className="h-16 w-16 rounded-xl overflow-hidden">
                <img src={meals.find(m=>m.id===suggest.mealId)?.image} alt="" className="w-full h-full object-cover" />
              </div>
              <div className="flex-1">
                <div className="font-semibold">Recipe: {meals.find(m=>m.id===suggest.mealId)?.title}</div>
                <div className="text-xs text-slate-500">Balanced and quick to prepare</div>
              </div>
              <div className="grid grid-cols-2 gap-2 w-44">
                <Button variant="outline" onClick={onViewRecipe}>View</Button>
                <Button onClick={onAcceptMeal} disabled={savingMeal}>{savingMeal ? 'Saving…' : 'Accept'}</Button>
              </div>
            </Card>

            <Card className="p-3 flex items-center gap-3">
              <div className="h-16 w-16 rounded-xl overflow-hidden">
                <img src={workouts.find(w=>w.id===suggest.workoutId)?.image} alt="" className="w-full h-full object-cover" />
              </div>
              <div className="flex-1">
                <div className="font-semibold">Workout: {workouts.find(w=>w.id===suggest.workoutId)?.title}</div>
                <div className="text-xs text-slate-500">Ready in under 30 minutes</div>
              </div>
              <div className="grid grid-cols-2 gap-2 w-44">
                <Button variant="outline" onClick={onStartWorkout}>Plan</Button>
                <Button onClick={goActive}>Start</Button>
              </div>
            </Card>

            <div className="flex justify-end">
              <Button variant="outline" onClick={onShuffle}>Shuffle</Button>
            </div>
          </div>
        )}
      </section>
      <section>
        <h3 className="font-bold text-lg mb-2">Music for your workout</h3>
        <div className="flex gap-3 overflow-x-auto no-scrollbar">
          {playlists.map((p) => (
            <Card key={p.id} className="min-w-[160px]">
              <img src={p.image} alt={p.title} className="w-full h-28 object-cover rounded-t-xl" />
              <div className="p-3">
                <p className="font-semibold text-sm">{p.title}</p>
                <p className="text-xs text-slate-500">{p.subtitle.split(' ').slice(0, 3).join(' ')}…</p>
              </div>
            </Card>
          ))}
        </div>
      </section>

      <section>
        <h3 className="font-bold text-lg mb-2">Meal Recommendations</h3>
        <div className="flex gap-3 overflow-x-auto no-scrollbar">
          {meals.map((m) => (
            <Card key={m.id} className="min-w-[200px]">
              <img src={m.image} alt={m.title} className="w-full h-32 object-cover rounded-t-xl" />
              <div className="p-3 font-semibold">{m.title}</div>
            </Card>
          ))}
        </div>
      </section>

      <section>
        <h3 className="font-bold text-lg mb-2">Workout Suggestions</h3>
        <div className="grid grid-cols-2 gap-3">
          {workouts.map((w) => (
            <Card key={w.id}>
              <img src={w.image} alt={w.title} className="w-full h-28 object-cover rounded-t-xl" />
              <div className="p-3">
                <p className="font-semibold">{w.title}</p>
              </div>
            </Card>
          ))}
        </div>
      </section>
      <Modal open={!!recipe} onClose={() => setRecipe(null)} title={recipe?.title}
        footer={<Button onClick={() => setRecipe(null)}>Close</Button>}>
        <div className="text-sm">
          <div className="font-semibold mb-1">Ingredients</div>
          <ul className="list-disc pl-5 mb-3">
            {recipe?.ingredients?.map((i) => <li key={i}>{i}</li>)}
          </ul>
          <div className="font-semibold mb-1">Steps</div>
          <ol className="list-decimal pl-5">
            {recipe?.steps?.map((s, idx) => <li key={idx}>{s}</li>)}
          </ol>
        </div>
      </Modal>

      <Modal open={!!plan} onClose={() => setPlan(null)} title={plan?.title}
        footer={<Button onClick={() => setPlan(null)}>Close</Button>}>
        <div className="text-sm">
          <ul className="list-disc pl-5">
            {plan?.steps?.map((s, i) => <li key={i}>{s.name} · {s.minutes} min</li>)}
          </ul>
        </div>
      </Modal>

    </div>
  );
}
