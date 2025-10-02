# pages/3_Strategy_Tools.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import fastf1
from matplotlib.cm import get_cmap
import io

# Enable FastF1 cache
fastf1.Cache.enable_cache('fastf1cache')

st.set_page_config(page_title="Strategy Tools", layout="wide")
st.title("Strategy Tools")
st.markdown("Insights into pit stops, tire strategy, top speed, and sector performance.")

# --- Driver Lists / Codes ---
YEAR_DRIVERS = {
    2023: ["VER","PER","HAM","RUS","LEC","SAI","NOR","PIA","ALO","OCO",
           "GAS","TSU","BOT","ZHO","MAG","HUL","SAR","STR","ALB","RIC"],
    2024: ["VER","PER","HAM","RUS","LEC","SAI","NOR","PIA","ALO","OCO",
           "GAS","TSU","BOT","ZHO","MAG","HUL","SAR","STR","ALB","RIC"],
    2025: ["VER","RUS","SAI","ANT","LAW","TSU","NOR","HAM","LEC","HAD",
           "BOR","BEA","ALB","OCO","ALO","HUL","STR","GAS","COL","PIA"]
}

TEAM_COLORS = {
    'Mercedes': '#00D2BE',
    'Red Bull': '#1E41FF',
    'Ferrari': '#DC0000',
    'McLaren': '#FF8700',
    'Alpine': '#0090FF',
    'Aston Martin': '#006F62',
    'AlphaTauri': '#2B4562',
    'Haas': '#B6BABD',
    'Alfa Romeo': '#900000',
    'Williams': '#005AFF'
}

YEARS = sorted(YEAR_DRIVERS.keys())
selected_year = st.selectbox("Select Year", YEARS, index=len(YEARS)-1, key="selected_year")
AVAILABLE_DRIVERS = YEAR_DRIVERS.get(selected_year, [])
# --- Grand Prix selector (populate from fastf1 schedule) ---
try:
    schedule = fastf1.get_event_schedule(selected_year)
    gp_options = schedule['EventName'].tolist()
    if not gp_options:
        gp_options = ['Baku']
except Exception:
    gp_options = ['Baku']

selected_gp = st.selectbox("Select Grand Prix", gp_options, index=0, key="selected_gp")

# removed the top "Load Session" button; each tab will load/cached the session on demand
# (session_data is fetched in each tab when needed and stored in st.session_state)

# --- Dark theme for matplotlib / tables ---
DARK_BG = "#0E1117"
TEXT_COLOR = "#E6E6E6"
GRID_COLOR = "#2F343A"

plt.style.use("dark_background")
plt.rcParams.update({
    "figure.facecolor": DARK_BG,
    "axes.facecolor": DARK_BG,
    "savefig.facecolor": DARK_BG,
    "axes.edgecolor": TEXT_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "text.color": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "grid.color": GRID_COLOR,
    "legend.edgecolor": TEXT_COLOR,
    "legend.facecolor": DARK_BG,
    "axes.titlecolor": TEXT_COLOR,
    "figure.edgecolor": DARK_BG,
})
 
