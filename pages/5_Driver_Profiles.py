import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Driver Profiles", layout="wide")
st.title("🏎️ Driver Profiles")

# Sidebar
st.sidebar.header("Driver Selector")
driver_id = st.sidebar.text_input("Enter Driver ID (e.g., verstappen, hamilton, alonso):", "verstappen")

# Fetch driver info from Ergast API
driver_url = f"https://ergast.com/api/f1/drivers/{driver_id}.json"
driver_response = requests.get(driver_url).json()
driver_data = driver_response["MRData"]["DriverTable"]["Drivers"][0]

# Basic info
name = f"{driver_data['givenName']} {driver_data['familyName']}"
nationality = driver_data["nationality"]
dob = driver_data["dateOfBirth"]

# Fetch constructor history
constructors_url = f"https://ergast.com/api/f1/drivers/{driver_id}/constructors.json?limit=100"
constructors_response = requests.get(constructors_url).json()
constructors = [c["name"] for c in constructors_response["MRData"]["ConstructorTable"]["Constructors"]]

# Fetch race wins (results where position = 1)
wins_url = f"https://ergast.com/api/f1/drivers/{driver_id}/results/1.json?limit=1000"
wins_response = requests.get(wins_url).json()
wins = wins_response["MRData"]["total"]

# Fetch championship count
titles_url = "https://ergast.com/api/f1/driverStandings/1.json?limit=1000"
titles_response = requests.get(titles_url).json()
titles = 0
for record in titles_response["MRData"]["StandingsTable"]["StandingsLists"]:
    for standing in record["DriverStandings"]:
        if standing["Driver"]["driverId"] == driver_id:
            titles += 1

# Display
st.header(name)
st.subheader(f"🇨🇭 Nationality: {nationality}")
st.write(f"🎂 Born: {dob}")
st.write(f"🏆 Championships: {titles}")
st.write(f"🥇 Race Wins: {wins}")
st.write(f"🏎️ Teams Raced For: {', '.join(constructors)}")

# Optional: Show detailed wins table
if st.checkbox("Show win details"):
    wins_list = []
    for race in wins_response["MRData"]["RaceTable"]["Races"]:
        wins_list.append({
            "Season": race["season"],
            "Race": race["raceName"],
            "Team": race["Results"][0]["Constructor"]["name"],
            "Date": race["date"]
        })
    wins_df = pd.DataFrame(wins_list)
    st.dataframe(wins_df)
