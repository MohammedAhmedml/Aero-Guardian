import streamlit as st
import pandas as pd
import random

st.title("🗺 Clean Route Intelligence")

try:
    df = pd.read_csv("pollution.csv")
except:
    df = pd.DataFrame()

if not df.empty:
    latest = df.groupby("city").tail(1).copy()

    for _, row in latest.iterrows():
        st.subheader(row["city"])

        routeA = row["pm25"] + random.randint(10,50)
        routeB = row["pm25"] - random.randint(5,40)
        routeC = row["pm25"] + random.randint(0,30)

        routes = {
            "Route A": routeA,
            "Route B": routeB,
            "Route C": routeC
        }

        best = min(routes, key=routes.get)

        st.write("Route Pollution Scores:", routes)
        st.success(f"Recommended Cleanest Route: {best}")
