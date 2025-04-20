import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Cyber Risk ROI", layout="wide")

# === TITLE ===
st.title("Cyber Risk ROI Calculator")

# === SIDEBAR INPUTS ===
st.sidebar.header("Input Parameters")

controls_cost_m = st.sidebar.number_input(
    "Cost of Preventative Controls ($M)", min_value=0.0, value=1.1,
    help="Annual cost of security measures implemented to prevent significant cyber incidents."
)
controls_cost = controls_cost_m * 1_000_000

revenue_m = st.sidebar.number_input(
    "Annual Revenue ($M)", min_value=0.0, value=500.0,
    help="Your organization’s annual gross revenue."
)
revenue = revenue_m * 1_000_000

st.sidebar.markdown("### Breach Impact Assumptions")
user_count = st.sidebar.number_input(
    "Estimated Affected Users", min_value=0, value=600000, step=10000,
    help="Estimated number of users who would require credit monitoring in the event of a breach."
)
monitoring_cost_per_user = st.sidebar.number_input(
    "Cost per User for Credit Monitoring ($)", min_value=0.0, value=10.0,
    help="Estimated cost per user to provide credit monitoring after a breach."
)
user_breach_cost = user_count * monitoring_cost_per_user

sle_m = st.sidebar.number_input(
    "Base SLE (Excluding Users) - Incident Cost ($M)", min_value=0.0, value=6.0,
    help="Estimated cost of a significant cyber incident, not including per-user costs."
)
base_sle = sle_m * 1_000_000

st.sidebar.markdown("### Downtime Impact Assumptions")
downtime_days = st.sidebar.slider(
    "Estimated Days of Downtime", min_value=5, max_value=30, value=5,
    help="Estimated number of days your business would be partially or fully down due to a major incident."
)
cost_per_day = st.sidebar.number_input(
    "Estimated Cost per Day of Downtime ($)", min_value=0, value=250000, step=5000,
    help="Estimated daily revenue loss or cost due to operational disruption."
)
downtime_cost = downtime_days * cost_per_day

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

# === RISK SURFACE OVERVIEW ===
with st.expander("🔍 Understanding Our Risk Surface", expanded=True):
    st.markdown(f"""
This calculator models the potential financial impact of a significant cyber event based on our organization's digital footprint and business operations.

**Key Factors in Our Risk Surface:**
- **{user_count:,} user accounts** containing sensitive personal data
- **Critical systems** that cannot be down for extended periods
- **Third-party integrations** and vendor dependencies
- **${revenue:,.0f} in annual revenue**, reliant on continuous uptime
- **Preventative control spend of ${controls_cost:,.0f} annually**

These factors contribute to a heightened risk profile and help define the variables below:
- **SLE** (Single Loss Expectancy) = estimated loss from one significant incident (base + user + downtime costs)
- **ARO** (Annual Rate of Occurrence) = estimated yearly likelihood of a breach
- **Downtime cost** = based on expected outage days × cost per day
- **Controls cost** = annual spend to reduce likelihood and impact

Understanding this surface helps ensure the model’s outputs are grounded in business reality.
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
cost_vs_risk_ratio = (controls_cost / risk_reduction) if risk_reduction > 0 else float("inf")

# === BREACH COST BREAKDOWN AT TOP ===
st.markdown("## 💥 Breach Cost Breakdown")
st.write(f"📊 **Base SLE:** ${base_sle / 1_000_000:.2f}M")
st.write(f"👥 **User Credit Monitoring:** ${user_breach_cost / 1_000_000:.2f}M")
st.write(f"🛑 **Downtime Cost** ({downtime_days} days @ ${cost_per_day:,}/day): ${downtime_cost / 1_000_000:.2f}M")
st.write(f"🧮 **Total Incident Cost (SLE):** ${sle / 1_000_000:.2f}M")

st.divider()

# === METRICS ===
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

text_props = {'color': 'white', 'fontsize': 12}

wedges, texts, autotexts = ax2.pie(
    cost_data["Amount (Millions $)"],
    labels=cost_data["Category"],
    autopct="%1.1f%%",
    startangle=90,
    textprops=text_props,
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
Estimated probability that a significant incident will happen in a year.

**ALE (Annualized Loss Expectancy):**  
Expected yearly financial loss due to cyber incidents.  
**Formula:** `ALE = SLE × ARO`

**ROI (Return on Investment):**  
How much value you get from investing in controls.  
**Formula:** `(Risk Reduction ÷ Control Cost) × 100`

**Cost vs. Risk Reduction Ratio:**  
A ratio < 1 means your spend is efficient for the risk reduced.

**User Breach Cost:**  
Cost of providing credit monitoring to affected users.

**Downtime Cost:**  
Lost revenue or costs due to operational disruption.

---
Want to go deeper? [Check out FAIR methodology →](https://www.fairinstitute.org/fair-model)
    """)
