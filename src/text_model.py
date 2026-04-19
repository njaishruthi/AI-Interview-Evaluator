def evaluate_text(user_answer, expected_answer):
    score = 0

    if user_answer.lower() in expected_answer.lower():
        score += 4

    if len(user_answer.split()) > 5:
        score += 3

    keywords = ["because", "example", "use", "defined", "means"]
    if any(word in user_answer.lower() for word in keywords):
        score += 3

    return min(score, 10)