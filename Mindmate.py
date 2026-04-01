import streamlit as st
import openai
import pandas as pd
import plotly.express as px
import datetime
import time
import json

# ---------- CONFIG ----------
st.set_page_config(page_title="MindMate", layout="wide", initial_sidebar_state="expanded")
st.title("🧘 MindMate: Your AI Mental Wellness Companion")
st.caption("Private, compassionate support – powered by AI and science.")

# OpenAI API key (from secrets)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    use_ai = True
except:
    use_ai = False
    st.warning("OpenAI API key not found. Using fallback responses.")

# ---------- INITIALISE SESSION STATE ----------
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []          # list of (date, mood)
if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = []   # list of (date, entry, reflection)
if "gratitude_log" not in st.session_state:
    st.session_state.gratitude_log = []     # list of (date, gratitude)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- SIDEBAR: Daily Check‑In ----------
with st.sidebar:
    st.header("📝 Today's Check‑In")
    today = datetime.date.today().isoformat()
    mood = st.slider("How are you feeling today?", 1, 10, 7, help="1 = awful, 10 = amazing")
    if st.button("Save Mood"):
        st.session_state.mood_log.append((today, mood))
        st.success("Mood saved! 🧠")

    st.divider()
    st.header("🙏 Gratitude Log")
    gratitude = st.text_area("What are you grateful for today? (optional)")
    if st.button("Save Gratitude"):
        if gratitude:
            st.session_state.gratitude_log.append((today, gratitude))
            st.success("Thanks for sharing. Gratitude rewires the brain for positivity.")
        else:
            st.warning("Write something – even a small thing counts.")

    st.divider()
    st.header("🫁 Breathing Exercise")
    if st.button("Start 4‑7‑8 Breathing"):
        with st.spinner("Inhale 4... Hold 7... Exhale 8..."):
            time.sleep(4)
            st.success("Done! Feel the calm.")

# ---------- MAIN: JOURNAL & AI REFLECTION ----------
st.header("📖 Private Journal")
st.write("Write freely about anything on your mind. MindMate will reflect and offer support.")
journal = st.text_area("Your entry:", height=200, placeholder="I've been feeling...")
if st.button("Get Reflection"):
    if not journal.strip():
        st.error("Please write something.")
    else:
        with st.spinner("MindMate is listening..."):
            if use_ai:
                prompt = f"""
                You are a compassionate mental wellness coach. 
                The user wrote: "{journal}"
                Provide a supportive reflection, and then suggest one actionable coping strategy 
                (e.g., CBT technique, mindfulness, physical activity) that fits their mood.
                Keep it warm and concise.
                """
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                reflection = response.choices[0].message.content
            else:
                reflection = "Thank you for sharing. Taking a moment to breathe can help. Try a short walk outside."

            st.session_state.journal_entries.append((today, journal, reflection))
            st.success("✨ Reflection generated ✨")
            st.write(reflection)

# ---------- CHAT WITH MINDMATE (optional) ----------
with st.expander("💬 Chat with MindMate (AI coach)"):
    for msg in st.session_state.chat_history:
        st.write(msg)
    user_input = st.text_input("Ask me anything (or just talk):")
    if user_input:
        st.session_state.chat_history.append(f"You: {user_input}")
        if use_ai:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a supportive mental wellness coach. Keep responses warm and short."},
                        {"role": "user", "content": user_input}
                    ]
                )
                reply = response.choices[0].message.content
            except:
                reply = "I'm here for you. Sometimes just talking helps."
        else:
            reply = "I'm here for you. Let's take a deep breath together."
        st.session_state.chat_history.append(f"MindMate: {reply}")
        st.rerun()

# ---------- DASHBOARD: TRENDS ----------
st.divider()
st.header("📊 Your Wellness Trends")

# Mood trend
if st.session_state.mood_log:
    df_mood = pd.DataFrame(st.session_state.mood_log, columns=["Date", "Mood"])
    df_mood["Date"] = pd.to_datetime(df_mood["Date"])
    fig_mood = px.line(df_mood, x="Date", y="Mood", title="Mood Over Time", markers=True)
    st.plotly_chart(fig_mood, use_container_width=True)
else:
    st.info("No mood data yet. Use the sidebar to log your mood.")

# Gratitude word cloud or simple list
if st.session_state.gratitude_log:
    st.subheader("Recent Gratitude Moments")
    for date, entry in st.session_state.gratitude_log[-5:]:
        st.write(f"**{date}:** {entry}")

# ---------- FOOTER ----------
st.divider()
st.caption("MindMate is not a replacement for professional help. If you're in crisis, please contact a mental health professional.")