# ----------------------------------------------------
# AFL EDGE DASHBOARD – Streamlit App (With Debugs & Section Numbers)
# ----------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import streamlit.components.v1 as components
import os, io, base64
from PIL import Image

# ————— Helpers —————
@st.cache_data
def load_fixtures():
    xls = pd.ExcelFile("Export.xlsx")
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
    overall = pd.read_excel("upcoming_round_summary.xlsx", sheet_name="Overall_Last5")
    venue   = pd.read_excel("upcoming_round_summary.xlsx", sheet_name="Venue_Last5")
    return overall, venue

def get_weather_forecast(city, game_date):
    try:
        api_key = st.secrets["openweather_api_key"]
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        r = requests.get(url); r.raise_for_status()
        data = r.json()
        if "list" not in data:
            return f"⚠️ Weather data unavailable – {game_date:%B %d} · {city}"
        for f in data["list"]:
            if pd.to_datetime(f["dt_txt"]).date() == game_date:
                temp = f["main"]["temp"]
                desc = f["weather"][0]["description"]
                emoji = "☀️" if "clear" in desc else "🌧️" if "rain" in desc else "🌤️"
                return f"{emoji} {temp:.1f}°C, {desc.capitalize()} – {game_date:%B %d} · {city}"
        return f"{game_date:%B %d} · {city} (forecast not found)"
    except:
        return "⚠️ Weather fetch failed"

def img_to_b64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def load_logo_b64(team):
    for ext in (".png", ".jpg", ".jpeg"):
        fn = f"{team}{ext}"
        if os.path.exists(fn):
            return img_to_b64(Image.open(fn).resize((30,30)))
    return None

def make_table_html(df, *, add_divider=False, date_fmt="%d %b"):
    V = "1px solid rgba(0,0,0,0.2)"
    H = "1px solid rgba(0,0,0,0.2)"
    divider_css = f"border-right:{V};" if add_divider else ""
    html = f'<table style="width:100%;border-collapse:collapse;{divider_css}"><tbody>'
    span = f"border: {H} {V}; padding:4px; vertical-align:middle;"
    top  = f"border-top:{H}; border-left:{V}; border-right:{V}; border-bottom:none; padding:4px; text-align:center"
    bot  = f"border-left:{V}; border-right:{V}; border-top:none; border-bottom:{H}; padding:4px; text-align:center"
    for _, r in df.iterrows():
        ha = str(r.get("HomeAway","")).lower()
        prefix = "<strong>VS</strong>&nbsp;" if ha=="home" else "<strong>@</strong>&nbsp;"
        d = pd.to_datetime(r["GameDate"]).strftime(date_fmt)
        html += "<tr>"
        html += f'<td rowspan="2" style="{span}">{d}</td>'
        b64 = load_logo_b64(r["Opponent"])
        if b64:
            html += (
                f'<td rowspan="2" style="{span}">'
                f'{prefix}<img src="data:image/png;base64,{b64}" width="30" height="30"/>'
                "</td>"
            )
        else:
            html += f'<td rowspan="2" style="{span}">{prefix}{r["Opponent"]}</td>'
        html += f'<td style="{top}">{r["Score"]}</td>'
        html += f'<td style="{top}">{r["Line"]}</td>'
        html += f'<td style="{top}">{r["O/U"]}</td>'
        html += "</tr>"
        html += (
            "<tr>"
            f'<td style="{bot}">{"✅" if r["Res"]=="W" else "❌"}</td>'
            f'<td style="{bot}">{"✅" if r["Covered"]=="Y" else "❌"}</td>'
            f'<td style="{bot}">{"&#9650;" if r["O/U Res"].lower()=="over" else "&#9660;"}</td>'
            "</tr>"
        )
    html += "</tbody></table>"
    return html

def style_table(df, odds_col, vs_col):
    def hl(r):
        e = r["Edge"]
        color = "#e9f9ec" if e>0 else "#faeaea"
        return [f"background-color: {color}"]*len(r)
    return (
        df.style
          .format({"Edge":lambda x:f"{x*100:.2f}%" if pd.notnull(x) else x,
                   odds_col:lambda x:f"${x:.2f}" if pd.notnull(x) else x})
          .apply(hl, axis=1)
    )

# ----------------------------------------------------
# 1. Page Setup
st.set_page_config(
    page_title="THE MODEL | Built for Punters",
    page_icon="favicon.png",
    layout="wide"
)

# ----------------------------------------------------
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

# ----------------------------------------------------
# 3. Load Fixtures & Stats
fixtures = load_fixtures()
overall, venue = load_stats()

# ----------------------------------------------------
# 4. Load Game Info
try:
    xls = pd.ExcelFile("Export.xlsx")
    sheet_names = xls.sheet_names
except Exception as e:
    st.error(f"❌ Failed to load Export.xlsx: {e}")
    st.stop()

game_name_mapping = {}
game_info_mapping = {}

for sheet in sheet_names:
    df0 = pd.read_excel(xls, sheet_name=sheet, header=None)
    try:
        m  = df0.iat[0,1]
        d  = df0.iat[1,3]
        ct = df0.iat[1,4]
        hp = df0.iat[1,2]
        ap = df0.iat[1,11]
        if isinstance(m, str) and "VS" in m:
            gm = m.strip()
            game_name_mapping[gm] = sheet
            home, away = [x.strip() for x in gm.split("VS")]
            game_info_mapping[gm] = {
                "round": 9,
                "home": home, "away": away,
                "home_percent": f"{float(hp)*100:.0f}%" if pd.notnull(hp) else "??",
                "away_percent": f"{float(ap)*100:.0f}%" if pd.notnull(ap) else "??",
                "date": pd.to_datetime(d).date() if pd.notnull(d) else None,
                "city": str(ct).strip(),
                "weather_city": "Melbourne" if str(ct).lower()=="marvel" else str(ct).strip()
            }
    except Exception as e:
        # <<<< fixed stray-quote here
        st.warning(f"⚠️ Error processing sheet '{sheet}': {e}")

