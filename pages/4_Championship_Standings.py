import streamlit as st
import pandas as pd
import fastf1

# Enable FastF1 cache
# fastf1.Cache.enable_cache("fastf1cache")
fastf1.Cache.enable_cache(".streamlit/cache")


st.set_page_config(page_title="Championship Standings", layout="wide")
st.title("Championship Standings Visualizer")

# Sidebar: Season selector
year = st.sidebar.selectbox("Select Season", list(range(2021, 2025)), index=3)

# Sidebar: Sub-options for what to show
view_option = st.sidebar.radio(
    "View Option",
    ["Driver Standings", "Constructor Standings", "Both"],
    index=2
)

# Add Load button in sidebar
load_clicked = st.sidebar.button("Load Standings")

# Session state to remember loaded data and year
if "standings_loaded" not in st.session_state:
    st.session_state.standings_loaded = False
    st.session_state.loaded_year = None
    st.session_state.driver_standings_df = None
    st.session_state.constructor_standings_df = None

# Reset loaded flag if year changed
if st.session_state.loaded_year != year:
    st.session_state.standings_loaded = False

def load_standings_for_year(year):
    driver_standings_snapshots = []
    constructor_standings_snapshots = []

    driver_points = {}
    constructor_points = {}

    schedule = fastf1.get_event_schedule(year, include_testing=False)

    for rnd in schedule["RoundNumber"].unique():
        try:
            session = fastf1.get_session(year, rnd, "R")
            session.load()
            results = session.results

            for _, row in results.iterrows():
                drv = row["Abbreviation"]
                team = row["TeamName"]
                pts = row["Points"]

                driver_points[drv] = driver_points.get(drv, 0) + pts
                constructor_points[team] = constructor_points.get(team, 0) + pts

            driver_df = pd.DataFrame({
                "Driver": list(driver_points.keys()),
                "Points": list(driver_points.values())
            }).sort_values(by="Points", ascending=False).reset_index(drop=True)
            driver_df["Round"] = rnd
            driver_standings_snapshots.append(driver_df)

            constructor_df = pd.DataFrame({
                "Constructor": list(constructor_points.keys()),
                "Points": list(constructor_points.values())
            }).sort_values(by="Points", ascending=False).reset_index(drop=True)
            constructor_df["Round"] = rnd
            constructor_standings_snapshots.append(constructor_df)

        except Exception as e:
            st.warning(f"Could not load round {rnd}: {e}")

    if driver_standings_snapshots:
        driver_standings = pd.concat(driver_standings_snapshots, ignore_index=True)
    else:
        driver_standings = pd.DataFrame(columns=["Driver", "Points", "Round"])

    if constructor_standings_snapshots:
        constructor_standings = pd.concat(constructor_standings_snapshots, ignore_index=True)
    else:
        constructor_standings = pd.DataFrame(columns=["Constructor", "Points", "Round"])

    return driver_standings, constructor_standings

# If user clicked load, or if already loaded for this year, load/keep data
if load_clicked:
    with st.spinner("Loading standings... this may take a while"):
        ddf, cdf = load_standings_for_year(year)
        st.session_state.driver_standings_df = ddf
        st.session_state.constructor_standings_df = cdf
        st.session_state.standings_loaded = True
        st.session_state.loaded_year = year

# ---- Display ----
if st.session_state.standings_loaded and st.session_state.loaded_year == year:
    driver_standings = st.session_state.driver_standings_df
    constructor_standings = st.session_state.constructor_standings_df

    if view_option in ["Driver Standings", "Both"]:
        st.subheader(f"Driver Standings {year}")
        if not driver_standings.empty:
            latest_driver = driver_standings[
                driver_standings["Round"] == driver_standings["Round"].max()
            ]
            st.dataframe(latest_driver, use_container_width=True)
        else:
            st.warning("No driver standings available for this season.")

    if view_option in ["Constructor Standings", "Both"]:
        st.subheader(f"Constructor Standings {year}")
        if not constructor_standings.empty:
            latest_constructor = constructor_standings[
                constructor_standings["Round"] == constructor_standings["Round"].max()
            ]
            st.dataframe(latest_constructor, use_container_width=True)
        else:
            st.warning("No constructor standings available for this season.")

else:
    st.info("Click 'Load Standings' in the sidebar to fetch and display season standings.")

# Next steps
# - Add wins/podiums by counting finishing positions
# - Add position change (compare vs previous round standings)
# - Add bump chart or line chart using matplotlib or plotly
# - Add team colors/logos for better visuals
