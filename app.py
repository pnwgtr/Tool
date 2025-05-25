import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === GUIDE STATE ===
if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

# === FLOATING HELP BUTTON ===
st.markdown("""
<style>
.floating-help {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #00cc96;
    color: white;
    padding: 10px 18px;
    border-radius: 30px;
    font-weight: bold;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    cursor: pointer;
    z-index: 10000;
}
</style>
<script>
function toggleGuide() {
    fetch('/?show_guide=1').then(() => window.location.reload());
}
</script>
<div class="floating-help" onclick="toggleGuide()">💡 Quick Start</div>
""", unsafe_allow_html=True)

# === SIDEBAR TOGGLE BUTTON + EXPANDER ===
if st.sidebar.button("💡 Quick Start Guide"):
    st.session_state.show_guide = not st.session_state.show_guide

if st.session_state.show_guide:
    with st.sidebar.expander("👋 Getting Started", expanded=True):
        st.markdown("""
Adjust these inputs to model your cybersecurity ROI:

- **Cybersecurity Budget** – Your annual spend on controls
- **Annual Revenue** – Used to estimate downtime loss
- **Users Affected** – For breach impact calculation
- **ARO Before/After** – Likelihood of incident before/after controls

Use **Executive Mode** to simplify the view.
        """)

# === SIDEBAR CONTROLS ===
st.sidebar.header("Input Parameters")
st.sidebar.markdown("### Program Configuration")
maturity_level = st.sidebar.select_slider(
    "Cybersecurity Program Maturity",
    options=["Initial", "Developing", "Defined", "Managed", "Optimized"],
    value="Initial"
)

controls_cost_m = st.sidebar.slider("Cybersecurity Budget ($M)", 0.0, 10.0, 1.1, 0.1)
controls_cost = controls_cost_m * 1_000_000

revenue_m = st.sidebar.slider("Annual Revenue ($M)", 0.0, 1000.0, 500.0, 10.0)
revenue = revenue_m * 1_000_000
default_cost_per_day = revenue / 365

st.sidebar.markdown("### Breach Impact Assumptions")
user_count_k = st.sidebar.slider("Estimated Affected Users (K)", 0, 1000, 600, 10)
user_count = user_count_k * 1000
monitoring_cost_per_user = st.sidebar.slider("Cost per User for Credit Monitoring ($)", 0, 20, 10, 1)

sle_m = st.sidebar.slider("Base Incident Cost (Excl. Users) ($M)", 0.0, 10.0, 6.0, 0.1)
base_sle = sle_m * 1_000_000
user_breach_cost = user_count * monitoring_cost_per_user

st.sidebar.markdown("### Downtime Impact Assumptions")
downtime_days = st.sidebar.slider("Estimated Days of Downtime", 5, 30, 5)
dcost_max_m = (default_cost_per_day / 1_000_000) * 2
cost_per_day_m = st.sidebar.slider("Downtime Cost/Day ($M)", 0.0, dcost_max_m, default_cost_per_day / 1_000_000, 0.1)
cost_per_day = cost_per_day_m * 1_000_000
downtime_cost = downtime_days * cost_per_day

st.sidebar.markdown("### Incident Likelihood")
aro_before_pct = st.sidebar.slider("Likelihood Before Controls (%)", 0, 100, 30)
aro_after_pct = st.sidebar.slider("Likelihood After Controls (%)", 0, 100, 10)

st.sidebar.markdown("### View Options")
executive_mode = st.sidebar.checkbox("Enable Executive Mode", value=True)
compact_mode = st.sidebar.checkbox("Enable Compact Layout", value=True)

# === CALCULATIONS ===
modifiers = {"Initial": 1.3, "Developing": 1.15, "Defined": 1.0, "Managed": 0.85, "Optimized": 0.7}
aro_before = (aro_before_pct / 100) * modifiers[maturity_level]
aro_after = (aro_after_pct / 100) * modifiers[maturity_level]

