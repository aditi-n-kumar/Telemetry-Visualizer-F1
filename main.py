import os
import streamlit as st
import fastf1
import matplotlib.pyplot as plt
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time
import threading

# -------------------------------
# Setup FastF1 cache safely
# -------------------------------
cache_dir = ".streamlit/cache"
os.makedirs(cache_dir, exist_ok=True)  # Create folder if it doesn't exist
fastf1.Cache.enable_cache(cache_dir)

# -------------------------------
# Function: preload sessions (runs once)
# -------------------------------
def preload_sessions(years, rounds):
    """Preload FastF1 sessions in parallel to speed up first access."""
    executor = ThreadPoolExecutor(max_workers=6)

    def _load_session(year, rnd):
        try:
            sess = fastf1.get_session(year, rnd, 'Race')
            sess.load()  # plain load, compatible with all versions
            _ = sess.results  # only access results, avoid telemetry/laps
            print(f"✅ Cached: {year} Round {rnd}")
        except Exception as e:
            print(f"❌ Error loading {year} Round {rnd}: {e}")

    futures = []
    for yr in years:
        for rnd in rounds:
            futures.append(executor.submit(_load_session, yr, rnd))
    # wait for all tasks to complete (optional)
    for f in futures:
        try:
            f.result(timeout=60)
        except:
            pass

# -------------------------------
# Preload cache in background (runs once per session)
# -------------------------------
if "cache_preloaded" not in st.session_state:
    st.session_state["cache_preloaded"] = True

    def background_warmup():
        time.sleep(2)  # slight delay so UI loads first
        preload_sessions([2021, 2022, 2023, 2024, 2026], range(1, 6))  # adjust years/rounds as needed
        print("✅ FastF1 cache warmup complete")

    threading.Thread(target=background_warmup, daemon=True).start()

# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(
    page_title="F1 Telemetry Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Main Content
# -------------------------------
st.title("🏁 Formula 1 Strategy Dashboard")
st.markdown("""
Welcome to the **F1 Strategy Dashboard**!

This app uses data from **FastF1** to help analyze race telemetry, compare drivers' fastest laps, and explore strategy insights.

### 📊 Pages Available:
- **Telemetry Viewer**: Compare telemetry data (speed, throttle, brake, etc.) between two drivers during a race or qualifying session.
- **Session Summary**: See drivers dashboard for each session, including lap times, sector times, and tire strategies.
- **Strategy Tools**: Analyze pit stops, tire strategies, top speeds, and sector performance.
- **Championship Standings**: See driver and constructor standings over the season.   
- *(More pages coming soon)*

---
To get started, click on **"Telemetry Visualizer"** in the left sidebar.
""")
