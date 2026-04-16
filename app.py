from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_PATH = DATA_DIR / "processed"

required_files = [
    PROCESSED_PATH / "latest_snapshot.csv",
    PROCESSED_PATH / "win_probability_trajectory.csv",
    PROCESSED_PATH / "score_trajectory.csv",
]

missing = [str(p.name) for p in required_files if not p.exists()]

if missing:
    st.error(f"Missing required data files: {', '.join(missing)}")
    st.stop()


# ---- STYLING ----

st.markdown("""
<style>
/* Headings */
h1, h2, h3 {
    color: #4C1D5A;
}

/* Progress bars */
div[data-testid="stProgressBar"] > div > div {
    background-color: #5B2A6E;
}

/* Subtle card border enhancement */
[data-testid="stMarkdownContainer"] > div {
    border-radius: 12px;
}

/* Expander header */
[data-testid="stExpander"] summary {
    font-weight: 600;
    color: #5B2A6E;
}
</style>
""", unsafe_allow_html=True)


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


# ---- NAVIGATION ----
st.markdown("**📊 Dashboard** (👈 you're here!)")
st.page_link("pages/2_🧬_Archetypes.py", label="🧬 Archetypes")


# ---- HEADER ----
st.title("🍍 TaskLab: Taskmaster Forecast")

st.markdown("""
<div style="
    background-color: rgba(91, 42, 110, 0.06);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 12px;
">

**Welcome to TaskLab!**

TaskLab is a playful data project exploring how predictable the world of
Taskmaster really is, and providing insights into who might take that coveted
trophy home.

Using simulation and historical patterns, we estimate who's most likely to win
as the series unfolds, and how that picture changes week by week.

*We're in no way affiliated with Taskmaster or its creators (we wish!), but
we're big fans and hope this adds a bit of extra fun for fellow enthusiasts.*
""", unsafe_allow_html=True)


# ---- LATEST RESULTS ----
st.subheader("💡 Latest Results")
st.write(
    """
    Early results can swing quickly. This dashboard shows both latest scores, ranking, and how likely each contestant is to win.
    """
)

st.info("""
📺 **Episode 1 is in.**

Joanna makes a strong start, and the model already reflects that -  assigning her a very high early win probability.

At this stage, predictions are highly sensitive to single-episode results. Historically, the model becomes more reliable as more data accumulates.

With 9 episodes still to go, this is very much an early snapshot - and there’s plenty of time for things to change.
""")

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

with st.expander("🔍 How does it work?", expanded=False):
    st.markdown("""
    <div style="
        background-color: rgba(91, 42, 110, 0.06);
        padding: 16px;
        border-radius: 10px;
    ">

*This is a simplified overview - for a more detailed explanation of the methods and data, check out the [GitHub repo](https://github.com/keira-p/tasklab).*

**How are the forecasts generated?**

We simulate the remainder of the series thousands of times to estimate each contestant's chances of winning.

- Episode scores are updated after each new episode
- Each contestant's current performance is summarised (average score, consistency, etc.)
- The remaining episodes are simulated many times based on these profiles
- Final rankings are recorded for each simulation

A contestant's win probability reflects how often they win across all simulations.

With limited data early in a series, predictions are highly uncertain - but as more episodes air, accuracy improves significantly (historically reaching ~90% by the final episodes).

⚠️ *This is a fan-made data project for entertainment and analysis only.*
""", unsafe_allow_html=True)
