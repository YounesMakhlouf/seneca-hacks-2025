import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# ----------------------------
# Utility function
# ----------------------------
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# ----------------------------
# Exercise check functions
# ----------------------------
def check_squat(landmarks):
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
           landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
             landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

    angle = calculate_angle(hip, knee, ankle)
    feedback = "Good squat ✅" if angle < 90 else "Go lower ⬇️"
    color = (0, 255, 0) if angle < 90 else (0, 0, 255)
    return feedback, knee, angle, color

def check_pushup(landmarks):
    """
    Friendly pushup check:
    - Elbow angle (flexion)
    - Shoulder-hip alignment
    - Hands roughly under shoulders
    """

    # Left side points
    shoulder = np.array([landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y])
    elbow = np.array([landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y])
    wrist = np.array([landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y])
    hip = np.array([landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y])
    knee = np.array([landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y])
    
    # Angles
    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    shoulder_hip_angle = calculate_angle(shoulder, hip, knee)

    # Hand position check (approx under shoulder)
    hand_shoulder_diff = np.abs(wrist[0] - shoulder[0])

    # Feedback list (friendly)
    feedback_list = []

    if elbow_angle < 90:
        feedback_list.append("Try bending elbows a bit more ")
    elif elbow_angle > 160:
        feedback_list.append("Good depth! ")
    else:
        feedback_list.append("Elbow depth is nice ")

    if not (160 <= shoulder_hip_angle <= 180):
        feedback_list.append("Keep your back a bit straighter ")
    else:
        feedback_list.append("Back alignment looks good ")

    if hand_shoulder_diff > 0.1:
        feedback_list.append("Hands slightly adjust under shoulders ")
    else:
        feedback_list.append("Hand placement is good ")

    # Combine feedback
    feedback = " | ".join(feedback_list)

    # Color: green if mostly good, orange if minor adjustments
    color = (0, 255, 0) if all("✅" in f or "👍" in f for f in feedback_list) else (0, 165, 255)  

    # Return elbow as anchor point for angle display
    px, py = elbow
    return feedback, (px, py), elbow_angle, color

def check_plank(landmarks):
    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
           landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
            landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

    angle = calculate_angle(shoulder, hip, knee)
    feedback = "Good plank ✅" if 160 <= angle <= 180 else "Adjust your hips ⬇️"
    color = (0, 255, 0) if 160 <= angle <= 180 else (0, 0, 255)
    return feedback, hip, angle, color

# Map exercises to functions
EXERCISE_CHECKS = {
    "squat": check_squat,
    "pushup": check_pushup,
    "plank": check_plank
}

# ----------------------------
# Video analysis function
# ----------------------------
def analyze_video(input_video, exercise="squat", output_video="output.mp4"):
    if exercise not in EXERCISE_CHECKS:
        raise ValueError(f"Exercise '{exercise}' not supported. Choose from {list(EXERCISE_CHECKS.keys())}")

    check_func = EXERCISE_CHECKS[exercise]

    cap = cv2.VideoCapture(input_video)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    with mp_pose.Pose(min_detection_confidence=0.5,
                      min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark
                feedback, point, angle, color = check_func(landmarks)
                px, py = tuple(np.multiply(point, [width, height]).astype(int))

                # Draw feedback
                cv2.rectangle(image, (30,20), (550,70), (0,0,0), -1)
                cv2.putText(image, feedback, (40,55), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                # Draw angle
                cv2.rectangle(image, (px-30, py-30), (px+30, py+30), (0,0,0), -1)
                cv2.putText(image, str(int(angle)), (px-20, py+10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

            except:
                pass

            # Draw skeleton
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            out.write(image)

    cap.release()
    out.release()
    print(f"Processing complete! Video saved as {output_video}")

# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    # analyze_video("video.mp4", exercise="squat", output_video="output_squat.mp4")
    analyze_video("video.mp4", exercise="pushup", output_video="output_pushup.mp4")
    # analyze_video("video.mp4", exercise="plank", output_video="output_plank.mp4")
