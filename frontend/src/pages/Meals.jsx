import { useEffect, useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import Chip from '../components/ui/Chip';
import { fetchMeals, selectMeal, getSuggestedMeal, acceptSuggestedMeal } from '../lib/api';

export default function Meals() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);
  const [savingId, setSavingId] = useState(null);
  const categories = ['breakfast', 'snack', 'lunch', 'dinner'];
  const [cat, setCat] = useState('breakfast');
  const [suggested, setSuggested] = useState(null);
  const [suggestLoading, setSuggestLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setLoading(true);
      const data = await fetchMeals();
      setItems(data);
      setLoading(false);
    })();
  }, []);

  useEffect(() => {
    (async () => {
      setSuggestLoading(true);
      const s = await getSuggestedMeal(cat);
      setSuggested(s);
      setSuggestLoading(false);
    })();
  }, [cat]);

  const onSelect = async (id) => {
    setSavingId(id);
    await selectMeal(id);
    setSelectedId(id);
    setSavingId(null);
  };

  const onOk = async () => {
    if (!suggested) return;
    setSavingId(suggested.id);
    await acceptSuggestedMeal(cat, suggested.id);
    setSelectedId(suggested.id);
    setSavingId(null);
  };

  const onNo = async () => {
    if (!suggested) return;
    setSuggestLoading(true);
    const next = await getSuggestedMeal(cat, suggested.id);
    setSuggested(next);
    setSuggestLoading(false);
  };

  return (
    <div className="px-4 pt-4 pb-24">
      <h2 className="text-xl font-bold mb-3">Meals</h2>

      <div className="mb-3">
        {categories.map((c) => (
          <Chip key={c} label={c} selected={c===cat} onClick={()=>setCat(c)} />
        ))}
      </div>

      <Card className="p-3 mb-4">
        <div className="font-semibold mb-2">Suggested {cat}</div>
        {suggestLoading || !suggested ? (
          <div className="flex items-center gap-2 text-slate-600"><Spinner /> <span>Finding option…</span></div>
        ) : (
          <div className="flex gap-3 items-center">
            <img src={suggested.image} alt="" className="w-20 h-20 rounded-xl object-cover" />
            <div className="flex-1">
              <div className="font-semibold">{suggested.title}</div>
              <div className="text-xs text-slate-500">{suggested.calories} kcal</div>
            </div>
            <div className="grid grid-cols-2 gap-2 w-40">
              <Button variant="outline" onClick={onNo}>No</Button>
              <Button onClick={onOk} disabled={savingId===suggested.id}>{savingId===suggested.id ? 'Saving…' : 'OK'}</Button>
            </div>
          </div>
        )}
      </Card>
      {loading ? (
        <div className="flex items-center gap-2 text-slate-600"><Spinner /> <span>Loading meals…</span></div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {items.map((m) => (
            <Card key={m.id}>
              <img src={m.image} alt="" className="w-full h-28 object-cover rounded-t-xl" />
              <div className="p-3">
                <div className="font-semibold">{m.title}</div>
                {m.calories && <div className="text-xs text-slate-500">{m.calories} kcal</div>}
                <Button className="mt-2" variant={selectedId === m.id ? 'outline' : 'primary'} onClick={() => onSelect(m.id)}>
                  {savingId === m.id ? 'Selecting…' : selectedId === m.id ? 'Selected' : 'Select'}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
