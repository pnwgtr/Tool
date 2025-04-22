import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# Hide Streamlit footer and menu for a clean UI
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

# Input Parameters
st.sidebar.header("Input Parameters")
controls_cost_m = st.sidebar.slider(
    "Cost of Preventative Controls ($M)",
    min_value=0.0, max_value=10.0, value=1.1, step=0.1,
    format="%0.1fM",
    help="Annual cost of security measures implemented to prevent significant cyber incidents."
)
controls_cost = controls_cost_m * 1_000_000

revenue_m = st.sidebar.slider(
    "Annual Revenue ($M)",
    min_value=0.0, max_value=1000.0, value=500.0, step=10.0,
    format="%0.0fM",
    help="Your organization’s annual gross revenue."
)
revenue = revenue_m * 1_000_000

default_cost_per_day = revenue / 365

# Breach Impact Assumptions
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

monitoring_cost_per_user = st.sidebar.slider(
    "Cost per User for Credit Monitoring ($)",
    min_value=0, max_value=20, value=10, step=1,
    help="Estimated cost per user to provide credit monitoring after a breach."
)

sle_m = st.sidebar.slider(
    "Base SLE (Excluding Users) - Incident Cost ($M)",
    min_value=0.0, max_value=20.0, value=6.0, step=1.0,
    format="%0.1fM",
    help="Single Loss Expectancy: core cost of one significant incident (e.g., forensic, legal, remediation), excluding per-user and downtime costs."
)
base_sle = sle_m * 1_000_000
user_breach_cost = user_count * monitoring_cost_per_user

# Downtime Impact Assumptions
st.sidebar.markdown("### Downtime Impact Assumptions")
downtime_days = st.sidebar.slider(
    "Estimated Days of Downtime",
    min_value=5, max_value=30, value=5,
    help="Estimated number of days your business would be partially or fully down due to a major incident."
)
# Slider for daily downtime cost in millions, up to 2× baseline
dcost_max_m = (revenue / 365) / 1_000_000 * 2
cost_per_day_m = st.sidebar.slider(
    "Estimated Cost per Day of Downtime ($M)",
    min_value=0.0,
    max_value=dcost_max_m,
    value=(default_cost_per_day / 1_000_000),
    step=0.1,
    format="%0.1fM",
    help="Estimated daily revenue loss due to disruption. Baseline: ${(default_cost_per_day/1_000_000):.2f}M; max set to 2× baseline for testing."
)
st.sidebar.markdown(
    f"<div style='font-size:12px;color:gray;'>📍 Baseline daily cost: ${(default_cost_per_day/1_000_000):.2f}M</div>",
    unsafe_allow_html=True
)
cost_per_day = cost_per_day_m * 1_000_000
downtime_cost = downtime_days * cost_per_day

# ARO Sliders
st.sidebar.markdown("### Incident Likelihood")
aro_before_percent = st.sidebar.slider(
    "Likelihood of Incident BEFORE Controls (%)",
    0, 100, 30,
    help="Estimated inherent annual likelihood of a significant cyber incident before controls (default 30%, based on industry benchmarks)."
)
aro_after_percent = st.sidebar.slider(
    "Likelihood of Incident AFTER Controls (%)",
    0, 100, 10,
    help="Estimated annual likelihood of a significant cyber incident after controls."
)
aro_before = aro_before_percent / 100
aro_after = aro_after_percent / 100

# Adjust for maturity
modifiers = {"Initial":1.3,"Developing":1.15,"Defined":1.0,"Managed":0.85,"Optimized":0.7}
aro_before *= modifiers[maturity_level]
aro_after *= modifiers[maturity_level]

# === RISK SURFACE OVERVIEW ===
with st.expander("🔍 Understanding Our Risk Surface", expanded=True):
    st.markdown(f"""
This calculator models the potential financial impact of a significant cyber event based on our organization's digital footprint and business operations.

**Key Factors:**
- **{user_count_k}K user accounts** with sensitive data
- **Mission-critical systems** needing high uptime
- **Vendor and integration exposures**
- **${revenue:,.0f} annual revenue** at risk
- **${controls_cost:,.0f} controls spend** per year

Variables:
- **SLE** = base + users + downtime costs
- **ARO** = probability of an event (adjusted for maturity)
- **Controls Cost** = preventive spend
- **Downtime Cost** = outage days × daily cost

Program maturity (_{maturity_level}_) influences the likelihood inputs.    
    """)

# === CALCULATIONS ===
sle = base_sle + user_breach_cost + downtime_cost
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = risk_reduction / controls_cost if controls_cost else 0
ale_before_pct = (ale_before / revenue) * 100 if revenue else 0
ale_after_pct = (ale_after / revenue) * 100 if revenue else 0
risk_red_pct = (risk_reduction / revenue) * 100 if revenue else 0

# === VISUAL COMPARISON ===
min_cost_per_day = revenue / 365
if cost_per_day < min_cost_per_day:
    st.warning(f"⚠️ Estimated daily cost (${cost_per_day:,.0f}) is below baseline (${min_cost_per_day:,.0f}).")
else:
    st.success(f"✅ Estimated daily cost (${cost_per_day:,.0f}) ≥ baseline (${min_cost_per_day:,.0f}).")

# === METRICS OUTPUT ===
colors = {"Initial":"red","Developing":"orange","Defined":"yellow","Managed":"lightgreen","Optimized":"green"}
col1, col2, col3 = st.columns(3)
col1.metric("ALE Before", f"${ale_before/1_000_000:.2f}M")
col2.metric("ALE After", f"${ale_after/1_000_000:.2f}M")
col3.metric("Risk Reduction", f"${risk_reduction/1_000_000:.2f}M")
# ROI with tooltip
st.markdown(
    f"### ROI: <span title='Return on Investment: (Risk Reduction ÷ Control Cost) × 100'>{(roi*100):.1f}%</span>",
    unsafe_allow_html=True
)

st.markdown("### Impact as % of Revenue"))
col4, col5, col6 = st.columns(3)
col4.metric("ALE Before", f"{ale_before_pct:.2f}%")
col5.metric("ALE After", f"{ale_after_pct:.2f}%")
col6.metric("Reduction", f"{risk_red_pct:.2f}%")

# === BAR CHART ===
st.subheader("Annual Loss Exposure")
ale_df = pd.DataFrame({"Scenario":["Before","After"],"ALE_M":[ale_before/1_000_000,ale_after/1_000_000]})
st.bar_chart(ale_df.set_index("Scenario"))

# === DONUT CHART ===
st.subheader("Cost vs Risk Reduction")
cost_df = pd.DataFrame({"Category":["Controls","Reduction"],"M":[controls_cost/1_000_000,risk_reduction/1_000_000]})
fig, ax = plt.subplots(facecolor='none')
ax.set_facecolor('none')
wedges, texts, autotexts = ax.pie(cost_df['M'], labels=cost_df['Category'], autopct="%1.1f%%", startangle=90, wedgeprops=dict(edgecolor='black'))
for t in texts+autotexts: t.set_color('white')
ax.axis('equal')
st.pyplot(fig, transparent=True)

# === FAQ ===
with st.sidebar.expander("📘 What These Mean", expanded=False):
    st.markdown("""
**SLE:** Cost per incident.  
**ARO:** Likelihood of incident.  
**ALE:** Annual expected loss.  
**ROI:** Return on controls.  
""")
