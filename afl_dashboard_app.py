# ----------------------------------------------------
# AFL EDGE DASHBOARD – Streamlit App
# ----------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime
import requests
st.set_page_config(
    page_title="THE MODEL | Built for Punters",
    page_icon="favicon.png",  # <- your custom icon here
    layout="wide"
)

# ----------------------------------------------------
# 0. Page Setup & Styling
# ----------------------------------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #FFF8F0;
    }

    section[data-testid="stSidebar"] {
        background-color: #faf9f6;
    }

    /* Better fix for long selectbox dropdowns */
    div[role="listbox"] {
        max-height: 400px !important;
        overflow-y: auto !important;
    }

    /* Ensure table cell and header content is centered */
    th, td {
        text-align: center !important;
        vertical-align: middle !important;
    }

    /* Optional: tweak the dropdown font size or spacing */
    .css-1wa3eu0 {
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)





# ----------------------------------------------------
# 1. Weather Forecast Function
# ----------------------------------------------------
def get_weather_forecast(city, game_date):
    try:
        # Try to access secret (only works on Streamlit Cloud)
        api_key = st.secrets["openweather_api_key"]
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()

        if "list" not in data:
            return f"Weather data unavailable – {game_date.strftime('%B %d')} · {city}"

        for forecast in data["list"]:
            dt_txt = forecast["dt_txt"]
            forecast_date = pd.to_datetime(dt_txt).date()
            if forecast_date == game_date:
                temp = forecast["main"]["temp"]
                desc = forecast["weather"][0]["description"]
                emoji = "☀️" if "clear" in desc else "🌧️" if "rain" in desc else "🌤️"
                return f"{emoji} {temp:.1f}°C, {desc.capitalize()} – {game_date.strftime('%B %d')} · {city}"

        return f"{game_date.strftime('%B %d')} · {city} (forecast not found)"

    except Exception:
        # Local fallback for testing
        return f"🌤️ 21°C, Partly Cloudy – {game_date.strftime('%B %d')} · {city}"

# ----------------------------------------------------
# 2. Load Game Info from Excel
# ----------------------------------------------------
excel_file = "Export.xlsx"
xls = pd.ExcelFile(excel_file)
sheet_names = xls.sheet_names

game_name_mapping = {}
game_info_mapping = {}

for sheet in sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet, header=None)
    try:
        matchup = df.iloc[0, 1]  # B1
        date = df.iloc[1, 3]     # D2
        city = df.iloc[1, 4]     # E2
        home_percent = df.iloc[1, 2]  # C2
        away_percent = df.iloc[1, 11] # L2

        if isinstance(matchup, str) and "VS" in matchup:
            game_name = matchup.strip()
            game_name_mapping[game_name] = sheet
            home, away = [x.strip() for x in game_name.split("VS")]

            game_info_mapping[game_name] = {
                "round": 4,
                "home": home,
                "away": away,
                "home_percent": f"{float(home_percent) * 100:.0f}%" if pd.notnull(home_percent) else "??",
                "away_percent": f"{float(away_percent) * 100:.0f}%" if pd.notnull(away_percent) else "??",
                "date": pd.to_datetime(date).date() if pd.notnull(date) else None,
                "city": str(city).strip(),
                "weather_city": "Melbourne" if str(city).strip().lower() == "marvel" else str(city).strip()

            }
    except Exception as e:
        print(f"Error processing {sheet}: {e}")

# ----------------------------------------------------
# 3. Sidebar Layout
# ----------------------------------------------------
import streamlit.components.v1 as components

with st.sidebar:
    # Logo
    st.image("logo.png", use_container_width=True)

    # Game dropdown
    selected_game = st.selectbox("Select a game", list(game_name_mapping.keys()))

    # Support section
    st.markdown("---")
    st.markdown("🎯 **Support The Model**")
    st.markdown("💖 [Become a Patron](https://www.patreon.com/The_Model)")
    st.markdown("☕️ [Buy me a coffee](https://www.buymeacoffee.com/aflmodel)")

    # Email section
    st.markdown("---")
    st.markdown("📬 **Stay in touch**")
    st.caption("Join the mailing list to get notified when each round goes live.")

    components.iframe(
        "https://tally.so/embed/3E6VNo?alignLeft=1&hideTitle=1&hideDescription=1&transparentBackground=1&dynamicHeight=1",
        height=130,
        scrolling=False
    )




