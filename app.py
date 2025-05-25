import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === THEME DETECTION ===
theme = st.get_option("theme.base")
text_color = "black" if theme == "light" else "white"

# === GUIDE STATE ===
if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

# === FLOATING QUICK START BUTTON (Streamlit-native) ===
with st.container():
    col1, col2, col3 = st.columns([0.7, 0.1, 0.2])
    with col3:
        st.markdown(
            f"""
            <style>
            div[data-testid="column"] button {{
                position: fixed;
                bottom: 90px;
                right: 30px;
                background-color: #00cc96;
                color: white;
                padding: 10px 18px;
                border-radius: 30px;
                font-weight: bold;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                z-index: 10000;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.button("💡 Quick Start"):
            st.session_state.show_guide = not st.session_state.get("show_guide", False)


# === SIDEBAR GUIDE ===
if st.sidebar.button("💡 Quick Start Guide"):
    st.session_state.show_guide = not st.session_state.show_guide

if st.session_state.show_guide:
    with st.sidebar.expander("👋 Getting Started", expanded=True):
        st.markdown("""
Adjust these inputs to model your cybersecurity ROI:

- **Cybersecurity Budget** – Your annual spend on controls  
- **Annual Revenue** – Used to estimate downtime loss  
- **Users Affected** – For breach impact calculation  
- **ARO Before/After** – Likelihood before and after implementing controls  
        """)

# === SIDEBAR INPUTS ===
st.sidebar.header("Input Parameters")
st.sidebar.markdown("### Program Configuration")
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

st.sidebar.markdown("### Breach Impact Assumptions")
user_count_k = st.sidebar.slider("Estimated Affected Users (K)", 0, 1000, 600, 10)
user_count = user_count_k * 1000
monitoring_cost_per_user = st.sidebar.slider("Cost per User for Credit Monitoring ($)", 0, 20, 10, 1)

sle_m = st.sidebar.slider("Base Incident Cost (Excl. Users) ($M)", 0.0, 10.0, 6.0, 0.1)
base_sle = sle_m * 1_000_000
user_breach_cost = user_count * monitoring_cost_per_user

st.sidebar.markdown("### Downtime Impact Assumptions")
downtime_days = st.sidebar.slider("Estimated Days of Downtime", 5, 30, 5)
dcost_max_m = (default_cost_per_day / 1_000_000) * 2
cost_per_day_m = st.sidebar.slider("Downtime Cost/Day ($M)", 0.0, dcost_max_m, default_cost_per_day / 1_000_000, 0.1)
cost_per_day = cost_per_day_m * 1_000_000
downtime_cost = downtime_days * cost_per_day

st.sidebar.markdown("### Incident Likelihood")
aro_before_pct = st.sidebar.slider("Likelihood Before Controls (%)", 0, 100, 30)
aro_after_pct = st.sidebar.slider("Likelihood After Controls (%)", 0, 100, 10)

st.sidebar.markdown("### View Options")
executive_mode = st.sidebar.checkbox("Enable Executive Mode", value=True)
compact_mode = st.sidebar.checkbox("Enable Compact Layout", value=True)

# === CALCULATIONS ===
modifiers = {"Initial": 1.3, "Developing": 1.15, "Defined": 1.0, "Managed": 0.85, "Optimized": 0.7}
aro_before = (aro_before_pct / 100) * modifiers[maturity_level]
aro_after = (aro_after_pct / 100) * modifiers[maturity_level]

sle = base_sle + user_breach_cost + downtime_cost
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after
roi = risk_reduction / controls_cost if controls_cost else 0
roi_pct = roi * 100
roi_color = "#e06c75" if roi_pct < 100 else "#e5c07b" if roi_pct < 200 else "#00cc96"

# === KPI TITLE ===
st.markdown("<h1 style='margin-top: 10px; text-align: center;'>Cyber Risk ROI Calculator</h1>", unsafe_allow_html=True)

# === HELPER FUNCTION ===
def apply_theme_style(ax):
    ax.set_facecolor('none')
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    for spine in ax.spines.values():
        spine.set_visible(False)

# === COST COMPONENT BREAKDOWN (ALWAYS VISIBLE) ===
st.subheader("Cost Component Breakdown")
cost_data = pd.DataFrame({
    "Component": ["Cybersecurity Budget", "User Breach Cost", "Downtime Cost", "Total Incident Cost"],
    "Millions": [controls_cost / 1e6, user_breach_cost / 1e6, downtime_cost / 1e6, sle / 1e6]
})
fig3, ax3 = plt.subplots(figsize=(6, 3) if compact_mode else (8, 4), facecolor='none')
bars = ax3.barh(cost_data["Component"], cost_data["Millions"], color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA'])
for bar, val in zip(bars, cost_data["Millions"]):
    ax3.text(val + 0.1, bar.get_y() + bar.get_height()/2, f"{val:.2f}M", va='center', color=text_color)
ax3.invert_yaxis()
ax3.set_xlabel("Millions $")
apply_theme_style(ax3)
st.pyplot(fig3, transparent=True)

# === OTHER CHARTS (IF EXEC MODE IS OFF) ===
if not executive_mode:
    st.subheader("Annual Loss Exposure (Before vs After Controls)")
    fig1, ax1 = plt.subplots(figsize=(5, 3) if compact_mode else (6, 4), facecolor='none')
    values = [ale_before / 1e6, ale_after / 1e6]
    bars = ax1.bar(["Before Controls", "After Controls"], values, color=['#EF553B', '#00CC96'])
    for bar, val in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.1, f"{val:.2f}M", ha='center', color=text_color)
    ax1.set_ylabel("ALE (Millions $)")
    apply_theme_style(ax1)
    st.pyplot(fig1, transparent=True)

    st.subheader("Cost vs Risk Reduction")
    fig2, ax2 = plt.subplots(figsize=(4, 3) if compact_mode else (6, 4), facecolor='none')
    wedges, texts, autotexts = ax2.pie(
        [controls_cost / 1e6, risk_reduction / 1e6],
        labels=["Cybersecurity Budget", "Risk Reduction"],
        autopct="%1.1f%%",
        startangle=90,
        colors=['#636EFA', '#00CC96'],
        wedgeprops=dict(width=0.3),
        textprops={'color': text_color, 'weight': 'bold'}
    )
    ax2.axis("equal")
    st.pyplot(fig2, transparent=True)
