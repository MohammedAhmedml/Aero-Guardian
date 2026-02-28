import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Health Assistant")

st.title("🤖 Aero Guardian – AI Health Assistant")

# -------- Load Latest Pollution Data --------
def load_data():
    try:
        df = pd.read_csv("dashboard.csv")
        latest = df.groupby("city").tail(1)
        return latest
    except:
        return None


# -------- AI Health Logic --------
def generate_response(pm25):
    if pm25 > 300:
        level = "🚨 Hazardous"
        mask = "Use N95 or KN95 mask."
        ventilation = "Keep windows closed."
        outdoor = "Avoid outdoor activity."
        route = "Avoid high-traffic routes."
    elif pm25 > 200:
        level = "⚠️ Very Unhealthy"
        mask = "Use N95 mask outdoors."
        ventilation = "Limit natural ventilation."
        outdoor = "Limit outdoor exposure."
        route = "Prefer low-traffic routes."
    elif pm25 > 150:
        level = "😷 Unhealthy"
        mask = "Consider wearing a mask."
        ventilation = "Avoid peak pollution hours."
        outdoor = "Reduce prolonged exposure."
        route = "Choose greener routes."
    elif pm25 > 100:
        level = "🌫 Moderate"
        mask = "Sensitive groups should wear mask."
        ventilation = "Ventilation acceptable."
        outdoor = "Short outdoor activity allowed."
        route = "Normal routes acceptable."
    else:
        level = "✅ Good"
        mask = "Mask not required."
        ventilation = "Safe ventilation."
        outdoor = "Outdoor activity safe."
        route = "All routes safe."

    return level, mask, ventilation, outdoor, route


data = load_data()

if data is None or data.empty:
    st.warning("Waiting for live pollution data...")
else:
    st.subheader("📊 Current Air Quality Snapshot")
    st.dataframe(data[["city", "pm25", "risk_level"]])

    st.markdown("---")

    st.subheader("💬 Ask a Question")

    user_question = st.text_input("Example: Is it safe in Delhi?")

    if user_question:

        question = user_question.lower()

        if "delhi" in question:
            city = "Delhi"
        elif "mumbai" in question:
            city = "Mumbai"
        elif "kanpur" in question:
            city = "Kanpur"
        else:
            city = data.iloc[0]["city"]

        city_data = data[data["city"] == city]

        if not city_data.empty:
            pm25 = city_data.iloc[0]["pm25"]

            level, mask, ventilation, outdoor, route = generate_response(pm25)

            st.markdown("## 📍 AI Response")

            st.write(f"**City:** {city}")
            st.write(f"**PM2.5 Level:** {pm25}")
            st.write(f"**Air Quality Status:** {level}")

            st.markdown("### 😷 Mask Recommendation")
            st.write(mask)

            st.markdown("### 🏠 Ventilation Advice")
            st.write(ventilation)

            st.markdown("### 🚶 Outdoor Advice")
            st.write(outdoor)

            st.markdown("### 🛣 Route Intelligence")
            st.write(route)

        else:
            st.error("City data not found.")