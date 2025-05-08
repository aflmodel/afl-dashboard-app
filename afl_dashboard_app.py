# team_stats_local.py

import streamlit as st
import pandas as pd
import os, io, base64
from datetime import datetime
import requests
import streamlit.components.v1 as components
from PIL import Image

# ————— CONFIG —————
EXPORT_FILE    = "Export.xlsx"
SUMMARY_FILE   = "upcoming_round_summary.xlsx"
SHEET_OVERALL  = "Overall_Last5"
SHEET_VENUE    = "Venue_Last5"

TICK, CROSS    = "✅", "❌"
UP_ARROW       = "&#9650;"
DN_ARROW       = "&#9660;"
ARROW_UP_HTML  = f'<span style="color:purple;">{UP_ARROW}</span>'
ARROW_DN_HTML  = f'<span style="color:orange;">{DN_ARROW}</span>'
VERT_BORDER    = "1px solid rgba(0,0,0,0.2)"
HORIZ_BORDER   = "1px solid rgba(0,0,0,0.2)"
# ——————————————————

@st.cache_data
def load_fixtures():
    xls = pd.ExcelFile(EXPORT_FILE)
    mapping = {}
    for sheet in xls.sheet_names:
        df0 = pd.read_excel(xls, sheet_name=sheet, header=None)
        if df0.shape[1] > 1:
            m = df0.iat[0,1]
            if isinstance(m, str) and "VS" in m:
                mapping[m.strip()] = sheet
    return mapping

@st.cache_data
def load_stats():
    overall = pd.read_excel(SUMMARY_FILE, sheet_name=SHEET_OVERALL)
    venue   = pd.read_excel(SUMMARY_FILE, sheet_name=SHEET_VENUE)
    return overall, venue

def res_icon(r):
    return TICK if str(r).upper().startswith("W") else CROSS

def cover_icon(v):
    return TICK if str(v).strip().upper() == "Y" else CROSS

def ou_icon(r):
    return ARROW_UP_HTML if str(r).lower().startswith("o") else ARROW_DN_HTML

def img_to_b64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def load_logo_b64(team):
    for ext in (".png", ".jpg", ".jpeg"):
        fn = f"{team}{ext}"
        if os.path.exists(fn):
            img = Image.open(fn).resize((30,30))
            return img_to_b64(img)
    return None

def make_table_html(df, *, add_divider=False, date_fmt="%d %b"):
    divider_css = f"border-right:{VERT_BORDER};" if add_divider else ""
    html = f'<table style="width:100%;border-collapse:collapse;{divider_css}"><tbody>'
    span = (
        f"border-top:{HORIZ_BORDER};border-bottom:{HORIZ_BORDER};"
        f"border-left:{VERT_BORDER};border-right:{VERT_BORDER};"
        "padding:4px;vertical-align:middle"
    )
    top = (
        f"border-top:{HORIZ_BORDER};border-left:{VERT_BORDER};"
        f"border-right:{VERT_BORDER};border-bottom:none;"
        "padding:4px;text-align:center"
    )
    bot = (
        f"border-left:{VERT_BORDER};border-right:{VERT_BORDER};"
        "border-top:none;"
        f"border-bottom:{HORIZ_BORDER};"
        "padding:4px;text-align:center"
    )

    for _, r in df.iterrows():
        ha = str(r.get("HomeAway","")).strip().lower()
        prefix = "<strong>VS</strong>&nbsp;" if ha=="home" else "<strong>@</strong>&nbsp;"
        dstr = pd.to_datetime(r["GameDate"]).strftime(date_fmt)

        html += "<tr>"
        html += f'<td rowspan="2" style="{span}">{dstr}</td>'
        b64 = load_logo_b64(r["Opponent"])
        if b64:
            html += (
                f'<td rowspan="2" style="{span}">'
                f'{prefix}<img src="data:image/png;base64,{b64}" '
                'width="30" height="30"/></td>'
            )
        else:
            html += f'<td rowspan="2" style="{span}">{prefix}{r["Opponent"]}</td>'

        for col in ["Score","Line","O/U"]:
            html += f'<td style="{top}">{r[col]}</td>'
        html += "</tr>"

        html += (
            "<tr>"
            f'<td style="{bot}">{res_icon(r["Res"])}</td>'
            f'<td style="{bot}">{cover_icon(r["Covered"])}</td>'
            f'<td style="{bot}">{ou_icon(r["O/U Res"])}</td>'
            "</tr>"
        )

    html += "</tbody></table>"
    return html

