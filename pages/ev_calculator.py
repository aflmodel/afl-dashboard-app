import streamlit as st
import base64
import os

# Correct path to favicon (one level up from pages/)
favicon_path = os.path.join(os.path.dirname(__file__), "..", "favicon.png")

# Read and encode the favicon image
with open(favicon_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

# Render it as a heading
st.markdown(f"""
    <h2 style="display: flex; align-items: center;">
        <img src="data:image/png;base64,{encoded_image}" width="30" style="margin-right: 10px;">
        EV Calculator
    </h2>
""", unsafe_allow_html=True)

# Input Mode Toggle
input_mode = st.radio("How do you estimate the chance of winning?", ["Probability (%)", "Fair Odds"], horizontal=True)

# Bookie Odds Input
odds = st.slider("Bookie Odds", min_value=1.01, max_value=20.0, value=2.00, step=0.05)

# Probability or Fair Odds
if input_mode == "Probability (%)":
    prob_percent = st.slider("Your Estimated Win Probability", 0, 100, 50)
    prob_decimal = prob_percent / 100
else:
    fair_odds = st.slider("Your Fair Odds", min_value=1.01, max_value=20.0, value=2.00, step=0.05)
    prob_decimal = 1 / fair_odds

# Stake Input
stake = st.slider("Stake ($)", min_value=5, max_value=1000, value=25, step=5)

# EV Calculation
ev = (prob_decimal * (odds * stake)) - ((1 - prob_decimal) * stake)

# ----------------------------------------------------
# Output
# ----------------------------------------------------
st.markdown("---")
st.subheader("Results")

col1, col2 = st.columns(2)
col1.metric("Expected Value", f"${ev:.2f}", delta_color="off")
col2.metric("Edge %", f"{(odds * prob_decimal - 1) * 100:.2f}%")

if ev > 0:
    st.success("✅ Positive EV — profitable in the long run.")
elif ev < 0:
    st.error("❌ Negative EV — likely unprofitable.")
else:
    st.info("➖ Neutral EV — breakeven.")

st.caption("Note: This tool assumes fixed odds and no commission.")
