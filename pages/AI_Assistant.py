import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(page_title="AI Assistant", layout="wide")

st.title("🤖 Aero Guardian AI Health Assistant")

# =============================
# USER SETTINGS
# =============================
profile = st.sidebar.selectbox("User Profile", ["Adult", "Child", "Elderly"])
exposure_time = st.sidebar.slider("Exposure Time (minutes)", 0, 120, 30)

# =============================
# LOAD DATA
# =============================
try:
    df = pd.read_csv("pollution.csv")
except:
    df = pd.DataFrame()

avg_pm = df["pm25"].mean() if not df.empty else 150

# =============================
# OPENROUTER SETUP
# =============================
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# =============================
# STRUCTURED RECOMMENDATION
# =============================
def structured_recommendation(pm25, profile, exposure):

    cigarette_equivalent = round(pm25 / 22, 1)

    recommendation = f"""
---

## 📊 Air Quality Assessment

**PM2.5 Level:** {round(pm25,2)}

**Cigarette Equivalent:** ≈ {cigarette_equivalent} cigarettes/day

---

## 🏥 Health Risk Analysis
"""

    if pm25 < 100:
        recommendation += "Air quality is acceptable with minor sensitivity risk.\n"
    elif pm25 < 200:
        recommendation += "Unhealthy for sensitive groups.\n"
    elif pm25 < 300:
        recommendation += "Very unhealthy. Reduce outdoor exposure.\n"
    else:
        recommendation += "Hazardous. Avoid outdoor activity.\n"

    recommendation += f"""

---

## 😷 Mask Recommendation
Use N95 or KN95 mask.

## 🏠 Ventilation Advice
Keep windows closed during peak pollution hours.

## 🚶 Outdoor Advice
Limit outdoor activity to {max(10, 60-exposure)} minutes.

## 🛣 Route Intelligence
Prefer low traffic routes and green corridors.

---
"""

    return recommendation

# =============================
# AI CALL
# =============================
def ask_ai(question):

    if not OPENROUTER_KEY:
        return "OpenRouter API key not found."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "HTTP-Referer": "http://localhost:8501",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an environmental health expert."},
            {"role": "user", "content": question}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except:
        return "AI Error occurred."

# =============================
# CHAT SESSION
# =============================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about air quality, health, routes...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    ai_reply = ask_ai(user_input)

    full_response = ai_reply + structured_recommendation(avg_pm, profile, exposure_time)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    with st.chat_message("assistant"):
        st.markdown(full_response)
