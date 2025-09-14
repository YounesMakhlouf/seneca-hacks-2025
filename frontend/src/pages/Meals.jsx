import { useEffect, useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import { fetchMeals, selectMeal } from '../lib/api';

export default function Meals() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);
  const [savingId, setSavingId] = useState(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      const data = await fetchMeals();
      setItems(data);
      setLoading(false);
    })();
  }, []);

  const onSelect = async (id) => {
    setSavingId(id);
    await selectMeal(id);
    setSelectedId(id);
    setSavingId(null);
  };

  return (
    <div className="px-4 pt-4 pb-24">
      <h2 className="text-xl font-bold mb-3">Meals</h2>
      {loading ? (
        <div className="flex items-center gap-2 text-slate-600"><Spinner /> <span>Loading meals…</span></div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {items.map((m) => (
            <Card key={m.id}>
              <img src={m.image} alt="" className="w-full h-28 object-cover rounded-t-xl" />
              <div className="p-3">
                <div className="font-semibold">{m.title}</div>
                <div className="text-xs text-slate-500">{m.calories} kcal</div>
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
