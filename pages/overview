import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Executive Overview", layout="wide")
st.title("Executive Overview")

def load_summary(path, sep=";"):
    if os.path.exists(path):
        df = pd.read_csv(path, sep=sep)
        if "metric" in df.columns and "value" in df.columns:
            return dict(zip(df["metric"], df["value"]))
    return {}

def safe_float(x):
    try:
        return float(x)
    except:
        return None

waci = load_summary("data/waci/dashboard_summary.csv")
physical = load_summary("data/physical_risk/dashboard_summary.csv")
gar = load_summary("data/gar/dashboard_summary.csv")
itr = load_summary("data/itr/dashboard_summary.csv")

st.markdown("## Key messages")

messages = []

waci_val = safe_float(waci.get("portfolio_indicator"))
if waci_val is not None:
    if waci_val > 300:
        messages.append("The portfolio shows elevated carbon intensity.")
    elif waci_val > 100:
        messages.append("The portfolio shows moderate carbon intensity.")
    else:
        messages.append("The portfolio shows relatively low carbon intensity.")

physical_val = safe_float(physical.get("portfolio_indicator"))
if physical_val is not None:
    if physical_val > 0.5:
        messages.append("Physical hazard exposure appears high.")
    elif physical_val > 0.2:
        messages.append("Physical hazard exposure appears moderate.")
    else:
        messages.append("Physical hazard exposure appears limited.")

itr_val = safe_float(itr.get("portfolio_indicator", itr.get("portfolio_itr")))
if itr_val is not None:
    if itr_val > 2.0:
        messages.append("Climate alignment appears weak.")
    elif itr_val > 1.5:
        messages.append("Climate alignment appears intermediate.")
    else:
        messages.append("Climate alignment appears relatively strong.")

gar_val = safe_float(gar.get("portfolio_indicator"))
if gar_val is not None:
    if gar_val < 0.25:
        messages.append("Green asset alignment remains limited.")
    elif gar_val < 0.5:
        messages.append("Green asset alignment is developing.")
    else:
        messages.append("Green asset alignment appears strong.")

for m in messages:
    st.write(f"- {m}")

st.markdown("## Management focus")
st.info("""
Management should read these indicators together:
- resilience to physical events,
- exposure to transition pressure,
- degree of green positioning,
- long-term alignment with climate scenarios.
""")
