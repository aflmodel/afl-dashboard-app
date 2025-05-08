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
ARROW_UP       = "⬆️"
ARROW_DN       = "⬇️"
# ——————————————————

@st.cache_data
def load_fixtures():
    xls = pd.ExcelFile(EXPORT_FILE)
    fixtures = []
    for sheet in xls.sheet_names:
        df0 = pd.read_excel(xls, sheet, header=None)
        if df0.shape[1] > 1:
            m = df0.iat[0, 1]
            if isinstance(m, str) and "VS" in m:
                fixtures.append(m.strip())
    return fixtures

@st.cache_data
def load_stats():
    overall = pd.read_excel(SUMMARY_FILE, sheet_name=SHEET_OVERALL)
    venue   = pd.read_excel(SUMMARY_FILE, sheet_name=SHEET_VENUE)
    return overall, venue

def res_icon(r):
    return TICK if str(r).upper().startswith("W") else CROSS

def cover_icon(v):
    return TICK if bool(v) else CROSS

def ou_icon(r):
    r = str(r).lower()
    return ARROW_UP if r.startswith("o") else ARROW_DN

def img_to_b64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def load_logo_b64(team):
    for ext in (".png", ".jpg", ".jpeg"):
        fn = f"{team}{ext}"
        if os.path.exists(fn):
            img = Image.open(fn).resize((30, 30))
            return img_to_b64(img)
    return None

def make_table_html(df, add_right_border=False):
    rows = []
    for _, r in df.iterrows():
        date = pd.to_datetime(r["GameDate"]).strftime("%d %b")
        b64  = load_logo_b64(r["Opponent"])
        if b64:
            logo_td = (
                f'<td rowspan="2" style="padding:4px;vertical-align:middle">'
                f'<img src="data:image/png;base64,{b64}" width="30" height="30"/></td>'
            )
        else:
            logo_td = f'<td rowspan="2" style="padding:4px;vertical-align:middle">{r["Opponent"]}</td>'

        # Row 1: Score, Line, O/U
        rows.append(f'''
<tr>
  <td rowspan="2" style="padding:4px;vertical-align:middle">{date}</td>
  {logo_td}
  <td style="padding:4px;text-align:center"><strong>{r["Score"]}</strong></td>
  <td style="padding:4px;text-align:center"><strong>{r["Line"]}</strong></td>
  <td style="padding:4px;text-align:center"><strong>{r["O/U"]}</strong></td>
</tr>
''')
        # Row 2: icons
        rows.append(f'''
<tr>
  <td style="padding:4px;text-align:center">{res_icon(r["Res"])}</td>
  <td style="padding:4px;text-align:center">{cover_icon(r["Covered"])}</td>
  <td style="padding:4px;text-align:center">{ou_icon(r["O/U Res"])}</td>
</tr>
''')
    border = 'border-right:1px solid rgba(0,0,0,0.1);' if add_right_border else ''
    return f'''
<table style="width:100%;border-collapse:collapse;{border}">
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
'''

def main():
    st.title("Team Stats Viewer")

    # 1) Fixture dropdown
    fixture = st.selectbox("Select fixture", load_fixtures())
    home, away = [x.strip() for x in fixture.split("VS")]

    # 2) Load data & choose view
    overall, venue = load_stats()
    view = st.radio("View", ["Last 5", "Last 5 at Venue"], horizontal=True)
    df = overall if view == "Last 5" else venue

    # 3) Single header
    st.subheader("Last 5")

    # 4) Two panels + faint divider
    left, mid, right = st.columns([1, 0.02, 1])
    with left:
        html_home = make_table_html(df[df["Team"] == home], add_right_border=True)
        st.markdown(html_home, unsafe_allow_html=True)
    with mid:
        # just filler for spacing—the border on left table is the divider
        st.write("")
    with right:
        html_away = make_table_html(df[df["Team"] == away], add_right_border=False)
        st.markdown(html_away, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
