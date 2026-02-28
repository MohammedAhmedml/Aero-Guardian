import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Aero Guardian",
    layout="wide",
)

# ---------------- CUSTOM STYLING ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
.main-title {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(90deg, #00f2fe, #4facfe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.card {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}
.route-box {
    background-color: #161a22;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌍 AERO GUARDIAN</div>', unsafe_allow_html=True)
st.caption("Real-Time Pollution & Smart Route Intelligence")

# ---------------- AUTO REFRESH WITHOUT PAGE RESET ----------------
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

refresh_interval = 5

if time.time() - st.session_state.last_update > refresh_interval:
    st.session_state.last_update = time.time()
    st.rerun()

# ---------------- LOAD DATA ----------------
try:
    df = pd.read_csv("dashboard.csv")
except:
    st.warning("Waiting for pollution data...")
    st.stop()

if df.empty:
    st.warning("No pollution data yet...")
    st.stop()

latest = df.groupby("city").tail(1)

# ---------------- CITY COORDINATES ----------------
city_coords = {
    "Delhi": [28.6139, 77.2090],
    "Mumbai": [19.0760, 72.8777],
    "Kanpur": [26.4499, 80.3319],
}

latest["lat"] = latest["city"].apply(lambda x: city_coords[x][0])
latest["lon"] = latest["city"].apply(lambda x: city_coords[x][1])

# ---------------- COLOR LOGIC ----------------
def get_color(pm25):
    if pm25 > 300:
        return [255, 0, 0]
    elif pm25 > 200:
        return [255, 140, 0]
    elif pm25 > 150:
        return [255, 255, 0]
    elif pm25 > 100:
        return [100, 149, 237]
    else:
        return [0, 200, 0]

latest["color"] = latest["pm25"].apply(get_color)
latest["radius"] = latest["pm25"] * 700

# ---------------- MAP ----------------
st.subheader("🗺 Live AQI Map")

scatter = pdk.Layer(
    "ScatterplotLayer",
    data=latest,
    get_position='[lon, lat]',
    get_fill_color="color",
    get_radius="radius",
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=22,
    longitude=78,
    zoom=4,
    pitch=30,
)

deck = pdk.Deck(
    layers=[scatter],
    initial_view_state=view_state,
)

st.pydeck_chart(deck)

# ---------------- AQI CARDS ----------------
st.markdown("## 📊 Live AQI Status")

cols = st.columns(len(latest))

for i, row in enumerate(latest.itertuples()):
    with cols[i]:
        st.markdown(f"""
        <div class="card">
            <h2>{row.city}</h2>
            <h1>{row.pm25}</h1>
            <p>{row.risk_level}</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- ROUTE INTELLIGENCE ----------------
st.markdown("## 🛣 Smart Route Intelligence")

selected_city = st.selectbox("Choose City", latest["city"].unique())
city_data = latest[latest["city"] == selected_city].iloc[0]
city_aqi = city_data.pm25

routes = [
    {"name": "Main Highway", "factor": 1.2},
    {"name": "Metro Corridor", "factor": 0.9},
    {"name": "Green Belt Road", "factor": 0.6},
]

for route in routes:
    route["exposure"] = round(city_aqi * route["factor"], 1)

best_route = min(routes, key=lambda x: x["exposure"])

for route in routes:
    if route == best_route:
        st.markdown(f"""
        <div class="route-box" style="border:2px solid #00ff9d;">
            <b>🟢 Recommended:</b> {route['name']} <br>
            Exposure Score: {route['exposure']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="route-box">
            {route['name']} <br>
            Exposure Score: {route['exposure']}
        </div>
        """, unsafe_allow_html=True)

# ---------------- BAR GRAPH ----------------
st.markdown("## 📈 City Comparison")

fig = px.bar(
    latest,
    x="city",
    y="pm25",
    color="pm25",
    color_continuous_scale="reds",
    text="pm25"
)

fig.update_layout(
    template="plotly_dark",
    height=400
)

st.plotly_chart(fig, use_container_width=True)