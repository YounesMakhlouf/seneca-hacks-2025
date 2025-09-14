import { useEffect, useState } from 'react';
import Chip from '../components/ui/Chip';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import { fetchPlaylists, playTrack, skipTrack } from '../lib/api';

const moods = ['Happy', 'Sad', 'Angry', 'Relaxed', 'Energetic'];

export default function Music() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [current, setCurrent] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    (async () => {
      setLoading(true);
      const data = await fetchPlaylists();
      setList(data);
      setLoading(false);
    })();
  }, []);

  const onPlay = async (id) => {
    setBusy(true);
    await playTrack(id);
    setCurrent(id);
    setBusy(false);
  };

  const onSkip = async () => {
    if (!current && list.length) {
      setCurrent(list[0].id);
      return;
    }
    setBusy(true);
    const r = await skipTrack(current);
    setCurrent(r.playlistId);
    setBusy(false);
  };

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
        {loading ? (
          <div className="flex items-center gap-2 text-slate-600"><Spinner /> <span>Loading playlists…</span></div>
        ) : (
          <div className="space-y-3">
            {list.map((p) => (
              <Card key={p.id} className={`flex gap-3 p-3 items-center ${current === p.id ? 'ring-2 ring-primary' : ''}`}>
                <img src={p.image} alt="" className="w-16 h-16 rounded-lg object-cover" />
                <div className="flex-1">
                  <p className="font-semibold">{p.title}</p>
                  <p className="text-xs text-slate-500">Playlist · {p.count} songs</p>
                  <p className="text-xs text-slate-500">{p.subtitle}</p>
                </div>
                <div className="grid grid-cols-2 gap-2 w-40">
                  <Button variant="outline" onClick={() => onPlay(p.id)} disabled={busy && current !== p.id}>
                    {busy && current !== p.id ? '…' : current === p.id ? 'Playing' : 'Play'}
                  </Button>
                  <Button onClick={onSkip} disabled={busy}>Skip</Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
