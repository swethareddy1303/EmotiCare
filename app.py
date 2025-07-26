# app.py

import streamlit as st
import json
import random
from gtts import gTTS
from playsound import playsound
import tempfile
import os
from rag_support import load_rag_chain  # ← from the fixed file

# ------------------------ LOADERS ------------------------

def load_quotes():
    with open("data/quotes.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def load_tips_for_mood(mood):
    with open("data/relaxation_tips.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(mood, [])[:4]

def speak(text):
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        temp_path = fp.name
        tts.save(temp_path)
    playsound(temp_path)
    os.remove(temp_path)

# ------------------------ UI START ------------------------

st.set_page_config(page_title="EmotiCare 💖", layout="centered")
st.title("😊 EmotiCare - Your Mood Companion")

# 👇 Speak welcome message once per session
if "welcomed" not in st.session_state:
    speak("Welcome to EmotiCare! How are you feeling today?")
    st.session_state.welcomed = True

# ------------------------ Mood Selection ------------------------

selected_mood = st.selectbox(
    "How are you feeling today?",
    ["", "Sad", "Anxious", "Lonely", "Angry", "Motivated", "Happy", "Excited", "Tired", "Bored", "Overwhelmed"]
)

# ------------------------ Quote of the Day ------------------------

st.subheader("🌟 Quote of the Day")
st.success(random.choice(load_quotes()))

# ------------------------ Relaxation Tips ------------------------

if selected_mood:
    st.subheader("🧘 Relaxation Tips for You")
    mood_tips = load_tips_for_mood(selected_mood)
    for tip in mood_tips:
        st.markdown(f"✅ {tip}")

# ------------------------ Mental Health Q&A ------------------------

st.divider()
st.subheader("🧠 Ask Anything About Mental Health")

suggested_questions = {
    "Sad": ["How to cope with sadness?", "Why do I feel low even after resting?", "How can I cheer up alone?", "Is crying okay?", "Can journaling help sadness?"],
    "Anxious": ["How can I reduce anxiety?", "What are grounding techniques?", "Can breathing help anxiety?", "How to stop overthinking?", "Why does my heart race?"],
    "Lonely": ["What should I do when I feel lonely?", "How to stay socially connected?", "Can self-talk help loneliness?", "How to enjoy being alone?", "Why do I feel invisible?"],
    "Angry": ["How to calm down when I’m angry?", "What helps with emotional control?", "Can movement release anger?", "Is it okay to feel angry?", "Why do I snap suddenly?"],
    "Motivated": ["How can I keep up the motivation?", "What are some productive habits?", "How to avoid burnout?", "Why do I lose focus?", "Can rewards boost motivation?"],
    "Happy": ["How to maintain positive energy?", "How can I help others feel happy too?", "Why is gratitude important?", "Can joy be shared?", "How to celebrate small wins?"],
    "Excited": ["How to channel excitement?", "What to do with sudden bursts of joy?", "Can excitement cause anxiety?", "How to stay grounded while excited?", "Should I share my excitement?"],
    "Tired": ["How to feel refreshed quickly?", "Does stretching help tiredness?", "What are healthy breaks?", "Should I nap or move?", "Why am I always tired?"],
    "Bored": ["What to do when bored?", "Can boredom lead to creativity?", "How to reset my mind?", "Is it okay to feel bored?", "What are fun 5-min activities?"],
    "Overwhelmed": ["How to manage overwhelm?", "Can deep breathing help stress?", "How to break down tasks?", "Should I ask for help?", "How to slow down my mind?"]
}

# ------------------------ Session States ------------------------

if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "step" not in st.session_state:
    st.session_state.step = 1
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

qa_chain = load_rag_chain()

def process_question(question):
    response = qa_chain.run(question)
    return response.strip().split("\n")[0][:300]

# ------------------------ First Step: Suggested Qs or Custom ------------------------

if st.session_state.step == 1:
    if selected_mood and selected_mood in suggested_questions:
        st.write("💡 Suggested Questions:")
        for q in suggested_questions[selected_mood]:
            if st.button(f"Ask: {q}", key=q):
                answer = process_question(q)
                st.session_state.conversation.append((q, answer))
                st.session_state.step = 2
                st.rerun()

    manual_q = st.text_input("Or type your own question:")
    if manual_q:
        answer = process_question(manual_q)
        st.session_state.conversation.append((manual_q, answer))
        st.session_state.step = 2
        st.rerun()

# ------------------------ Step 2: Display conversation + follow-up ------------------------

if st.session_state.step == 2:
    for i, (q, a) in enumerate(st.session_state.conversation):
        st.markdown(f"**❓ You:** {q}")
        st.info(f"**🧠 EmotiCare:** {a}")

    another = st.radio("Do you have another question?", ["No", "Yes"], key="continue", horizontal=True)

    if another == "Yes":
        follow_up = st.text_input("What's your next question?", key="next_q")
        if follow_up:
            answer = process_question(follow_up)
            st.session_state.conversation.append((follow_up, answer))
            st.rerun()

    elif another == "No":
        st.success("🌸 Keep smiling! You will have a great day!")
        if st.button("🔊 Say it out loud"):
            speak("Keep smiling! You will have a great day!")
