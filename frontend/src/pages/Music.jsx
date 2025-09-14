import Chip from '../components/ui/Chip';
import Card from '../components/ui/Card';
import { playlists } from '../data/demo';

const moods = ['Happy', 'Sad', 'Angry', 'Relaxed', 'Energetic'];

export default function Music() {
  return (
    <div className="px-4 pt-4 pb-24 space-y-4">
      <h2 className="text-xl font-bold">Music</h2>
      <section>
        <h3 className="font-semibold mb-2">Mood</h3>
        {moods.map((m) => (
          <Chip key={m} label={m} />
        ))}
      </section>

      <section>
        <h3 className="font-semibold mb-2">Top picks</h3>
        <div className="space-y-3">
          {playlists.map((p) => (
            <Card key={p.id} className="flex gap-3 p-3 items-center">
              <img src={p.image} alt="" className="w-16 h-16 rounded-lg object-cover" />
              <div>
                <p className="font-semibold">{p.title}</p>
                <p className="text-xs text-slate-500">Playlist · {p.count} songs</p>
                <p className="text-xs text-slate-500">{p.subtitle}</p>
              </div>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
