# team_stats_local.py

import streamlit as st
import pandas as pd
import os, io, base64
from PIL import Image

# ————— CONFIG —————
EXPORT_FILE    = "Export.xlsx"
SUMMARY_FILE   = "upcoming_round_summary.xlsx"
SHEET_OVERALL  = "Overall_Last5"
SHEET_VENUE    = "Venue_Last5"

TICK, CROSS    = "✅", "❌"

# ▲ and ▼ as HTML entities, colored purple/orange
UP_ARROW       = "&#9650;"
DN_ARROW       = "&#9660;"
ARROW_UP_HTML  = f'<span style="color:purple;">{UP_ARROW}</span>'
ARROW_DN_HTML  = f'<span style="color:orange;">{DN_ARROW}</span>'

# border styles
VERT_BORDER   = "1px solid rgba(0,0,0,0.2)"
HORIZ_BORDER  = "1px solid rgba(0,0,0,0.2)"
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

    span_style = (
        f"border-top:{HORIZ_BORDER};border-bottom:{HORIZ_BORDER};"
        f"border-left:{VERT_BORDER};border-right:{VERT_BORDER};"
        "padding:4px;vertical-align:middle"
    )
    top_only = (
        f"border-top:{HORIZ_BORDER};border-left:{VERT_BORDER};"
        f"border-right:{VERT_BORDER};border-bottom:none;"
        "padding:4px;text-align:center"
    )
    bottom_only = (
        f"border-left:{VERT_BORDER};border-right:{VERT_BORDER};"
        "border-top:none;"
        f"border-bottom:{HORIZ_BORDER};"
        "padding:4px;text-align:center"
    )

    for _, r in df.iterrows():
        ha = str(r.get("HomeAway","")).strip().lower()
        prefix = "<strong>VS</strong>&nbsp;" if ha == "home" else "<strong>@</strong>&nbsp;"

        date_str = pd.to_datetime(r["GameDate"]).strftime(date_fmt)

        html += "<tr>"
        html += f'<td rowspan="2" style="{span_style}">{date_str}</td>'

        b64 = load_logo_b64(r["Opponent"])
        if b64:
            html += (
                f'<td rowspan="2" style="{span_style}">'
                f'{prefix}<img src="data:image/png;base64,{b64}" width="30" height="30"/>'
                "</td>"
            )
        else:
            html += f'<td rowspan="2" style="{span_style}">{prefix}{r["Opponent"]}</td>'

        for col in ["Score","Line","O/U"]:
            html += f'<td style="{top_only}">{r[col]}</td>'
        html += "</tr>"

        html += (
            "<tr>"
            f'<td style="{bottom_only}">{res_icon(r["Res"])}</td>'
            f'<td style="{bottom_only}">{cover_icon(r["Covered"])}</td>'
            f'<td style="{bottom_only}">{ou_icon(r["O/U Res"])}</td>'
            "</tr>"
        )

    html += "</tbody></table>"
    return html

def main():
    st.title("Team Stats Viewer")

    # load fixtures & data
    fixtures = load_fixtures()
    fixture = st.selectbox("Select fixture", list(fixtures.keys()))
    overall, venue = load_stats()

    # parse home/away
    home, away = [x.strip() for x in fixture.split("VS")]

    # --- Last 5 ---
    st.subheader("Last 5")
    left, spacer, right = st.columns([1,0.02,1])
    with left:
        st.caption(f"*{home}*")
        df_h = overall[overall["Team"] == home]
        st.markdown(
            make_table_html(df_h, add_divider=True, date_fmt="%d %b"),
            unsafe_allow_html=True
        )
    with spacer:
        st.write("")
    with right:
        st.caption(f"*{away}*")
        df_a = overall[overall["Team"] == away]
        st.markdown(
            make_table_html(df_a, add_divider=False, date_fmt="%d %b"),
            unsafe_allow_html=True
        )

    # --- Last 5 at Venue ---
    # determine stadium from the venue summary
    stadium = venue[venue["Team"] == home]["Venue"].iloc[0]
    st.subheader(f"Last 5 at {stadium}")
    left, spacer, right = st.columns([1,0.02,1])
    with left:
        st.caption(f"*{home}*")
        df_hv = venue[venue["Team"] == home]
        st.markdown(
            make_table_html(df_hv, add_divider=True, date_fmt="%d/%m/%Y"),
            unsafe_allow_html=True
        )
    with spacer:
        st.write("")
    with right:
        st.caption(f"*{away}*")
        df_av = venue[venue["Team"] == away]
        st.markdown(
            make_table_html(df_av, add_divider=False, date_fmt="%d/%m/%Y"),
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