# ----------------------------------------------------
# 4. Load Selected Game Data
# ----------------------------------------------------
sheet_name = game_name_mapping[selected_game]
game_info = game_info_mapping[selected_game]
df_sheet = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)

# AGS Section
home_ags  = df_sheet.iloc[3:8, 1:5]
away_ags  = df_sheet.iloc[3:8, 8:12]

# 2+ Goals
home_2plus = df_sheet.iloc[10:15, 1:5]
away_2plus = df_sheet.iloc[10:15, 8:12]

# 3+ Goals
home_3plus = df_sheet.iloc[17:22, 1:5]
away_3plus = df_sheet.iloc[17:22, 8:12]

# Rename columns
home_ags.columns = ["Players", "Edge", "AGS Odds", f"VS {game_info['away']}"]
away_ags.columns = ["Players", "Edge", "AGS Odds", f"VS {game_info['home']}"]
home_2plus.columns = ["Players", "Edge", "2+ Odds", f"VS {game_info['away']}"]
away_2plus.columns = ["Players", "Edge", "2+ Odds", f"VS {game_info['home']}"]
home_3plus.columns = ["Players", "Edge", "3+ Odds", f"VS {game_info['away']}"]
away_3plus.columns = ["Players", "Edge", "3+ Odds", f"VS {game_info['home']}"]

# ----------------------------------------------------
# 5. Styling Function
# ----------------------------------------------------

def highlight_positive_edge(row):
    edge = row["Edge"]
    if pd.notnull(edge):
        if edge > 0:
            return ["background-color: #e9f9ec"] * len(row)  # light green
        else:
            return ["background-color: #faeaea"] * len(row)  # light red
    else:
        return [""] * len(row)


def style_table(df, odds_col, vs_col):
    return (
        df.style
        .format({
            "Edge": lambda x: f"{x*100:.2f}%" if pd.notnull(x) and isinstance(x, (int, float)) else x,
            odds_col: lambda x: f"${x:.2f}" if pd.notnull(x) and isinstance(x, (int, float)) else x,
            vs_col: lambda x: x  # emoji or text
        })
        .apply(highlight_positive_edge, axis=1)
        .set_table_styles([
            {"selector": f"td.col{df.columns.get_loc(vs_col)}", "props": [("text-align", "center")]}
        ], overwrite=False)
    )



# ----------------------------------------------------
# 6. Dashboard Layout
# ----------------------------------------------------

dashboard_tab = st.radio("Select dashboard", ["Goalscorer", "Disposals"], horizontal=True)
st.title("AFL Dashboard")

# Game Title
st.markdown(f"### **Round {game_info['round']}: {game_info['home']} VS {game_info['away']}**")

# Weather Forecast Setup
api_key = st.secrets["openweather_api_key"]
venue_display = (
    "Melbourne (Marvel Stadium)" if game_info["city"].lower() == "marvel"
    else game_info["city"]
)

try:
    if (game_info["date"] - datetime.today().date()).days <= 5:
        raw_forecast = get_weather_forecast(game_info["weather_city"], game_info["date"], api_key)

        if isinstance(raw_forecast, str):
            desc = raw_forecast.lower()
            emoji = "☀️" if "clear" in desc else "🌧️" if "rain" in desc else "🌤️"

            if "·" in raw_forecast:
                weather_line = f"{emoji} " + raw_forecast.rsplit("·", 1)[0] + f"· {venue_display}"
            else:
                weather_line = f"{emoji} " + raw_forecast
        else:
            weather_line = f"{game_info['date'].strftime('%B %d')} · {venue_display} (forecast unavailable)"
    else:
        weather_line = f"{game_info['date'].strftime('%B %d')} · {venue_display} (too far ahead)"
except Exception:
    weather_line = f"Weather unavailable – {venue_display}"

# Display the weather forecast
st.markdown(weather_line)

# Divider
st.markdown("---")



