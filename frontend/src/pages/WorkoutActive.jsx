import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProgressBar from '../components/ui/ProgressBar';
import Button from '../components/ui/Button';
import { demoImages } from '../data/demo';
import { skipWorkoutStep, completeWorkout } from '../lib/api';

export default function WorkoutActive() {
  const navigate = useNavigate();
  const [seconds, setSeconds] = useState(23);
  const [minutes, setMinutes] = useState(15);
  const [progress, setProgress] = useState(30);
  const [paused, setPaused] = useState(false);
  const [step, setStep] = useState(1);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (paused) return;
    const id = setInterval(() => setProgress((p) => Math.min(100, p + 1)), 1000);
    return () => clearInterval(id);
  }, [paused]);

  return (
    <div className="px-4 pt-4 pb-24 space-y-4">
      <div className="flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="text-2xl">✕</button>
        <h2 className="text-lg font-bold">Workout</h2>
        <span />
      </div>
      <div>
        <p className="text-sm text-slate-600 mb-2">Workout Progress</p>
        <ProgressBar value={progress} />
        <p className="text-xs text-slate-500 mt-1">{progress}% Complete</p>
      </div>

      <div className="grid grid-cols-2 gap-4 text-center">
        <div className="bg-white rounded-xl p-4 border text-2xl font-bold">{minutes}<div className="text-xs text-slate-500">Minutes</div></div>
        <div className="bg-white rounded-xl p-4 border text-2xl font-bold">{seconds}<div className="text-xs text-slate-500">Seconds</div></div>
      </div>

      <div className="text-center">
        <h3 className="font-semibold">Exercise {step}: Jumping Jacks</h3>
        <p className="text-slate-500 text-sm">Duration: 1 minute</p>
      </div>

      <div className="w-full h-48 rounded-2xl overflow-hidden">
        <img src={demoImages.run} alt="Jumping Jacks" className="w-full h-full object-cover" />
      </div>

      <div className="fixed bottom-20 left-0 right-0 mobile-shell mx-auto px-4 grid grid-cols-3 gap-3">
        <Button variant="outline" onClick={() => setPaused((p) => !p)}>{paused ? 'Resume' : 'Pause'}</Button>
        <Button variant="outline" onClick={async () => { setBusy(true); await skipWorkoutStep(step); setStep((s) => s + 1); setBusy(false); }} disabled={busy}>Skip</Button>
        <Button onClick={async () => { setBusy(true); await completeWorkout(1); setBusy(false); navigate('/dashboard'); }} disabled={busy}>Complete</Button>
      </div>
    </div>
  );
}
