# Form Corrector Service (FastAPI)

A standalone FastAPI microservice that analyzes workout form (pushup/squat/plank) using MediaPipe Pose and OpenCV. It exposes a simple upload endpoint returning a processed MP4 overlaying feedback.

## Endpoints
- GET /health → { ok: true }
- GET /exercises → list of supported exercise ids
- POST /vision/analyze (multipart/form-data)
  - file: video/mp4
  - exercise: pushup | squat | plank
  - returns: video/mp4 with overlays

## Run locally (Windows PowerShell)

```powershell
# From repo root or this folder
cd .\form-corrector

# Create and activate venv (optional)
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# Install deps
pip install -r requirements.txt fastapi uvicorn

# Start server on port 9000
uvicorn app:app --host 0.0.0.0 --port 9000 --reload
```

Once running, the frontend can POST to http://localhost:9000/vision/analyze.

> Note: OpenCV/MediaPipe are CPU-only. For large videos, first seconds of processing can take a moment.

## Reuse of Analyzer
The logic comes from `exercise_analyzer.py` in this folder. We import and reuse it without changes.
