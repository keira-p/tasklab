from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_PATH = DATA_DIR / "processed"


# ---- PAGE CONFIG ----

st.set_page_config(
    page_title="TaskLab: Taskmaster Forecast",
    layout="wide"
)


# ---- LOADING DATA ----
# NOTE: DUMMY DATA

latest_snapshot = pd.read_csv(PROCESSED_PATH / "latest_snapshot.csv")
win_probability_trajectory = pd.read_csv(PROCESSED_PATH / "win_probability_trajectory.csv")
score_trajectory = pd.read_csv(PROCESSED_PATH / "score_trajectory.csv")

# Tidy data for display
latest_snapshot["current_rank"] = latest_snapshot["current_rank"].astype(int)
latest_snapshot["latest_episode_score"] = latest_snapshot["latest_episode_score"].round(3)
win_probability_trajectory["episode"] = win_probability_trajectory["episode"].astype(int)
score_trajectory["episode"] = score_trajectory["episode"].astype(int)

# First names only for display
def get_first_name(name):
    return name.split()[0]

latest_snapshot["contestant"] = latest_snapshot["contestant"].apply(get_first_name)
win_probability_trajectory["contestant"] = win_probability_trajectory["contestant"].apply(get_first_name)
score_trajectory["contestant"] = score_trajectory["contestant"].apply(get_first_name)


# ---- HEADER ----

st.title("🍍 TaskLab: Taskmaster Forecast")

st.markdown("""
**Welcome to TaskLab!**

TaskLab is a playful data project exploring how predictable the world of
Taskmaster really is, and providing insights into who might take that coveted
trophy home.

Using simulation and historical patterns, we estimate who’s most likely to win
as the series unfolds, and how that picture changes week by week.

*We’re in no way affiliated with Taskmaster or its creators (we wish!), but
we're big fans and hope this adds a bit of extra fun for fellow enthusiasts.*
""")

st.info("""
⚠️ This is currently using dummy data for demonstration purposes.
Real episode results and live updates will be added once the new series begins.
""")

# ---- LATEST RESULTS ----

st.subheader("💡 Latest Results")
st.write(
    """
    Early results can swing quickly. This dashboard shows both latest scores, ranking, and how likely each contestant is to win.
    """
)

# Results table
display_df = latest_snapshot.rename(columns={
    "contestant": "Contestant",
    "latest_episode_score": "Latest episode score",
    "cumulative_score": "Total so far",
    "current_rank": "Current rank",
    "win_probability": "Chance to win series"
})[["Contestant", "Latest episode score", "Total so far", "Current rank", "Chance to win series"]]

display_df = display_df.sort_values("Current rank").reset_index(drop=True)

styled_df = display_df.style.format({
    "Latest episode score": "{:.0f}",
    "Total score so far": "{:.0f}",
    "Chance to win series": "{:.2%}"
}).background_gradient(subset=["Chance to win series"], cmap="Greens")

# Current win probabilities
bar_data = latest_snapshot.copy()
bar_data["win_probability_pct"] = bar_data["win_probability"] * 100

bar_chart = (
    alt.Chart(bar_data)
    .mark_bar()
    .encode(
        x=alt.X("contestant:N", sort="-y", title="Contestant"),
        y=alt.Y(
            "win_probability_pct:Q",
            title="Win probability (%)",
            scale=alt.Scale(domain=[0, 100])
        ),
        tooltip=[
            alt.Tooltip("contestant:N", title="Contestant"),
            alt.Tooltip("win_probability_pct:Q", title="Win probability (%)", format=".1f")
        ]
    )
    .properties(height=350)
)




col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("⭐️ Scores so far")
    st.table(styled_df)

with col2:
    st.subheader("👀 Current win probabilities")
    st.altair_chart(bar_chart, use_container_width=True)


# ---- TRAJECTORY CHARTS ----

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📈 Score trajectory")

    score_chart = (
        alt.Chart(score_trajectory)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "episode:O",
                title="Episode",
                axis=alt.Axis(labelAngle=0)
            ),
            y=alt.Y("cumulative_score:Q", title="Total Score So Far"),
            color=alt.Color("contestant:N", title="Contestant"),
            tooltip=[
                alt.Tooltip("contestant:N", title="Contestant"),
                alt.Tooltip("episode:Q", title="Episode"),
                alt.Tooltip("episode_score:Q", title="Episode Score"),
                alt.Tooltip("cumulative_score:Q", title="Cumulative Score")
            ]
        ).properties(height=350)
    )

    st.altair_chart(score_chart, use_container_width=True)


with col2:
    st.subheader("🏆 Win probability over time")

    prob_chart_data = win_probability_trajectory.copy()
    prob_chart_data["win_probability_pct"] = prob_chart_data["win_probability"] * 100

    prob_chart = (
        alt.Chart(prob_chart_data)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "episode:O",
                title="Episode",
                axis=alt.Axis(labelAngle=0)
            ),
            y=alt.Y("win_probability_pct:Q", title="Win probability (%)"),
            color=alt.Color("contestant:N", title="Contestant"),
            tooltip=[
                alt.Tooltip("contestant:N", title="Contestant"),
                alt.Tooltip("episode:Q", title="Episode"),
                alt.Tooltip("win_probability_pct:Q", title="Win probability (%)", format=".1f")
            ]
        )
        .properties(height=350)
    )

    st.altair_chart(prob_chart, use_container_width=True)


# ---- METHODS ----

with st.expander("🔍 How does it work?", expanded=True):
    st.markdown("""
Our forecasts are generated through a simulation approach that models
the dynamics of Taskmaster episodes. Here's a high-level overview of how we create our predictions:

- Episode scores are added after each new episode
- Current performance is summarised per contestant
- The remaining series is simulated many times
- Win probability reflects how often each contestant wins across those simulations

⚠️ This is a fan-made data project for entertainment and analysis only.
""")
