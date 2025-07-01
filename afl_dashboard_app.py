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
import base64

with open("PC_Logo.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

# ————— Helpers —————
@st.cache_data
def load_fixtures():
    xls = pd.ExcelFile("Export_simple.xlsx")
    mapping = {}
    for sheet in xls.sheet_names:
        df0 = pd.read_excel(xls, sheet_name=sheet, header=None)
        m = df0.iat[0, 0]             # <-- sheet name lives in A1
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

def make_table_html(df, *, add_divider=False, date_fmt="%d %b", headers=None):
    V = "1px solid rgba(0,0,0,0.2)"
    H = "1px solid rgba(0,0,0,0.2)"
    divider_css = f"border-right:{V};" if add_divider else ""
    # add font‐family and size to match pandas tables:
    html = f'<table style="width:100%;border-collapse:collapse;font-family:inherit;font-size:14px;{divider_css}">'

    span = f"border-top:{H};border-bottom:{H};border-left:{V};border-right:{V};padding:4px;vertical-align:middle"
    top  = f"border-top:{H};border-left:{V};border-right:{V};border-bottom:none;padding:4px;text-align:center"
    bot  = f"border-left:{V};border-right:{V};border-top:none;border-bottom:{H};padding:4px;text-align:center"

    if headers:
        # give your <th> the same background & boldness as pandas header cells
        header_span = span + ";background-color:#F0F4FF;font-weight:bold"
        html += "<thead><tr>"
        for h in headers:
            html += f'<th style="{header_span}">{h}</th>'
        html += "</tr></thead>"

    html += "<tbody>"
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


def style_table(df, odds_col):
    def hl(r):
        # we color by the numeric Edge % value
        e = float(r["Edge %"].rstrip("%"))
        color = "#e9f9ec" if e > 0 else "#faeaea"
        return [f"background-color: {color}"] * len(r)

    return (
        df.style
          .format({
              odds_col:      lambda x: f"${x:.2f}" if pd.notnull(x) else x,
              "Edge %":      lambda x: f"{x:.1f}%",
              "Adj Edge %":  lambda x: f"{x:.1f}%"
          })
          # ensure the header row here also picks up that same light‐blue + bold style
          .set_table_styles([
              {"selector": "th", "props": [("background-color", "#F0F4FF"), ("font-weight","bold")]}
          ])
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
# 4. Load Game Info (from Export_simple.xlsx)
try:
    xls = pd.ExcelFile("Export_simple.xlsx")
    sheet_names = xls.sheet_names
except Exception as e:
    st.error(f"❌ Failed to load Export_simple.xlsx: {e}")
    st.stop()

game_name_mapping = {}
game_info_mapping = {}

for sheet in sheet_names:
    df0 = pd.read_excel(xls, sheet_name=sheet, header=None)
    try:
        m  = df0.iat[0, 0]     # sheet name at A1
        d  = df0.iat[1, 0]     # date at A2
        ct = df0.iat[1, 1]     # city at B2
        if isinstance(m, str) and "VS" in m:
            gm = m.strip()
            game_name_mapping[gm] = sheet
            home, away = [x.strip() for x in gm.split("VS")]

            game_info_mapping[gm] = {
    "round": 17,
    "home": home,
    "away": away,
    "date": pd.to_datetime(d).date() if pd.notnull(d) else None,
    # always display whatever is in the Excel cell (e.g. “Marvel”)
    "city": str(ct).strip(),
    # but if that cell says “Marvel”, force the weather lookup to Melbourne,AU
    "weather_city": (
        "Melbourne,AU" 
        if str(ct).lower() == "marvel" 
        else f"{str(ct).strip()},AU"
    )
}

    except Exception as e:
        st.warning(f"⚠️ Error processing sheet '{sheet}': {e}")


# ----------------------------------------------------
# 5. Sidebar
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    selected_game = st.selectbox("Select a game", list(game_name_mapping.keys()))
    st.markdown("---")
    st.markdown("🎯 **Support The Model**")
    # ←── Insert PC_Logo.png as a Patreon link
    st.markdown(
        f'''
<div style="text-align:center; margin: 10px 0;">
  <a href="https://www.patreon.com/The_Model" target="_blank">
    <img src="data:image/png;base64,{b64}" width="120" alt="Patreon Logo">
  </a>
</div>
        ''',
        unsafe_allow_html=True
    )


    st.markdown("💖 [Join The Model Punt Club](https://www.patreon.com/The_Model)")
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
# 6. Load Selected Game from Export_simple.xlsx
# ----------------------------------------------------
sheet_name = game_name_mapping[selected_game]
game_info  = game_info_mapping[selected_game]

# read the entire sheet, no header
raw = pd.read_excel("Export_simple.xlsx", sheet_name=sheet_name, header=None)

# helper to pull out each 5-row block for home & away
def parse_block(label):
    # find the two occurrences of the block label
    idxs = list(raw.index[ raw[0]==label ])
    if len(idxs)!=2:
        st.error(f"Couldn’t find two '{label}' blocks in {sheet_name}")
        return pd.DataFrame(), pd.DataFrame()
    home_i, away_i = idxs
    # header row is 1 row below label
    header = list(raw.iloc[home_i+1].values)
    # data is the next 5 rows
    df_home = raw.iloc[home_i+2:home_i+7, :len(header)].copy()
    df_away = raw.iloc[away_i+2:away_i+7, :len(header)].copy()
    df_home.columns = header
    df_away.columns = header
    return df_home, df_away

# 7. pull in all markets
home_ags,     away_ags     = parse_block("Anytime Goalscorer")
home_2plus,  away_2plus   = parse_block("2+ Goalscorer")
home_3plus,  away_3plus   = parse_block("3+ Goalscorer")
home_15,     away_15      = parse_block("15+ Disposals")
home_20,     away_20      = parse_block("20+ Disposals")
home_25,     away_25      = parse_block("25+ Disposals")
home_30,     away_30      = parse_block("30+ Disposals")

# ─── 8. Table Styling ──────────────────────────────────────────────────────────
def style_table(df, odds_col):
    def hl(r):
        # r["Edge %"] is already a float, so just use it directly
        e = r["Edge %"]
        color = "#e9f9ec" if e > 0 else "#faeaea"
        return [f"background-color: {color}"] * len(r)

    return (
        df.style
          .format({
              odds_col:     lambda x: f"${x:.2f}" if pd.notnull(x) else x,
              "Edge %":     lambda x: f"{x:.1f}%",
              "Adj Edge %": lambda x: f"{x:.1f}%"
          })
          .set_table_styles([
              {"selector": "th", "props": [("background-color", "#F0F4FF"), ("font-weight","bold")]}
          ])
          .apply(hl, axis=1)
    )
def prep(df):
    """
    Rename BookieOdds→Odds, pick just the four columns, and
    hand off to style_table for colouring & formatting.
    """
    df2 = (
        df
        .rename(columns={"BookieOdds": "Odds"})
        [["Player", "Odds", "Edge %", "Adj Edge %"]]
    )
    return style_table(df2, odds_col="Odds")


# ----------------------------------------------------
# 9. Dashboard Layout
st.title("AFL Dashboard")
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

# ─── 10. Goalscorer – show Odds, Edge % and Adj Edge % ────────────────────
if dashboard_tab == "Goalscorer":
    for label, hdf, adf in [
        ("Anytime Goalscorer", home_ags, away_ags),
        ("2+ Goalscorer",      home_2plus, away_2plus),
        ("3+ Goalscorer",      home_3plus, away_3plus),
    ]:
        st.subheader(label)
        c1, c2 = st.columns(2)

        with c1:
            st.caption(game_info["home"])
            st.dataframe(
                prep(hdf),
                height=218,
                use_container_width=True,
                hide_index=True
            )

        with c2:
            st.caption(game_info["away"])
            st.dataframe(
                prep(adf),
                height=218,
                use_container_width=True,
                hide_index=True
            )


# ─── 11. Disposals – same + add the 30+ table ──────────────────────────────
elif dashboard_tab == "Disposals":
    for label, hdf, adf in [
        ("15+ Disposals", home_15, away_15),
        ("20+ Disposals", home_20, away_20),
        ("25+ Disposals", home_25, away_25),
        ("30+ Disposals", home_30, away_30),   # new!
    ]:
        st.subheader(label)
        c1, c2 = st.columns(2)

        with c1:
            st.caption(game_info["home"])
            if not hdf.empty:
                st.dataframe(
                    prep(hdf),
                    height=218,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No data for home team.")

        with c2:
            st.caption(game_info["away"])
            if not adf.empty:
                st.dataframe(
                    prep(adf),
                    height=218,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No data for away team.")

# ----------------------------------------------------
# ----------------------------------------------------
# 12. Teams
else:
    # define the column headings you want
    headers = ["Date","Game","Result","Line","O/U"]

    # Last 5
    st.subheader("Last 5")
    L,_,R = st.columns([1,0.02,1])
    with L:
        st.caption(f"*{game_info['home']}*")
        df_h = overall[overall["Team"] == game_info["home"]]
        st.markdown(
            make_table_html(
                df_h,
                add_divider=True,
                date_fmt="%d %b",
                headers=headers
            ),
            unsafe_allow_html=True
        )
    with R:
        st.caption(f"*{game_info['away']}*")
        df_a = overall[overall["Team"] == game_info["away"]]
        st.markdown(
            make_table_html(
                df_a,
                add_divider=False,
                date_fmt="%d %b",
                headers=headers
            ),
            unsafe_allow_html=True
        )

    # Last 5 at Venue
    stadium = venue[venue["Team"] == game_info["home"]]["Venue"].iloc[0]
    st.subheader(f"Last 5 at {stadium}")
    L,_,R = st.columns([1,0.02,1])
    with L:
        st.caption(f"*{game_info['home']}*")
        df_hv = venue[venue["Team"] == game_info["home"]]
        st.markdown(
            make_table_html(
                df_hv,
                add_divider=True,
                date_fmt="%d/%m/%Y",
                headers=headers
            ),
            unsafe_allow_html=True
        )
    with R:
        st.caption(f"*{game_info['away']}*")
        df_av = venue[venue["Team"] == game_info["away"]]
        st.markdown(
            make_table_html(
                df_av,
                add_divider=False,
                date_fmt="%d/%m/%Y",
                headers=headers
            ),
            unsafe_allow_html=True
        )