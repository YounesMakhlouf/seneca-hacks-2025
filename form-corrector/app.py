from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
import shutil

# Reuse existing analyzer module in this folder
from exercise_analyzer import analyze_video as run_analyze_video, EXERCISE_CHECKS
import cv2
import numpy as np
import mediapipe as mp

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
        # Use a more robust analyzer with FPS fallback first
        ok = _analyze_video_safe(in_path, exercise, out_path)
        if not ok:
            # Fallback to original implementation if something went wrong
            run_analyze_video(in_path, exercise=exercise, output_video=out_path)
        # Validate output exists and non-empty
        if not os.path.exists(out_path) or os.path.getsize(out_path) < 1024:
            return JSONResponse({"error": "processing failed: empty output"}, status_code=500)
        return FileResponse(out_path, media_type="video/mp4", filename="processed.mp4")
    finally:
        try:
            os.remove(in_path)
        except OSError:
            pass


def _analyze_frame_bytes(image_bytes: bytes, exercise: str):
    """Run pose on a single image frame and return feedback + landmarks.

    Returns dict: {feedback, angle, point: [x,y], color: [r,g,b], landmarks: [[x,y,visibility]...], width, height}
    """
    if exercise not in EXERCISE_CHECKS:
        return {"error": f"exercise must be one of {list(EXERCISE_CHECKS.keys())}"}

    npbuf = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npbuf, cv2.IMREAD_COLOR)
    if img is None:
        return {"error": "invalid image"}
    h, w = img.shape[:2]

    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        res = pose.process(rgb)
        if not res.pose_landmarks:
            return {"feedback": "No person detected", "landmarks": [], "width": w, "height": h}
        lms = res.pose_landmarks.landmark
        check_func = EXERCISE_CHECKS[exercise]
        try:
            feedback, point, angle, color = check_func(lms)
        except Exception:
            feedback, point, angle, color = ("", (0, 0), 0.0, (0, 255, 0))
        # normalize output
        lm_list = [[float(p.x), float(p.y), float(getattr(p, 'visibility', 0.0))] for p in lms]
        return {
            "feedback": feedback,
            "angle": float(angle),
            "point": [float(point[0]), float(point[1])],
            "color": [int(color[2]), int(color[1]), int(color[0])],  # convert BGR to RGB order
            "landmarks": lm_list,
            "width": int(w),
            "height": int(h),
        }


@app.post("/vision/stream-frame")
async def stream_frame(file: UploadFile = File(...), exercise: str = Form("pushup")):
    data = await file.read()
    result = _analyze_frame_bytes(data, exercise)
    if "error" in result:
        return JSONResponse(result, status_code=400)
    return result


def _analyze_video_safe(input_video: str, exercise: str, output_video: str) -> bool:
    if exercise not in EXERCISE_CHECKS:
        return False
    check_func = EXERCISE_CHECKS[exercise]

    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        return False
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 360)
    fps = cap.get(cv2.CAP_PROP_FPS)
    try:
        fps = float(fps)
        if fps <= 1 or fps != fps:  # <=1 or NaN
            fps = 24.0
    except Exception:
        fps = 24.0

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    wrote_any = False

    mp_pose = mp.solutions.pose
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.pose_landmarks:
                lms = results.pose_landmarks.landmark
                try:
                    feedback, point, angle, color = check_func(lms)
                    px, py = tuple(np.multiply(point, [width, height]).astype(int))
                    cv2.rectangle(image, (30, 20), (min(width - 30, 560), 70), (0, 0, 0), -1)
                    cv2.putText(image, feedback, (40, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    cv2.rectangle(image, (px - 30, py - 30), (px + 30, py + 30), (0, 0, 0), -1)
                    cv2.putText(image, str(int(angle)), (px - 20, py + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                except Exception:
                    pass
                mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            out.write(image)
            wrote_any = True

    cap.release()
    out.release()
    return wrote_any and os.path.exists(output_video)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=9000, reload=True)
