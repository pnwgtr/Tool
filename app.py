import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === TITLE ===
st.title("Cyber Risk ROI Calculator")

# === SIDEBAR INPUTS ===

# Program Maturity
st.sidebar.markdown("### Program Maturity Level")
maturity_level = st.sidebar.select_slider(
    "Cybersecurity Program Maturity",
    options=["Initial", "Developing", "Defined", "Managed", "Optimized"],
    value="Defined",
    help="Indicates the overall maturity of your cybersecurity program, based on people, process, and technology."
)

# Controls Cost
st.sidebar.header("Input Parameters")
controls_cost_m = st.sidebar.slider(
    "Cost of Preventative Controls ($M)",
    min_value=0.0, max_value=20.0, value=1.1, step=0.1,
    help="Annual cost of security measures implemented to prevent significant cyber incidents."
)
controls_cost = controls_cost_m * 1_000_000

# Revenue
revenue_m = st.sidebar.slider(
    "Annual Revenue ($M)",
    min_value=0.0, max_value=5000.0, value=500.0, step=10.0,
    help="Your organization’s annual gross revenue."
)
revenue = revenue_m * 1_000_000

# Breach Impact: Users
st.sidebar.markdown("### Breach Impact Assumptions")
user_count_k = st.sidebar.slider(
    "Estimated Affected Users",
    min_value=0, max_value=1000, value=600, step=10,
    format="%dK",
    help="Estimated number of users who would require credit monitoring in the event of a breach."
)
st.sidebar.markdown(
    f"<div style='font-size:12px;color:gray;'>📍 Based on current data, expected user count is around {user_count_k}K</div>",
    unsafe_allow_html=True
)
user_count = user_count_k * 1000

# Per‑user monitoring cost
monitoring_cost_per_user = st.sidebar.slider(
    "Cost per User for Credit Monitoring ($)",
    min_value=0, max_value=20, value=10, step=1,
    help="Estimated cost per user to provide credit monitoring after a breach."
)

# Base SLE
sle_m = st.sidebar.slider(
    "Base SLE (Excluding Users) - Incident Cost ($M)",
    min_value=0.0, max_value=100.0, value=6.0, step=1.0,
    help="Estimated cost of a significant cyber incident, not including per-user costs."
)
base_sle = sle_m * 1_000_000
user_breach_cost = user_count * monitoring_cost_per_user

# Downtime Impact
st.sidebar.markdown("### Downtime Impact Assumptions")
downtime_days = st.sidebar.slider(
    "Estimated Days of Downtime",
    min_value=5, max_value=30, value=5,
    help="Estimated number of days your business would be partially or fully down due to a major incident."
)
default_cost_per_day = round(revenue / 365)
cost_per_day_k = st.sidebar.slider(
    "Estimated Cost per Day of Downtime ($K)",
    min_value=0, max_value=1000, value=int(default_cost_per_day/1000), step=5,
    format="%dK",
    help=f"Estimated daily revenue loss due to operational disruption. Baseline: ${int(default_cost_per_day/1000)}K."
)
st.sidebar.markdown(
    f"<div style='font-size:12px;color:gray;'>📍 Minimum daily cost based on revenue: ${int(default_cost_per_day/1000)}K</div>",
    unsafe_allow_html=True
)
cost_per_day = cost_per_day_k * 1000
downtime_cost = downtime_days * cost_per_day

# ARO sliders
aro_before_percent = st.sidebar.slider(
    "Likelihood of Incident BEFORE Controls (%)", 0, 100, 20,
    help="Estimated likelihood of a significant incident occurring without controls in place."
)
aro_after_percent = st.sidebar.slider(
    "Likelihood of Incident AFTER Controls (%)", 0, 100, 10,
    help="Estimated likelihood of a significant incident occurring after controls are implemented."
)
aro_before = aro_before_percent / 100
aro_after = aro_after_percent / 100

# Apply maturity modifier
maturity_modifiers = {
    "Initial": 1.3,
    "Developing": 1.15,
    "Defined": 1.0,
    "Managed": 0.85,
    "Optimized": 0.7
}
aro_modifier = maturity_modifiers[maturity_level]
aro_before *= aro_modifier
aro_after *= aro_modifier

# === RISK SURFACE OVERVIEW ===
with st.expander("🔍 Understanding Our Risk Surface", expanded=True):
    st.markdown(f"""
This calculator models the potential financial impact of a significant cyber event based on our organization's digital footprint and business operations.

**Key Factors in Our Risk Surface:**
- **{user_count_k}K user accounts** containing sensitive personal data
- **Mission-critical systems** that cannot be down for extended periods
- **Third-party integrations** and vendor dependencies
- **${revenue:,.0f} in annual revenue**, reliant on continuous uptime
- **Preventative control spend of ${controls_cost:,.0f} annually**

These factors contribute to a heightened risk profile and help define the variables below:
- **SLE** (Single Loss Expectancy) = base + user + downtime costs
- **ARO** (Annual Rate of Occurrence) = yearly likelihood of a breach
- **Downtime cost** = outage days × daily cost
- **Controls cost** = annual spend
- **Program maturity** = _{maturity_level}_ (adjusts ARO)
    """)

# === CALCULATIONS ===
sle = base_sle + user_breach_cost + downtime_cost
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = (risk_reduction / controls_cost) if controls_cost > 0 else 0
ale_before_pct = (ale_before / revenue) * 100 if revenue > 0 else 0
ale_after_pct = (ale_after / revenue) * 100 if revenue > 0 else 0
risk_reduction_pct = (risk_reduction / revenue) * 100 if revenue > 0 else 0

# === VISUAL COMPARISON: Cost Per Day ===
min_cost_per_day = revenue / 365
if cost_per_day < min_cost_per_day:
    st.warning(f"⚠️ Your estimated daily cost of downtime (${cost_per_day:,}) is **below** the baseline (${min_cost_per_day:,.0
