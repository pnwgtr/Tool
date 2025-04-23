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
st.markdown("<h1 style='text-align: center;'>Cyber Risk ROI Calculator</h1>", unsafe_allow_html=True)

# === SIDEBAR INPUTS ===
st.sidebar.markdown("### Program Maturity Level")
maturity_level = st.sidebar.select_slider(
    "Cybersecurity Program Maturity",
    options=["Initial", "Developing", "Defined", "Managed", "Optimized"],
    value="Defined"
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
    "Estimated Affected Users (K)", 0, 1000, 600, 10, format="%dK"
)
user_count = user_count_k * 1000
monitoring_cost_per_user = st.sidebar.slider(
    "$ Cost per User for Credit Monitoring", 0, 20, 10, 1, format="$%d"
)

sle_m = st.sidebar.slider(
    "Base SLE (Excluding Users) - Incident Cost ($M)", 0.0, 10.0, 6.0, 0.1, format="%0.1fM"
)
base_sle = sle_m * 1_000_000
user_breach_cost = user_count * monitoring_cost_per_user

st.sidebar.markdown("### Downtime Impact Assumptions")
downtime_days = st.sidebar.slider("Estimated Days of Downtime", 5, 30, 5)
dcost_max_m = (default_cost_per_day / 1_000_000) * 2
cost_per_day_m = st.sidebar.slider(
    "Estimated Cost per Day of Downtime ($M)",
    0.0, dcost_max_m, default_cost_per_day/1_000_000, 0.1, format="%0.1fM"
)
cost_per_day = cost_per_day_m * 1_000_000
downtime_cost = downtime_days * cost_per_day

st.sidebar.markdown("### Incident Likelihood")
aro_before_percent = st.sidebar.slider("Likelihood Before Controls (%)", 0, 100, 30)
aro_after_percent = st.sidebar.slider("Likelihood After Controls (%)", 0, 100, 10)
modifiers = {"Initial":1.3, "Developing":1.15, "Defined":1.0, "Managed":0.85, "Optimized":0.7}
aro_before = (aro_before_percent/100) * modifiers[maturity_level]
aro_after = (aro_after_percent/100) * modifiers[maturity_level]

st.sidebar.markdown("### Additional Industry Metrics")
mttd = st.sidebar.number_input("MTTD (Mean Time to Detect) in hours", value=72.0)
mttr = st.sidebar.number_input("MTTR (Mean Time to Respond) in hours", value=48.0)
vuln_rate = st.sidebar.slider("Vulnerability Remediation Rate (%)", 0, 100, 80)
compliance_score = st.sidebar.slider("Compliance Score (%)", 0, 100, 90)
risk_appetite = st.sidebar.slider("Risk Appetite Threshold (%)", 0, 100, 20)
cost_noncompliance_m = st.sidebar.number_input(
    "Cost of Non-Compliance ($M)", value=0.5, step=0.1, format="%0.1f"
)
cost_noncompliance = cost_noncompliance_m * 1_000_000

# === CALCULATIONS ===
sle = base_sle + user_breach_cost + downtime_cost
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = risk_reduction / controls_cost if controls_cost else 0
ale_before_pct = (ale_before / revenue * 100) if revenue else 0
ale_after_pct = (ale_after / revenue * 100) if revenue else 0
residual_risk = ale_after_pct - risk_appetite

# === HIGHLIGHTED METRICS ===
highlight_html = f"""
<div style="display:flex; gap:20px; justify-content:center; margin:20px 0;">
  <div style="background:#20232A; padding:20px; border-radius:8px; width:25%; text-align:center;">
    <h3 style="color:#61dafb; margin:0;">ALE Before</h3>
    <p style="font-size:24px; color:white; margin:5px 0;">${ale_before/1e6:.2f}M</p>
  </div>
  <div style="background:#20232A; padding:20px; border-radius:8px; width:25%; text-align:center;">
    <h3 style="color:#e06c75; margin:0;">ALE After</h3>
    <p style="font-size:24px; color:white; margin:5px 0;">${ale_after/1e6:.2f}M</p>
  </div>
  <div style="background:#20232A; padding:20px; border-radius:8px; width:25%; text-align:center;">
    <h3 style="color:#98c379; margin:0;">Risk Reduction</h3>
    <p style="font-size:24px; color:white; margin:5px 0;">${risk_reduction/1e6:.2f}M</p>
  </div>
</div>
"""
st.markdown(highlight_html, unsafe_allow_html=True)

# === ADDITIONAL METRICS OUTPUT ===
st.subheader("Additional Industry Metrics")
cols = st.columns(3)
cols[0].metric("MTTD (hrs)", f"{mttd:.1f}")
cols[1].metric("MTTR (hrs)", f"{mttr:.1f}")
cols[2].metric("Vulnerability Remediation Rate (%)", f"{vuln_rate}")
cols2 = st.columns(3)
cols2[0].metric("Compliance Score (%)", f"{compliance_score}")
cols2[1].metric("Residual Risk (%)", f"{residual_risk:.1f}")
cols2[2].metric("Cost of Non-Compliance", f"${cost_noncompliance/1e6:.2f}M")

# === ANNUAL LOSS EXPOSURE CHART ===
st.subheader("Annual Loss Exposure (Before vs After Controls)")
bar_fig, bar_ax = plt.subplots(facecolor='none')
bar_ax.set_facecolor('none')
scenarios = ["Before Controls", "After Controls"]
values = [ale_before/1e6, ale_after/1e6]
bar_colors = ['#EF553B', '#636EFA']
bars = bar_ax.bar(scenarios, values, color=bar_colors)
for bar, v in zip(bars, values):
    bar_ax.text(bar.get_x() + bar.get_width()/2, v + max(values)*0.02, f"{v:.2f}M", ha='center', color='white')
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
    cost_df['M'], labels=cost_df['Category'], autopct='%1.1f%%', startangle=90, pctdistance=0.75,
    colors=['#636EFA','#00CC96'], textprops={'color':'white','weight':'bold'}
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
comp = cost_comp_df['Component']
amts = cost_comp_df['Amount (Millions $)']
colors = ['#636EFA','#EF553B','#00CC96','#AB63FA']
bars3 = ax3.barh(comp, amts, color=colors)
max_amt = amts.max()
for bar, v in zip(bars3, amts):
    ax3.text(v + max_amt*0.01, bar.get_y() + bar.get_height()/2,
             f"{v:.2f}M", va='center', color='white')
for lbl in ax3.get_xticklabels() + ax3.get_yticklabels(): lbl.set_color('white')
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
