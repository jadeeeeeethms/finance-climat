import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finance & Climate", layout="wide")

st.title("Finance & Climate Link")
st.write("This page explains how climate indicators connect to portfolio construction and financial risk management.")

st.markdown("## Climate analytics as financial intelligence")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
### Physical dimension
Climate hazards can affect:
- asset location,
- operating continuity,
- collateral quality,
- insurance pricing,
- expected losses.
""")

    st.markdown("""
### Transition dimension
Transition pressure can affect:
- margins,
- carbon costs,
- regulation exposure,
- stranded asset risk,
- sector repricing.
""")

with col2:
    st.markdown("""
### Strategic portfolio dimension
Climate metrics can support:
- asset allocation decisions,
- sector rotation,
- country exposure review,
- exclusion / engagement policies,
- sustainable finance reporting.
""")

    st.markdown("""
### Investor interpretation
A climate dashboard helps answer:
- where is risk concentrated?
- which assets drive the weakest profile?
- where can capital be reallocated first?
""")

st.markdown("## Indicator-to-finance mapping")

mapping = pd.DataFrame([
    {
        "Indicator": "Physical Risk",
        "Climate meaning": "hazard exposure",
        "Finance meaning": "operational disruption, collateral and insurance risk",
        "Typical action": "reduce concentration in exposed areas"
    },
    {
        "Indicator": "WACI",
        "Climate meaning": "carbon intensity",
        "Finance meaning": "transition pressure and repricing vulnerability",
        "Typical action": "reduce high-carbon contributors"
    },
    {
        "Indicator": "GAR",
        "Climate meaning": "green alignment",
        "Finance meaning": "strategic positioning toward sustainable assets",
        "Typical action": "increase aligned assets"
    },
    {
        "Indicator": "ITR",
        "Climate meaning": "scenario alignment",
        "Finance meaning": "forward-looking transition consistency",
        "Typical action": "prioritize better-aligned counterparties"
    },
])

st.dataframe(mapping, use_container_width=True, hide_index=True)

st.markdown("## Key message")
st.success("""
Climate metrics become useful when they are translated into portfolio decisions.
The purpose is not only to observe climate exposure, but to support allocation, risk reduction and strategic steering.
""")
