import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# === PAGE CONFIG ===
if "dismiss_overlay" not in st.session_state:
    st.session_state.dismiss_overlay = False
st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === OVERLAY CSS & DISMISS BUTTON ===
if "dismiss_overlay" not in st.session_state:
    st.session_state.dismiss_overlay = False

if not st.session_state.dismiss_overlay:
    with st.container():
        st.markdown("""
        <style>
        .overlay-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0,0,0,0.92);
            z-index: 9999;
            padding-top: 100px;
            text-align: center;
            color: white;
        }
        .overlay-content {
            max-width: 500px;
            margin: auto;
        }
        .overlay-content h2 {
            font-size: 32px;
            margin-bottom: 20px;
        }
        .overlay-content ul {
            list-style-type: disc;
            text-align: left;
            padding-left: 40px;
        }
        </style>

        <div class="overlay-container">
            <div class="overlay-content">
                <h2>👋 Welcome to the Cyber Risk ROI Calculator</h2>
                <p>Please review and adjust the following inputs:</p>
                <ul>
                    <li><b>Cybersecurity Budget</b>: How much you're spending</li>
                    <li><b>Revenue</b>: Annual gross revenue</li>
                    <li><b>Users Affected</b>: Customer or user impact</li>
                    <li><b>ARO</b>: Likelihood before and after controls</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Place a normal Streamlit button BELOW the overlay block
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
        if st.button("✅ Got it!"):
            st.session_state.dismiss_overlay = True
        st.stop()


# === SIDEBAR CONTROLS ===
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
executive_mode = st.sidebar.checkbox("Enable Executive Mode", value=True, key="executive_mode_toggle")
compact_mode = st.sidebar.checkbox("Enable Compact Layout", value=True, key="compact_toggle")

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

# === KPI GRID ===
st.markdown("<h1 style='margin-top: 10px; text-align: center;'>Cyber Risk ROI Calculator</h1>", unsafe_allow_html=True)

kpi_style = """
<style>
.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: %s;
  margin-top: 10px;
}
.metric-box {
  background-color: #1f1f1f;
  border-radius: 10px;
  padding: %s;
  text-align: center;
  color: white;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
}
.metric-box h4 {
  margin: 0 0 4px 0;
  color: #61dafb;
  font-size: %s;
}
.metric-box p {
  font-size: %s;
  margin: 0;
  font-weight: bold;
}
</style>
""" % (
    "10px" if compact_mode else "20px",
    "10px" if compact_mode else "20px",
    "16px" if compact_mode else "18px",
    "26px" if compact_mode else "30px",
)
st.markdown(kpi_style, unsafe_allow_html=True)

highlight_grid = f"""
<div class="metric-grid">
  <div class="metric-box">
    <h4>ALE Before Controls</h4>
    <p>${ale_before/1e6:.2f}M</p>
  </div>
  <div class="metric-box">
    <h4>ALE After Controls</h4>
    <p>${ale_after/1e6:.2f}M</p>
  </div>
  <div class="metric-box">
    <h4>Risk Reduction</h4>
    <p>${risk_reduction/1e6:.2f}M</p>
  </div>
  <div class="metric-box">
    <h4>Return on Investment</h4>
    <p style="color:{roi_color};">{roi_pct:.1f}%</p>
  </div>
</div>
"""
st.markdown(highlight_grid, unsafe_allow_html=True)

# === VISUAL RISK OVERVIEW HEADING ===
if not compact_mode:
    st.markdown("<h2 style='text-align: center; color: #00cc96;'>📊 Visual Risk Overview</h2>", unsafe_allow_html=True)

# === CHARTS === (You can insert your chart logic here)
# We'll skip generating the actual matplotlib charts for brevity
# You can reinsert your fig1, fig2, fig3 logic here as needed

# === EXECUTIVE MODE ENRICHMENT ===
if not executive_mode:
    st.markdown("### Key Assumptions (Grouped)")
    assumptions_data = {
        "Category": [
            "Financials", "Financials",
            "Breach Impact", "Breach Impact",
            "Downtime Impact", "Downtime Impact",
            "Loss Expectancy",
            "Incident Likelihood", "Incident Likelihood",
            "Program Info"
        ],
        "Variable": [
            "Cybersecurity Budget", "Annual Revenue",
            "Estimated Users Affected", "Monitoring Cost/User",
            "Downtime Days", "Cost per Day of Downtime",
            "Base Incident Cost (Excl. Users)",
            "ARO Before Controls", "ARO After Controls",
            "Program Maturity"
        ],
        "Value": [
            f"${controls_cost:,.0f}", f"${revenue:,.0f}",
            f"{user_count:,}", f"${monitoring_cost_per_user}",
            f"{downtime_days}", f"${cost_per_day:,.0f}",
            f"${base_sle:,.0f}",
            f"{aro_before_pct}%", f"{aro_after_pct}%",
            maturity_level
        ]
    }
    assumptions_df = pd.DataFrame(assumptions_data)
    st.dataframe(assumptions_df, use_container_width=True)

    st.markdown("### ROI Insight")
    if roi_pct < 100:
        st.info("⚠️ ROI is below 100%. Consider optimizing spend or increasing risk reduction.")
    elif roi_pct < 200:
        st.success("ROI is in a healthy range. Continue monitoring control effectiveness.")
    else:
        st.success("🎯 Strong ROI! Your cybersecurity investments are paying off.")

    st.markdown("### Projected ALE Trend (3 Years)")
    trend_df = pd.DataFrame({
        "Year": [2025, 2026, 2027],
        "Projected ALE": [ale_before/1e6, (ale_before+ale_after)/2e6, ale_after/1e6]
    })
    st.line_chart(trend_df.set_index("Year"))