def get_weather_forecast(city, game_date):
    try:
        api_key = st.secrets["openweather_api_key"]
        url = (f"http://api.openweathermap.org/data/2.5/forecast"
               f"?q={city}&appid={api_key}&units=metric")
        resp = requests.get(url); resp.raise_for_status()
        data = resp.json()
        if "list" not in data:
            return f"⚠️ Weather data unavailable – {game_date.strftime('%b %d')} · {city}"
        for f in data["list"]:
            if pd.to_datetime(f["dt_txt"]).date() == game_date:
                temp = f["main"]["temp"]
                desc = f["weather"][0]["description"]
                emj  = "☀️" if "clear" in desc else "🌧️" if "rain" in desc else "🌤️"
                return (f"{emj} {temp:.1f}°C, {desc.capitalize()} – "
                        f"{game_date.strftime('%b %d')} · {city}")
        return f"{game_date.strftime('%b %d')} · {city} (forecast not found)"
    except:
        return f"⚠️ Weather fetch failed"

def main():
    st.set_page_config(page_title="THE MODEL | Built for Punters",
                       page_icon="favicon.png", layout="wide")
    st.title("AFL Dashboard")

    # Sidebar
    fixtures = load_fixtures()
    selected_game = st.selectbox("Select a game", list(fixtures.keys()))

    # Data
    overall_stats, venue_stats = load_stats()
    sheet = fixtures[selected_game]
    xls   = pd.ExcelFile(EXPORT_FILE)
    df0   = pd.read_excel(xls, sheet_name=sheet, header=None)

    # parse game info
    matchup = df0.iat[0,1]
    date    = df0.iat[1,3]
    city    = df0.iat[1,4]
    home, away = [x.strip() for x in matchup.split("VS")]
    game_info = {
        "round": 9,
        "home": home, "away": away,
        "date": pd.to_datetime(date).date(),
        "city": str(city).strip().capitalize(),
        "weather_city": ("Melbourne" if str(city).lower()=="marvel"
                         else str(city).strip())
    }

    # Dashboard‐type selector now includes Teams
    dashboard_tab = st.radio("Select dashboard",
                             ["Goalscorer","Disposals","Teams"],
                             horizontal=True)

    # Header
    st.markdown(f"### **Round {game_info['round']}: "
                f"{home} VS {away}**")

    # Weather
    venue_disp = ("Melbourne (Marvel Stadium)"
                  if game_info["city"].lower()=="marvel"
                  else game_info["city"])
    days_ahead = (game_info["date"] - datetime.today().date()).days
    if days_ahead <= 5:
        wline = get_weather_forecast(game_info["weather_city"],
                                     game_info["date"])
    else:
        wline = (f"{game_info['date'].strftime('%b %d')} · "
                 f"{venue_disp} (too far ahead)")
    st.markdown(wline)
    st.markdown("---")

    # 10. Goalscorer
    if dashboard_tab=="Goalscorer":
        for label, hdf, adf, col in [
            ("Anytime Goal Scorer", df0.iloc[3:8,1:5], df0.iloc[3:8,8:12], "AGS Odds"),
            ("2+ Goals",             df0.iloc[10:15,1:5], df0.iloc[10:15,8:12], "2+ Odds"),
            ("3+ Goals",             df0.iloc[17:22,1:5], df0.iloc[17:22,8:12], "3+ Odds")
        ]:
            st.subheader(label)
            c1,c2 = st.columns(2)
            with c1:
                st.caption(home)
                st.dataframe(style_table(hdf, col, f"VS {away}"),
                             height=218, hide_index=True)
            with c2:
                st.caption(away)
                st.dataframe(style_table(adf, col, f"VS {home}"),
                             height=218, hide_index=True)

    # 11. Disposals
    elif dashboard_tab=="Disposals":
        try:
            disp = pd.read_excel("ExportDisposals.xlsx",
                                  sheet_name=sheet, header=None)
            # ... existing disposals slicing & styling unchanged ...
        except Exception as e:
            st.error(f"❌ Failed to load ExportDisposals.xlsx: {e}")

    # 12. Teams: Last 5 + Last 5 at Venue
    else:
        # Last 5
        st.subheader("Last 5")
        L,_,R = st.columns([1,0.02,1])
        with L:
            st.caption(f"*{home}*")
            df_h = overall_stats[overall_stats["Team"]==home]
            st.markdown(make_table_html(df_h, add_divider=True,
                        date_fmt="%d %b"), unsafe_allow_html=True)
        with R:
            st.caption(f"*{away}*")
            df_a = overall_stats[overall_stats["Team"]==away]
            st.markdown(make_table_html(df_a, add_divider=False,
                        date_fmt="%d %b"), unsafe_allow_html=True)

        # Last 5 at Venue
        stadium = venue_stats[venue_stats["Team"]==home]["Venue"].iloc[0]
        st.subheader(f"Last 5 at {stadium}")
        L,_,R = st.columns([1,0.02,1])
        with L:
            st.caption(f"*{home}*")
            df_hv = venue_stats[venue_stats["Team"]==home]
            st.markdown(make_table_html(df_hv, add_divider=True,
                        date_fmt="%d/%m/%Y"), unsafe_allow_html=True)
        with R:
            st.caption(f"*{away}*")
            df_av = venue_stats[venue_stats["Team"]==away]
            st.markdown(make_table_html(df_av, add_divider=False,
                        date_fmt="%d/%m/%Y"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
