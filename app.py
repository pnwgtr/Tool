import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === THEME DETECTION ===
theme = st.get_option("theme.base")
text_color = "black" if theme == "light" else "white"

# === SIDEBAR GUIDE STATE ===
if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

if st.sidebar.button("💡 Quick Start Guide"):
    st.session_state.show_guide = not st.session_state.show_guide

if st.session_state.show_guide:
    with st.sidebar.expander("👋 Getting Started", expanded=True):
        st.markdown("""
Adjust these inputs to model your cybersecurity ROI:

- **Cybersecurity Budget** – Annual spend on controls  
- **Annual Revenue** – Used to estimate downtime cost  
- **Users Affected** – For breach impact  
- **ARO Before/After** – Likelihood before/after controls
""")

# === SIDEBAR INPUTS ===
st.sidebar.header("Input Parameters")

## Program configuration
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

## Breach assumptions
user_count_k = st.sidebar.slider("Estimated Affected Users (K)", 0, 1000, 600, 10)
user_count = user_count_k * 1000
monitoring_cost_per_user = st.sidebar.slider("Credit‑Monitoring Cost per User ($)", 0, 20, 10, 1)

sle_m = st.sidebar.slider("Base Incident Cost (Excl. Users) ($M)", 0.0, 10.0, 6.0, 0.1)
base_sle = sle_m * 1_000_000
user_breach_cost = user_count * monitoring_cost_per_user

## Downtime
st.sidebar.markdown("### Downtime")
downtime_days = st.sidebar.slider("Estimated Days of Downtime", 5, 30, 5)
dcost_max_m = (default_cost_per_day/1_000_000) * 2
cost_per_day_m = st.sidebar.slider("Cost per Day ($M)", 0.0, dcost_max_m, default_cost_per_day/1_000_000, 0.1)
cost_per_day = cost_per_day_m * 1_000_000
downtime_cost = downtime_days * cost_per_day

## Likelihood
st.sidebar.markdown("### Incident Likelihood")
aro_before_pct = st.sidebar.slider("Likelihood Before Controls (%)", 0, 100, 30)
aro_after_pct = st.sidebar.slider("Likelihood After Controls (%)", 0, 100, 10)

## View options
st.sidebar.markdown("### View Options")
executive_mode = st.sidebar.checkbox("Enable Executive Mode", value=True)
compact_mode = st.sidebar.checkbox("Enable Compact Layout", value=True)

# === CALCULATIONS ===
mod = {"Initial":1.3,"Developing":1.15,"Defined":1.0,"Managed":0.85,"Optimized":0.7}
aro_before = (aro_before_pct/100) * mod[maturity_level]
aro_after = (aro_after_pct/100) * mod[maturity_level]

sle = base_sle + user_breach_cost + downtime_cost
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = risk_reduction / controls_cost if controls_cost else 0
roi_pct = roi * 100
roi_color = "#e06c75" if roi_pct < 100 else "#e5c07b" if roi_pct < 200 else "#00cc96"

total_incident_cost = sle
benchmark_pct = 0.005
benchmark_budget = revenue * benchmark_pct

# === PAGE TITLE ===
st.markdown("<h1 style='text-align:center;margin-top:10px;'>Cyber Risk ROI Calculator</h1>", unsafe_allow_html=True)

# === THEME HELP ===

