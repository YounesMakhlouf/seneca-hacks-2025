import { useRef, useState } from 'react';

export default function FormCorrector() {
  const [exercise, setExercise] = useState('pushup');
  const [status, setStatus] = useState('');
  const [videoUrl, setVideoUrl] = useState(null);
  const fileRef = useRef();

  const onUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setStatus('Uploading…');
    const body = new FormData();
    body.append('file', file);
    body.append('exercise', exercise);
    try {
      const res = await fetch('http://localhost:9000/vision/analyze', {
        method: 'POST',
        body,
      });
      if (!res.ok) throw new Error('Upload failed');
      const blob = await res.blob();
      setVideoUrl(URL.createObjectURL(blob));
      setStatus('');
    } catch (err) {
      setStatus('Error: ' + err.message);
    }
  };

  return (
    <div className="pb-24">
      <h1 className="text-xl font-bold mb-2">Form Corrector</h1>
      <p className="text-slate-600 mb-4">Upload a short video and get real-time form feedback overlay.</p>

      <label className="block mb-2 text-sm">Exercise</label>
      <select className="w-full rounded-xl border border-slate-200 px-3 py-2 bg-white" value={exercise} onChange={e=>setExercise(e.target.value)}>
        <option value="pushup">Pushup</option>
        <option value="squat">Squat</option>
        <option value="plank">Plank</option>
      </select>

      <div className="mt-4">
        <input ref={fileRef} type="file" accept="video/mp4,video/webm" onChange={onUpload} className="hidden" />
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
