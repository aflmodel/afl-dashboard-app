import streamlit as st
import pandas as pd

# Set the page layout to wide
st.set_page_config(layout="wide")

# ----------------------------------------------------
# 1. Mapping: Full Game Name -> Actual Sheet Name
# ----------------------------------------------------
game_name_mapping = {
    "Essendon VS Port Adelaide": "Essendon VS Port Adelaide",
    "Carlton VS Western Bulldogs": "Carlton VS Western Bulldogs",
    "Melbourne VS Gold Coast": "Melbourne VS Gold Coast",
    "St Kilda VS Richmond": "St Kilda VS Richmond",
    "Brisbane Lions VS Geelong": "Brisbane Lions VS Geelong",
    "Hawthorn VS Greater Western Sydney": "Hawthorn VS Greater Western Syd",  # truncated in Excel
    "Adelaide VS North Melbourne": "Adelaide VS North Melbourne",
    "West Coast VS Fremantle": "West Coast VS Fremantle"
}
game_names = list(game_name_mapping.keys())

# ----------------------------------------------------
# 2. Extra Game Info (Round, Team Names, Percentages)
# ----------------------------------------------------
game_info_mapping = {
    "Essendon VS Port Adelaide": {
        "round": 3,
        "home": "Essendon",
        "home_percent": "44%",
        "away": "Port Adelaide",
        "away_percent": "61%"
    },
    "Carlton VS Western Bulldogs": {
        "round": 3,
        "home": "Carlton",
        "home_percent": "49%",
        "away": "Western Bulldogs",
        "away_percent": "55%"
    },
    "Melbourne VS Gold Coast": {
        "round": 3,
        "home": "Melbourne",
        "home_percent": "??",
        "away": "Gold Coast",
        "away_percent": "??"
    },
    "St Kilda VS Richmond": {
        "round": 3,
        "home": "St Kilda",
        "home_percent": "??",
        "away": "Richmond",
        "away_percent": "??"
    },
    "Brisbane Lions VS Geelong": {
        "round": 3,
        "home": "Brisbane Lions",
        "home_percent": "??",
        "away": "Geelong",
        "away_percent": "??"
    },
    "Hawthorn VS Greater Western Sydney": {
        "round": 3,
        "home": "Hawthorn",
        "home_percent": "??",
        "away": "Greater Western Sydney",
        "away_percent": "??"
    },
    "Adelaide VS North Melbourne": {
        "round": 3,
        "home": "Adelaide",
        "home_percent": "??",
        "away": "North Melbourne",
        "away_percent": "??"
    },
    "West Coast VS Fremantle": {
        "round": 3,
        "home": "West Coast",
        "home_percent": "??",
        "away": "Fremantle",
        "away_percent": "??"
    }
}

# ----------------------------------------------------
# 3. Sidebar: Game Selection
# ----------------------------------------------------
selected_game = st.sidebar.selectbox("Select a game", game_names)
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
# 8. Display the Dashboard
# ----------------------------------------------------
st.title("AFL Betting Dashboard (Example)")

st.markdown(f"### **Round {game_info['round']}: {game_info['home']} VS {game_info['away']}**")
col_perc_left, col_perc_right = st.columns(2)
with col_perc_left:
    st.markdown(f"**{game_info['home']}:** {game_info['home_percent']}")
with col_perc_right:
    st.markdown(f"**{game_info['away']}:** {game_info['away_percent']}")

st.write("---")  # Horizontal rule

# Anytime Goal Scorer (AGS)
st.subheader("Anytime Goal Scorer (AGS)")
col1, col2 = st.columns(2)
with col1:
    st.caption(f"{game_info['home']}")
    st.dataframe(style_table(home_ags, "AGS Odds", f"VS {game_info['away']}"), height=250, hide_index=True)
with col2:
    st.caption(f"{game_info['away']}")
    st.dataframe(style_table(away_ags, "AGS Odds", f"VS {game_info['home']}"), height=250, hide_index=True)

# 2+ Goals
st.subheader("2+ Goals")
col3, col4 = st.columns(2)
with col3:
    st.caption(f"{game_info['home']}")
    st.dataframe(style_table(home_2plus, "2+ Odds", f"VS {game_info['away']}"), height=250, hide_index=True)
with col4:
    st.caption(f"{game_info['away']}")
    st.dataframe(style_table(away_2plus, "2+ Odds", f"VS {game_info['home']}"), height=250, hide_index=True)

# 3+ Goals
st.subheader("3+ Goals")
col5, col6 = st.columns(2)
with col5:
    st.caption(f"{game_info['home']}")
    st.dataframe(style_table(home_3plus, "3+ Odds", f"VS {game_info['away']}"), height=250, hide_index=True)
with col6:
    st.caption(f"{game_info['away']}")
    st.dataframe(style_table(away_3plus, "3+ Odds", f"VS {game_info['home']}"), height=250, hide_index=True)
