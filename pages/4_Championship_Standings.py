import fastf1
import streamlit as st
import pandas as pd
import fastf1
import threading
import time

# ---------------------------
# ⚡ Enable lightweight FastF1 cache
# ---------------------------
# fastf1.Cache.enable_cache(".streamlit/cache")
fastf1.Cache.enable_cache('fastf1cache')


st.set_page_config(page_title="Championship Standings", layout="wide")
st.title("🏆 Championship Standings Visualizer")

# Sidebar: Season selector
year = st.sidebar.selectbox("Select Season", list(range(2021, 2026)), index=3)

# Sidebar: View option
view_option = st.sidebar.radio(
    "View Option",
    ["Driver Standings", "Constructor Standings", "Both"],
    index=2
)

# Sidebar: Load button
load_clicked = st.sidebar.button("Load Standings")

# ---------------------------
# 🧠 Session state init
# ---------------------------
if "standings_loaded" not in st.session_state:
    st.session_state.standings_loaded = False
    st.session_state.loaded_year = None
    st.session_state.driver_standings_df = None
    st.session_state.constructor_standings_df = None

# Reset if user changes year
if st.session_state.loaded_year != year:
    st.session_state.standings_loaded = False

# ---------------------------
# 🏎️ Load Standings Function
# ---------------------------
def load_standings_for_year(year):
    driver_points = {}
    constructor_points = {}

    schedule = fastf1.get_event_schedule(year, include_testing=False)
    rounds = sorted(schedule["RoundNumber"].unique())

    for rnd in rounds:
        try:
            session = fastf1.get_session(year, rnd, "R")
            # ⚡ load only results — skip telemetry/laps/weather
            # session.load(results=True, telemetry=False, laps=False, weather=False)
            session.load()
            results = session.results

            for _, row in results.iterrows():
                drv = row.get("Abbreviation") or row.get("Driver")
                team = row.get("TeamName") or row.get("Constructor")
                pts = row.get("Points", 0) or 0

                if drv:
                    driver_points[drv] = driver_points.get(drv, 0) + float(pts)
                if team:
                    constructor_points[team] = constructor_points.get(team, 0) + float(pts)

        except Exception as e:
            st.warning(f"⚠️ Could not load round {rnd}: {e}")

    driver_standings = pd.DataFrame({
        "Driver": list(driver_points.keys()),
        "Points": list(driver_points.values())
    }).sort_values(by="Points", ascending=False).reset_index(drop=True)

    constructor_standings = pd.DataFrame({
        "Constructor": list(constructor_points.keys()),
        "Points": list(constructor_points.values())
    }).sort_values(by="Points", ascending=False).reset_index(drop=True)

    return driver_standings, constructor_standings

# ---------------------------
# 🚀 Background Cache Warmup (runs ONCE)
# ---------------------------
if "cache_warmup_started" not in st.session_state:
    st.session_state.cache_warmup_started = True

    def warmup_delayed():
        time.sleep(3)  # let UI load first
        for yr in range(2021, 2025):
            try:
                load_standings_for_year(yr)
                print(f"✅ Cached {yr} standings.")
            except Exception as e:
                print(f"Warmup error for {yr}: {e}")

    threading.Thread(target=warmup_delayed, daemon=True).start()

# ---------------------------
# 🧩 Load + Display Logic
# ---------------------------
if load_clicked:
    with st.spinner("Loading standings... this may take a while ⏳"):
        ddf, cdf = load_standings_for_year(year)
        st.session_state.driver_standings_df = ddf
        st.session_state.constructor_standings_df = cdf
        st.session_state.standings_loaded = True
        st.session_state.loaded_year = year

if st.session_state.standings_loaded and st.session_state.loaded_year == year:
    driver_standings = st.session_state.driver_standings_df
    constructor_standings = st.session_state.constructor_standings_df

    if view_option in ["Driver Standings", "Both"]:
        st.subheader(f"🏁 Driver Standings {year}")
        if driver_standings is not None and not driver_standings.empty:
            driver_standings["Points"] = pd.to_numeric(driver_standings["Points"], errors="coerce").fillna(0)
            driver_standings = driver_standings.sort_values(by="Points", ascending=False).reset_index(drop=True)
            driver_standings["Position"] = driver_standings.index + 1
            st.dataframe(driver_standings[["Position", "Driver", "Points"]], use_container_width=True)
        else:
            st.warning("No driver standings available for this season.")

    if view_option in ["Constructor Standings", "Both"]:
        st.subheader(f"🏗️ Constructor Standings {year}")
        if constructor_standings is not None and not constructor_standings.empty:
            constructor_standings["Points"] = pd.to_numeric(constructor_standings["Points"], errors="coerce").fillna(0)
            constructor_standings = constructor_standings.sort_values(by="Points", ascending=False).reset_index(drop=True)
            constructor_standings["Position"] = constructor_standings.index + 1
            st.dataframe(constructor_standings[["Position", "Constructor", "Points"]], use_container_width=True)
        else:
            st.warning("No constructor standings available for this season.")
