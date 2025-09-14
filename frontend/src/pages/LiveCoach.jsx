import { useEffect, useRef, useState } from 'react';
import { Pose } from '@mediapipe/pose';
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';
import { Camera } from '@mediapipe/camera_utils';

export default function LiveCoach() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [status, setStatus] = useState('');

  useEffect(() => {
    let cam = null;
    const videoEl = videoRef.current;
    const canvasEl = canvasRef.current;
    const ctx = canvasEl.getContext('2d');

    const pose = new Pose({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`});
    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      enableSegmentation: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
    });

    pose.onResults((results) => {
      // Resize canvas to video
      canvasEl.width = videoEl.videoWidth;
      canvasEl.height = videoEl.videoHeight;
      ctx.save();
      ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
      // Draw the image first
      ctx.drawImage(results.image, 0, 0, canvasEl.width, canvasEl.height);
      // Draw landmarks
      if (results.poseLandmarks) {
        drawConnectors(ctx, results.poseLandmarks, Pose.POSE_CONNECTIONS, {color: '#22e3a7', lineWidth: 4});
        drawLandmarks(ctx, results.poseLandmarks, {color: '#0f172a', lineWidth: 1, radius: 2});
        setStatus('Tracking…');
      } else {
        setStatus('No person detected');
      }
      ctx.restore();
    });

    (async () => {
      try {
        setStatus('Requesting camera…');
        cam = new Camera(videoEl, {
          onFrame: async () => {
            await pose.send({image: videoEl});
          },
          width: 640,
          height: 480,
        });
        await cam.start();
        setStatus('Camera started');
      } catch (e) {
        setStatus('Camera error: ' + (e?.message || e));
      }
    })();

    return () => {
      try { cam?.stop(); } catch {}
    };
  }, []);

  return (
    <div className="pb-24">
      <h1 className="text-xl font-bold mb-2">Live Coach</h1>
      <p className="text-slate-600 mb-4">Real-time pose landmarks from your webcam. Grant camera access when prompted.</p>
      <div className="relative w-full rounded-xl overflow-hidden bg-black">
        <video ref={videoRef} className="w-full" playsInline style={{display:'none'}} />
        <canvas ref={canvasRef} className="w-full" />
      </div>
      <div className="mt-3 text-sm text-slate-600">{status}</div>
      <p className="mt-2 text-xs text-slate-500">Tip: Stand back so your full body is visible and ensure good lighting.</p>
    </div>
  );
}
