import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === TITLE ===
st.title("Cyber Risk ROI Calculator")

# === SIDEBAR INPUTS ===

st.sidebar.markdown("### Program Maturity Level")
maturity_level = st.sidebar.select_slider(
    "Cybersecurity Program Maturity",
    options=["Initial", "Developing", "Defined", "Managed", "Optimized"],
    value="Defined",
    help="Indicates the overall maturity of your cybersecurity program, based on people, process, and technology."
)

st.sidebar.header("Input Parameters")
controls_cost_m = st.sidebar.slider(
    "Cost of Preventative Controls ($M)", min_value=0.0, max_value=20.0, value=1.1, step=0.1,
    help="Annual cost of security measures implemented to prevent significant cyber incidents."
)
controls_cost = controls_cost_m * 1_000_000

revenue_m = st.sidebar.slider(
    "Annual Revenue ($M)", min_value=0.0, max_value=5000.0, value=500.0, step=10.0,
    help="Your organization’s annual gross revenue."
)
revenue = revenue_m * 1_000_000

default_cost_per_day = round(revenue / 365)

st.sidebar.markdown("### Breach Impact Assumptions")
user_count = st.sidebar.slider(
    "Estimated Affected Users", min_value=0, max_value=1000000, value=600000, step=10000,
    help="Estimated number of users who would require credit monitoring in the event of a breach."
)
monitoring_cost_per_user = st.sidebar.slider(
    "Cost per User for Credit Monitoring ($)", min_value=0, max_value=100, value=10, step=1,
    help="Estimated cost per user to provide credit monitoring after a breach."
)

sle_m = st.sidebar.slider(
    "Base SLE (Excluding Users) - Incident Cost ($M)", min_value=0.0, max_value=100.0, value=6.0, step=1.0,
    help="Estimated cost of a significant cyber incident, not including per-user costs."
)
base_sle = sle_m * 1_000_000
user_breach_cost = user_count * monitoring_cost_per_user

st.sidebar.markdown("### Downtime Impact Assumptions")
downtime_days = st.sidebar.slider(
    "Estimated Days of Downtime", min_value=5, max_value=30, value=5,
    help="Estimated number of days your business would be partially or fully down due to a major incident."
)
cost_per_day_k = st.sidebar.slider(
    "Estimated Cost per Day of Downtime ($K)",
    min_value=0,
    max_value=1000,
    value=int(default_cost_per_day / 1000),
    step=5,
    format="%dK",
    help=f"Estimated daily revenue loss or cost due to operational disruption. Based on revenue, the minimum estimated daily cost is ${int(default_cost_per_day / 1000)}K."
)
cost_per_day = cost_per_day_k * 1000
