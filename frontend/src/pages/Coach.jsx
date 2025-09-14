import { useNavigate } from 'react-router-dom';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

export default function Coach() {
  const navigate = useNavigate();
  return (
    <div className="px-4 pt-4 pb-24 space-y-4">
      <h1 className="text-xl font-bold">Live Coach</h1>
      <p className="text-slate-600">Choose how you'd like to get form feedback.</p>

      <div className="grid grid-cols-1 gap-3">
        <Card className="p-4 flex items-center gap-3">
          <div className="h-12 w-12 rounded-xl bg-primary/15 text-primary flex items-center justify-center text-2xl" aria-hidden>📹</div>
          <div className="flex-1">
            <div className="font-semibold">Upload a Video</div>
            <div className="text-sm text-slate-500">Process a short clip and get an annotated result.</div>
          </div>
          <Button className="w-auto" onClick={() => navigate('/form-corrector')}>Open</Button>
        </Card>

        <Card className="p-4 flex items-center gap-3">
          <div className="h-12 w-12 rounded-xl bg-primary/15 text-primary flex items-center justify-center text-2xl" aria-hidden>🔴</div>
          <div className="flex-1">
            <div className="font-semibold">Live Camera</div>
            <div className="text-sm text-slate-500">Use your camera to get real-time feedback.</div>
          </div>
          <Button className="w-auto" onClick={() => navigate('/live-coach')}>Open</Button>
        </Card>
      </div>
    </div>
  );
}
