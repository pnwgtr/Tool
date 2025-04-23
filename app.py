import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# Inject tooltip CSS
tooltip_style = """
<style>
.tooltip { position: relative; display:inline-block; }
.tooltip .tooltiptext { visibility: hidden; width: 160px; background-color: #555; color: #fff; text-align: center; border-radius: 6px; padding: 5px; position: absolute; z-index: 1; bottom: 125%; left: 50%; margin-left: -80px; opacity: 0; transition: opacity 0.3s; }
.tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }
</style>
"""
st.markdown(tooltip_style, unsafe_allow_html=True)

# Hide Streamlit footer and menu for a clean UI
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# === TITLE ===
st.markdown("<h1 style='text-align: center;'>Cyber Risk ROI Calculator</h1>", unsafe_allow_html=True)

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
    "Cost of Preventative Controls ($M)", 0.0, 10.0, 1.1, 0.1, format="%0.1fM"
)
controls_cost = controls_cost_m * 1_000_000

revenue_m = st.sidebar.slider(
    "Annual Revenue ($M)", 0.0, 1000.0, 500.0, 10.0, format="%0.0fM"
)
revenue = revenue_m * 1_000_000

default_cost_per_day = revenue / 365

st.sidebar.markdown("### Breach Impact Assumptions")
user_count_k = st.sidebar.slider(
    "Estimated Affected Users (K)", 0, 1000, 600, 10, format="%dK",
    help="Estimated number of users who would require credit monitoring in the event of a breach."
)
user_count = user_count_k * 1000
monitoring_cost_per_user = st.sidebar.slider(
    "$ Cost per User for Credit Monitoring", 0, 20, 10, 1, format="$%d",
    help="Estimated cost per user to provide credit monitoring after a breach."
)

sle_m = st.sidebar.slider(
    "Base SLE (Excluding Users) - Incident Cost ($M)", 0.0, 10.0, 6.0, 0.1, format="%0.1fM",
    help="Single Loss Expectancy: core cost of one significant incident, excluding per-user and downtime costs."
)
base_sle = sle_m * 1_000_000
user_breach_cost = user_count * monitoring_cost_per_user

st.sidebar.markdown("### Downtime Impact Assumptions")
downtime_days = st.sidebar.slider(
    "Estimated Days of Downtime", 5, 30, 5,
    help="Estimated number of days your business would be partially or fully down due to a major incident."
)
dcost_max_m = (default_cost_per_day / 1_000_000) * 2
cost_per_day_m = st.sidebar.slider(
    "Estimated Cost per Day of Downtime ($M)", 0.0, dcost_max_m, default_cost_per_day/1_000_000, 0.1, format="%0.1fM",
    help=f"Baseline daily cost: ${(default_cost_per_day/1_000_000):.2f}M; max 2× baseline."
)
cost_per_day = cost_per_day_m * 1_000_000
downtime_cost = downtime_days * cost_per_day

st.sidebar.markdown("### Incident Likelihood")
aro_before_percent = st.sidebar.slider(
    "Likelihood Before Controls (%)", 0, 100, 30,
    help="Inherent annual likelihood before controls."
)
aro_after_percent = st.sidebar.slider(
    "Likelihood After Controls (%)", 0, 100, 10,
    help="Residual annual likelihood after controls."
)
modifiers = {"Initial":1.3, "Developing":1.15, "Defined":1.0, "Managed":0.85, "Optimized":0.7}
aro_before = (aro_before_percent / 100) * modifiers[maturity_level]
aro_after = (aro_after_percent / 100) * modifiers[maturity_level]

#st.sidebar.markdown("### Additional Industry Metrics")
#mttd = st.sidebar.number_input("MTTD (Mean Time to Detect) in hours", value=72.0)
#mttr = st.sidebar.number_input("MTTR (Mean Time to Respond) in hours", value=48.0)
#vuln_rate = st.sidebar.slider("Vulnerability Remediation Rate (%)", 0, 100, 80)
#compliance_score = st.sidebar.slider("Compliance Score (%)", 0, 100, 90)
#risk_appetite = st.sidebar.slider("Risk Appetite Threshold (%)", 0, 100, 20)
#cost_noncompliance_m = st.sidebar.number_input("Cost of Non-Compliance ($M)", value=0.5, step=0.1, format="%0.1f")
#cost_noncompliance = cost_noncompliance_m * 1_000_000


# === CALCULATIONS ===
sle = base_sle + user_breach_cost + downtime_cost
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = risk_reduction / controls_cost if controls_cost else 0
roi_pct = roi * 100
ale_before_pct = (ale_before / revenue * 100) if revenue else 0
ale_after_pct = (ale_after / revenue * 100) if revenue else 0
#residual_risk = ale_after_pct - risk_appetite

# Determine ROI color and tooltip
if roi_pct < 100:
    roi_color = "#e06c75"
    roi_tooltip = "ROI below expected (under 100%)."
elif roi_pct < 200:
    roi_color = "#e5c07b"
    roi_tooltip = "ROI moderate (100–200%)."
else:
    roi_color = "#98c379"
    roi_tooltip = "ROI strong (over 200%)."