sle = base_sle + user_breach_cost + downtime_cost
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = risk_reduction / controls_cost if controls_cost else 0
roi_pct = roi * 100
roi_color = "#e06c75" if roi_pct < 100 else "#e5c07b" if roi_pct < 200 else "#00cc96"

# === KPI GRID ===
st.markdown("<h1 style='margin-top: 10px; text-align: center;'>Cyber Risk ROI Calculator</h1>", unsafe_allow_html=True)

kpi_style = f"""
<style>
.metric-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: {'10px' if compact_mode else '20px'};
  margin-top: 10px;
}}
.metric-box {{
  background-color: #1f1f1f;
  border-radius: 10px;
  padding: {'10px' if compact_mode else '20px'};
  text-align: center;
  color: white;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
}}
.metric-box h4 {{
  margin: 0 0 4px 0;
  color: #61dafb;
  font-size: {'16px' if compact_mode else '18px'};
}}
.metric-box p {{
  font-size: {'26px' if compact_mode else '30px'};
  margin: 0;
  font-weight: bold;
}}
</style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)

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
if executive_mode:
    st.subheader("Cost Component Breakdown")
    cost_data = pd.DataFrame({
        "Component": ["Cybersecurity Budget", "User Breach Cost", "Downtime Cost", "Total Incident Cost"],
        "Millions": [controls_cost / 1e6, user_breach_cost / 1e6, downtime_cost / 1e6, sle / 1e6]
    })
    fig3, ax3 = plt.subplots(figsize=(6, 3) if compact_mode else (8, 4))
    bars = ax3.barh(cost_data["Component"], cost_data["Millions"], color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA'])
    for bar, val in zip(bars, cost_data["Millions"]):
        ax3.text(val + 0.1, bar.get_y() + bar.get_height()/2, f"{val:.2f}M", va='center')
    ax3.invert_yaxis()
    ax3.set_xlabel("Millions $")
    st.pyplot(fig3)
else:
    # Show cost component breakdown first
    st.subheader("Cost Component Breakdown")
    cost_data = pd.DataFrame({
        "Component": ["Cybersecurity Budget", "User Breach Cost", "Downtime Cost", "Total Incident Cost"],
        "Millions": [controls_cost / 1e6, user_breach_cost / 1e6, downtime_cost / 1e6, sle / 1e6]
    })
    fig3, ax3 = plt.subplots(figsize=(6, 3) if compact_mode else (8, 4))
    bars = ax3.barh(cost_data["Component"], cost_data["Millions"], color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA'])
    for bar, val in zip(bars, cost_data["Millions"]):
        ax3.text(val + 0.1, bar.get_y() + bar.get_height()/2, f"{val:.2f}M", va='center')
    ax3.invert_yaxis()
    ax3.set_xlabel("Millions $")
    st.pyplot(fig3)

    # Then show the other two
    st.subheader("Annual Loss Exposure (Before vs After Controls)")
    fig1, ax1 = plt.subplots(figsize=(5, 3) if compact_mode else (6, 4))
    scenarios = ["Before Controls", "After Controls"]
    values = [ale_before / 1e6, ale_after / 1e6]
    bars = ax1.bar(scenarios, values, color=['#EF553B', '#00CC96'])
    ax1.set_ylabel('ALE (Millions $)')
    ax1.set_ylim(0, max(values) * 1.25)
    for bar, val in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.1, f"{val:.2f}M", ha='center', va='bottom')
    st.pyplot(fig1)

    st.subheader("Cost vs Risk Reduction")
    fig2, ax2 = plt.subplots(figsize=(4, 3) if compact_mode else (6, 4))
    costs = [controls_cost / 1e6, risk_reduction / 1e6]
    labels = ["Cybersecurity Budget", "Risk Reduction"]
    colors = ['#636EFA', '#00CC96']
    wedges, texts, autotexts = ax2.pie(
        costs,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        wedgeprops=dict(width=0.3)
    )
    ax2.axis('equal')
    st.pyplot(fig2)