def apply_theme(ax):
    ax.set_facecolor('none')
    for lbl in ax.get_xticklabels()+ax.get_yticklabels():
        lbl.set_color(text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    for s in ax.spines.values():
        s.set_visible(False)

# === KPI GRID ===
st.markdown(f"""
<style>
.metric-grid {{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin:30px 0;}}
.metric-box {{background:#1f1f1f;border-radius:10px;padding:20px;text-align:center;color:white;box-shadow:0 0 10px rgba(0,0,0,0.3);}}
.metric-box h4 {{margin:0 0 8px;color:#61dafb;font-size:18px;}}
.metric-box p {{font-size:28px;margin:0;font-weight:bold;}}
</style>
<div class='metric-grid'>
  <div class='metric-box'><h4>ALE Before Controls</h4><p>{ale_before/1e6:.2f}M</p></div>
  <div class='metric-box'><h4>ALE After Controls</h4><p>{ale_after/1e6:.2f}M</p></div>
  <div class='metric-box'><h4>Risk Reduction</h4><p>{risk_reduction/1e6:.2f}M</p></div>
  <div class='metric-box'><h4>ROI</h4><p style='color:{roi_color};'>{roi_pct:.1f}%</p></div>
</div>
<p style='text-align:center;font-size:14px;color:#aaa;margin-top:15px'>📘 Calculations: ALE = SLE × ARO — ROI = Risk Reduction ÷ Cybersecurity Budget</p>
""", unsafe_allow_html=True)

# === INCIDENT COST BREAKDOWN ===
st.markdown("<h3 style='text-align:center;margin:10px 0;'>Incident Cost Components</h3>", unsafe_allow_html=True)
incident_df = pd.DataFrame({
    'Component':['Base Incident Cost','User Breach Cost','Downtime Cost'],
    'Millions':[base_sle/1e6,user_breach_cost/1e6,downtime_cost/1e6]
})
fig_i, ax_i = plt.subplots(figsize=(6,3) if compact_mode else (8,4), facecolor='none')
ax_i.barh(incident_df['Component'], incident_df['Millions'], color=['#EF553B','#00CC96','#AB63FA'])
for v,c in zip(incident_df['Millions'], incident_df['Component']):
    ax_i.text(v+0.1, c, f"{v:.2f}M", va='center', color=text_color)
ax_i.invert_yaxis(); ax_i.set_xlabel('Millions $'); apply_theme(ax_i)
st.pyplot(fig_i, transparent=True)

st.markdown(f"<div style='text-align:center;margin:25px 0;'><span style='display:inline-block;background:#EF553B;border-radius:10px;padding:14px 28px;font-size:30px;font-weight:800;color:white;box-shadow:0 4px 12px rgba(0,0,0,0.25);'>💰 Total Estimated Incident Cost: {total_incident_cost/1e6:.2f}M</span></div>", unsafe_allow_html=True)

# === PROGRAM SPEND VS BENCHMARK ===
if not executive_mode:
    st.markdown("""
<h3 style='text-align:center;'>Cybersecurity Program Spend vs Benchmark</h3>
<p style='text-align:center;font-size:14px;color:#aaa;margin-bottom:6px;'>Benchmark is set at <b>0.5% of annual revenue</b> (industry median).</p>
""", unsafe_allow_html=True)

    spend_df = pd.DataFrame({
        'Category':['Current Budget','Benchmark','Risk Reduction'],
        'Millions':[controls_cost/1e6, benchmark_budget/1e6, risk_reduction/1e6]
    })

    fig_s, ax_s = plt.subplots(figsize=(6,3) if compact_mode else (8,4), facecolor='none')
    bars = ax_s.bar(spend_df['Category'], spend_df['Millions'], color=['#636EFA','#FFA15A','#00CC96'])
    ax_s.set_xticklabels(spend_df['Category'], rotation=0, ha='center')
    for b,v in zip(bars, spend_df['Millions']):
        ax_s.text(b.get_x()+b.get_width()/2, v+0.1, f"{v:.2f}M", ha='center', color=text_color)
    ax_s.set_ylabel('Millions $'); apply_theme(ax_s); fig_s.tight_layout(); st.pyplot(fig_s, transparent=True)

        delta = controls_cost - benchmark_budget
    if delta >= 0:
        msg = f"🔎 Your current cybersecurity budget is **{delta/1e6:.2f}M** above the 0.5% benchmark."
        col = '#00cc96'
    else:
        msg = f"⚠️ Your current cybersecurity budget is **{abs(delta)/1e6:.2f}M** below the 0.5% benchmark. Consider increasing investment."
        col = '#ef553b'
    st.markdown(f"<p style='text-align:center;font-size:16px;font-weight:bold;color:{col};margin-top:10px'>{msg}</p>", unsafe_allow_html=True)(f"<p style='text-align:center;font-size:16px;font-weight:bold;color:{col};margin-top:10px'>{msg}</p>", unsafe_allow_html=True)
