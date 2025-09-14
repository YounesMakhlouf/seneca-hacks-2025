import { useEffect, useRef, useState } from 'react';

export default function LiveCoach() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [status, setStatus] = useState('');
  const [exercise, setExercise] = useState('pushup');
  const runningRef = useRef(false);

  useEffect(() => {
    let stream;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    (async () => {
      try {
        setStatus('Requesting camera…');
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
        video.srcObject = stream;
        await video.play();
        setStatus('Camera started');
        runningRef.current = true;
        requestAnimationFrame(loop);
      } catch (e) {
        setStatus('Camera error: ' + (e?.message || e));
      }
    })();

    const loop = async () => {
      if (!runningRef.current) return;
      const w = video.videoWidth || 640;
      const h = video.videoHeight || 480;
      canvas.width = w; canvas.height = h;
      // Draw current frame to canvas & get PNG bytes
      ctx.drawImage(video, 0, 0, w, h);
      const blob = await new Promise(res => canvas.toBlob(res, 'image/jpeg', 0.7));
      try {
        const form = new FormData();
        form.append('file', blob, 'frame.jpg');
        form.append('exercise', exercise);
        const r = await fetch('http://localhost:9000/vision/stream-frame', { method: 'POST', body: form });
        if (r.ok) {
          const data = await r.json();
          drawOverlay(ctx, data, w, h);
          setStatus(data.feedback || 'Tracking…');
        } else {
          setStatus('Server error');
        }
      } catch (err) {
        setStatus('Network error');
      }
      requestAnimationFrame(loop);
    };

    return () => {
      runningRef.current = false;
      try { stream?.getTracks().forEach(t => t.stop()); } catch {}
    };
  }, [exercise]);

  const drawOverlay = (ctx, data, w, h) => {
    if (!data || !data.landmarks) return;
    ctx.save();
    // Clear and redraw frame image has already been drawn; just draw overlays
    const pts = data.landmarks.map(([x,y]) => ({x: x * w, y: y * h}));
    ctx.strokeStyle = '#22e3a7';
    ctx.fillStyle = '#0f172a';
    for (const p of pts) {
      ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, Math.PI*2); ctx.fill();
    }
    // Feedback banner
    if (data.feedback) {
      ctx.fillStyle = 'rgba(0,0,0,0.6)';
      ctx.fillRect(10, 10, Math.min(w-20, 360), 36);
      ctx.fillStyle = '#22e3a7';
      ctx.font = '16px sans-serif';
      ctx.fillText(data.feedback, 20, 34);
    }
    ctx.restore();
  };

  return (
    <div className="px-4 pt-4 pb-24">
      <h1 className="text-xl font-bold mb-2">Live Coach</h1>
      <p className="text-slate-600 mb-4">Streaming frames to backend for feedback. Choose an exercise below.</p>
      <div className="flex gap-2 mb-3">
        <select value={exercise} onChange={e=>setExercise(e.target.value)} className="rounded-xl border border-slate-200 px-3 py-2 bg-white">
          <option value="pushup">Pushup</option>
          <option value="squat">Squat</option>
          <option value="plank">Plank</option>
        </select>
      </div>
      <div className="relative w-full rounded-xl overflow-hidden bg-black">
        <video ref={videoRef} className="w-full" playsInline muted />
        <canvas ref={canvasRef} className="w-full absolute inset-0" />
      </div>
      <div className="mt-3 text-sm text-slate-600">{status}</div>
      <p className="mt-2 text-xs text-slate-500">Tip: Stand back so your full body is visible and ensure good lighting.</p>
    </div>
  );
}
