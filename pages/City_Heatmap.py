import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🌍 City Pollution Overview")

try:
    df = pd.read_csv("pollution.csv")
except:
    df = pd.DataFrame()

if not df.empty:
    latest = df.groupby("city").tail(1)
    fig = px.bar(latest, x="city", y="pm25", color="pm25")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data yet.")
