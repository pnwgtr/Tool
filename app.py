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
# Program Maturity Level
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
    f"<div style='font-size:12px;color:gray;'>📍 Expected user count ~{user_count_k}K</div>",
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
    min_value=0.0, max_value=10.0, value=6.0, step=.1,
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
dcost_max_m = (default_cost_per_day / 1_000_000) * 2
cost_per_day_m = st.sidebar.slider(
    "Estimated Cost per Day of Downtime ($M)",
    min_value=0.0,
    max_value=dcost_max_m,
    value=(default_cost_per_day / 1_000_000),
    step=0.1,
    format="%0.1fM",
    help=f"Estimated daily revenue loss. Baseline: ${(default_cost_per_day/1_000_000):.2f}M; max 2× baseline."
)
st.sidebar.markdown(
    f"<div style='font-size:12px;color:gray;'>📍 Baseline daily cost: ${(default_cost_per_day/1_000_000):.2f}M</div>",
    unsafe_allow_html=True
)
cost_per_day = cost_per_day_m * 1_000_000
downtime_cost = downtime_days * cost_per_day

# Incident Likelihood (ARO)
st.sidebar.markdown("### Incident Likelihood")
aro_before_percent = st.sidebar.slider(
    "Likelihood of Incident BEFORE Controls (%)",
    0, 100, 30,
    help="Inherent annual likelihood of a significant incident before controls (default 30%)."
)
aro_after_percent = st.sidebar.slider(
    "Likelihood of Incident AFTER Controls (%)",
    0, 100, 10,
    help="Annual likelihood of a significant incident after controls."
)
aro_before = aro_before_percent / 100
aro_after = aro_after_percent / 100

# Adjust for maturity
modifiers = {"Initial":1.3, "Developing":1.15, "Defined":1.0, "Managed":0.85, "Optimized":0.7}
aro_before *= modifiers[maturity_level]
aro_after *= modifiers[maturity_level]

# === RISK SURFACE OVERVIEW ===
with st.expander("🔍 Understanding Our Risk Surface", expanded=True):
    st.markdown(f"""
This calculator models the potential financial impact of a significant cyber event.

**Risk Surface:**
- **{user_count_k}K user accounts**
- **${revenue:,.0f} in revenue**
- **${controls_cost:,.0f} in controls spend**
- **Program maturity:** _{maturity_level}_

Variables feed calculations below:
- **SLE** = base + user breach + downtime
- **ARO** = likelihood (adjusted by maturity)
- **Controls cost** = preventive spend
- **Downtime cost** = days × daily cost
""")

# === CALCULATIONS ===
sle = base_sle + user_breach_cost + downtime_cost
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = risk_reduction / controls_cost if controls_cost else 0
ale_before_pct = ale_before / revenue * 100 if revenue else 0
ale_after_pct = ale_after / revenue * 100 if revenue else 0
risk_red_pct = risk_reduction / revenue * 100 if revenue else 0

# === VISUAL COMPARISON ===
min_cost_per_day = default_cost_per_day
if cost_per_day < min_cost_per_day:
    st.warning(
        f"⚠️ Your estimated daily downtime cost of ${cost_per_day:,.0f} is below the expected baseline of ${min_cost_per_day:,.0f} (revenue/365). "
        "Underestimating downtime costs can leave you unprepared for recovery expenses and broader business impact. Consider revising this value."
    )
else:
    st.success(
        f"✅ Your estimated daily downtime cost of ${cost_per_day:,.0f} meets or exceeds the baseline of ${min_cost_per_day:,.0f}, indicating a realistic assessment of potential outage impact."
    )

