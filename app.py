import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === TITLE ===
st.title("Cyber Risk ROI Calculator")

# === SIDEBAR INPUTS ===
st.sidebar.header("Input Parameters")
revenue_m = st.sidebar.number_input("Annual Revenue ($M)", min_value=0.0, value=500.0)
revenue = revenue_m * 1_000_000
st.sidebar.markdown("### Breach Impact Assumptions")
user_count = st.sidebar.number_input("Estimated Affected Users", min_value=0, value=600000, step=10000)
monitoring_cost_per_user = st.sidebar.number_input("Cost per User for Credit Monitoring ($)", min_value=0.0, value=10.0)
user_breach_cost = user_count * monitoring_cost_per_user

controls_cost_m = st.sidebar.number_input("Cost of Preventative Controls ($M)", min_value=0.0, value=1.1)
sle_m = st.sidebar.number_input("Single Loss Expectancy (SLE) - Incident Cost ($M)", min_value=0.0, value=6.0)
aro_before = st.sidebar.slider("Likelihood of Incident BEFORE Controls", 0.0, 1.0, 0.2)
aro_after = st.sidebar.slider("Likelihood of Incident AFTER Controls", 0.0, 1.0, 0.1)

# Convert to full dollar amounts
controls_cost = controls_cost_m * 1_000_000
base_sle = sle_m * 1_000_000
sle = base_sle + user_breach_cost

# === CALCULATIONS ===
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = (risk_reduction / controls_cost) if controls_cost > 0 else 0
ale_before_pct = (ale_before / revenue) * 100 if revenue > 0 else 0
ale_after_pct = (ale_after / revenue) * 100 if revenue > 0 else 0
risk_reduction_pct = (risk_reduction / revenue) * 100 if revenue > 0 else 0
cost_vs_risk_ratio = (controls_cost / risk_reduction) if risk_reduction > 0 else float("inf")

# === METRICS OUTPUT ===
col1, col2, col3 = st.columns(3)
col1.metric("ALE Before Controls", f"${ale_before/1_000_000:.2f}M")
col2.metric("ALE After Controls", f"${ale_after/1_000_000:.2f}M")
col3.metric("Annual Risk Reduction", f"${risk_reduction/1_000_000:.2f}M")

st.metric("ROI", f"{roi * 100:.1f}%")
st.caption("Tip: ROI > 200% and ratio < 1.0 generally indicate strong cybersecurity value.")
st.markdown("### Impact as % of Annual Revenue")
col4, col5, col6 = st.columns(3)
col4.metric("ALE Before Controls", f"{ale_before_pct:.2f}% of revenue")
col5.metric("ALE After Controls", f"{ale_after_pct:.2f}% of revenue")
col6.metric("Risk Reduction", f"{risk_reduction_pct:.2f}% of revenue")

# === BAR CHART: ALE Before vs After ===
st.subheader("Annual Loss Exposure: Before vs After Controls")
ale_df = pd.DataFrame({
    "Scenario": ["Before Controls", "After Controls"],
    "ALE (Millions $)": [ale_before/1_000_000, ale_after/1_000_000]
})
st.bar_chart(ale_df.set_index("Scenario"))

# === PIE CHART: Cost vs Risk Reduction ===
st.subheader("Cost vs Risk Reduction Breakdown")
cost_data = pd.DataFrame({
    "Category": ["Preventative Controls Cost", "Risk Reduction"],
    "Amount (Millions $)": [controls_cost/1_000_000, risk_reduction/1_000_000]
})
fig2, ax2 = plt.subplots()
ax2.pie(cost_data["Amount (Millions $)"], labels=cost_data["Category"], autopct="%1.1f%%", startangle=90)
ax2.axis("equal")
st.pyplot(fig2)
st.markdown("### Breach Cost Breakdown")
st.write(f" Base SLE: ${base_sle / 1_000_000:.2f}M")
st.write(f" Credit Monitoring for Users: ${user_breach_cost / 1_000_000:.2f}M")
st.write(f"Total Incident Cost (SLE): ${sle / 1_000_000:.2f}M")


