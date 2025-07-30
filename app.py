# === FULL CFO-FRIENDLY CYBER RISK ROI APP (HIGH DPI FOR CRISP CHARTS) ===
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === GLOBAL STYLING ===
st.markdown("""
<style>
    .block-container {padding:0.5rem 1rem;}
    h1 {font-size:24px !important; margin-bottom:4px;}
    h3 {font-size:16px !important; margin:4px 0;}
</style>
""", unsafe_allow_html=True)

text_color = "black" if st.get_option("theme.base") == "light" else "white"

# === SIDEBAR ===
st.sidebar.header("Input Parameters")
maturity_level = st.sidebar.select_slider("Cybersecurity Program Maturity",["Initial","Developing","Defined","Managed","Optimized"],value="Initial")
controls_cost_m = st.sidebar.slider("Cybersecurity Budget ($M)",0.0,10.0,1.1,0.1)
controls_cost = controls_cost_m*1_000_000
revenue_m = st.sidebar.slider("Annual Revenue ($M)",0.0,1000.0,500.0,10.0)
revenue = revenue_m*1_000_000
default_cost_per_day = revenue/365
user_count_k = st.sidebar.slider("Estimated Affected Users (K)",0,1000,600,10)
user_count = user_count_k*1000
monitoring_cost_per_user = st.sidebar.slider("Credit‑Monitoring Cost/User ($)",0,20,10,1)
sle_m = st.sidebar.slider("Base Incident Cost ($M)",0.0,10.0,6.0,0.1)
base_sle = sle_m*1_000_000
user_breach_cost = user_count*monitoring_cost_per_user
st.sidebar.markdown("### Downtime")
downtime_days = st.sidebar.slider("Estimated Days of Downtime",5,30,5)
dcost_max_m = (default_cost_per_day/1_000_000)*2
cost_per_day_m = st.sidebar.slider("Cost per Day ($M)",0.0,dcost_max_m,default_cost_per_day/1_000_000,0.1)
cost_per_day = cost_per_day_m*1_000_000
downtime_cost = downtime_days*cost_per_day
st.sidebar.markdown("### Incident Likelihood")
aro_before_pct = st.sidebar.slider("Likelihood Before Controls (%)",0,100,30)
aro_after_pct = st.sidebar.slider("Likelihood After Controls (%)",0,100,10)
compact_mode = st.sidebar.checkbox("Enable Compact Mode",True)

# === CALC ===
mod = {"Initial":1.3,"Developing":1.15,"Defined":1.0,"Managed":0.85,"Optimized":0.7}
aro_before = (aro_before_pct/100)*mod[maturity_level]
aro_after  = (aro_after_pct/100)*mod[maturity_level]
sle = base_sle+user_breach_cost+downtime_cost
ale_before = sle*aro_before
ale_after  = sle*aro_after
risk_reduction = ale_before-ale_after
roi_pct = (risk_reduction/controls_cost*100) if controls_cost else 0
roi_color = "#e06c75" if roi_pct<100 else "#e5c07b" if roi_pct<200 else "#00cc96"
total_incident_cost = sle

# === TITLE ===
st.markdown("<h1 style='text-align:center;'>Cyber Risk ROI Calculator</h1>",unsafe_allow_html=True)

# === KPI GRID ===
metric_padding = "2px" if compact_mode else "8px"
metric_font = "20px" if compact_mode else "28px"
st.markdown(f"""
<style>
.metric-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:4px;margin:4px 0;}}
.metric-box{{background:#1f1f1f;border-radius:4px;padding:{metric_padding};text-align:center;color:white;}}
.metric-box h4{{font-size:12px;margin:0;color:#61dafb;}}
.metric-box p{{font-size:{metric_font};margin:0;font-weight:bold;}}
</style>
<div class='metric-grid'>
    <div class='metric-box'><h4>Estimated Annual Loss (Before)</h4><p>{ale_before/1e6:.2f}M</p></div>
    <div class='metric-box'><h4>Estimated Annual Loss (After)</h4><p>{ale_after/1e6:.2f}M</p></div>
    <div class='metric-box'><h4>Risk Reduction (Avoided Loss)</h4><p>{risk_reduction/1e6:.2f}M</p></div>
    <div class='metric-box'><h4>Return on Investment</h4><p style='color:{roi_color};'>{roi_pct:.1f}%</p></div>
</div>
""",unsafe_allow_html=True)

# === BIG TOTAL COST BANNER ===
st.markdown(f"""
<div style='text-align:center;margin:8px 0;'>
    <span style='display:inline-block;background:#EF553B;border-radius:4px;padding:6px 12px;font-size:22px;font-weight:900;color:white;'>
     Total Estimated Incident Cost: {total_incident_cost/1e6:.2f}M
    </span>
</div>
""",unsafe_allow_html=True)

# === CHARTS (HIGH DPI) ===
chart_size = (2.5,1.3) if compact_mode else (5,3)

def style_chart(ax):
    ax.set_facecolor('none')
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)
    ax.xaxis.label.set_size(6)
    ax.yaxis.label.set_size(6)
    for lbl in ax.get_xticklabels()+ax.get_yticklabels():
        lbl.set_color(text_color)
        lbl.set_fontsize(6)

st.markdown("<h3 style='text-align:center;'>Risk Exposure: Before vs After Controls</h3>", unsafe_allow_html=True)
risk_df = pd.DataFrame({"Stage":["Before Controls","After Controls"],"Millions":[ale_before/1e6,ale_after/1e6]})
fig_r, ax_r = plt.subplots(figsize=chart_size, dpi=150, facecolor='none')
bars = ax_r.bar(risk_df['Stage'], risk_df['Millions'], color=["#EF553B","#00CC96"])
for bar, val in zip(bars, risk_df['Millions']):
    ax_r.text(bar.get_x()+bar.get_width()/2, val+0.05, f"{val:.2f}M", ha='center', color=text_color, fontsize=6)
ax_r.set_ylabel("Millions $", color=text_color)
style_chart(ax_r)
st.pyplot(fig_r, transparent=True)

st.markdown("<h3 style='text-align:center;'>Incident Cost Components</h3>", unsafe_allow_html=True)
inc_df = pd.DataFrame({"Component":["Base Incident Cost","User Breach Cost","Downtime Cost"],"Millions":[base_sle/1e6,user_breach_cost/1e6,downtime_cost/1e6]})
fig_i, ax_i = plt.subplots(figsize=chart_size, dpi=150, facecolor='none')
ax_i.barh(inc_df['Component'], inc_df['Millions'], color=['#EF553B','#00CC96','#AB63FA'])
for v,c in zip(inc_df['Millions'],inc_df['Component']):
    ax_i.text(v+0.1,c,f"{v:.2f}M",va='center',color=text_color,fontsize=6)
ax_i.invert_yaxis(); ax_i.set_xlabel('Millions $', color=text_color)
style_chart(ax_i)
st.pyplot(fig_i, transparent=True)