# === HIGHLIGHTED METRICS SECTION WITH EMBEDDED TOOLTIP ===
highlight_html = f"""
<div style="display:flex; gap:20px; justify-content:center; margin:20px 0;">
  <div style="flex:1; min-width:150px; background:#20232A; padding:20px; border-radius:8px; text-align:center;">
    <h3 style="color:#cc0000; margin:0;">ALE Before</h3>
    <p style="font-size:24px; color:white; margin:5px 0;">${ale_before/1e6:.2f}M</p>
  </div>
  <div style="flex:1; min-width:150px; background:#20232A; padding:20px; border-radius:8px; text-align:center;">
    <h3 style="color:#61DAFB; margin:0;">ALE After</h3>
    <p style="font-size:24px; color:white; margin:5px 0;">${ale_after/1e6:.2f}M</p>
  </div>
  <div style="flex:1; min-width:150px; background:#20232A; padding:20px; border-radius:8px; text-align:center;">
    <h3 style="color:#98c379; margin:0;">Risk Reduction</h3>
    <p style="font-size:24px; color:white; margin:5px 0;">${risk_reduction/1e6:.2f}M</p>
  </div>
  <div class="tooltip" style="flex:1; min-width:150px; background:#20232A; padding:20px; border-radius:8px; text-align:center;">
    <h3 style="color:#ffd966; margin:0;">ROI</h3>
    <p style="font-size:24px; color:{roi_color}; margin:5px 0;">{roi_pct:.1f}%</p>
    <span class="tooltiptext">{roi_tooltip}</span>
  </div>
</div>
"""
st.markdown(highlight_html, unsafe_allow_html=True)

# === CORE ROI METRICS OUTPUT ===
st.subheader("Core ROI Metrics and Controls")
st.markdown(
    f"<span class='tooltip'>**ROI:** {roi_pct:.1f}%<span class='tooltiptext'>Return on Investment: (Risk Reduction ÷ Control Cost) × 100</span></span>",
    unsafe_allow_html=True
)

# === ANNUAL LOSS EXPOSURE CHART ===
st.subheader("Annual Loss Exposure (Before vs After Controls)")
bar_fig, bar_ax = plt.subplots(facecolor='none')
bar_ax.set_facecolor('none')
scenarios = ["Before Controls", "After Controls"]
values = [ale_before/1e6, ale_after/1e6]
colors = ['#EF553B', '#636EFA']
bars = bar_ax.bar(scenarios, values, color=colors)
for bar, v in zip(bars, values):
    bar_ax.text(bar.get_x() + bar.get_width() / 2, v + max(values)*0.02, f"{v:.2f}M", ha='center', color='white')
bar_ax.set_ylabel('ALE (Millions $)', color='white')
bar_ax.set_ylim(0, max(values)*1.25)
for lbl in bar_ax.get_xticklabels() + bar_ax.get_yticklabels(): lbl.set_color('white')
bar_ax.spines['top'].set_visible(False)
bar_ax.spines['right'].set_visible(False)
bar_ax.spines['left'].set_color('white')
bar_ax.spines['bottom'].set_color('white')
st.pyplot(bar_fig, transparent=True)

# === DONUT CHART ===
st.subheader("Cost vs Risk Reduction (Donut View)")
cost_df = pd.DataFrame({
    "Category": ["Preventative Controls", "Risk Reduction"],
    "M": [controls_cost/1e6, risk_reduction/1e6]
})
fig_donut, ax_donut = plt.subplots(figsize=(6,4), facecolor='none')
ax_donut.set_facecolor('none')
wedges, texts, autotexts = ax_donut.pie(
    cost_df['M'], labels=cost_df['Category'], autopct='%1.1f%%', startangle=90,
    pctdistance=0.75, colors=['#636EFA','#00CC96'], textprops={'color':'white','weight':'bold'}
)
for w in wedges: w.set_edgecolor('none')
ax_donut.axis('equal')
st.pyplot(fig_donut, transparent=True)

# === COST COMPONENT BREAKDOWN ===
st.subheader("Cost Component Breakdown")
cost_comp_df = pd.DataFrame({
    "Component": ["Preventative Controls","User Breach Cost","Downtime Cost","Total Incident Cost"],
    "Amount (Millions $)": [controls_cost/1e6, user_breach_cost/1e6, downtime_cost/1e6, sle/1e6]
})
fig3, ax3 = plt.subplots(facecolor='none')
ax3.set_facecolor('none')
bars3 = ax3.barh(cost_comp_df['Component'], cost_comp_df['Amount (Millions $)'], color=['#636EFA','#EF553B','#00CC96','#AB63FA'])
max_amt = cost_comp_df['Amount (Millions $)'].max()
for bar, v in zip(bars3, cost_comp_df['Amount (Millions $)']):
    ax3.text(v + max_amt*0.01, bar.get_y()+bar.get_height()/2, f"{v:.2f}M", va='center', color='white')
for lbl in ax3.get_xticklabels()+ax3.get_yticklabels(): lbl.set_color('white')
for spine in ax3.spines.values(): spine.set_color('none')
ax3.set_xlabel('Amount (Millions $)')
ax3.invert_yaxis()
st.pyplot(fig3, transparent=True)

# === FAQ ===
with st.sidebar.expander(" What These Mean", expanded=False):
    st.markdown("""
**SLE:** Cost per incident.
**ARO:** Likelihood of incident.
**ALE:** Annual expected loss.
**ROI:** Return on controls.
**MTTD:** Mean Time to Detect.
**MTTR:** Mean Time to Respond.
**Vulnerability Remediation Rate:** % patched within SLA.
**Compliance Score:** Control compliance percentage.
**Residual Risk:** ALE after controls vs appetite.
**Cost of Non-Compliance:** Projected regulatory fines.
""", unsafe_allow_html=True)
