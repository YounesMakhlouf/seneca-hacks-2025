import { useRef, useState, useEffect } from 'react';

export default function FormCorrector() {
  const [exercise, setExercise] = useState('pushup');
  const [status, setStatus] = useState('');
  const [videoUrl, setVideoUrl] = useState(null);
  const fileRef = useRef();
  const API_BASE = process.env.REACT_APP_FORM_CORRECTOR_URL || 'http://localhost:9000';

  useEffect(() => {
    return () => {
      if (videoUrl) URL.revokeObjectURL(videoUrl);
    };
  }, [videoUrl]);

  const onUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setStatus('Uploading…');
    const body = new FormData();
    body.append('file', file);
    body.append('exercise', exercise);
    try {
      const res = await fetch(`${API_BASE}/vision/analyze`, {
        method: 'POST',
        headers: {
          Accept: 'video/mp4,application/json',
        },
        body,
      });
      const ctype = res.headers.get('content-type') || '';
      if (!res.ok) {
        // Try to parse JSON error message first
        let msg = `Upload failed (${res.status})`;
        try {
          if (ctype.includes('application/json')) {
            const j = await res.json();
            if (j && (j.error || j.detail)) msg = j.error || j.detail;
          } else {
            const t = await res.text();
            if (t) msg = t;
          }
        } catch (_) { /* ignore */ }
        throw new Error(msg);
      }
      if (ctype.includes('application/json')) {
        // Backend returned JSON instead of video; surface message
        const j = await res.json();
        throw new Error(j?.error || 'Unexpected JSON response from server');
      }
      const blob = await res.blob();
      if (!blob || !blob.size) throw new Error('Empty video returned');
      const url = URL.createObjectURL(blob);
      setVideoUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return url;
      });
      setStatus('');
    } catch (err) {
      setStatus('Error: ' + err.message);
    }
  };

  return (
    <div className="px-4 pt-4 pb-24">
      <h1 className="text-xl font-bold mb-1">Form Corrector</h1>
      <p className="text-slate-600 mb-4">Upload a short video and get real-time form feedback overlay.</p>

      <label className="block mb-2 text-sm">Exercise</label>
      <select className="w-full rounded-xl border border-slate-200 px-3 py-2 bg-white" value={exercise} onChange={e=>setExercise(e.target.value)}>
        <option value="pushup">Pushup</option>
        <option value="squat">Squat</option>
        <option value="plank">Plank</option>
      </select>

      <div className="mt-4">
        <input ref={fileRef} type="file" accept="video/*" onChange={onUpload} className="hidden" />
        <button onClick={()=>fileRef.current?.click()} className="w-full py-3 rounded-xl bg-ink text-white">Upload Video</button>
      </div>

      {status && <div className="mt-3 text-sm text-slate-600">{status}</div>}

      {videoUrl && (
        <div className="mt-4">
          <video className="w-full rounded-xl" controls src={videoUrl} />
          <a href={videoUrl} download className="inline-block mt-3 text-primary font-semibold">Download Processed Video</a>
        </div>
      )}

      <div className="mt-6 text-sm text-slate-500">
        Tip: Keep videos short (≤30s) for faster processing. Recording with your phone in portrait works well.
      </div>
    </div>
  );
}
