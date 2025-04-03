import streamlit as st
import pandas as pd
from datetime import datetime


# Set the page layout to wide
st.set_page_config(layout="wide")
# Custom page background style
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFF8F0; /* very soft orange */
    }
    section[data-testid="stSidebar"] {
        background-color: #eaf6ff;  /* pale light blue */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ----------------------------------------------------
# 1. Mapping: Full Game Name -> Actual Sheet Name
# ----------------------------------------------------
game_name_mapping = {
    "Collingwood VS Carlton": "Collingwood VS Carlton",
    "Geelong VS Melbourne": "Geelong VS Melbourne",
    "Gold Coast VS Adelaide": "Gold Coast VS Adelaide",
    "Richmond VS Brisbane Lions": "Richmond VS Brisbane Lions",
    "North Melbourne VS Sydney": "North Melbourne VS Sydney",
    "Greater Western Sydney VS West Coast": "Greater Western Sydney VS West",  # truncated in Excel
    "Port Adelaide VS St Kilda": "Port Adelaide VS St Kilda",
    "Fremantle VS Western Bulldogs": "Fremantle VS Western Bulldogs"
}
game_names = list(game_name_mapping.keys())

# ----------------------------------------------------
# 2. Extra Game Info (Round, Team Names, Percentages)
# ----------------------------------------------------
game_info_mapping = {
    "Collingwood VS Carlton": {
        "round": 4,
        "home": "Collingwood",
        "home_percent": "68%",
        "away": "Carlton",
        "away_percent": "37%"
    },
    "Geelong VS Melbourne": {
        "round": 4,
        "home": "Geelong",
        "home_percent": "83%",
        "away": "Melbourne",
        "away_percent": "22%"
    },
    "Gold Coast VS Adelaide": {
        "round": 4,
        "home": "Gold Coast",
        "home_percent": "58%",
        "away": "Adelaide",
        "away_percent": "47%"
    },
    "Richmond VS Brisbane Lions": {
        "round": 4,
        "home": "Richmond",
        "home_percent": "13%",
        "away": "Brisbane Lions",
        "away_percent": "93%"
    },
    "North Melbourne VS Sydney": {
        "round": 4,
        "home": "North Melbourne",
        "home_percent": "41%",
        "away": "Sydney",
        "away_percent": "64%"
    },
    "Greater Western Sydney VS West Coast": {
        "round": 4,
        "home": "Greater Western Sydney",
        "home_percent": "96%",
        "away": "West Coast",
        "away_percent": "9%"
    },
    "Port Adelaide VS St Kilda": {
        "round": 4,
        "home": "Port Adelaide",
        "home_percent": "65%",
        "away": "St Kilda",
        "away_percent": "40%"
    },
    "Fremantle VS Western Bulldogs": {
        "round": 4,
        "home": "Fremantle",
        "home_percent": "63%",
        "away": "Western Bulldogs",
        "away_percent": "43%"
    }
}

# ----------------------------------------------------
# 3. Sidebar
# ----------------------------------------------------

# Logo ---
st.sidebar.image("logo.png", use_container_width=True)




# Game Selection
# ----------------------------------------------------

selected_game = st.sidebar.selectbox("Select a game", game_names)
# ----------------------------------------------------
# Sidebar: BMC
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("☕️ **Support the project**")
st.sidebar.markdown(
    "[Buy me a coffee](https://www.buymeacoffee.com/aflmodel)"
)

sheet_name = game_name_mapping[selected_game]
game_info = game_info_mapping.get(selected_game, {
    "round": "??", "home": "Home", "home_percent": "??", "away": "Away", "away_percent": "??"
})

# ----------------------------------------------------
# 4. Load the Excel Sheet (No Header, so we assign our own later)
# ----------------------------------------------------
excel_file = "Export.xlsx"
# header=None prevents pandas from treating the first row as column names.

df_sheet = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)

# ----------------------------------------------------
# 5. Extract Tables Based on Your Updated Coordinates
# ----------------------------------------------------
# AGS Section:
#   Home: starts at B4 -> Excel row 4 (index 3), column B (index 1) through E (index 1:5), 5 rows (3:8)
home_ags  = df_sheet.iloc[3:8, 1:5]
#   Away: starts at I4 -> Excel row 4 (index 3), column I (index 8) through L (8:12), 5 rows
away_ags  = df_sheet.iloc[3:8, 8:12]

# 2+ Goals Section:
#   Home: starts at B11 -> Excel row 11 (index 10), columns B to E (indices 1 to 5), 5 rows
home_2plus = df_sheet.iloc[10:15, 1:5]
#   Away: starts at I11 -> Excel row 11 (index 10), columns I to L (indices 8 to 12), 5 rows
away_2plus = df_sheet.iloc[10:15, 8:12]

