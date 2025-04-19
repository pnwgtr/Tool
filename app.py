import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

st.title("Cyber Risk ROI Calculator")

st.sidebar.header("Input Parameters")

# Inputs
controls_cost = st.sidebar.number_input("Cost of Preventative Controls ($)", min_value=0, value=1100000)
sle = st.sidebar.number_input("Single Loss Expectancy (SLE) - Incident Cost ($)", min_value=0, value=6000000)
aro_before = st.sidebar.slider("Likelihood of Incident BEFORE Controls", 0.0, 1.0, 0.2)
aro_after = st.sidebar.slider("Likelihood of Incident AFTER Controls", 0.0, 1.0, 0.1)

# Calculations
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = (risk_reduction / controls_cost) if controls_cost > 0 else 0
cost_vs_risk_ratio = (controls_cost / risk_reduction) if risk_reduction > 0 else float("inf")

# Output
col1, col2, col3 = st.columns(3)
col1.metric("ALE Before Controls", f"${ale_before:,.2f}")
col2.metric("ALE After Controls", f"${ale_after:,.2f}")
col3.metric("Annual Risk Reduction", f"${risk_reduction:,.2f}")

st.metric("ROI", f"{roi * 100:.1f}%")
st.caption("Tip: ROI > 200% and ratio < 1.0 generally indicate strong cybersecurity value.")

# -------------------------------
# 📊 Graph 1: ALE Before vs After
# -------------------------------
st.subheader("Annual Loss Exposure: Before vs After Controls")

ale_df = pd.DataFrame({
    "Scenario": ["Before Controls", "After Controls"],
    "ALE ($)": [ale_before, ale_after]
})

st.bar_chart(ale_df.set_index("Scenario"))

# -------------------------------
# 📊 Graph 2: ROI Breakdown
# -------------------------------
st.subheader("Cost vs Risk Reduction Breakdown")

cost_data = pd.DataFrame({
    "Category": ["Preventative Controls Cost", "Risk Reduction"],
    "Amount ($)": [controls_cost, risk_reduction]
})

fig2, ax2 = plt.subplots()
ax2.pie(cost_data["Amount ($)"], labels=cost_data["Category"], autopct="%1.1f%%", startangle=90)
ax2.axis("equal")
st.pyplot(fig2)

# -------------------------------
# Optional future graph ideas
# -------------------------------
# - Line chart of ROI vs ARO
# - Monte Carlo-style range estimates (with FAIR inputs)

