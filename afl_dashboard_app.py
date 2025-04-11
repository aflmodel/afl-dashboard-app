# ----------------------------------------------------
# AFL EDGE DASHBOARD – Streamlit App (With Debugs & Section Numbers)
# ----------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import streamlit.components.v1 as components

# 1. Page Setup
st.set_page_config(
    page_title="THE MODEL | Built for Punters",
    page_icon="favicon.png",
    layout="wide"
)
st.info("✅ App started successfully – debug marker")


# 2. Styling
st.markdown("""
    <style>
    .stApp { background-color: #FFF8F0; }
    section[data-testid="stSidebar"] { background-color: #faf9f6; }
    div[role="listbox"] { max-height: 400px !important; overflow-y: auto !important; }
    th, td { text-align: center !important; vertical-align: middle !important; }
    .css-1wa3eu0 { font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

# 3. Weather Forecast Function (With Secrets Debug)
def get_weather_forecast(city, game_date):
    try:
        try:
            api_key = st.secrets["openweather_api_key"]
        except Exception:
            return f"⚠️ Missing OpenWeather API key in secrets"

        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "list" not in data:
            return f"⚠️ Weather data unavailable – {game_date.strftime('%B %d')} · {city}"

        for forecast in data["list"]:
            dt_txt = forecast["dt_txt"]
            forecast_date = pd.to_datetime(dt_txt).date()
            if forecast_date == game_date:
                temp = forecast["main"]["temp"]
                desc = forecast["weather"][0]["description"]
                emoji = "☀️" if "clear" in desc else "🌧️" if "rain" in desc else "🌤️"
                return f"{emoji} {temp:.1f}°C, {desc.capitalize()} – {game_date.strftime('%B %d')} · {city}"

        return f"{game_date.strftime('%B %d')} · {city} (forecast not found)"
    except Exception as e:
        return f"⚠️ Weather fetch failed: {type(e).__name__}: {e}"

# 4. Load Game Info (With Excel Debug)
try:
    xls = pd.ExcelFile("Export.xlsx")
    sheet_names = xls.sheet_names
except Exception as e:
    st.error(f"❌ Failed to load Export.xlsx: {e}")
    st.stop()

game_name_mapping = {}
game_info_mapping = {}

for sheet in sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet, header=None)
    try:
        matchup = df.iloc[0, 1]
        date = df.iloc[1, 3]
        city = df.iloc[1, 4]
        home_percent = df.iloc[1, 2]
        away_percent = df.iloc[1, 11]

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
        st.warning(f"⚠️ Error processing sheet '{sheet}': {e}")

# 5. Sidebar Layout
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    selected_game = st.selectbox("Select a game", list(game_name_mapping.keys()))
    st.markdown("---")
    st.markdown("🎯 **Support The Model**")
    st.markdown("💖 [Become a Patron](https://www.patreon.com/The_Model)")
    st.markdown("☕️ [Buy me a coffee](https://www.buymeacoffee.com/aflmodel)")
    st.markdown("---")
    st.markdown("📬 **Stay in touch**")
    st.caption("Join the mailing list to get notified when each round goes live.")
    components.iframe(
        "https://tally.so/embed/3E6VNo?alignLeft=1&hideTitle=1&hideDescription=1&transparentBackground=1&dynamicHeight=1",
        height=130,
        scrolling=False
    )

# 6. Load Selected Game Data
sheet_name = game_name_mapping[selected_game]
game_info = game_info_mapping[selected_game]
df_sheet = pd.read_excel("Export.xlsx", sheet_name=sheet_name, header=None)

# 7. Extract AGS Tables
home_ags  = df_sheet.iloc[3:8, 1:5]
away_ags  = df_sheet.iloc[3:8, 8:12]
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

# 8. Table Styling

def highlight_positive_edge(row):
    edge = row["Edge"]
    if pd.notnull(edge):
        return ["background-color: #e9f9ec" if edge > 0 else "background-color: #faeaea"] * len(row)
    return [""] * len(row)

def style_table(df, odds_col, vs_col):
    return (
        df.style
        .format({
            "Edge": lambda x: f"{x*100:.2f}%" if pd.notnull(x) else x,
            odds_col: lambda x: f"${x:.2f}" if pd.notnull(x) else x
        })
        .apply(highlight_positive_edge, axis=1)
    )

# 9. Dashboard Layout
st.title("AFL Dashboard")
dashboard_tab = st.radio("Select dashboard", ["Goalscorer", "Disposals"], horizontal=True)
st.markdown(f"### **Round {game_info['round']}: {game_info['home']} VS {game_info['away']}**")

# Weather Display
venue_display = "Melbourne (Marvel Stadium)" if game_info["city"].lower() == "marvel" else game_info["city"]
if (game_info["date"] - datetime.today().date()).days <= 5:
    weather_line = get_weather_forecast(game_info["weather_city"], game_info["date"])
else:
    weather_line = f"{game_info['date'].strftime('%B %d')} · {venue_display} (too far ahead)"

st.markdown(weather_line)
st.markdown("---")

# 10. Goalscorer Tables
if dashboard_tab == "Goalscorer":
    for label, home_df, away_df, colname in [
        ("Anytime Goal Scorer", home_ags, away_ags, "AGS Odds"),
        ("2+ Goals", home_2plus, away_2plus, "2+ Odds"),
        ("3+ Goals", home_3plus, away_3plus, "3+ Odds")
    ]:
        st.subheader(label)
        col1, col2 = st.columns(2)
        with col1:
            st.caption(game_info["home"])
            st.dataframe(style_table(home_df, colname, f"VS {game_info['away']}"), height=218, hide_index=True)
        with col2:
            st.caption(game_info["away"])
            st.dataframe(style_table(away_df, colname, f"VS {game_info['home']}"), height=218, hide_index=True)

# 11. Disposals Tables
elif dashboard_tab == "Disposals":
    try:
        disp = pd.read_excel("ExportDisposals.xlsx", sheet_name=sheet_name, header=None)
        h15, a15 = disp.iloc[3:8, 1:5], disp.iloc[3:8, 8:12]
        h20, a20 = disp.iloc[10:15, 1:5], disp.iloc[10:15, 8:12]
        h25, a25 = disp.iloc[17:22, 1:5], disp.iloc[17:22, 8:12]

        for df, opp in [(h15, 'away'), (a15, 'home'), (h20, 'away'), (a20, 'home'), (h25, 'away'), (a25, 'home')]:
            label = df.columns[2] = df.iloc[0, 2]  # rename middle column with first row value
        h15.columns = ["Players", "Edge", "15+ Odds", f"VS {game_info['away']}"]
        a15.columns = ["Players", "Edge", "15+ Odds", f"VS {game_info['home']}"]
        h20.columns = ["Players", "Edge", "20+ Odds", f"VS {game_info['away']}"]
        a20.columns = ["Players", "Edge", "20+ Odds", f"VS {game_info['home']}"]
        h25.columns = ["Players", "Edge", "25+ Odds", f"VS {game_info['away']}"]
        a25.columns = ["Players", "Edge", "25+ Odds", f"VS {game_info['home']}"]

        for label, home_df, away_df, colname in [
            ("15+ Disposals", h15, a15, "15+ Odds"),
            ("20+ Disposals", h20, a20, "20+ Odds"),
            ("25+ Disposals", h25, a25, "25+ Odds")
        ]:
            st.subheader(label)
            col1, col2 = st.columns(2)
            with col1:
                st.caption(game_info["home"])
                st.dataframe(style_table(home_df, colname, f"VS {game_info['away']}"), height=218, hide_index=True)
            with col2:
                st.caption(game_info["away"])
                st.dataframe(style_table(away_df, colname, f"VS {game_info['home']}"), height=218, hide_index=True)
    except Exception as e:
        st.error(f"❌ Failed to load ExportDisposals.xlsx: {e}")