# 3+ Goals Section:
#   Home: starts at B18 -> Excel row 18 (index 17), columns B to E (indices 1 to 5), 5 rows
home_3plus = df_sheet.iloc[17:22, 1:5]
#   Away: starts at I18 -> Excel row 18 (index 17), columns I to L (indices 8 to 12), 5 rows
away_3plus = df_sheet.iloc[17:22, 8:12]

# ----------------------------------------------------
# 6. Option A: Manually Rename Columns
# ----------------------------------------------------
home_ags.columns = ["Players", "Edge", "AGS Odds", f"VS {game_info['away']}"]
away_ags.columns = ["Players", "Edge", "AGS Odds", f"VS {game_info['home']}"]

home_2plus.columns = ["Players", "Edge", "2+ Odds", f"VS {game_info['away']}"]
away_2plus.columns = ["Players", "Edge", "2+ Odds", f"VS {game_info['home']}"]

home_3plus.columns = ["Players", "Edge", "3+ Odds", f"VS {game_info['away']}"]
away_3plus.columns = ["Players", "Edge", "3+ Odds", f"VS {game_info['home']}"]

# ----------------------------------------------------
# 7. Define a Function to Style Tables
# ----------------------------------------------------
def style_table(df, odds_col, vs_col):
    """
    Formats:
      - "Edge" and vs columns as percentages (x100, 2 decimals)
      - Odds columns as currency (2 decimals)
    """
    return df.style.format({
        "Edge": lambda x: f"{x*100:.2f}%" if pd.notnull(x) else "",
        odds_col: lambda x: f"${x:.2f}" if pd.notnull(x) else "",
        vs_col: lambda x: f"{x*100:.2f}%" if pd.notnull(x) else ""
    })

# ----------------------------------------------------
# 8. Select Dashboard Tab (Goalscorer or Disposals)
# ----------------------------------------------------
dashboard_tab = st.radio("Select dashboard", ["Goalscorer", "Disposals"], horizontal=True)

# ----------------------------------------------------
# 9. Display Selected Dashboard
# ----------------------------------------------------
st.title("AFL Edge Dashboard")

# Fetch API key securely
api_key = st.secrets["openweather_api_key"]

# Get weather forecast
weather_line = get_weather_forecast(game_info["city"], game_info["date"], api_key)

# Game day forecast
st.markdown(f"**Game Day Forecast:** {weather_line}")

# Game title
st.markdown(f"### **Round {game_info['round']}: {game_info['home']} VS {game_info['away']}**")

# Game day forecast
st.markdown(f"**Game Day Forecast:** {weather_line}")

col_perc_left, col_perc_right = st.columns(2)
with col_perc_left:
    st.markdown(f"**{game_info['home']}:** {game_info['home_percent']}")
with col_perc_right:
    st.markdown(f"**{game_info['away']}:** {game_info['away_percent']}")

st.write("---")  # Horizontal rule



# ----------------------------------------------------
# Show GOALSCORER Dashboard
# ----------------------------------------------------
if dashboard_tab == "Goalscorer":
    st.subheader("Anytime Goal Scorer (AGS)")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"{game_info['home']}")
        st.dataframe(style_table(home_ags, "AGS Odds", f"VS {game_info['away']}"), height=215, hide_index=True)
    with col2:
        st.caption(f"{game_info['away']}")
        st.dataframe(style_table(away_ags, "AGS Odds", f"VS {game_info['home']}"), height=215, hide_index=True)

    st.subheader("2+ Goals")
    col3, col4 = st.columns(2)
    with col3:
        st.caption(f"{game_info['home']}")
        st.dataframe(style_table(home_2plus, "2+ Odds", f"VS {game_info['away']}"), height=215, hide_index=True)
    with col4:
        st.caption(f"{game_info['away']}")
        st.dataframe(style_table(away_2plus, "2+ Odds", f"VS {game_info['home']}"), height=215, hide_index=True)

    st.subheader("3+ Goals")
    col5, col6 = st.columns(2)
    with col5:
        st.caption(f"{game_info['home']}")
        st.dataframe(style_table(home_3plus, "3+ Odds", f"VS {game_info['away']}"), height=215, hide_index=True)
    with col6:
        st.caption(f"{game_info['away']}")
        st.dataframe(style_table(away_3plus, "3+ Odds", f"VS {game_info['home']}"), height=215, hide_index=True)

# ----------------------------------------------------
# Show DISPOSALS Dashboard (Coming Soon)
# ----------------------------------------------------
elif dashboard_tab == "Disposals":
    st.subheader("Disposals Dashboard")
    st.info("This section will display player disposals once integrated.")
