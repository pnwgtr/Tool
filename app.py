
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === DETECT THEME FOR COLOR ADAPTATION ===
theme = st.get_option("theme.base")
text_color = "black" if theme == "light" else "white"

# === GUIDE STATE ===
if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

# === SIDEBAR GUIDE TOGGLE ===
if st.sidebar.button("💡 Quick Start Guide"):
    st.session_state.show_guide = not st.session_state.show_guide

if st.session_state.show_guide:
    with st.sidebar.expander("👋 Getting Started", expanded=True):
        st.markdown("""
Adjust these inputs to model your cybersecurity ROI:

- **Cybersecurity Budget** – Your annual spend on controls  
- **Annual Revenue** – Used to estimate downtime loss  
- **Users Affected** – For breach impact calculation  
- **ARO Before/After** – Likelihood of incidents before/after controls  
        """)

# === SIDEBAR INPUTS ===
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
cost_per_day_m = st.sidebar.slider(
    "Downtime Cost/Day ($M)", 0.0, dcost_max_m, default_cost_per_day / 1_000_000, 0.1
)
cost_per_day = cost_per_day_m * 1_000_000
downtime_cost = downtime_days * cost_per_day

st.sidebar.markdown("### Incident Likelihood")
aro_before_pct = st.sidebar.slider("Likelihood Before Controls (%)", 0, 100, 30)
aro_after_pct = st.sidebar.slider("Likelihood After Controls (%)", 0, 100, 10)

st.sidebar.markdown("### View Options")
executive_mode = st.sidebar.checkbox("Enable Executive Mode", value=True)
compact_mode = st.sidebar.checkbox("Enable Compact Layout", value=True)

# === CALCULATIONS ===
modifiers = {
    "Initial": 1.3,
    "Developing": 1.15,
    "Defined": 1.0,
    "Managed": 0.85,
    "Optimized": 0.7
}
aro_before = (aro_before_pct / 100) * modifiers[maturity_level]
aro_after = (aro_after_pct / 100) * modifiers[maturity_level]

sle = base_sle + user_breach_cost + downtime_cost
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = risk_reduction / controls_cost if controls_cost else 0
roi_pct = roi * 100
roi_color = "#e06c75" if roi_pct < 100 else "#e5c07b" if roi_pct < 200 else "#00cc96"

# === PAGE TITLE ===
st.markdown("<h1 style='margin-top: 10px; text-align: center;'>Cyber Risk ROI Calculator</h1>", unsafe_allow_html=True)

# === KPI METRIC BOXES ===
st.markdown(f"""
<style>
.metric-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin: 30px 0;
}}
.metric-box {{
  background-color: #1f1f1f;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  color: white;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
}}
.metric-box h4 {{
  margin: 0 0 8px 0;
  color: #61dafb;
  font-size: 18px;
}}
.metric-box p {{
  font-size: 28px;
  margin: 0;
  font-weight: bold;
}}
</style>
<div class="metric-grid">
  <div class="metric-box">
    <h4>ALE Before Controls</h4>
    <p>{{ale_before / 1_000_000:.2f}}M</p>
  </div>
  <div class="metric-box">
    <h4>ALE After Controls</h4>
    <p>{{ale_after / 1_000_000:.2f}}M</p>
  </div>
  <div class="metric-box">
    <h4>Risk Reduction</h4>
    <p>{{risk_reduction / 1_000_000:.2f}}M</p>
  </div>
  <div class="metric-box">
    <h4>ROI</h4>
    <p style="color:{{roi_color}};">{{roi_pct:.1f}}%</p>
  </div>
</div>
<p style='text-align: center; margin-top: 15px; font-size: 14px; color: #aaa;'>
  📘 Calculations: ALE = SLE × ARO, ROI = Risk Reduction ÷ Cybersecurity Budget
</p>
""", unsafe_allow_html=True)

# === THEME-STYLING HELPER ===
def apply_theme_style(ax):
    ax.set_facecolor("none")
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    for spine in ax.spines.values():
        spine.set_visible(False)

# === COST COMPONENT BREAKDOWN (ALWAYS VISIBLE) ===
# === INCIDENT COST BREAKDOWN CHART ===
st.subheader("Incident Cost Components")
incident_cost_data = pd.DataFrame({
    "Component": [
        "Base Incident Cost",
        "User Breach Cost",
        "Downtime Cost"
    ],
    "Millions": [
        base_sle / 1e6,
        user_breach_cost / 1e6,
        downtime_cost / 1e6
    ]
})
fig_incident, ax_incident = plt.subplots(figsize=(6, 3) if compact_mode else (8, 4), facecolor="none")
bars = ax_incident.barh(
    incident_cost_data["Component"],
    incident_cost_data["Millions"],
    color=["#EF553B", "#00CC96", "#AB63FA"]
)
for bar, val in zip(bars, incident_cost_data["Millions"]):
    ax_incident.text(
        val + 0.1,
        bar.get_y() + bar.get_height() / 2,
        f"{val:.2f}M",
        va="center",
        color=text_color
    )
ax_incident.invert_yaxis()
ax_incident.set_xlabel("Millions $")
apply_theme_style(ax_incident)
st.pyplot(fig_incident, transparent=True)

# === ADDITIONAL CHARTS IF EXEC MODE DISABLED ===
if not executive_mode:
    st.subheader("Annual Loss Exposure (Before vs After Controls)")
    fig1, ax1 = plt.subplots(figsize=(5, 3) if compact_mode else (6, 4), facecolor="none")
    values = [ale_before / 1e6, ale_after / 1e6]
    bars = ax1.bar(["Before Controls", "After Controls"], values, color=["#EF553B", "#00CC96"])
    for bar, val in zip(bars, values):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.1,
            f"{val:.2f}M",
            ha="center",
            color=text_color
        )
    ax1.set_ylabel("ALE (Millions $)")
    apply_theme_style(ax1)
    st.pyplot(fig1, transparent=True)

    st.subheader("Cost vs Risk Reduction")
    fig2, ax2 = plt.subplots(figsize=(4, 3) if compact_mode else (6, 4), facecolor="none")
    wedges, texts, autotexts = ax2.pie(
        [controls_cost / 1e6, risk_reduction / 1e6],
        labels=["Cybersecurity Budget", "Risk Reduction"],
        autopct="%1.1f%%",
        startangle=90,
        colors=["#636EFA", "#00CC96"],
        wedgeprops=dict(width=0.3),
        textprops={"color": text_color, "weight": "bold"}
    )
    ax2.axis("equal")
    st.pyplot(fig2, transparent=True)
