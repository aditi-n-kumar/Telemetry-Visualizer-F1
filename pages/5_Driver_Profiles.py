import fastf1
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Driver Profiles", layout="wide")
st.title("Driver Profiles")

fastf1.Cache.enable_cache("fastf1cache")

# --- Sidebar controls ---
year_options = list(range(2018, 2026))
selected_year = st.sidebar.selectbox("Select Season", year_options, index=year_options.index(2024))
load_profiles = st.sidebar.button("Load Profiles")

# --- Session state ---
if "session_loaded" not in st.session_state:
    st.session_state.session_loaded = False
if "teams" not in st.session_state:
    st.session_state.teams = []
if "driver_meta" not in st.session_state:
    st.session_state.driver_meta = {}
if "selected_team" not in st.session_state:
    st.session_state.selected_team = None

# --- Load session when button pressed ---
if load_profiles:
    with st.spinner(f"Loading {selected_year} driver and team data..."):
        try:
            # Try Bahrain first, fallback to Melbourne
            try:
                session = fastf1.get_session(selected_year, "Bahrain", "R")
                session.load()
            except Exception:
                session = fastf1.get_session(selected_year, "Melbourne", "R")
                session.load()

            drivers = session.drivers
            teams = set()
            driver_meta = {}

            for d in drivers:
                info = session.get_driver(d)
                team = info.get("TeamName", "Unknown")
                teams.add(team)
                driver_meta[d] = info

            st.session_state.teams = sorted(list(teams))
            st.session_state.driver_meta = driver_meta
            st.session_state.session_loaded = True
            st.session_state.selected_team = st.session_state.teams[0] if st.session_state.teams else None
            st.rerun()

        except Exception as e:
            st.sidebar.error(f"Failed to load FastF1 session: {e}")
            st.session_state.session_loaded = False

# --- Sidebar: team buttons ---
st.sidebar.subheader("Teams")

if not st.session_state.session_loaded:
    st.sidebar.caption("Click 'Load Profiles' first to show available teams.")
else:
    for team in st.session_state.teams:
        if st.sidebar.button(team, key=f"team_{team}"):
            st.session_state.selected_team = team
            st.rerun()

# --- Main display ---
if not st.session_state.session_loaded:
    st.info("Choose a season and click **Load Profiles** to populate teams and drivers.")
else:
    team = st.session_state.selected_team
    driver_meta = st.session_state.driver_meta
    drivers_in_team = [d for d, m in driver_meta.items() if m.get("TeamName") == team]

    st.header(f"{selected_year} — {team}")

    if not drivers_in_team:
        st.warning("No drivers found for this team.")
    else:
        cols = st.columns(len(drivers_in_team))
        for col, d in zip(cols, drivers_in_team):
            info = driver_meta.get(d, {})
            name = info.get("FullName", f"{info.get('FirstName','')} {info.get('LastName','')}".strip())
            nationality = info.get("CountryCode", "N/A")

            with col:
                st.subheader(name)
                st.write(f"🏳️ Nationality: {nationality}")
                st.write(f"🏎️ Team: {team}")




# ---------------------
# import fastf1
# import streamlit as st
# import pandas as pd

# st.set_page_config(page_title="Driver Profiles", layout="wide")
# st.title("Driver Profiles")

# fastf1.Cache.enable_cache("fastf1cache")

# # Sidebar: only year and team dropdowns
# year_options = list(range(2018, 2026))
# selected_year = st.sidebar.selectbox("Select Season", year_options, index=year_options.index(2024))

# # Load a single session (kept as Bahrain race as before)
# with st.spinner(f"Loading session for {selected_year} — this may take a moment..."):
#     session = fastf1.get_session(selected_year, "Bahrain", "R")
#     session.load()

# # Build teams list from session drivers
# drivers = session.drivers
# team_set = set()
# driver_meta = {}
# for d in drivers:
#     info = session.get_driver(d)
#     team = info.get("TeamName", "Unknown")
#     team_set.add(team)
#     driver_meta[d] = info

# team_names = sorted(team_set)
# if not team_names:
#     st.sidebar.error("No teams found for this session.")
# else:
#     selected_team = st.sidebar.selectbox("Select Team", team_names)

# # Main area: show drivers for selected team side-by-side
# st.header(f"{selected_year} — {selected_team}")

# drivers_in_team = [d for d, m in driver_meta.items() if m.get("TeamName") == selected_team]

# if not drivers_in_team:
#     st.info("No drivers found for the selected team.")
# else:
#     cols = st.columns(len(drivers_in_team))
#     for col, d in zip(cols, drivers_in_team):
#         info = driver_meta[d]
#         name = info.get("FullName", d)
#         team = info.get("TeamName", "N/A")
#         country = info.get("CountryCode", "N/A")
#         with col:
#             st.header(name)
#             st.subheader(f"Team: {team}")
#             st.write(f"Country: {country}")








