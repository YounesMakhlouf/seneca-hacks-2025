from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
import shutil

# Reuse existing analyzer module in this folder
from exercise_analyzer import analyze_video as run_analyze_video, EXERCISE_CHECKS

app = FastAPI(title="Form Corrector Service", version="0.1.0")

# Dev CORS for local React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/exercises")
def exercises():
    return {"supported": list(EXERCISE_CHECKS.keys())}


@app.post("/vision/analyze")
def analyze(file: UploadFile = File(...), exercise: str = Form("pushup")):
    if exercise not in EXERCISE_CHECKS:
        return JSONResponse({"error": f"exercise must be one of {list(EXERCISE_CHECKS.keys())}"}, status_code=400)

    tmp_dir = os.path.abspath("temp")
    os.makedirs(tmp_dir, exist_ok=True)
    in_path = os.path.join(tmp_dir, f"in_{uuid.uuid4().hex}.mp4")
    out_path = os.path.join(tmp_dir, f"out_{uuid.uuid4().hex}.mp4")
    with open(in_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        run_analyze_video(in_path, exercise=exercise, output_video=out_path)
        return FileResponse(out_path, media_type="video/mp4", filename="processed.mp4")
    finally:
        try:
            os.remove(in_path)
        except OSError:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=9000, reload=True)
