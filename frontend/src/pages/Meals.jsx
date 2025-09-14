import Card from '../components/ui/Card';
import { meals } from '../data/demo';

export default function Meals() {
  return (
    <div className="px-4 pt-4 pb-24">
      <h2 className="text-xl font-bold mb-3">Meals</h2>
      <div className="grid grid-cols-2 gap-3">
        {meals.map((m) => (
          <Card key={m.id}>
            <img src={m.image} alt="" className="w-full h-28 object-cover rounded-t-xl" />
            <div className="p-3 font-semibold">{m.title}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}
