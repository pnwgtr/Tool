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

default_cost_per_day = round(revenue / 365)

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
    min_value=0.0, max_value=100.0, value=6.0, step=1.0,
    help="Single Loss Expectancy: core cost of one significant incident (e.g., forensic, legal, remediation), excluding per-user credit monitoring and downtime losses."
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
cost_per_day_k = st.sidebar.slider(
    "Estimated Cost per Day of Downtime ($K)",
    min_value=0, max_value=1000, value=int(default_cost_per_day/1000), step=5,
    format="%dK",
    help=f"Estimated daily revenue loss due to operational disruption. Baseline: ${int(default_cost_per_day/1000)}K."
)
st.sidebar.markdown(
    f"<div style='font-size:12px;color:gray;'>📍 Minimum daily cost based on revenue: {int(default_cost_per_day/1000)}K</div>",
    unsafe_allow_html=True
)
cost_per_day = cost_per_day_k * 1000

downtime_cost = downtime_days * cost_per_day

# ARO Sliders
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

# Apply Maturity Modifier
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
- **SLE** (Single Loss Expectancy) = estimated loss from one significant incident (base + user + downtime costs)
- **ARO** (Annual Rate of Occurrence) = estimated yearly likelihood of a breach
- **Downtime cost** = based on expected outage days × cost per day
- **Controls cost** = annual spend to reduce likelihood and impact
- **Program maturity rated as _{maturity_level}_**, influencing how likely incidents are to occur
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
    st.warning(f"⚠️ Your estimated daily cost of downtime (${cost_per_day:,}) is **below** the baseline (${min_cost_per_day:,.0f}).")
else:
    st.success(f"✅ Your estimated daily cost of downtime (${cost_per_day:,}) meets or exceeds the minimum (${min_cost_per_day:,.0f}).")

# === METRICS OUTPUT ===
maturity_colors = {
    "Initial": "red",
    "Developing": "orange",
    "Defined": "yellow",
    "Managed": "lightgreen",
    "Optimized": "green"
}
maturity_color = maturity_colors[maturity_level]
st.markdown(
    f"### Program Maturity: <span style='color:{maturity_color}; font-weight:bold' title='Maturity reflects the strength of your cybersecurity program. Higher maturity reduces the likelihood of significant incidents.'>{maturity_level}</span>",
    unsafe_allow_html=True
)

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

# === BAR CHART ===
st.subheader("Annual Loss Exposure: Before vs After Controls")
ale_df = pd.DataFrame({
    "Scenario": ["Before Controls", "After Controls"],
    "ALE (Millions $)": [ale_before / 1_000_000, ale_after / 1_000_000]
})
st.bar_chart(ale_df.set_index("Scenario"))

# === PIE CHART ===
st.subheader("Cost vs Risk Reduction Breakdown")
cost_data = pd.DataFrame({
    "Category": ["Preventative Controls Cost", "Risk Reduction"],
    "Amount (Millions $)": [controls_cost / 1_000_000, risk_reduction / 1_000_000]
})
fig2, ax2 = plt.subplots(facecolor='none')
ax2.set_facecolor('none')
wedges, texts, autotexts = ax2.pie(
    cost_data["Amount (Millions $)"],
    labels=cost_data["Category"],
    autopct="%1.1f%%",
    startangle=90,
    textprops={'color':'white','fontsize':12},
    wedgeprops=dict(edgecolor='black')
)
for text in texts + autotexts:
    text.set_color('white')
ax2.axis("equal")
st.pyplot(fig2, transparent=True)

# === FAQ ===
with st.sidebar.expander("📘 What Do These Terms Mean?", expanded=False):
    st.markdown("""
**SLE (Single Loss Expectancy):**  
Estimated cost of one significant cyber event.

**ARO (Annualized Rate of Occurrence):**  
Probability a significant incident happens in a year.

**ALE (Annualized Loss Expectancy):**  
Expected yearly financial loss due to cyber incidents.  
**Formula:** `ALE = SLE × ARO`

**ROI (Return on Investment):**  
Value gained from investing in controls.  
**Formula:** `(Risk Reduction ÷ Control Cost) × 100`

**Cost vs. Risk Reduction Ratio:**  
Ratio < 1 means efficient spend.

**User Breach Cost:**  
Credit monitoring cost for affected users.

**Downtime Cost:**  
Lost revenue due to operational disruption.

---
Want to go deeper? [Learn FAIR methodology →](https://www.fairinstitute.org/fair-model)
    """)
