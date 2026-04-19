def evaluate_audio(speech_rate, energy, pauses):
    score = 0

    if 120 <= speech_rate <= 160:
        score += 4
    if energy > 0.5:
        score += 3
    if pauses < 5:
        score += 3

    return min(score, 10)


def evaluate_video(emotion, eye_contact, stability):
    score = 0

    if emotion == "confident":
        score += 4
    if eye_contact == "good":
        score += 3
    if stability == "stable":
        score += 3

    return min(score, 10)


def final_score(text, audio, video):
    return round((0.5 * text) + (0.3 * audio) + (0.2 * video), 2)


def performance_level(score):
    if score >= 8:
        return "Excellent"
    elif score >= 6:
        return "Good"
    elif score >= 4:
        return "Average"
    else:
        return "Weak"