def dark_fig(figsize=(8,4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    return fig, ax

def fig_to_png_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf.getvalue()

# --- Fetch session ---
@st.cache_resource(show_spinner=False)
def load_session(year, grand_prix='Baku', session='R'):
    s = fastf1.get_session(year, grand_prix, session)
    s.load()
    return s

# --- Tabs ---
tabs = st.tabs(["Pit Stop Analyzer", "Tire Strategy Visualizer", "Top Speed Comparison", "Sector Heatmap"])


# 1️⃣ Pit Stop Analyzer
with tabs[0]:
    st.header("Pit Stop Analyzer")
    driver_pit = st.selectbox("Select Driver", AVAILABLE_DRIVERS, key="pit_driver")

    load_pits = st.button("Load Pit Stops")

    if load_pits:
        with st.spinner("Loading pit stop data..."):
            session_data = st.session_state.get('session_data')
            if session_data is None:
                session_data = load_session(selected_year, selected_gp, 'R')
                st.session_state['session_data'] = session_data

            driver_laps = session_data.laps.pick_driver(driver_pit)

            # Pit stop detection: laps where PitInTime is set
            pit_laps = driver_laps[driver_laps['PitInTime'].notna()].copy()

            if pit_laps.empty:
                st.warning(f"No pit stops recorded for {driver_pit}.")
            else:
                # Calculate pit stop duration (time difference between PitIn and PitOut)
                pit_laps['PitDuration'] = (pit_laps['PitOutTime'] - pit_laps['PitInTime']).dt.total_seconds()

                # Show as table
                st.subheader("Pit Stop Summary")
                st.dataframe(
                    pit_laps[['LapNumber', 'Compound', 'PitInTime', 'PitOutTime', 'PitDuration']].style
                    .background_gradient(cmap="RdYlGn_r", subset=['PitDuration'])
                    .format({"PitDuration": "{:.2f}"})
                )

                # Plot bar chart of pit stop durations
                fig, ax = dark_fig(figsize=(8, 4))
                ax.bar(pit_laps['LapNumber'], pit_laps['PitDuration'], color="#FFD700", edgecolor="black")
                ax.set_xlabel("Lap Number")
                ax.set_ylabel("Pit Stop Duration (s)")
                ax.set_title(f"Pit Stops — {driver_pit} ({selected_year} {selected_gp})")
                st.pyplot(fig)

                # Download option
                png = fig_to_png_bytes(fig)
                st.download_button(
                    "Download Pit Stop Chart PNG",
                    data=png,
                    file_name=f"pitstops_{driver_pit}_{selected_year}_{selected_gp}.png",
                    mime="image/png"
                )
                plt.clf()
    else:
        st.info("Click 'Load Pit Stops' to fetch pit stop data.")




# 2️⃣ Tire Strategy Visualizer
with tabs[1]:
    st.header("Tire Strategy Visualizer")
    driver_tire = st.selectbox("Select Driver", AVAILABLE_DRIVERS, key="tire_driver")
    lap_range_tire = st.slider("Lap Range", 1, 50, (1,50), key="lap_range_tire")
    
    # Load button
    load_tire = st.button("Load Tire Strategy")
    
    if load_tire:
        with st.spinner("Loading tire strategy..."):
            session_data = st.session_state.get('session_data')
            if session_data is None:
                session_data = load_session(selected_year, selected_gp, 'R')
                st.session_state['session_data'] = session_data
            driver_laps = session_data.laps.pick_driver(driver_tire)
            driver_laps = driver_laps[(driver_laps['LapNumber'] >= lap_range_tire[0]) &
                                      (driver_laps['LapNumber'] <= lap_range_tire[1])]
            stints = driver_laps['Compound'].values
            laps = driver_laps['LapNumber'].values

            colors = {'SOFT':'#ff9999','MEDIUM':'#ffe599','HARD':'#99ccff'}
            fig, ax = plt.subplots(figsize=(12,2))
            for lap, stint in zip(laps, stints):
                ax.barh(0, 1, left=lap-1, color=colors.get(stint.upper(),'grey'), edgecolor='black')
            ax.set_yticks([])
            ax.set_xlabel("Lap")
            ax.set_title(f"Tire Strategy - {driver_tire}")
            st.pyplot(fig)

            # allow download of the chart as PNG
            png = fig_to_png_bytes(fig)
            st.download_button(
                "Download Tire Strategy PNG",
                data=png,
                file_name=f"tire_strategy_{driver_tire}_{selected_year}.png",
                mime="image/png"
            )
            plt.clf()
    else:
        st.info("Click 'Load Tire Strategy' to fetch tire data.")

# 3️⃣ Top Speed Comparison
with tabs[2]:
    st.header("Top Speed Comparison")
    drivers_speed = st.multiselect("Select Drivers", AVAILABLE_DRIVERS, key="speed_drivers")

    load_speed = st.button("Load Top Speeds")

    if load_speed:
        if drivers_speed:
            with st.spinner("Loading top speed data..."):
                session_data = st.session_state.get('session_data')
                if session_data is None:
                    session_data = load_session(selected_year, selected_gp, 'R')
                    st.session_state['session_data'] = session_data
                top_speeds = []
                colors = []
                teams_used = []

                # optional alias map for variations you may encounter
                TEAM_ALIASES = {
                    "Red Bull Racing": "Red Bull",
                    "Red Bull RB": "Red Bull",
                    "Aston Martin Cognizant": "Aston Martin",
                    "Scuderia Ferrari": "Ferrari",
                    "McLaren F1 Team": "McLaren",
                    "Alpine F1 Team": "Alpine",
                    "AlphaTauri": "AlphaTauri",
                    # add others you encounter
                }

                for drv in drivers_speed:
                    driver_laps = session_data.laps.pick_driver(drv)

                    # get top speed safely
                    if driver_laps.empty:
                        top_speed = np.nan
                        raw_team = None
                    else:
                        if 'TopSpeed' in driver_laps.columns:
                            top_speed = driver_laps['TopSpeed'].max()
                        elif 'SpeedST' in driver_laps.columns:
                            top_speed = driver_laps['SpeedST'].max()
                        else:
                            top_speed = np.nan

                        raw_team = None
                        if 'Team' in driver_laps.columns:
                            raw_team = driver_laps['Team'].dropna().astype(str).str.strip().iloc[0] if not driver_laps['Team'].dropna().empty else None

                    # fallback: try session.results lookup (common reliable source)
                    if not raw_team:
                        try:
                            res_row = session_data.results.loc[session_data.results['Abbreviation'] == drv]
                            if not res_row.empty and 'Team' in res_row.columns:
                                raw_team = str(res_row['Team'].iloc[0]).strip()
                        except Exception:
                            raw_team = raw_team

                    # normalize via alias map and simple reductions
                    team_normalized = None
                    if raw_team:
                        team_normalized = TEAM_ALIASES.get(raw_team, raw_team)
                        # further reduce to known key if partial match
                        for key in TEAM_COLORS.keys():
                            if key.lower() in team_normalized.lower() or team_normalized.lower() in key.lower():
                                team_normalized = key
                                break

                    top_speeds.append(top_speed)
                    teams_used.append(team_normalized or "Unknown")
                    colors.append(TEAM_COLORS.get(team_normalized, "#444444"))

                speeds_df = pd.DataFrame({
                    "Driver": drivers_speed,
                    "Top Speed (km/h)": top_speeds,
                    "Team": teams_used
                })

                # Matplotlib bar chart with team colors
                fig, ax = dark_fig(figsize=(8, 4))
                values = speeds_df["Top Speed (km/h)"].fillna(0).astype(float)
                ax.bar(speeds_df["Driver"], values, color=colors, edgecolor='black')
                ax.set_ylabel("Top Speed (km/h)")
                ax.set_title(f"Top Speeds — {selected_year} Baku R")
                ax.set_ylim(0, max(values.max() * 1.1, 10))

                # annotate values
                for i, v in enumerate(values):
                    if v > 0:
                        ax.text(i, v + (values.max() * 0.02), f"{int(v)}", ha='center', va='bottom', fontsize=8)

                # legend for teams present
                from matplotlib.patches import Patch
                unique_teams = [t for t in dict.fromkeys(teams_used) if t and t != "Unknown"]
                handles = [Patch(color=TEAM_COLORS.get(t, "#444444"), label=t) for t in unique_teams]
                if handles:
                    ax.legend(handles=handles, title="Team", bbox_to_anchor=(1.02, 1), loc='upper left')

                st.pyplot(fig)
                # provide PNG download for top speeds chart
                png = fig_to_png_bytes(fig)
                driver_slug = "_".join(drivers_speed)
                st.download_button(
                    "Download Top Speeds PNG",
                    data=png,
                    file_name=f"top_speeds_{driver_slug}_{selected_year}.png",
                    mime="image/png"
                )
                plt.clf()
        else:
            st.info("Select one or more drivers to compare top speeds.")
    else:
        st.info("Click 'Load Top Speeds' to fetch data.")

# 4️⃣ Sector Heatmap
with tabs[3]:
    st.header("Sector Heatmap")
    driver_sector = st.selectbox("Select Driver", AVAILABLE_DRIVERS, key="sector_driver")
    lap_range_sector = st.slider("Lap Range", 1, 50, (1,50), key="lap_range_sector")
    
    load_sector = st.button("Load Sector Data")
    
    if load_sector:
        with st.spinner("Loading sector data..."):
            session_data = st.session_state.get('session_data')
            if session_data is None:
                session_data = load_session(selected_year, selected_gp, 'R')
                st.session_state['session_data'] = session_data
            driver_laps = session_data.laps.pick_driver(driver_sector)
            driver_laps = driver_laps[(driver_laps['LapNumber'] >= lap_range_sector[0]) &
                                      (driver_laps['LapNumber'] <= lap_range_sector[1])]
            sector_cols = ['Sector1','Sector2','Sector3']
            available_cols = [c for c in sector_cols if c in driver_laps.columns]
            
            if available_cols:
                sector_data = driver_laps[available_cols]
                sty = sector_data.style.background_gradient(cmap="RdYlGn_r")
                sty = sty.set_table_styles(
                    [{"selector": "table", "props": [("background-color", DARK_BG), ("color", TEXT_COLOR)]}]
                ).set_properties(**{"background-color": DARK_BG, "color": TEXT_COLOR})
                st.dataframe(sty)
            else:
                st.warning("Sector data not available for this session.")
    else:
        st.info("Click 'Load Sector Data' to fetch sector performance.")

