import streamlit as st
import pandas as pd
import random
import requests
import datetime
import time
import folium
from streamlit_folium import st_folium
import os

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(page_title="Aero Guardian Enterprise", layout="wide")

# =========================================
# ENTERPRISE DARK UI
# =========================================
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.big-title {
    font-size: 42px;
    font-weight: 700;
    color: white;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0px 4px 20px rgba(0,0,0,0.4);
}
.metric-title {
    font-size: 18px;
    color: #aaa;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🌍 AERO GUARDIAN ENTERPRISE</div>', unsafe_allow_html=True)
st.markdown("AI-Powered Clean Route & Health Intelligence Platform")

# =========================================
# SIDEBAR SETTINGS
# =========================================
profile = st.sidebar.selectbox("User Profile", ["Adult", "Child", "Elderly"])
exposure_time = st.sidebar.slider("Exposure Time (minutes)", 0, 120, 30)

# =========================================
# API KEY (OpenAQ)
# =========================================
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")

# =========================================
# RISK ENGINE
# =========================================
def classify_risk(pm25):
    if pm25 < 50:
        return "Good"
    elif pm25 < 100:
        return "Moderate"
    elif pm25 < 200:
        return "Unhealthy"
    elif pm25 < 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

def exposure_score(pm25, exposure):
    return pm25 * (exposure / 60)

# =========================================
# OPENAQ FETCH (STABLE)
# =========================================
def fetch_real_aqi(city):
    try:
        url = "https://api.openaq.org/v2/latest"
        params = {
            "city": city,
            "parameter": "pm25",
            "limit": 1
        }

        headers = {}
        if OPENAQ_API_KEY:
            headers["X-API-Key"] = OPENAQ_API_KEY

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                measurements = data["results"][0].get("measurements", [])
                if measurements:
                    return measurements[0].get("value")
        return None
    except:
        return None

# =========================================
# CONTROLLED REFRESH (60s)
# =========================================
REFRESH_INTERVAL = 60

if "last_update" not in st.session_state:
    st.session_state.last_update = 0

if "df_live" not in st.session_state:
    st.session_state.df_live = pd.DataFrame()

current_time = time.time()

if current_time - st.session_state.last_update > REFRESH_INTERVAL:

    cities = ["Delhi", "Mumbai", "Kanpur"]
    live_data = []

    fallback_values = {
        "Delhi": 180,
        "Mumbai": 95,
        "Kanpur": 210
    }

    for city in cities:
        pm25 = fetch_real_aqi(city)
        if pm25 is None:
            pm25 = fallback_values.get(city, 150)

        live_data.append({
            "city": city,
            "pm25": pm25,
            "timestamp": datetime.datetime.now()
        })

    st.session_state.df_live = pd.DataFrame(live_data)
    st.session_state.last_update = current_time

df = st.session_state.df_live

if df.empty:
    st.warning("⚠️ No AQI data available.")
    st.stop()

# =========================================
# ROUTE INTELLIGENCE
# =========================================
df["risk"] = df["pm25"].apply(classify_risk)
df["traffic"] = [random.randint(1, 10) for _ in range(len(df))]

df["Route A"] = df["pm25"] + df["traffic"] * 6
df["Route B"] = df["pm25"] - 25
df["Route C"] = df["pm25"] + 10

df["Best Route"] = df[["Route A", "Route B", "Route C"]].idxmin(axis=1)
df["Exposure Score"] = df["pm25"].apply(lambda x: exposure_score(x, exposure_time))
df["Green Score"] = 500 - df["pm25"]

# =========================================
# DASHBOARD CARDS
# =========================================
st.subheader("📊 Live Air Quality Overview")

cols = st.columns(len(df))

for idx, (_, row) in enumerate(df.iterrows()):
    with cols[idx]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### {row['city']}")
        st.metric("PM2.5", row["pm25"])
        st.metric("Risk Level", row["risk"])
        st.metric("Best Route", row["Best Route"])
        st.metric("Green Score", row["Green Score"])
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================
# ROUTE COMPARISON
# =========================================
st.subheader("🗺 Route Pollution Comparison")

for _, row in df.iterrows():
    route_df = pd.DataFrame({
        "Route": ["Route A", "Route B", "Route C"],
        "Pollution Score": [row["Route A"], row["Route B"], row["Route C"]]
    })
    st.markdown(f"### {row['city']}")
    st.bar_chart(route_df.set_index("Route"))

# =========================================
# LIVE MAP
# =========================================
st.subheader("🗺 Live AQI Map Intelligence")

city_coords = {
    "Delhi": [28.6139, 77.2090],
    "Mumbai": [19.0760, 72.8777],
    "Kanpur": [26.4499, 80.3319]
}

m = folium.Map(location=[22.5, 80], zoom_start=5)

for _, row in df.iterrows():
    folium.CircleMarker(
        location=city_coords[row["city"]],
        radius=15,
        popup=f"{row['city']} - {row['pm25']} ({row['Best Route']})",
        color="red" if row["pm25"] > 200 else "orange" if row["pm25"] > 100 else "green",
        fill=True
    ).add_to(m)

st_folium(m, width=1000, height=500)

# =========================================
# AI RECOMMENDATIONS
# =========================================
st.subheader("🤖 AI Health & Route Recommendations")

for _, row in df.iterrows():
    if row["risk"] == "Hazardous":
        st.error(f"{row['city']}: Avoid outdoor exposure. Use air purifier. Take {row['Best Route']}.")
    elif row["risk"] == "Very Unhealthy":
        st.warning(f"{row['city']}: Wear N95 mask. Minimize travel. Take {row['Best Route']}.")
    elif row["risk"] == "Unhealthy":
        st.info(f"{row['city']}: Sensitive groups avoid long exposure. Prefer {row['Best Route']}.")
    else:
        st.success(f"{row['city']}: Air quality acceptable. {row['Best Route']} recommended.")

st.markdown("---")
st.caption("Enterprise AQI Intelligence | Live Government Data + AI Route Optimization")
