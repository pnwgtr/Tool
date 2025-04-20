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
    "Cost per User for Credit Monitoring ($)", min_value=0, value=10, step=1,
    help="Estimated cost per user to provide credit monitoring after a breach."
)

# === PLACEHOLDER VARIABLES ===
sle_m = 6.0  # Base SLE in millions (can be made an input if needed)
sle = sle_m * 1_000_000 + (user_count * monitoring_cost_per_user)
aro_before = 0.2  # Likelihood before controls (can be made an input)
aro_after = 0.1   # Likelihood after controls (can be made an input)
ale_before = sle * aro_before
ale_after = sle * aro_after
risk_reduction = ale_before - ale_after

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
