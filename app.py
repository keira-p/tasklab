from pathlib import Path
import streamlit as st
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_PATH = DATA_DIR / "processed"


st.set_page_config(page_title="TaskLab", layout="wide")

st.title("🧠 TaskLab — Taskmaster Forecast")

st.markdown("""
Forecasting Taskmaster outcomes using simulation and historical patterns.

⚠️ Not affiliated with Taskmaster
⚠️ Not for betting use
""")

# DUMMY DATA
data = pd.read_csv(PROCESSED_PATH / "latest_snapshot.csv")

# tidy display
data["win_probability"] = data["win_probability"].round(3)
data["current_rank"] = data["current_rank"].astype(int)

st.subheader("Latest win probabilities")
st.dataframe(data, hide_index=True)
