import streamlit as st
import fastf1

import matplotlib.pyplot as plt
import pandas as pd

# Enable FastF1 cache
fastf1.Cache.enable_cache('fastf1cache')

# Page title
st.title("F1 Telemetry Dashboard")

# --- Helper Functions ---
@st.cache_data(show_spinner=False)
def load_session(year, gp, session_type):
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return session

@st.cache_data(show_spinner=False)
def get_driver_telemetry(_session, driver_code: str):
    lap = _session.laps.pick_driver(driver_code).pick_fastest()
    telemetry = lap.get_telemetry()
    return lap, telemetry

def smooth_telemetry(telemetry: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    return telemetry.rolling(window=window, min_periods=1).mean()

# --- Sidebar ---
st.sidebar.header("Session Selection")
year = st.sidebar.selectbox("Select Year", list(range(2022, 2026)))
gp = st.sidebar.selectbox("Select Grand Prix", [
    'Australian Grand Prix', 'Chinese Grand Prix', 'Japanese Grand Prix', 'Bahrain Grand Prix', 
    'Saudi Arabian Grand Prix', 'Miami Grand Prix', 'British Grand Prix', 'Monaco Grand Prix', 'Italian Grand Prix', 
    'Singapore Grand Prix'
])
session_type = st.sidebar.selectbox("Select Session", ['Q', 'R', 'S'])  # Qualifying, Race, Sprint

session = load_session(year, gp, session_type)

# Get list of available drivers
# drivers_df = session.results[['Abbreviation', 'FullName']]
# driver_list = sorted(drivers_df['Abbreviation'].tolist())

drivers_df = session.results[['Abbreviation', 'FullName']].dropna()
drivers_df['Display'] = drivers_df['FullName'].apply(lambda x: x.split()[-1]) + " (" + drivers_df['Abbreviation'] + ")"

# Create mapping from display name to code
display_to_code = dict(zip(drivers_df['Display'], drivers_df['Abbreviation']))
driver_list = sorted(display_to_code.keys())

st.sidebar.header("Driver Selection")
driver1 = st.sidebar.selectbox("Select Driver 1", driver_list)
driver2 = st.sidebar.selectbox("Select Driver 2 (optional)", ['None'] + driver_list)

# Look up actual driver codes
driver1 = display_to_code[driver1]
driver2 = display_to_code[driver2] if driver2 != 'None' else 'None'

telemetry_option = st.sidebar.selectbox(
    "Select Telemetry Type",
    ['Speed', 'Throttle', 'Brake', 'RPM', 'Gear', 'DRS', 'nGear']
)

# trying to make things cleaner
apply_smoothing = st.sidebar.checkbox("Apply Smoothing", value=False)

load_btn = st.sidebar.button("Load Telemetry")

# --- Main Content ---
if load_btn and driver1:
    with st.spinner("Loading telemetry data..."):
        try:
            lap1, telemetry1 = get_driver_telemetry(session, driver1)

            # Driver 1 Plot
            st.subheader(f"{driver1} - {telemetry_option}")
            fig1, ax1 = plt.subplots()
            ax1.plot(telemetry1['Distance'], telemetry1[telemetry_option], label=driver1, color='blue')
            ax1.set_xlabel('Distance (m)')
            ax1.set_ylabel(telemetry_option)
            ax1.set_title(f'{driver1} {telemetry_option} on Fastest Lap - {gp} {year}')
            ax1.legend()
            st.pyplot(fig1)

            # Track Map
            st.subheader(f"{driver1} - Track Map")
            fig_map, ax_map = plt.subplots()
            ax_map.plot(telemetry1['X'], telemetry1['Y'], label=driver1, color='blue')
            ax_map.set_title(f'{driver1} Track Map - {gp} {year}')
            ax_map.axis('equal')
            st.pyplot(fig_map)

            # Lap Summary
            st.subheader("Lap Summary")
            st.write({
                "Lap Time": str(lap1['LapTime']),
                "Sector 1": str(lap1['Sector1Time']),
                "Sector 2": str(lap1['Sector2Time']),
                "Sector 3": str(lap1['Sector3Time']),
                "Compound": lap1['Compound']
            })
            
            ''' trying this out'''
            if apply_smoothing:
                telemetry1 = smooth_telemetry(telemetry1)

            # Download CSV
            csv1 = telemetry1.to_csv(index=False)
            st.download_button(f"Download {driver1} Telemetry CSV", csv1, f"{driver1}_telemetry.csv", "text/csv")

            # Optional Driver 2
            if driver2 != 'None':
                try:
                    lap2, telemetry2 = get_driver_telemetry(session, driver2)

                    # Comparison Plot
                    st.subheader(f"Comparison: {driver1} vs {driver2} - {telemetry_option}")
                    fig_compare, ax_compare = plt.subplots()
                    ax_compare.plot(telemetry1['Distance'], telemetry1[telemetry_option], label=driver1, color='blue')
                    ax_compare.plot(telemetry2['Distance'], telemetry2[telemetry_option], label=driver2, color='red')
                    ax_compare.set_xlabel('Distance (m)')
                    ax_compare.set_ylabel(telemetry_option)
                    ax_compare.set_title(f'{driver1} vs {driver2} - {telemetry_option} - {gp} {year}')
                    ax_compare.legend()
                    st.pyplot(fig_compare)

                    # Track Map Comparison
                    st.subheader("Track Map Comparison")
                    fig_map2, ax_map2 = plt.subplots()
                    ax_map2.plot(telemetry1['X'], telemetry1['Y'], label=driver1, color='blue')
                    ax_map2.plot(telemetry2['X'], telemetry2['Y'], label=driver2, color='red')
                    ax_map2.set_title(f'{driver1} vs {driver2} Track Map - {gp} {year}')
                    ax_map2.axis('equal')
                    ax_map2.legend()
                    st.pyplot(fig_map2)


                    # Delta Time Plot
                    st.subheader("Delta Time Plot")
                    try:
                        delta, ref_tel = fastf1.plotting.delta_time(lap1, lap2)

                        fig_delta, ax_delta = plt.subplots()
                        ax_delta.plot(ref_tel['Distance'], delta, color='purple')
                        ax_delta.set_xlabel('Distance (m)')
                        ax_delta.set_ylabel('Delta Time (s)')
                        ax_delta.axhline(0, color='black', linestyle='--', linewidth=1)
                        ax_delta.set_title(f"{driver2} vs {driver1} Delta Time (Negative = {driver2} ahead)")
                        st.pyplot(fig_delta)

                    except Exception as e:
                        st.error(f"Could not calculate delta time: {e}")



                    # Lap Summary Comparison
                    st.subheader("Lap Summary Comparison")
                    st.write({
                        driver1: {
                            "Lap Time": str(lap1['LapTime']),
                            "Sector 1": str(lap1['Sector1Time']),
                            "Sector 2": str(lap1['Sector2Time']),
                            "Sector 3": str(lap1['Sector3Time']),
                            "Compound": lap1['Compound']
                        },
                        driver2: {
                            "Lap Time": str(lap2['LapTime']),
                            "Sector 1": str(lap2['Sector1Time']),
                            "Sector 2": str(lap2['Sector2Time']),
                            "Sector 3": str(lap2['Sector3Time']),
                            "Compound": lap2['Compound']
                        }
                    })
                    ''' trying this out'''
                    if apply_smoothing:
                        telemetry2 = smooth_telemetry(telemetry2)

                    # Download CSV for Driver 2
                    csv2 = telemetry2.to_csv(index=False)
                    st.download_button(f"Download {driver2} Telemetry CSV", csv2, f"{driver2}_telemetry.csv", "text/csv")

                except Exception as e:
                    st.error(f"Could not load telemetry for {driver2}: {e}")

        except Exception as e:
            st.error(f"Failed to load session: {e}")

####--------------------------------------------------------------------------------------------------------------------

# import streamlit as st
# import fastf1
# import matplotlib.pyplot as plt
# import pandas as pd
# from fastf1.core import Laps

# # Enable cache
# fastf1.Cache.enable_cache('fastf1cache')

# # Page title
# st.title("F1 Telemetry Dashboard")

# # --- Helper Functions ---
# @st.cache_data(show_spinner=False)
# def load_session(year, gp, session_type):
#     session = fastf1.get_session(year, gp, session_type)
#     session.load()
#     return session

# @st.cache_data(show_spinner=False)
# def get_driver_telemetry(_session, driver_code: str):  # 🛠️ Fix: ignore session hashing
#     lap = _session.laps.pick_driver(driver_code).pick_fastest()
#     telemetry = lap.get_telemetry()
#     return lap, telemetry

# # --- Sidebar ---
# st.sidebar.header("Session Selection")
# year = st.sidebar.selectbox("Select Year", list(range(2018, 2024)))
# gp = st.sidebar.selectbox("Select Grand Prix", [
#     'British Grand Prix', 'Monaco Grand Prix', 'Italian Grand Prix'
# ])
# session_type = st.sidebar.selectbox("Select Session", ['Q', 'R', 'S'])  # Qualifying, Race, Sprint

# st.sidebar.header("Driver Selection")
# driver1 = st.sidebar.text_input("Driver 1 Code (e.g. HAM, VER)").upper()
# driver2 = st.sidebar.text_input("Driver 2 Code (Optional)").upper()

# telemetry_option = st.sidebar.selectbox(
#     "Select Telemetry Type",
#     ['Speed', 'Throttle', 'Brake', 'RPM', 'Gear', 'DRS', 'nGear']
# )

# load_btn = st.sidebar.button("Load Telemetry")

# # --- Main Content ---
# if load_btn and driver1:
#     with st.spinner("Loading telemetry data..."):
#         try:
#             session = load_session(year, gp, session_type)
#             lap1, telemetry1 = get_driver_telemetry(session, driver1)

#             # Driver 1 Plot
#             st.subheader(f"{driver1} - {telemetry_option}")
#             fig1, ax1 = plt.subplots()
#             ax1.plot(telemetry1['Distance'], telemetry1[telemetry_option], label=driver1, color='blue')
#             ax1.set_xlabel('Distance (m)')
#             ax1.set_ylabel(telemetry_option)
#             ax1.set_title(f'{driver1} {telemetry_option} on Fastest Lap - {gp} {year}')
#             ax1.legend()
#             st.pyplot(fig1)

#             # Track Map
#             st.subheader(f"{driver1} - Track Map")
#             fig_map, ax_map = plt.subplots()
#             ax_map.plot(telemetry1['X'], telemetry1['Y'], label=driver1, color='blue')
#             ax_map.set_title(f'{driver1} Track Map - {gp} {year}')
#             ax_map.axis('equal')
#             st.pyplot(fig_map)

#             # Lap Summary
#             st.subheader("Lap Summary")
#             st.write({
#                 "Lap Time": str(lap1['LapTime']),
#                 "Sector 1": str(lap1['Sector1Time']),
#                 "Sector 2": str(lap1['Sector2Time']),
#                 "Sector 3": str(lap1['Sector3Time']),
#                 "Compound": lap1['Compound']
#             })

#             # Download CSV
#             csv1 = telemetry1.to_csv(index=False)
#             st.download_button(f"Download {driver1} Telemetry CSV", csv1, f"{driver1}_telemetry.csv", "text/csv")

#             # Optional Driver 2
#             if driver2:
#                 try:
#                     lap2, telemetry2 = get_driver_telemetry(session, driver2)

#                     # Comparison Plot
#                     st.subheader(f"Comparison: {driver1} vs {driver2} - {telemetry_option}")
#                     fig_compare, ax_compare = plt.subplots()
#                     ax_compare.plot(telemetry1['Distance'], telemetry1[telemetry_option], label=driver1, color='blue')
#                     ax_compare.plot(telemetry2['Distance'], telemetry2[telemetry_option], label=driver2, color='red')
#                     ax_compare.set_xlabel('Distance (m)')
#                     ax_compare.set_ylabel(telemetry_option)
#                     ax_compare.set_title(f'{driver1} vs {driver2} - {telemetry_option} - {gp} {year}')
#                     ax_compare.legend()
#                     st.pyplot(fig_compare)

#                     # Track Map Comparison
#                     st.subheader("Track Map Comparison")
#                     fig_map2, ax_map2 = plt.subplots()
#                     ax_map2.plot(telemetry1['X'], telemetry1['Y'], label=driver1, color='blue')
#                     ax_map2.plot(telemetry2['X'], telemetry2['Y'], label=driver2, color='red')
#                     ax_map2.set_title(f'{driver1} vs {driver2} Track Map - {gp} {year}')
#                     ax_map2.axis('equal')
#                     ax_map2.legend()
#                     st.pyplot(fig_map2)

#                     # Lap Summary Comparison
#                     st.subheader("Lap Summary Comparison")
#                     st.write({
#                         driver1: {
#                             "Lap Time": str(lap1['LapTime']),
#                             "Sector 1": str(lap1['Sector1Time']),
#                             "Sector 2": str(lap1['Sector2Time']),
#                             "Sector 3": str(lap1['Sector3Time']),
#                             "Compound": lap1['Compound']
#                         },
#                         driver2: {
#                             "Lap Time": str(lap2['LapTime']),
#                             "Sector 1": str(lap2['Sector1Time']),
#                             "Sector 2": str(lap2['Sector2Time']),
#                             "Sector 3": str(lap2['Sector3Time']),
#                             "Compound": lap2['Compound']
#                         }
#                     })

#                     # Download CSV for Driver 2
#                     csv2 = telemetry2.to_csv(index=False)
#                     st.download_button(f"Download {driver2} Telemetry CSV", csv2, f"{driver2}_telemetry.csv", "text/csv")

#                 except Exception as e:
#                     st.error(f"Could not load telemetry for {driver2}: {e}")

#         except Exception as e:
#             st.error(f"Failed to load session: {e}")


# ----------------------------------------------------------------------------------------------------------------------------------------

# import streamlit as st
# import fastf1
# import matplotlib.pyplot as plt
# import pandas as pd


# # Enable FastF1 cache
# fastf1.Cache.enable_cache('fastf1cache')

# # Page title
# st.title("F1 Telemetry Dashboard")

# # Sidebar inputs
# st.sidebar.header("Session Selection")
# year = st.sidebar.selectbox("Select Year", list(range(2018, 2024)))
# gp = st.sidebar.selectbox("Select Grand Prix", [
#     'British Grand Prix', 'Monaco Grand Prix', 'Italian Grand Prix'
# ])
# session_type = st.sidebar.selectbox("Select Session", ['Q', 'R', 'S'])  # Qualifying, Race, Sprint

# st.sidebar.header("Driver Selection")
# driver1 = st.sidebar.text_input("Driver 1 Code (e.g. HAM, VER)").upper()
# driver2 = st.sidebar.text_input("Driver 2 Code (Optional)").upper()

# telemetry_option = st.sidebar.selectbox(
#     "Select Telemetry Type",
#     ['Speed', 'Throttle', 'Brake', 'RPM', 'Gear', 'DRS', 'nGear']
# )

# load_btn = st.sidebar.button("Load Telemetry")

# # Main content
# if load_btn and driver1:
#     with st.spinner("Loading session..."):
#         try:
#             session = fastf1.get_session(year, gp, session_type)
#             session.load()

#             lap1 = session.laps.pick_driver(driver1).pick_fastest()
#             telemetry1 = lap1.get_telemetry()

#             # Driver 1 Plot
#             st.subheader(f"{driver1} - {telemetry_option}")
#             fig1, ax1 = plt.subplots()
#             ax1.plot(telemetry1['Distance'], telemetry1[telemetry_option], label=driver1, color='blue')
#             ax1.set_xlabel('Distance (m)')
#             ax1.set_ylabel(telemetry_option)
#             ax1.set_title(f'{driver1} {telemetry_option} on Fastest Lap - {gp} {year}')
#             ax1.legend()
#             st.pyplot(fig1)

#             # Track Map
#             st.subheader(f"{driver1} - Track Map")
#             fig_map, ax_map = plt.subplots()
#             ax_map.plot(telemetry1['X'], telemetry1['Y'], label=driver1, color='blue')
#             ax_map.set_title(f'{driver1} Track Map - {gp} {year}')
#             ax_map.axis('equal')
#             st.pyplot(fig_map)

#             # Lap Summary
#             st.subheader("Lap Summary")
#             st.write({
#                 "Lap Time": str(lap1['LapTime']),
#                 "Sector 1": str(lap1['Sector1Time']),
#                 "Sector 2": str(lap1['Sector2Time']),
#                 "Sector 3": str(lap1['Sector3Time']),
#                 "Compound": lap1['Compound']
#             })

#             # CSV Download
#             st.subheader("Download Telemetry")
#             csv1 = telemetry1.to_csv(index=False)
#             st.download_button(f"Download {driver1} Telemetry CSV", csv1, f"{driver1}_telemetry.csv", "text/csv")

#             # Driver 2 comparison
#             if driver2:
#                 try:
#                     lap2 = session.laps.pick_driver(driver2).pick_fastest()
#                     telemetry2 = lap2.get_telemetry()

#                     st.subheader(f"Comparison: {driver1} vs {driver2} - {telemetry_option}")
#                     fig_compare, ax_compare = plt.subplots()
#                     ax_compare.plot(telemetry1['Distance'], telemetry1[telemetry_option], label=driver1, color='blue')
#                     ax_compare.plot(telemetry2['Distance'], telemetry2[telemetry_option], label=driver2, color='red')
#                     ax_compare.set_xlabel('Distance (m)')
#                     ax_compare.set_ylabel(telemetry_option)
#                     ax_compare.set_title(f'{driver1} vs {driver2} - {telemetry_option} - {gp} {year}')
#                     ax_compare.legend()
#                     st.pyplot(fig_compare)

#                     # Track Map Comparison
#                     st.subheader("Track Map Comparison")
#                     fig_map2, ax_map2 = plt.subplots()
#                     ax_map2.plot(telemetry1['X'], telemetry1['Y'], label=driver1, color='blue')
#                     ax_map2.plot(telemetry2['X'], telemetry2['Y'], label=driver2, color='red')
#                     ax_map2.set_title(f'{driver1} vs {driver2} Track Map - {gp} {year}')
#                     ax_map2.axis('equal')
#                     ax_map2.legend()
#                     st.pyplot(fig_map2)

#                     # Lap Summary Comparison
#                     st.subheader("Lap Summary Comparison")
#                     st.write({
#                         driver1: {
#                             "Lap Time": str(lap1['LapTime']),
#                             "Sector 1": str(lap1['Sector1Time']),
#                             "Sector 2": str(lap1['Sector2Time']),
#                             "Sector 3": str(lap1['Sector3Time']),
#                             "Compound": lap1['Compound']
#                         },
#                         driver2: {
#                             "Lap Time": str(lap2['LapTime']),
#                             "Sector 1": str(lap2['Sector1Time']),
#                             "Sector 2": str(lap2['Sector2Time']),
#                             "Sector 3": str(lap2['Sector3Time']),
#                             "Compound": lap2['Compound']
#                         }
#                     })

#                     # CSV for Driver 2
#                     csv2 = telemetry2.to_csv(index=False)
#                     st.download_button(f"Download {driver2} Telemetry CSV", csv2, f"{driver2}_telemetry.csv", "text/csv")

#                 except Exception as e:
#                     st.error(f"Could not load telemetry for {driver2}: {e}")

#         except Exception as e:
#             st.error(f"Failed to load session: {e}")