# ----------------------------------------------------
# 5. Sidebar
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
        "https://tally.so/embed/3E6VNo?alignLeft=1&hideTitle=1&hideDescription=1"
        "&transparentBackground=1&dynamicHeight=1",
        height=130, scrolling=False
    )

# ----------------------------------------------------
# 6. Load Selected Game
sheet_name = game_name_mapping[selected_game]
game_info  = game_info_mapping[selected_game]
df_sheet   = pd.read_excel("Export.xlsx", sheet_name=sheet_name, header=None)

# ----------------------------------------------------
# 7. Extract AGS Tables
home_ags   = df_sheet.iloc[3:8, 1:5]
away_ags   = df_sheet.iloc[3:8, 8:12]
home_2plus = df_sheet.iloc[10:15, 1:5]
away_2plus = df_sheet.iloc[10:15, 8:12]
home_3plus = df_sheet.iloc[17:22, 1:5]
away_3plus = df_sheet.iloc[17:22, 8:12]

home_ags.columns   = ["Players","Edge","AGS Odds",f"VS {game_info['away']}"]
away_ags.columns   = ["Players","Edge","AGS Odds",f"VS {game_info['home']}"]
home_2plus.columns = ["Players","Edge","2+ Odds",f"VS {game_info['away']}"]
away_2plus.columns = ["Players","Edge","2+ Odds",f"VS {game_info['home']}"]
home_3plus.columns = ["Players","Edge","3+ Odds",f"VS {game_info['away']}"]
away_3plus.columns = ["Players","Edge","3+ Odds",f"VS {game_info['home']}"]

# ----------------------------------------------------
# 8. Table Styling
# (style_table defined above)

# ----------------------------------------------------
# 9. Dashboard Layout
st.title("AFL Dashboards")
dashboard_tab = st.radio("Select dashboard",
                        ["Goalscorer", "Disposals", "Teams"],
                        horizontal=True)
st.markdown(f"### **Round {game_info['round']}: "
            f"{game_info['home']} VS {game_info['away']}**")

# ----------------------------------------------------
# Weather Display
venue_disp = ("Melbourne (Marvel Stadium)" 
              if game_info["city"].lower()=="marvel"
              else game_info["city"])
if (game_info["date"] - datetime.today().date()).days <= 5:
    st.markdown(get_weather_forecast(game_info["weather_city"], game_info["date"]))
else:
    st.markdown(f"{game_info['date']:%B %d} · {venue_disp} (too far ahead)")
st.markdown("---")

# ----------------------------------------------------
# 10. Goalscorer
if dashboard_tab == "Goalscorer":
    for label, hdf, adf, col in [
        ("Anytime Goal Scorer", home_ags,   away_ags,   "AGS Odds"),
        ("2+ Goals",             home_2plus, away_2plus, "2+ Odds"),
        ("3+ Goals",             home_3plus, away_3plus, "3+ Odds")
    ]:
        st.subheader(label)
        c1, c2 = st.columns(2)
        with c1:
            st.caption(game_info["home"])
            st.dataframe(style_table(hdf, col, f"VS {game_info['away']}"),
                         height=218, hide_index=True)
        with c2:
            st.caption(game_info["away"])
            st.dataframe(style_table(adf, col, f"VS {game_info['home']}"),
                         height=218, hide_index=True)

# ----------------------------------------------------
# 11. Disposals
elif dashboard_tab == "Disposals":
    try:
        disp = pd.read_excel("ExportDisposals.xlsx",
                             sheet_name=sheet_name, header=None)
        # … your existing disposals slices & styling …
    except Exception as e:
        st.error(f"❌ Failed to load ExportDisposals.xlsx: {e}")

# ----------------------------------------------------
# 12. Teams
else:
    # Last 5
    st.subheader("Last 5")
    L,_,R = st.columns([1,0.02,1])
    with L:
        st.caption(f"*{game_info['home']}*")
        df_h = overall[overall["Team"]==game_info["home"]]
        st.markdown(make_table_html(df_h, add_divider=True, date_fmt="%d %b"),
                    unsafe_allow_html=True)
    with R:
        st.caption(f"*{game_info['away']}*")
        df_a = overall[overall["Team"]==game_info["away"]]
        st.markdown(make_table_html(df_a, add_divider=False, date_fmt="%d %b"),
                    unsafe_allow_html=True)

    # Last 5 at Venue
    stadium = venue[venue["Team"]==game_info["home"]]["Venue"].iloc[0]
    st.subheader(f"Last 5 at {stadium}")
    L,_,R = st.columns([1,0.02,1])
    with L:
        st.caption(f"*{game_info['home']}*")
        df_hv = venue[venue["Team"]==game_info["home"]]
        st.markdown(make_table_html(df_hv, add_divider=True, date_fmt="%d/%m/%Y"),
                    unsafe_allow_html=True)
    with R:
        st.caption(f"*{game_info['away']}*")
        df_av = venue[venue["Team"]==game_info["away"]]
        st.markdown(make_table_html(df_av, add_divider=False, date_fmt="%d/%m/%Y"),
                    unsafe_allow_html=True)
