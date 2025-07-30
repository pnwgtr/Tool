# === FULL CFO-FRIENDLY CYBER RISK ROI APP (LARGER KPI VALUES) ===
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === GLOBAL STYLING FOR TIGHTER LAYOUT & HEADER SIZES ===
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    h1 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-size:28px !important;
    }
    h3 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-size:22px !important;
    }
</style>
""", unsafe_allow_html=True)

# === THEME ===
text_color = "black" if st.get_option("theme.base") == "light" else "white"

# === QUICK-START ===
if "show_guide" not in st.session_state:
    st.session_state.show_guide = False
if st.sidebar.button("💡 Quick Start Guide"):
    st.session_state.show_guide = not st.session_state.show_guide
if st.session_state.show_guide:
    with st.sidebar.expander("👋 Getting Started", True):
        st.markdown("""
Adjust these inputs to model your cybersecurity ROI.
- **Cybersecurity Budget** – Annual spend on controls
- **Annual Revenue** – Used to derive downtime loss
- **Users Affected** – For breach-impact cost
- **ARO Before/After** – Likelihood before/after controls
""")

# === SIDEBAR INPUTS ===
st.sidebar.header("Input Parameters")
maturity_level = st.sidebar.select_slider(
    "Cybersecurity Program Maturity",
    ["Initial", "Developing", "Defined", "Managed", "Optimized"],
    value="Initial")

with st.sidebar.expander("ℹ️ What do these maturity levels mean?", False):
    st.markdown(
        """
**Initial** – Ad-hoc and reactive; processes are informal or not documented.
**Developing** – Basic policies in place; some repeatable practices but still largely siloed.
**Defined** – Processes are documented, standardized, and communicated across the organization.
**Managed** – Controls are actively measured, monitored, and optimized; management uses metrics to make decisions.
**Optimized** – Continuous improvement culture with automated, adaptive controls aligned to business objectives.
        """
    )

controls_cost_m = st.sidebar.slider("Cybersecurity Budget ($M)", 0.0, 10.0, 1.1, 0.1)
controls_cost = controls_cost_m * 1_000_000
revenue_m = st.sidebar.slider("Annual Revenue ($M)", 0.0, 1000.0, 500.0, 10.0)
revenue = revenue_m * 1_000_000
default_cost_per_day = revenue / 365

user_count_k = st.sidebar.slider("Estimated Affected Users (K)", 0, 1000, 600, 10)
user_count = user_count_k * 1000
monitoring_cost_per_user = st.sidebar.slider("Credit-Monitoring Cost/User ($)", 0, 20, 10, 1)

sle_m = st.sidebar.slider("Base Incident Cost ($M)", 0.0, 10.0, 6.0, 0.1)
base_sle = sle_m * 1_000_000
user_breach_cost = user_count * monitoring_cost_per_user

st.sidebar.markdown("### Downtime")
downtime_days = st.sidebar.slider("Estimated Days of Downtime", 5, 30, 5)
dcost_max_m = (default_cost_per_day / 1_000_000) * 2
cost_per_day_m = st.sidebar.slider("Cost per Day ($M)", 0.0, dcost_max_m, default_cost_per_day / 1_000_000, 0.1)
cost_per_day = cost_per_day_m * 1_000_000
downtime_cost = downtime_days * cost_per_day

st.sidebar.markdown("### Incident Likelihood")
aro_before_pct = st.sidebar.slider("Likelihood Before Controls (%)", 0, 100, 30)
aro_after_pct = st.sidebar.slider("Likelihood After Controls (%)", 0, 100, 10)

st.sidebar.markdown("### View Options")
executive_mode = st.sidebar.checkbox("Enable Executive Mode", True)
compact_mode = st.sidebar.checkbox("Enable Compact Layout", True)

# === CALC ===
mod = {"Initial": 1.3, "Developing": 1.15, "Defined": 1.0, "Managed": 0.85, "Optimized": 0.7}
aro_before = (aro_before_pct / 100) * mod[maturity_level]
aro_after = (aro_after_pct / 100) * mod[maturity_level]

sle = base_sle + user_breach_cost + downtime_cost
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi_pct = (risk_reduction / controls_cost * 100) if controls_cost else 0
roi_color = "#e06c75" if roi_pct < 100 else "#e5c07b" if roi_pct < 200 else "#00cc96"

total_incident_cost = sle
benchmark_pct = 0.005
benc
