## VERSION
# load progress bar at both top and bottom of sidebar



import fastf1
import streamlit as st
import fastf1
from fastf1.utils import delta_time
import matplotlib.pyplot as plt
import pandas as pd

# Enable FastF1 cache
# fastf1.Cache.enable_cache('fastf1cache')

#redoing this
# fastf1.Cache.enable_cache(".streamlit/cache")

fastf1.Cache.enable_cache('fastf1cache')

# Sidebar progress placeholder (VERY top of the sidebar)
sidebar_top = st.sidebar.container()
top_progress = sidebar_top.progress(0)
top_status = sidebar_top.empty()

# Page title
st.title("F1 Telemetry Dashboard")

# --- Helper Functions ---
@st.cache_resource(show_spinner=False)
def load_session(year, gp, session_type):
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return session

def get_driver_telemetry(_session, driver_code: str):
    # do not cache this function because it accepts complex session objects
    try:
        lap = _session.laps.pick_driver(driver_code).pick_fastest()
        telemetry = lap.get_telemetry()
        return lap, telemetry
    except Exception as e:
        raise RuntimeError(f"No telemetry for {driver_code}: {e}")

def smooth_telemetry(telemetry: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    return telemetry.rolling(window=window, min_periods=1).mean()

# --- Dark theme for matplotlib ---
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

# Sidebar progress placeholder (bottom, just below the load button)
sidebar_bottom = st.sidebar.container()
bottom_progress = sidebar_bottom.progress(0)
bottom_status = sidebar_bottom.empty()

# --- Main Content ---
if load_btn and driver1:
    # initialize status/percent at both top and bottom of sidebar
    top_progress.progress(2)
    bottom_progress.progress(2)
    top_status.text("Starting telemetry load...")
    bottom_status.text("Starting telemetry load...")

    with st.spinner("Loading telemetry data..."):
        try:
            # load driver1 telemetry
            top_progress.progress(15)
            bottom_progress.progress(15)
            top_status.text(f"Loading telemetry for {driver1}...")
            bottom_status.text(f"Loading telemetry for {driver1}...")
            lap1, telemetry1 = get_driver_telemetry(session, driver1)

            # Optional driver2
            has_driver2 = driver2 != 'None'
            if has_driver2:
                try:
                    top_progress.progress(30)
                    bottom_progress.progress(30)
                    top_status.text(f"Loading telemetry for {driver2}...")
                    bottom_status.text(f"Loading telemetry for {driver2}...")
                    lap2, telemetry2 = get_driver_telemetry(session, driver2)
                except Exception as e:
                    has_driver2 = False
                    telemetry2 = None
                    lap2 = None
                    st.error(f"Could not load telemetry for {driver2}: {e}")

            # Apply smoothing before plotting if requested
            if apply_smoothing:
                top_progress.progress(55)
                bottom_progress.progress(55)
                top_status.text("Applying smoothing...")
                bottom_status.text("Applying smoothing...")
                telemetry1 = smooth_telemetry(telemetry1)
                if has_driver2 and telemetry2 is not None:
                    telemetry2 = smooth_telemetry(telemetry2)
            else:
                top_progress.progress(50)
                bottom_progress.progress(50)
                top_status.text("Smoothing skipped")
                bottom_status.text("Smoothing skipped")

            # 1) Comparison plot (full width) - only if we have a second driver
            if has_driver2:
                st.subheader(f"Comparison: {driver1} vs {driver2} - {telemetry_option}")
                fig_compare, ax_compare = dark_fig(figsize=(10, 4))
                plotted = False
                if telemetry_option in telemetry1.columns:
                    ax_compare.plot(telemetry1['Distance'], telemetry1[telemetry_option], label=driver1, color='tab:blue')
                    plotted = True
                if telemetry_option in telemetry2.columns:
                    ax_compare.plot(telemetry2['Distance'], telemetry2[telemetry_option], label=driver2, color='tab:red')
                    plotted = True

                if plotted:
                    ax_compare.set_xlabel('Distance (m)')
                    ax_compare.set_ylabel(telemetry_option)
                    ax_compare.set_title(f'{driver1} vs {driver2} - {telemetry_option} - {gp} {year}')
                    ax_compare.legend()
                    st.pyplot(fig_compare)
                else:
                    st.warning(f"Telemetry field '{telemetry_option}' not available for comparison.")

            # 2) Individual plots side-by-side
            top_progress.progress(75)
            bottom_progress.progress(75)
            top_status.text("Rendering plots...")
            bottom_status.text("Rendering plots...")
            cols = st.columns(2)
            # Driver 1 column
            with cols[0]:
                st.subheader(f"{driver1} - {telemetry_option}")
                fig1, ax1 = dark_fig(figsize=(6, 3))
                if telemetry_option in telemetry1.columns:
                    ax1.plot(telemetry1['Distance'], telemetry1[telemetry_option], label=driver1, color='tab:blue')
                    ax1.set_xlabel('Distance (m)')
                    ax1.set_ylabel(telemetry_option)
                    ax1.set_title(f'{driver1} {telemetry_option} - {gp} {year}')
                    ax1.legend()
                    st.pyplot(fig1)
                else:
                    st.warning(f"Telemetry field '{telemetry_option}' not available for {driver1}.")

                st.subheader(f"{driver1} - Track Map")
                fig_map1, ax_map1 = dark_fig(figsize=(6, 3))
                ax_map1.plot(telemetry1['X'], telemetry1['Y'], label=driver1, color='tab:blue')
                ax_map1.set_title(f'{driver1} Track Map - {gp} {year}')
                ax_map1.axis('equal')
                st.pyplot(fig_map1)

                st.write({
                    "Lap Time": str(lap1['LapTime']),
                    "Sector 1": str(lap1['Sector1Time']),
                    "Sector 2": str(lap1['Sector2Time']),
                    "Sector 3": str(lap1['Sector3Time']),
                    "Compound": lap1.get('Compound', None)
                })

            # Driver 2 column (if present)
            with cols[1]:
                if has_driver2:
                    st.subheader(f"{driver2} - {telemetry_option}")
                    fig2, ax2 = dark_fig(figsize=(6, 3))
                    if telemetry_option in telemetry2.columns:
                        ax2.plot(telemetry2['Distance'], telemetry2[telemetry_option], label=driver2, color='tab:red')
                        ax2.set_xlabel('Distance (m)')
                        ax2.set_ylabel(telemetry_option)
                        ax2.set_title(f'{driver2} {telemetry_option} - {gp} {year}')
                        ax2.legend()
                        st.pyplot(fig2)
                    else:
                        st.warning(f"Telemetry field '{telemetry_option}' not available for {driver2}.")

                    st.subheader(f"{driver2} - Track Map")
                    fig_map2, ax_map2 = dark_fig(figsize=(6, 3))
                    ax_map2.plot(telemetry2['X'], telemetry2['Y'], label=driver2, color='tab:red')
                    ax_map2.set_title(f'{driver2} Track Map - {gp} {year}')
                    ax_map2.axis('equal')
                    st.pyplot(fig_map2)

                    st.write({
                        driver1: {
                            "Lap Time": str(lap1['LapTime']),
                            "Sector 1": str(lap1['Sector1Time']),
                            "Sector 2": str(lap1['Sector2Time']),
                            "Sector 3": str(lap1['Sector3Time']),
                            "Compound": lap1.get('Compound', None)
                        },
                        driver2: {
                            "Lap Time": str(lap2['LapTime']),
                            "Sector 1": str(lap2['Sector1Time']),
                            "Sector 2": str(lap2['Sector2Time']),
                            "Sector 3": str(lap2['Sector3Time']),
                            "Compound": lap2.get('Compound', None)
                        }
                    })
                else:
                    st.info("No second driver selected — select a second driver to show a side-by-side comparison column.")

            # Download CSVs (kept below so UI remains clean)
            top_progress.progress(95)
            bottom_progress.progress(95)
            top_status.text("Preparing downloads...")
            bottom_status.text("Preparing downloads...")
            csv1 = telemetry1.to_csv(index=False)
            st.download_button(f"Download {driver1} Telemetry CSV", csv1, f"{driver1}_telemetry.csv", "text/csv")
            if has_driver2 and telemetry2 is not None:
                csv2 = telemetry2.to_csv(index=False)
                st.download_button(f"Download {driver2} Telemetry CSV", csv2, f"{driver2}_telemetry.csv", "text/csv")

            top_progress.progress(100)
            bottom_progress.progress(100)
            top_status.success("Telemetry load complete")
            bottom_status.success("Telemetry load complete")

        except Exception as e:
            top_progress.progress(100)
            bottom_progress.progress(100)
            top_status.error("Failed to load telemetry")
            bottom_status.error("Failed to load telemetry")
            st.error(f"Failed to load session: {e}")
