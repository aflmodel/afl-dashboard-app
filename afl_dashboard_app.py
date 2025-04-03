import streamlit as st
import pandas as pd
from datetime import datetime

# Set page layout and background colors
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .stApp {
        background-color: #FFF8F0;
    }
    section[data-testid="stSidebar"] {
        background-color: #eaf6ff;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 0. Weather Forecast Function
# ----------------------------------------------------
def get_weather_forecast(city, game_date, api_key):
    import requests
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()

        if "list" not in data:
            return "Weather data unavailable"

        for forecast in data["list"]:
            dt_txt = forecast["dt_txt"]
            forecast_date = pd.to_datetime(dt_txt).date()
            if forecast_date == game_date:
                temp = forecast["main"]["temp"]
                desc = forecast["weather"][0]["description"]
                return f"{temp:.1f}°C, {desc.capitalize()} – {game_date.strftime('%B %d')} · {city}"

        return f"Forecast not found – {game_date.strftime('%B %d')} · {city}"

    except Exception as e:
        return f"Weather fetch failed: {e}"

# ----------------------------------------------------
# 1. Mapping: Full Game Name -> Actual Sheet Name
# ----------------------------------------------------
game_name_mapping = {
    "Collingwood VS Carlton": "Collingwood VS Carlton",
    "Geelong VS Melbourne": "Geelong VS Melbourne",
    "Gold Coast VS Adelaide": "Gold Coast VS Adelaide",
    "Richmond VS Brisbane Lions": "Richmond VS Brisbane Lions",
    "North Melbourne VS Sydney": "North Melbourne VS Sydney",
    "Greater Western Sydney VS West Coast": "Greater Western Sydney VS West",  # truncated
    "Port Adelaide VS St Kilda": "Port Adelaide VS St Kilda",
    "Fremantle VS Western Bulldogs": "Fremantle VS Western Bulldogs"
}
game_names = list(game_name_mapping.keys())

# ----------------------------------------------------
# 2. Game Info Mapping
# ----------------------------------------------------
game_info_mapping = {
    "Collingwood VS Carlton": {
        "round": 4, "home": "Collingwood", "home_percent": "68%", "away": "Carlton", "away_percent": "37%", "date": datetime(2024, 4, 3).date(), "city": "Melbourne"
    },
    # ... repeat for all other games
    "Fremantle VS Western Bulldogs": {
        "round": 4, "home": "Fremantle", "home_percent": "63%", "away": "Western Bulldogs", "away_percent": "43%", "date": datetime(2024, 4, 7).date(), "city": "Perth"
    }
}

# ----------------------------------------------------
# 3. Sidebar Layout
# ----------------------------------------------------
st.sidebar.image("logo.png", use_container_width=True)
selected_game = st.sidebar.selectbox("Select a game", game_names)
st.sidebar.markdown("---")
st.sidebar.markdown("☕️ **Support the project**")
st.sidebar.markdown("[Buy me a coffee](https://www.buymeacoffee.com/aflmodel)")

# ----------------------------------------------------
# 4. Load Excel Sheet
# ----------------------------------------------------
excel_file = "Export.xlsx"
sheet_name = game_name_mapping[selected_game]
df_sheet = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
game_info = game_info_mapping[selected_game]

# ----------------------------------------------------
# 5. Extract Data Tables
# ----------------------------------------------------
home_ags = df_sheet.iloc[3:8, 1:5]
away_ags = df_sheet.iloc[3:8, 8:12]
home_2plus = df_sheet.iloc[10:15, 1:5]
away_2plus = df_sheet.iloc[10:15, 8:12]
home_3plus = df_sheet.iloc[17:22, 1:5]
away_3plus = df_sheet.iloc[17:22, 8:12]

home_ags.columns = ["Players", "Edge", "AGS Odds", f"VS {game_info['away']}"]
away_ags.columns = ["Players", "Edge", "AGS Odds", f"VS {game_info['home']}"]
home_2plus.columns = ["Players", "Edge", "2+ Odds", f"VS {game_info['away']}"]
away_2plus.columns = ["Players", "Edge", "2+ Odds", f"VS {game_info['home']}"]
home_3plus.columns = ["Players", "Edge", "3+ Odds", f"VS {game_info['away']}"]
away_3plus.columns = ["Players", "Edge", "3+ Odds", f"VS {game_info['home']}"]

# ----------------------------------------------------
# 6. Table Styling Function
# ----------------------------------------------------
def style_table(df, odds_col, vs_col):
    return df.style.format({
        "Edge": lambda x: f"{x*100:.2f}%" if pd.notnull(x) else "",
        odds_col: lambda x: f"${x:.2f}" if pd.notnull(x) else "",
        vs_col: lambda x: f"{x*100:.2f}%" if pd.notnull(x) else ""
    })

# ----------------------------------------------------
# 7. Tabs and Display
# ----------------------------------------------------
dashboard_tab = st.radio("Select dashboard", ["Goalscorer", "Disposals"], horizontal=True)
st.title("AFL Edge Dashboard")

# Weather
api_key = st.secrets["openweather_api_key"]
weather_line = get_weather_forecast(game_info["city"], game_info["date"], api_key)

# Game Info + Forecast
st.markdown(f"### **Round {game_info['round']}: {game_info['home']} VS {game_info['away']}**")
st.markdown(f"**Game Day Forecast:** {weather_line}")
col_left, col_right = st.columns(2)
col_left.markdown(f"**{game_info['home']}:** {game_info['home_percent']}")
col_right.markdown(f"**{game_info['away']}:** {game_info['away_percent']}")
st.write("---")

# ----------------------------------------------------
# Goalscorer Dashboard
# ----------------------------------------------------
if dashboard_tab == "Goalscorer":
    st.subheader("Anytime Goal Scorer (AGS)")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(game_info["home"])
        st.dataframe(style_table(home_ags, "AGS Odds", f"VS {game_info['away']}"), height=215, hide_index=True)
    with col2:
        st.caption(game_info["away"])
        st.dataframe(style_table(away_ags, "AGS Odds", f"VS {game_info['home']}"), height=215, hide_index=True)

    st.subheader("2+ Goals")
    col3, col4 = st.columns(2)
    with col3:
        st.caption(game_info["home"])
        st.dataframe(style_table(home_2plus, "2+ Odds", f"VS {game_info['away']}"), height=215, hide_index=True)
    with col4:
        st.caption(game_info["away"])
        st.dataframe(style_table(away_2plus, "2+ Odds", f"VS {game_info['home']}"), height=215, hide_index=True)

    st.subheader("3+ Goals")
    col5, col6 = st.columns(2)
    with col5:
        st.caption(game_info["home"])
        st.dataframe(style_table(home_3plus, "3+ Odds", f"VS {game_info['away']}"), height=215, hide_index=True)
    with col6:
        st.caption(game_info["away"])
        st.dataframe(style_table(away_3plus, "3+ Odds", f"VS {game_info['home']}"), height=215, hide_index=True)

# ----------------------------------------------------
# Disposals Tab
# ----------------------------------------------------
elif dashboard_tab == "Disposals":
    st.subheader("Disposals Dashboard")
    st.info("This section will display player disposals once integrated.")
