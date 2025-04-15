import streamlit as st
import base64
import pandas as pd

# ----------------------------------------------------
# 1. Page Setup
# ----------------------------------------------------
st.set_page_config(
    page_title="Betting Tools | The Model",
    page_icon="favicon.png",
    layout="wide"
)

# ----------------------------------------------------
# 2. Load and encode logo
# ----------------------------------------------------
with open("logo.png", "rb") as image_file:
    encoded_logo = base64.b64encode(image_file.read()).decode()

# ----------------------------------------------------
# 3. Styling
# ----------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #FFF8F0; }
    section[data-testid="stSidebar"] { background-color: #faf9f6; }
    th, td { text-align: center !important; vertical-align: middle !important; }
    .css-1wa3eu0 { font-size: 13px; }

    /* Radio buttons bold and larger font */
    div[data-baseweb="radio"] label {
        font-size: 16px;
        font-weight: normal;
    }
    div[data-baseweb="radio"] input:checked + div {
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 4. Header with logo
# ----------------------------------------------------
st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <img src="data:image/png;base64,{encoded_logo}" width="120" style="margin-right: 20px;">
        <h1 style="margin: 0;">Betting Tools</h1>
    </div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 5. Tool Selector
# ----------------------------------------------------
tool = st.radio("Select Tool", ["EV Calculator", "Staking Tool", "Betfair Calculator"], horizontal=True)
st.markdown("---")

# ----------------------------------------------------
# 6. EV Calculator
# ----------------------------------------------------
if tool == "EV Calculator":
    input_mode = st.radio("How do you estimate the chance of winning?", ["Probability (%)", "Fair Odds"], horizontal=True)
    odds = st.slider("Bookie Odds", min_value=1.01, max_value=20.0, value=2.00, step=0.05)

    if input_mode == "Probability (%)":
        prob_percent = st.slider("Your Estimated Win Probability", 0, 100, 50)
        prob_decimal = prob_percent / 100
    else:
        fair_odds = st.slider("Your Fair Odds", min_value=1.01, max_value=20.0, value=2.00, step=0.05)
        prob_decimal = 1 / fair_odds

    stake = st.slider("Stake ($)", min_value=5, max_value=1000, value=25, step=5)
    ev = (prob_decimal * (odds * stake)) - ((1 - prob_decimal) * stake)

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

    # Kelly Table for $100 Bankroll
    st.markdown("---")
    st.subheader("Kelly Table (based on $100 Bankroll)")

    kelly_data = []
    for k in [0.1, 0.25, 0.5, 1.0]:
        edge = (odds * prob_decimal - 1)
        full_kelly = edge / (odds - 1) * 100
        suggested = max(0, full_kelly * k)
        kelly_data.append([f"{int(k*100)}%", f"${suggested:.2f}"])

    df_kelly = pd.DataFrame(kelly_data, columns=["Kelly Fraction", "Suggested Stake"])
    st.table(df_kelly)

# ----------------------------------------------------
# 7. Staking Tool (Standalone Kelly)
# ----------------------------------------------------
elif tool == "Staking Tool":
    odds = st.number_input("Bookie Odds", min_value=1.01, max_value=100.0, value=2.0, step=0.01)
    prob = st.slider("Your Estimated Probability (%)", 0, 100, 50) / 100
    bankroll = st.number_input("Your Bankroll ($)", min_value=1.0, value=100.0)

    edge = (odds * prob - 1)
    full_kelly = edge / (odds - 1) * bankroll
    kelly_fraction = st.radio("Select Kelly Fraction", [0.1, 0.25, 0.5, 1.0], format_func=lambda x: f"{int(x*100)}% Kelly", horizontal=True)
    stake = max(0, full_kelly * kelly_fraction)

    st.metric("Suggested Stake", f"${stake:.2f}")
    st.caption("Kelly Criterion formula: Edge / (Odds - 1) × Bankroll")

# ----------------------------------------------------
# 8. Betfair Back/Lay Calculator
# ----------------------------------------------------
elif tool == "Betfair Calculator":
    st.info("🛠️ Coming soon — back and lay calculator with implied % and commission adjustments.")
