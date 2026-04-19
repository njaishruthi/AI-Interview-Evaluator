import streamlit as st
import pandas as pd
import os
from datetime import datetime, date, timedelta

from src.text_model import evaluate_text
from src.evaluator import final_score

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2ff, #e0f2fe);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e3a8a);
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Card */
.card {
    background: rgba(255,255,255,0.85);
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

/* Score */
.score {
    font-size: 50px;
    font-weight: bold;
    color: #1e3a8a;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "📝 Practice"

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "scores" not in st.session_state:
    st.session_state.scores = []

if "total_questions" not in st.session_state:
    st.session_state.total_questions = 1

if "interview_type" not in st.session_state:
    st.session_state.interview_type = "HR"

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 👤 Alex Johnson")

if st.sidebar.button("📝 Practice"):
    st.session_state.page = "📝 Practice"

if st.sidebar.button("📊 Progress"):
    st.session_state.page = "📊 Progress"

if st.sidebar.button("🔥 Streak"):
    st.session_state.page = "🔥 Streak"

if st.sidebar.button("💬 Feedback"):
    st.session_state.page = "💬 Feedback"

st.sidebar.markdown(f"### 📍 {st.session_state.page}")

# ---------------- LOAD DATA ----------------
file_path = "data/text/interview_questions.csv"

if not os.path.exists(file_path):
    st.error("Dataset not found ❌")
    st.stop()

df = pd.read_csv(file_path, encoding="latin1")

# ---------------- STREAK ----------------
def get_streak():
    file = "data/results.csv"
    if not os.path.exists(file):
        return 0

    df = pd.read_csv(file)
    df["date"] = pd.to_datetime(df["datetime"]).dt.date
    days = sorted(set(df["date"]))

    streak = 0
    today = date.today()
    current = today if today in days else days[-1]

    while current in days:
        streak += 1
        current = current - timedelta(days=1)

    return streak

# ================= PRACTICE =================
if st.session_state.page == "📝 Practice":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.title("Practice Setup")
    st.write("### Hi Alex 👋")

    role = st.selectbox("Choose Role", ["Student", "Professional"])

    interview_type = st.selectbox("Interview Type", ["HR", "Technical"])

    company = st.selectbox("Target Company", ["Google", "Amazon", "Microsoft"])
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Advanced"])
    num_q = st.slider("Number of Questions", 1, 10, 3)

    if st.button("🚀 Start Interview"):
        st.session_state.page = "Interview"
        st.session_state.q_index = 0
        st.session_state.total_questions = num_q
        st.session_state.scores = []
        st.session_state.interview_type = interview_type
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ================= INTERVIEW =================
elif st.session_state.page == "Interview":

    st.title("Interview Session")

    # SAFE FILTERING
    if "Type" not in df.columns:
        st.warning("⚠ No 'Type' column found → showing all questions")
        filtered_df = df.copy()
    else:
        filtered_df = df[df["Type"] == st.session_state.interview_type].reset_index(drop=True)

    if len(filtered_df) == 0:
        st.error("No questions available ❌")
        st.stop()

    idx = st.session_state.q_index % len(filtered_df)
    total = st.session_state.total_questions

    question = filtered_df.iloc[idx]["Question"]
    expected = filtered_df.iloc[idx]["Answer"]

    col1, col2 = st.columns([2,1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🎥 Camera")
        img = st.camera_input("Turn on your camera")

        st.write(f"### Question ({idx+1}/{total})")
        st.write(question)

        user_answer = st.text_area("Your Answer")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🎤 Microphone")
        audio = st.audio_input("Record answer")
        st.progress(80)
        st.markdown('</div>', unsafe_allow_html=True)

    # SUBMIT
    if st.button("✅ Submit Answer"):

        if not user_answer or len(user_answer.split()) < 3:
            st.error("Answer too short ❌")
        else:
            text_score = evaluate_text(user_answer, expected)
            audio_score = 7 if audio else 3
            video_score = 7 if img else 3

            final = final_score(text_score, audio_score, video_score)
            st.session_state.scores.append(final)

            # SAVE
            result = {
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "score": final
            }

            file = "data/results.csv"

            if os.path.exists(file):
                df_r = pd.read_csv(file)
                df_r = pd.concat([df_r, pd.DataFrame([result])], ignore_index=True)
            else:
                df_r = pd.DataFrame([result])

            df_r.to_csv(file, index=False)

            st.success(f"Score: {final:.1f}/10")

    # NAVIGATION
    colA, colB, colC = st.columns(3)

    if colA.button("⬅ Previous") and idx > 0:
        st.session_state.q_index -= 1
        st.rerun()

    if colB.button("Next ➡"):
        st.session_state.q_index += 1
        st.rerun()

    if colC.button("❌ Finish Exam"):
        st.session_state.page = "💬 Feedback"
        st.rerun()

# ================= FEEDBACK =================
elif st.session_state.page == "💬 Feedback":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.title("Performance Feedback")

    if st.session_state.scores:
        avg = sum(st.session_state.scores) / len(st.session_state.scores)
        st.markdown(f'<p class="score">{avg:.1f}/10</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Trends")
            st.line_chart(st.session_state.scores)

        with col2:
            st.subheader("✅ Strengths")
            st.success("Good structure\nClear explanation")

            st.subheader("⚠ Weaknesses")
            st.error("Improve confidence\nReduce hesitation")

    st.markdown('</div>', unsafe_allow_html=True)

# ================= STREAK =================
elif st.session_state.page == "🔥 Streak":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.title("🔥 Streak")

    streak = get_streak()
    st.metric("Current Streak", f"{streak} days")

    st.markdown('</div>', unsafe_allow_html=True)

# ================= PROGRESS =================
elif st.session_state.page == "📊 Progress":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.title("📊 Progress")

    file = "data/results.csv"

    if os.path.exists(file):
        df_r = pd.read_csv(file)
        df_r["datetime"] = pd.to_datetime(df_r["datetime"])
        df_r = df_r.sort_values("datetime")
        df_r.set_index("datetime", inplace=True)

        st.line_chart(df_r["score"])
    else:
        st.warning("No data yet.")

    st.markdown('</div>', unsafe_allow_html=True)