import streamlit as st
import pandas as pd

st.set_page_config(page_title="TaskLab", layout="wide")

st.title("🧠 TaskLab — Taskmaster Forecast")

st.markdown("""
Forecasting Taskmaster outcomes using simulation and historical patterns.

⚠️ Not affiliated with Taskmaster
⚠️ Not for betting use
""")

# Placeholder data (replace later)
data = pd.DataFrame({
    "contestant": ["A", "B", "C", "D", "E"],
    "win_probability": [0.42, 0.33, 0.15, 0.07, 0.03]
})

st.subheader("Latest win probabilities")

st.dataframe(data)