# ----------------------------------------------------
# 7. Goalscorer Dashboard
# ----------------------------------------------------
if dashboard_tab == "Goalscorer":
    st.subheader("Anytime Goal Scorer")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(game_info["home"])
        st.dataframe(style_table(home_ags, "AGS Odds", f"VS {game_info['away']}"), height=218, hide_index=True)
    with col2:
        st.caption(game_info["away"])
        st.dataframe(style_table(away_ags, "AGS Odds", f"VS {game_info['home']}"), height=218, hide_index=True)

    st.subheader("2+ Goals")
    col3, col4 = st.columns(2)
    with col3:
        st.caption(game_info["home"])
        st.dataframe(style_table(home_2plus, "2+ Odds", f"VS {game_info['away']}"), height=218, hide_index=True)
    with col4:
        st.caption(game_info["away"])
        st.dataframe(style_table(away_2plus, "2+ Odds", f"VS {game_info['home']}"), height=218, hide_index=True)

    st.subheader("3+ Goals")
    col5, col6 = st.columns(2)
    with col5:
        st.caption(game_info["home"])
        st.dataframe(style_table(home_3plus, "3+ Odds", f"VS {game_info['away']}"), height=218, hide_index=True)
    with col6:
        st.caption(game_info["away"])
        st.dataframe(style_table(away_3plus, "3+ Odds", f"VS {game_info['home']}"), height=218, hide_index=True)

# ----------------------------------------------------
# 8. Disposals Tab 
# ----------------------------------------------------
elif dashboard_tab == "Disposals":
    
    # Load the ExportDisposals sheet for this game
    disposals_sheet = pd.read_excel("ExportDisposals.xlsx", sheet_name=sheet_name, header=None)

    # Extract 15+, 20+, 25+ tables
    home_15 = disposals_sheet.iloc[3:8, 1:5]
    away_15 = disposals_sheet.iloc[3:8, 8:12]
    home_20 = disposals_sheet.iloc[10:15, 1:5]
    away_20 = disposals_sheet.iloc[10:15, 8:12]
    home_25 = disposals_sheet.iloc[17:22, 1:5]
    away_25 = disposals_sheet.iloc[17:22, 8:12]

    # Rename columns
    home_15.columns = ["Players", "Edge", "15+ Odds", f"VS {game_info['away']}"]
    away_15.columns = ["Players", "Edge", "15+ Odds", f"VS {game_info['home']}"]
    home_20.columns = ["Players", "Edge", "20+ Odds", f"VS {game_info['away']}"]
    away_20.columns = ["Players", "Edge", "20+ Odds", f"VS {game_info['home']}"]
    home_25.columns = ["Players", "Edge", "25+ Odds", f"VS {game_info['away']}"]
    away_25.columns = ["Players", "Edge", "25+ Odds", f"VS {game_info['home']}"]

    # 15+ Disposals
    st.subheader("15+ Disposals")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(game_info["home"])
        st.dataframe(style_table(home_15, "15+ Odds", f"VS {game_info['away']}"), height=218, hide_index=True)
    with col2:
        st.caption(game_info["away"])
        st.dataframe(style_table(away_15, "15+ Odds", f"VS {game_info['home']}"), height=218, hide_index=True)

    # 20+ Disposals
    st.subheader("20+ Disposals")
    col3, col4 = st.columns(2)
    with col3:
        st.caption(game_info["home"])
        st.dataframe(style_table(home_20, "20+ Odds", f"VS {game_info['away']}"), height=218, hide_index=True)
    with col4:
        st.caption(game_info["away"])
        st.dataframe(style_table(away_20, "20+ Odds", f"VS {game_info['home']}"), height=218, hide_index=True)

    # 25+ Disposals
    st.subheader("25+ Disposals")
    col5, col6 = st.columns(2)
    with col5:
        st.caption(game_info["home"])
        st.dataframe(style_table(home_25, "25+ Odds", f"VS {game_info['away']}"), height=218, hide_index=True)
    with col6:
        st.caption(game_info["away"])
        st.dataframe(style_table(away_25, "25+ Odds", f"VS {game_info['home']}"), height=218, hide_index=True)