# === METRICS OUTPUT ===
col1, col2, col3 = st.columns(3)
col1.metric("ALE Before", f"${ale_before/1_000_000:.2f}M")
col2.metric("ALE After", f"${ale_after/1_000_000:.2f}M")
col3.metric("Risk Reduction", f"${risk_reduction/1_000_000:.2f}M")
# ROI with tooltip and tip
st.markdown(
    f"### ROI: <span title='Return on Investment: (Risk Reduction ÷ Control Cost) × 100'>{(roi*100):.1f}%</span>",
    unsafe_allow_html=True
)
st.caption("Tip: ROI > 200% and ratio < 1.0 generally indicate strong cybersecurity value.")

# === ANNUAL LOSS EXPOSURE CHART ===
st.subheader("Annual Loss Exposure (Before vs After Controls)")
bar_fig, bar_ax = plt.subplots(facecolor='none')
bar_ax.set_facecolor('none')
scenarios = ["Before Controls", "After Controls"]
values = [ale_before/1_000_000, ale_after/1_000_000]
bar_colors = ['#EF553B', '#636EFA']
bar_container = bar_ax.bar(scenarios, values, color=bar_colors)
# Annotate bars
for bar, v in zip(bar_container, values):
    bar_ax.text(bar.get_x() + bar.get_width() / 2, v + max(values)*0.02, f"{v:.2f}M", ha='center', color='white')
# Style axes
bar_ax.set_ylabel('ALE (Millions $)', color='white')
bar_ax.set_ylim(0, max(values)*1.25)
for label in bar_ax.get_xticklabels() + bar_ax.get_yticklabels():
    label.set_color('white')
bar_ax.spines['top'].set_visible(False)
bar_ax.spines['right'].set_visible(False)
bar_ax.spines['left'].set_color('white')
bar_ax.spines['bottom'].set_color('white')
st.pyplot(bar_fig, transparent=True)

# === DONUT CHART ===
st.subheader("Cost vs Risk Reduction")
cost_df = pd.DataFrame({"Category": ["Controls", "Reduction"], "M": [controls_cost/1_000_000, risk_reduction/1_000_000]})
fig, ax = plt.subplots(facecolor='none')
ax.set_facecolor('none')
wedges, texts, autotexts = ax.pie(cost_df['M'], labels=cost_df['Category'], autopct="%1.1f%%", startangle=90, wedgeprops=dict(edgecolor='black'))
for t in texts+autotexts:
    t.set_color('white')
ax.axis('equal')
st.pyplot(fig, transparent=True)


# === COST COMPONENT BREAKDOWN ===
st.subheader("Cost Component Breakdown")
cost_comp_df = pd.DataFrame({
    "Component": ["Preventative Controls", "User Breach Cost", "Downtime Cost", "Total Incident Cost"],
    "Amount (Millions $)": [
        controls_cost / 1_000_000,
        user_breach_cost / 1_000_000,
        downtime_cost / 1_000_000,
        sle / 1_000_000
    ]
})
# Matplotlib horizontal bar chart for clear comparison
fig3, ax3 = plt.subplots(facecolor='none')
ax3.set_facecolor('none')
components = cost_comp_df['Component']
amounts = cost_comp_df['Amount (Millions $)']
colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA']
bars = ax3.barh(components, amounts, color=colors)
# Annotate values at end of bars
max_amount = amounts.max()
for bar, v in zip(bars, amounts):
    ax3.text(
        v + max_amount * 0.01,
        bar.get_y() + bar.get_height()/2,
        f"{v:.2f}M",
        va='center',
        color='white'
    )
# Set axis text to white
for label in ax3.get_xticklabels() + ax3.get_yticklabels():
    label.set_color('white')
ax3.xaxis.label.set_color('white')
# Hide spines for a cleaner look
for spine in ax3.spines.values():
    spine.set_color('none')
ax3.set_xlabel('Amount (Millions $)')
ax3.invert_yaxis()
st.pyplot(fig3, transparent=True)

# === FAQ ===
with st.sidebar.expander("📘 What These Mean", expanded=False):
    st.markdown("""
**SLE:** Cost per incident.
**ARO:** Likelihood of incident.
**ALE:** Annual expected loss.
**ROI:** Return on controls.
""")
