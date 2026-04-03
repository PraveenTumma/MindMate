import streamlit as st
import random
import pandas as pd
import plotly.express as px
import datetime
import os
import time
import json
#import google.generativeai as genai
from groq import Groq

# ---------- CONFIG ----------
st.set_page_config(page_title="MindMate", page_icon="🧘", layout="wide", initial_sidebar_state="expanded")

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Tip of the Day Feature
tips = [
    "Take 5 deep breaths before opening your email today.",
    "A 10-minute walk outside can significantly reduce cortisol levels.",
    "Write down one thing you're proud of doing today.",
    "Drink a glass of water right now to rehydrate your brain.",
    "Stretch your arms and do a quick shoulder roll."
]

st.markdown(f"""
<div class='tip-of-the-day'>
    <div class='tip-title'>💡 Tip of the Day</div>
    <p class='tip-content'>{random.choice(tips)}</p>
</div>
""", unsafe_allow_html=True)

st.title("🧘 MindMate: Your AI Mental Wellness Companion")
st.markdown("""
<div class='intro-banner'>
    <h3 style='margin: 0;'>Private, compassionate support – powered by AI and science.</h3>
</div>
""", unsafe_allow_html=True)


# Google Gemnin API key (from secrets)
# Load API key from secrets
try:
    api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("No API key found")
    client = Groq(api_key=api_key)
    use_ai = True
#try:
#    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
#    model = genai.GenerativeModel('gemini-1.5-pro')
#    use_ai = True
except Exception as e:
    use_ai = False
    st.warning("Groq API key not found. Using fallback responses. Please add your Groq API key to `.streamlit/secrets.toml` or set it as an environment variable (`GROQ_API_KEY`).")

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
    st.header("🌬️ Breathing Exercise")
    if st.button("Start 4‑7‑8 Breathing"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Inhale
        status_text.text("Inhale 4s... 👃")
        for i in range(40):
            time.sleep(0.1)
            progress_bar.progress((i + 1) / 40)
        
        # Hold
        status_text.text("Hold 7s... 🧘")
        progress_bar.progress(0)
        for i in range(70):
            time.sleep(0.1)
            progress_bar.progress((i + 1) / 70)
            
        # Exhale
        status_text.text("Exhale 8s... 🌬️")
        progress_bar.progress(0)
        for i in range(80):
            time.sleep(0.1)
            progress_bar.progress((i + 1) / 80)
            
        status_text.text("Done! Feel the calm. ✨")
        st.success("You did great!")

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
                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",  # Changed from decommissioned llama3-8b-8192
                        messages=[
                            {"role": "system", "content": "You are a supportive mental wellness coach. Be warm and concise."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=300
                    )
                    reflection = response.choices[0].message.content
                except Exception as e:
                    st.error(f"AI error: {e}")
                    reflection = "Thank you for sharing. Taking a moment to breathe can help. Try a short walk outside."
            else:
                reflection = "Thank you for sharing. Taking a moment to breathe can help. Try a short walk outside."
            st.session_state.journal_entries.append((today, journal, reflection))
            st.success("✨ Reflection generated ✨")
            st.write(reflection)

# ---------- CHAT WITH MINDMATE (optional) ----------
with st.expander("💬 Chat with MindMate (AI coach)"):
    st.markdown("<div style='max-height: 400px; overflow-y: auto;'>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg.startswith("You:"):
            st.markdown(f"""
            <div class='chat-message user-message'>
                <strong>You:</strong><br>{msg[4:]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-message bot-message'>
                <strong>MindMate:</strong><br>{msg[10:]}
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    user_input = st.text_input("Ask me anything (or just talk):", key="chat_input")
    if st.button("Send Message"):
        if user_input:
            st.session_state.chat_history.append(f"You: {user_input}")
            if use_ai:
                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a supportive mental wellness coach. Keep responses warm, short and helpful."},
                            {"role": "user", "content": user_input}
                        ],
                        temperature=0.7,
                        max_tokens=200
                    )
                    reply = response.choices[0].message.content
                except Exception as e:
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
