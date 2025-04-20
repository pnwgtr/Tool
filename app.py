import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === TITLE ===
st.title("Cyber Risk ROI Calculator")

# === SIDEBAR INPUTS ===
st.sidebar.header("Input Parameters")

# Revenue
revenue_m = st.sidebar.number_input("Annual Revenue ($M)", min_value=0.0, value=500.0)
revenue = revenue_m * 1_000_000

# User breach impact
st.sidebar.markdown("### Breach Impact Assumptions")
user_count = st.sidebar.number_input("Estimated Affected Users", min_value=0, value=600000, step=10000)
monitoring_cost_per_user = st.sidebar.number_input("Cost per User for Credit Monitoring ($)", min_value=0.0, value=10.0)
user_breach_cost = user_count * monitoring_cost_per_user

# SLE input
sle_m = st.sidebar.number_input("Base SLE (Excluding Users) - Incident Cost ($M)", min_value=0.0, value=6.0)
base_sle = sle_m * 1_000_000
sle = base_sle + user_breach_cost

# ARO sliders (now using percent)
aro_before_percent = st.sidebar.slider("Likelihood of Incident BEFORE Controls (%)", 0, 100, 20)
aro_after_percent = st.sidebar.slider("Likelihood of Incident AFTER Controls (%)", 0, 100, 10)
aro_before = aro_before_percent / 100
aro_after = aro_after_percent / 100

# Convert to decimal (for math)
aro_before = aro_before_percent / 100
aro_after = aro_after_percent / 100

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

# ==== ROI Pie Chart: Cost vs Risk Reduction ====

# Make sure this comes right before the chart
cost_data = pd.DataFrame({
    "Category": ["Preventative Controls Cost", "Risk Reduction"],
    "Amount (Millions $)": [controls_cost / 1_000_000, risk_reduction / 1_000_000]
})

st.subheader("Cost vs Risk Reduction Breakdown")

fig2, ax2 = plt.subplots(facecolor='none')
ax2.set_facecolor('none')

text_props = {'color': 'white', 'fontsize': 12}

wedges, texts, autotexts = ax2.pie(
    cost_data["Amount (Millions $)"],
    labels=cost_data["Category"],
    autopct="%1.1f%%",
    startangle=90,
    textprops=text_props,
    wedgeprops=dict(edgecolor='black')
)

for text in texts + autotexts:
    text.set_color('white')

ax2.axis("equal")
st.pyplot(fig2, transparent=True)


