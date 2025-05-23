import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === STYLES ===
st.markdown("""
<style>
.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 20px;
}
.metric-box {
  background-color: #1f1f1f;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  color: white;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
}
.metric-box h4 {
  margin: 0;
  color: #61dafb;
  font-size: 18px;
}
.metric-box p {
  font-size: 28px;
  margin: 10px 0 0;
  font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# === TITLE ===
st.markdown("<h1 style='text-align: center;'>Cyber Risk ROI Calculator</h1>", unsafe_allow_html=True)

# === SIDEBAR INPUTS ===
st.sidebar.markdown("### Program Maturity Level")
maturity_level = st.sidebar.select_slider("Cybersecurity Program Maturity",
    options=["Initial", "Developing", "Defined", "Managed", "Optimized"], value="Defined")

st.sidebar.header("Input Parameters")
controls_cost_m = st.sidebar.slider("Cost of Preventative Controls ($M)", 0.0, 10.0, 1.1, 0.1)
controls_cost = controls_cost_m * 1_000_000

revenue_m = st.sidebar.slider("Annual Revenue ($M)", 0.0, 1000.0, 500.0, 10.0)
revenue = revenue_m * 1_000_000
default_cost_per_day = revenue / 365

st.sidebar.markdown("### Breach Impact Assumptions")
user_count_k = st.sidebar.slider("Estimated Affected Users (K)", 0, 1000, 600, 10)
user_count = user_count_k * 1000
monitoring_cost_per_user = st.sidebar.slider("$ Cost per User for Credit Monitoring", 0, 20, 10, 1)

sle_m = st.sidebar.slider("Base SLE (Excl. Users) - Incident Cost ($M)", 0.0, 10.0, 6.0, 0.1)
base_sle = sle_m * 1_000_000
user_breach_cost = user_count * monitoring_cost_per_user

st.sidebar.markdown("### Downtime Impact Assumptions")
downtime_days = st.sidebar.slider("Estimated Days of Downtime", 5, 30, 5)
dcost_max_m = (default_cost_per_day / 1_000_000) * 2
cost_per_day_m = st.sidebar.slider("Cost per Day of Downtime ($M)", 0.0, dcost_max_m, default_cost_per_day/1_000_000, 0.1)
cost_per_day = cost_per_day_m * 1_000_000
downtime_cost = downtime_days * cost_per_day

st.sidebar.markdown("### Incident Likelihood")
aro_before_pct = st.sidebar.slider("Likelihood Before Controls (%)", 0, 100, 30)
aro_after_pct = st.sidebar.slider("Likelihood After Controls (%)", 0, 100, 10)
modifiers = {"Initial":1.3,"Developing":1.15,"Defined":1.0,"Managed":0.85,"Optimized":0.7}
aro_before = (aro_before_pct/100)*modifiers[maturity_level]
aro_after = (aro_after_pct/100)*modifiers[maturity_level]

# === CALCULATIONS ===
sle = base_sle + user_breach_cost + downtime_cost
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = risk_reduction / controls_cost if controls_cost else 0
roi_pct = roi * 100

# === ROI COLOR ===
if roi_pct < 100:
    roi_color = "#e06c75"
elif roi_pct < 200:
    roi_color = "#e5c07b"
else:
    roi_color = "#98c379"

# === KPI GRID ===
highlight_grid = f"""
<div class="metric-grid">
  <div class="metric-box">
    <h4>ALE Before Controls</h4>
    <p>${ale_before/1e6:.2f}M</p>
  </div>
  <div class="metric-box">
    <h4>ALE After Controls</h4>
    <p>${ale_after/1e6:.2f}M</p>
  </div>
  <div class="metric-box">
    <h4>Risk Reduction</h4>
    <p>${risk_reduction/1e6:.2f}M</p>
  </div>
  <div class="metric-box">
    <h4>Return on Investment</h4>
    <p style="color:{roi_color};">{roi_pct:.1f}%</p>
  </div>
</div>
"""
st.markdown(highlight_grid, unsafe_allow_html=True)

# === CHARTS ===
st.markdown("## 📊 Visual Risk Overview")

# Cost Component Breakdown
st.markdown("### Cost Component Breakdown")
fig3, ax3 = plt.subplots(figsize=(6.5, 2.8), facecolor='none')
comp_labels = ["Controls", "User Breach Cost", "Downtime Cost", "Total Incident Cost"]
comp_values = [controls_cost/1e6, user_breach_cost/1e6, downtime_cost/1e6, sle/1e6]
colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA']
bars3 = ax3.barh(comp_labels, comp_values, color=colors)
for bar, val in zip(bars3, comp_values):
    ax3.text(val + max(comp_values) * 0.01, bar.get_y() + bar.get_height()/2,
             f"{val:.2f}M", va='center', ha='left', color='white', fontsize=9)
ax3.set_xlabel("Millions ($)", labelpad=6, color='white')
ax3.set_facecolor('none')
for spine in ax3.spines.values(): spine.set_color('none')
for label in ax3.get_xticklabels() + ax3.get_yticklabels(): label.set_color('white')
ax3.invert_yaxis()
fig3.tight_layout()
st.pyplot(fig3, transparent=True)

# Stacked side-by-side charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Annual Loss Exposure")
    fig1, ax1 = plt.subplots(figsize=(4.5, 2.2), facecolor='none')
    scenarios = ["Before Controls", "After Controls"]
    values = [ale_before/1e6, ale_after/1e6]
    bars = ax1.barh(scenarios, values, color=['#EF553B','#636EFA'])
    ax1.set_xlabel('ALE (Millions $)', labelpad=6, color='white')
    ax1.invert_yaxis()
    for bar, val in zip(bars, values):
        ax1.text(val + max(values) * 0.01, bar.get_y() + bar.get_height()/2,
                 f"{val:.2f}M", va='center', ha='left', color='white', fontsize=9)
    pct_diff = ((ale_before - ale_after) / ale_before) * 100 if ale_before else 0
    ax1.text(0.5, 1.1, f"↓ {pct_diff:.1f}% Risk Reduction", color="#98c379",
             ha='center', va='bottom', transform=ax1.transAxes, fontsize=9)
    ax1.set_facecolor('none')
    for spine in ax1.spines.values(): spine.set_color('none')
    for label in ax1.get_xticklabels() + ax1.get_yticklabels(): label.set_color('white')
    fig1.tight_layout()
    st.pyplot(fig1, transparent=True)

with col2:
    st.markdown("### Cost vs Risk Reduction")
    fig2, ax2 = plt.subplots(figsize=(4.2, 3), facecolor='none')
    labels = ["Controls Cost", "Risk Reduction"]
    sizes = [controls_cost/1e6, risk_reduction/1e6]
    colors = ['#636EFA', '#00CC96']
    wedges, texts, autotexts = ax2.pie(
        sizes, labels=labels,
        autopct=lambda p: f"${p*sum(sizes)/100:.1f}M",
        startangle=90, colors=colors,
        wedgeprops=dict(width=0.35),
        textprops=dict(
