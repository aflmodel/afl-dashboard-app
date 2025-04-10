import streamlit as st
import base64
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from components.sidebar import render_sidebar

# ----------------------------------------------------
# Page Setup
# ----------------------------------------------------
st.set_page_config(
    page_title="EV Calculator | The Model",
    page_icon="../favicon.png",  # point to root-level image
    layout="wide"
)


# Hide default nav + styling
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    .stApp {
        background-color: #FFF8F0;
    }
    section[data-testid="stSidebar"] {
        background-color: #faf9f6;
    }
    th, td {
        text-align: center !important;
        vertical-align: middle !important;
    }
    .css-1wa3eu0 {
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------
with st.sidebar:
    render_sidebar()

# ----------------------------------------------------
# Header
# ----------------------------------------------------
try:
    with open("../favicon.png", "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
        <h2 style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{encoded_image}" width="30" style="margin-right: 10px;">
            Kelly Criterion Calculator
        </h2>
    """, unsafe_allow_html=True)
except FileNotFoundError:
    st.header("Kelly Criterion Calculator")

# ----------------------------------------------------
# Calculator Inputs
# ----------------------------------------------------
st.markdown("Use the Kelly Criterion to determine the **optimal stake size** based on your edge.")

odds = st.slider("Bookie Odds", min_value=1.01, max_value=20.0, value=2.00, step=0.05)
prob_percent = st.slider("Your Estimated Win Probability", 0, 100, 50)
bankroll = st.slider("Current Bankroll ($)", min_value=50, max_value=10000, value=1000, step=50)

# ----------------------------------------------------
# Calculations
# ----------------------------------------------------
p = prob_percent / 100
b = odds - 1

kelly_fraction = ((b * p) - (1 - p)) / b if b != 0 else 0
kelly_fraction = max(kelly_fraction, 0)  # No negative staking

stake = kelly_fraction * bankroll
ev = (p * (odds * stake)) - ((1 - p) * stake)

# ----------------------------------------------------
# Output
# ----------------------------------------------------
st.markdown("---")
st.subheader("Results")

col1, col2 = st.columns(2)
col1.metric("Optimal Stake", f"${stake:.2f}")
col2.metric("Kelly Fraction", f"{kelly_fraction * 100:.2f}%")

st.markdown(f"**Expected Value:** ${ev:.2f}")

if kelly_fraction > 0:
    st.success("✅ You have an edge — Kelly recommends a positive stake.")
elif kelly_fraction == 0:
    st.info("➖ No edge — Kelly recommends no bet.")
else:
    st.error("❌ Negative edge — do not bet.")

st.caption("Note: The Kelly Criterion maximizes long-term bankroll growth but can be volatile.")
