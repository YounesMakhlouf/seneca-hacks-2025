import Card from '../components/ui/Card';
import { playlists, meals, workouts } from '../data/demo';

export default function Dashboard() {
  return (
    <div className="px-4 pt-4 pb-24 space-y-4">
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
    </div>
  );
}
