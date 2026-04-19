import numpy as np
import cv2

# ---------------- AUDIO ANALYSIS ----------------
def analyze_audio(audio_file):
    if audio_file is None:
        return 2

    try:
        audio_bytes = audio_file.getvalue()

        if len(audio_bytes) < 1000:
            return 2  # too short

        # Convert bytes → numbers
        data = np.frombuffer(audio_bytes, dtype=np.uint8)

        energy = np.mean(data)
        variation = np.std(data)

        score = 5

        if energy > 100:
            score += 2
        if variation > 20:
            score += 2

        return min(score, 10)

    except:
        return 3


# ---------------- VIDEO ANALYSIS ----------------
def analyze_video(image):
    if image is None:
        return 2

    try:
        file_bytes = np.asarray(bytearray(image.getvalue()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            return 2

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        brightness = np.mean(gray)
        variation = np.std(gray)

        score = 5

        if brightness > 80:
            score += 2
        if variation > 30:
            score += 2

        return min(score, 10)

    except:
        return 3