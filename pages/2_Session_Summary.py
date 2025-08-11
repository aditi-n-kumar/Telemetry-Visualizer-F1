import streamlit as st
import fastf1
import pandas as pd

fastf1.Cache.enable_cache('fastf1cache')

st.title("F1 Mini Race Summary")

# --- Sidebar selections ---
year = st.sidebar.selectbox("Select Year", list(range(2022, 2026)), key='year')
gp = st.sidebar.selectbox("Select Grand Prix", [
    'Australian Grand Prix', 'Chinese Grand Prix', 'Japanese Grand Prix', 'Bahrain Grand Prix', 
    'Saudi Arabian Grand Prix', 'Miami Grand Prix', 'British Grand Prix', 'Monaco Grand Prix', 
    'Italian Grand Prix', 'Singapore Grand Prix'
], key='gp')

session_type = st.sidebar.selectbox("Select Session", ['Q', 'R', 'S'], key='session_type')

# --- Load button ---
if st.sidebar.button("Load Session"):
    st.session_state['session_loaded'] = False  # reset first

    with st.spinner("Loading session..."):
        try:
            session = fastf1.get_session(st.session_state.year, st.session_state.gp, st.session_state.session_type)
            session.load()
            st.session_state['session'] = session
            st.session_state['session_loaded'] = True
            st.success("Session loaded!")
        except Exception as e:
            st.error(f"Failed to load session: {e}")
            st.session_state['session_loaded'] = False

# --- If session is loaded, continue ---
if st.session_state.get('session_loaded', False):
    session = st.session_state['session']
    results = session.results

    summary_df = results[['Position', 'GridPosition', 'Abbreviation', 'FullName', 'Time', 'Status', 'TeamName']].copy()
    # Fill missing values to prevent blank rows while keeping all drivers
    summary_df['Position'] = summary_df['Position'].fillna('—')
    summary_df['GridPosition'] = summary_df['GridPosition'].fillna('—')
    summary_df['Abbreviation'] = summary_df['Abbreviation'].fillna('—')
    summary_df['FullName'] = summary_df['FullName'].fillna('Unknown')
    summary_df['Time'] = summary_df['Time'].fillna('—')
    summary_df['Status'] = summary_df['Status'].fillna('Unknown')
    summary_df['TeamName'] = summary_df['TeamName'].fillna('—')

    summary_df['Positions Gained'] = summary_df['GridPosition'] - summary_df['Position']

    def format_time(t):
        try:
            return str(t)
        except:
            return t

    summary_df['TimeFormatted'] = summary_df['Time'].apply(format_time)
    # summary_df = summary_df.sort_values('Position')
    # Custom sort: numeric positions first, others after
    summary_df['SortOrder'] = summary_df['Position'].apply(lambda x: int(x) if str(x).isdigit() else 999)
    summary_df = summary_df.sort_values('SortOrder').drop(columns='SortOrder')


    # team_colors = {
    #     'Mercedes': '#00D2BE',
    #     'Red Bull': '#1E41FF',
    #     'Ferrari': '#DC0000',
    #     'McLaren': '#FF8700',
    #     'Alpine': '#0090FF',
    #     'Aston Martin': '#006F62',
    #     'Williams': '#005AFF',
    #     'AlphaTauri': '#2B4562',
    #     'Alfa Romeo': '#900000',
    #     'Haas': '#B6BABD',
    # }

    team_colors = {
    'Mercedes': '#00D2BE',
    'Mercedes AMG Petronas Motorsport': '#00D2BE',
    
    'Red Bull': '#1E41FF',
    'Red Bull Racing': '#1E41FF',
    'Red Bull Racing Honda RBPT': '#1E41FF',
    
    'Ferrari': '#DC0000',
    'Scuderia Ferrari': '#DC0000',
    
    'McLaren': '#FF8700',
    'McLaren Mercedes': '#FF8700',
    
    'Alpine': '#0090FF',
    'Alpine Renault': '#0090FF',
    'Renault': '#FFD700',
    
    'Aston Martin': '#006F62',
    'Aston Martin Aramco Mercedes': '#006F62',
    'Racing Point': '#F596C8',
    'Force India': '#F596C8',
    
    'Williams': '#005AFF',
    
    'AlphaTauri': '#2B4562',
    'RB Honda RBPT': '#2B4562',
    'Toro Rosso': '#2B4562',
    
    'Alfa Romeo': '#900000',
    'Sauber': "#12B709",
    'Kick Sauber Ferrari': "#12B709",
    'Stake F1 Team Kick Sauber': "#12B709",
    
    'Haas': '#B6BABD',
    'Haas Ferrari': '#B6BABD',
    
    # Older teams
    'Lotus': '#FFB800',
    'Caterham': '#006F62',
    'Manor': '#FF0000',
}

    def color_team(row):
        color = team_colors.get(row['TeamName'], '#FFFFFF')
        return [f'background-color: {color}; color: white;' for _ in row]

    st.subheader(f"Race Results Summary - {gp} {year}")
    st.dataframe(summary_df.style.apply(color_team, axis=1))

else:
    st.info("Select session details and click 'Load Session' to view race summary.")


# import streamlit as st
# import fastf1
# import pandas as pd

# fastf1.Cache.enable_cache('fastf1cache')

# st.title("F1 Mini Race Summary")

# # Sidebar: Session selection
# year = st.sidebar.selectbox("Select Year", list(range(2022, 2026)))
# gp = st.sidebar.selectbox("Select Grand Prix", [
#     'Australian Grand Prix', 'Chinese Grand Prix', 'Japanese Grand Prix', 'Bahrain Grand Prix', 
#     'Saudi Arabian Grand Prix', 'Miami Grand Prix', 'British Grand Prix', 'Monaco Grand Prix', 'Italian Grand Prix', 
#     'Singapore Grand Prix'
# ])
# session_type = st.sidebar.selectbox("Select Session", ['Q', 'R', 'S'])  # Qualifying, Race, Sprint

# @st.cache_data
# def load_session(year, gp, session_type):
#     session = fastf1.get_session(year, gp, session_type)
#     session.load()
#     return session

# session = load_session(year, gp, session_type)

# results = session.results

# # Clean up and select key columns
# summary_df = results[['Position', 'GridPosition', 'Abbreviation', 'FullName', 'Time', 'Status', 'TeamName']].copy()

# # Calculate positions gained or lost
# summary_df['Positions Gained'] = summary_df['GridPosition'] - summary_df['Position']

# # Fix times: if 'Time' is a timedelta, convert to seconds or format nicely
# def format_time(t):
#     try:
#         # timedelta to string in mm:ss.sss format
#         return str(t)
#     except:
#         return t

# summary_df['TimeFormatted'] = summary_df['Time'].apply(format_time)

# # Sort by finishing position
# summary_df = summary_df.sort_values('Position')

# team_colors = {
#     'Mercedes': '#00D2BE',
#     'Red Bull': '#1E41FF',
#     'Ferrari': '#DC0000',
#     'McLaren': '#FF8700',
#     'Alpine': '#0090FF',
#     'Aston Martin': '#006F62',
#     'Williams': '#005AFF',
#     'AlphaTauri': '#2B4562',
#     'Alfa Romeo': '#900000',
#     'Haas': '#B6BABD',
#     # Add others as needed
# }

# def color_team(row):
#     color = team_colors.get(row['TeamName'], '#FFFFFF')
#     return [f'background-color: {color}; color: white;' for _ in row]

# st.subheader(f"Race Results Summary - {gp} {year}")
# st.dataframe(summary_df.style.apply(color_team, axis=1))