else:
    st.info("Click **'Load Standings'** in the sidebar to fetch and display season standings.")



# import streamlit as st
# import pandas as pd
# import fastf1

# # Enable FastF1 cache
# # fastf1.Cache.enable_cache("fastf1cache")
# fastf1.Cache.enable_cache(".streamlit/cache")


# st.set_page_config(page_title="Championship Standings", layout="wide")
# st.title("Championship Standings Visualizer")

# # Sidebar: Season selector
# year = st.sidebar.selectbox("Select Season", list(range(2021, 2025)), index=3)

# # Sidebar: Sub-options for what to show
# view_option = st.sidebar.radio(
#     "View Option",
#     ["Driver Standings", "Constructor Standings", "Both"],
#     index=2
# )

# # Add Load button in sidebar
# load_clicked = st.sidebar.button("Load Standings")

# # Session state to remember loaded data and year
# if "standings_loaded" not in st.session_state:
#     st.session_state.standings_loaded = False
#     st.session_state.loaded_year = None
#     st.session_state.driver_standings_df = None
#     st.session_state.constructor_standings_df = None

# # Reset loaded flag if year changed
# if st.session_state.loaded_year != year:
#     st.session_state.standings_loaded = False

# def load_standings_for_year(year):
#     driver_points = {}
#     constructor_points = {}

#     schedule = fastf1.get_event_schedule(year, include_testing=False)
#     rounds = sorted(schedule["RoundNumber"].unique())

#     for rnd in rounds:
#         try:
#             session = fastf1.get_session(year, rnd, "R")
#             session.load()
#             results = session.results

#             for _, row in results.iterrows():
#                 drv = row.get("Abbreviation") or row.get("Driver")
#                 team = row.get("TeamName") or row.get("Constructor")
#                 pts = row.get("Points", 0) or 0

#                 if drv:
#                     driver_points[drv] = driver_points.get(drv, 0) + float(pts)
#                 if team:
#                     constructor_points[team] = constructor_points.get(team, 0) + float(pts)

#         except Exception as e:
#             st.warning(f"Could not load round {rnd}: {e}")

#     # Final aggregated standings (end of season totals)
#     driver_standings = pd.DataFrame({
#         "Driver": list(driver_points.keys()),
#         "Points": list(driver_points.values())
#     }).sort_values(by="Points", ascending=False).reset_index(drop=True)

#     constructor_standings = pd.DataFrame({
#         "Constructor": list(constructor_points.keys()),
#         "Points": list(constructor_points.values())
#     }).sort_values(by="Points", ascending=False).reset_index(drop=True)

#     return driver_standings, constructor_standings

# # If user clicked load, or if already loaded for this year, load/keep data
# if load_clicked:
#     with st.spinner("Loading standings... this may take a while"):
#         ddf, cdf = load_standings_for_year(year)
#         st.session_state.driver_standings_df = ddf
#         st.session_state.constructor_standings_df = cdf
#         st.session_state.standings_loaded = True
#         st.session_state.loaded_year = year

# # ---- Display ----
# if st.session_state.standings_loaded and st.session_state.loaded_year == year:
#     driver_standings = st.session_state.driver_standings_df
#     constructor_standings = st.session_state.constructor_standings_df

#     if view_option in ["Driver Standings", "Both"]:
#         st.subheader(f"Driver Standings {year}")
#         if driver_standings is not None and not driver_standings.empty:
#             # ensure numeric and sort by points (descending)
#             driver_standings["Points"] = pd.to_numeric(driver_standings["Points"], errors="coerce").fillna(0)
#             driver_standings = driver_standings.sort_values(by="Points", ascending=False).reset_index(drop=True)
#             driver_standings["Position"] = driver_standings.index + 1
#             st.dataframe(driver_standings[["Position", "Driver", "Points"]], use_container_width=True)
#         else:
#             st.warning("No driver standings available for this season.")

#     if view_option in ["Constructor Standings", "Both"]:
#         st.subheader(f"Constructor Standings {year}")
#         if constructor_standings is not None and not constructor_standings.empty:
#             constructor_standings["Points"] = pd.to_numeric(constructor_standings["Points"], errors="coerce").fillna(0)
#             constructor_standings = constructor_standings.sort_values(by="Points", ascending=False).reset_index(drop=True)
#             constructor_standings["Position"] = constructor_standings.index + 1
#             st.dataframe(constructor_standings[["Position", "Constructor", "Points"]], use_container_width=True)
#         else:
#             st.warning("No constructor standings available for this season.")

# else:
#     st.info("Click 'Load Standings' in the sidebar to fetch and display season standings.")

# # Next steps
# # - Add wins/podiums by counting finishing positions
# # - Add position change (compare vs previous round standings)
# # - Add bump chart or line chart using matplotlib or plotly
# # - Add team colors/logos for better visuals
