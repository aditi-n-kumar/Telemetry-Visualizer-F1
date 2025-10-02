import os
import streamlit as st
import fastf1
import matplotlib.pyplot as plt
import pandas as pd

# -------------------------------
# Setup FastF1 cache safely
# -------------------------------
cache_dir = ".streamlit/cache"
os.makedirs(cache_dir, exist_ok=True)  # Create folder if it doesn't exist
fastf1.Cache.enable_cache(cache_dir)

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
- **Telemetry Visualizer**: Compare telemetry data (speed, throttle, brake, etc.) between two drivers during a race or qualifying session.
- **Session Summary**: See drivers dashboard for each session, including lap times, sector times, and tire strategies.
- **Strategy Tools**: Analyze pit stops, tire strategies, top speeds, and sector performance.
- *(More pages coming soon)*

---
To get started, click on **"Telemetry Visualizer"** in the left sidebar.
""")

# import streamlit as st
# import fastf1
# import matplotlib.pyplot as plt
# import pandas as pd

# fastf1.Cache.enable_cache('fastf1cache')

# st.title("F1 Telemetry Dashboard")

# # User inputs
# year = st.selectbox("Select Year", list(range(2018, 2024)))
# gp = st.selectbox("Select Grand Prix", ['British Grand Prix', 'Monaco Grand Prix', 'Italian Grand Prix'])
# session_type = st.selectbox("Select Session", ['Q', 'R', 'S'])  # Qualifying, Race, Sprint

# driver1 = st.text_input("Enter Driver 1 Code (e.g. HAM, VER)")
# driver2 = st.text_input("Enter Driver 2 Code to Compare (Optional)")

# telemetry_option = st.selectbox(
#     "Select Telemetry Type",
#     ['Speed', 'Throttle', 'Brake', 'RPM', 'Gear', 'DRS', 'nGear']
# )

# if st.button("Load Telemetry") and driver1:
#     session = fastf1.get_session(year, gp, session_type)
#     session.load()
    
#     lap1 = session.laps.pick_driver(driver1).pick_fastest()
#     telemetry1 = lap1.get_telemetry()
    
#     st.subheader(f"{driver1} - {telemetry_option}")
#     fig1, ax1 = plt.subplots()
#     ax1.plot(telemetry1['Distance'], telemetry1[telemetry_option], label=driver1, color='blue')
#     ax1.set_xlabel('Distance (m)')
#     ax1.set_ylabel(telemetry_option)
#     ax1.set_title(f'{driver1} {telemetry_option} on Fastest Lap - {gp} {year}')
#     ax1.legend()
#     st.pyplot(fig1)

#     # Track Map
#     st.subheader(f"{driver1} - Track Map")
#     fig_map, ax_map = plt.subplots()
#     ax_map.plot(telemetry1['X'], telemetry1['Y'], label=driver1, color='blue')
#     ax_map.set_title(f'{driver1} Track Map - {gp} {year}')
#     ax_map.axis('equal')
#     st.pyplot(fig_map)

#     # Lap Summary
#     st.subheader("Lap Summary")
#     st.write({
#         "Lap Time": str(lap1['LapTime']),
#         "Sector 1": str(lap1['Sector1Time']),
#         "Sector 2": str(lap1['Sector2Time']),
#         "Sector 3": str(lap1['Sector3Time']),
#         "Compound": lap1['Compound']
#     })

#     # CSV Download
#     st.subheader("Download Telemetry")
#     csv1 = telemetry1.to_csv(index=False)
#     st.download_button(f"Download {driver1} Telemetry CSV", csv1, f"{driver1}_telemetry.csv", "text/csv")

#     # Driver 2 comparison
#     if driver2:
#         try:
#             lap2 = session.laps.pick_driver(driver2).pick_fastest()
#             telemetry2 = lap2.get_telemetry()

#             st.subheader(f"Comparison: {driver1} vs {driver2} - {telemetry_option}")
#             fig_compare, ax_compare = plt.subplots()
#             ax_compare.plot(telemetry1['Distance'], telemetry1[telemetry_option], label=driver1, color='blue')
#             ax_compare.plot(telemetry2['Distance'], telemetry2[telemetry_option], label=driver2, color='red')
#             ax_compare.set_xlabel('Distance (m)')
#             ax_compare.set_ylabel(telemetry_option)
#             ax_compare.set_title(f'{driver1} vs {driver2} - {telemetry_option} - {gp} {year}')
#             ax_compare.legend()
#             st.pyplot(fig_compare)

#             # Track Map Comparison
#             st.subheader("Track Map Comparison")
#             fig_map2, ax_map2 = plt.subplots()
#             ax_map2.plot(telemetry1['X'], telemetry1['Y'], label=driver1, color='blue')
#             ax_map2.plot(telemetry2['X'], telemetry2['Y'], label=driver2, color='red')
#             ax_map2.set_title(f'{driver1} vs {driver2} Track Map - {gp} {year}')
#             ax_map2.axis('equal')
#             ax_map2.legend()
#             st.pyplot(fig_map2)

#             # Comparison Lap Summary
#             st.subheader("Lap Summary Comparison")
#             st.write({
#                 driver1: {
#                     "Lap Time": str(lap1['LapTime']),
#                     "Sector 1": str(lap1['Sector1Time']),
#                     "Sector 2": str(lap1['Sector2Time']),
#                     "Sector 3": str(lap1['Sector3Time']),
#                     "Compound": lap1['Compound']
#                 },
#                 driver2: {
#                     "Lap Time": str(lap2['LapTime']),
#                     "Sector 1": str(lap2['Sector1Time']),
#                     "Sector 2": str(lap2['Sector2Time']),
#                     "Sector 3": str(lap2['Sector3Time']),
#                     "Compound": lap2['Compound']
#                 }
#             })

#             # CSV for Driver 2
#             csv2 = telemetry2.to_csv(index=False)
#             st.download_button(f"Download {driver2} Telemetry CSV", csv2, f"{driver2}_telemetry.csv", "text/csv")
        
#         except Exception as e:
#             st.error(f"Could not load telemetry for {driver2}: {e}")
