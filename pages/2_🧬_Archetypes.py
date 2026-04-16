from pathlib import Path
import pandas as pd
import streamlit as st


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
st.set_page_config(page_title="Archetypes", page_icon="🧬", layout="wide")

st.markdown("""
<style>
.archetype-card {
    min-height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 8px;
}
</style>
""", unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_PATH = BASE_DIR / "data" / "processed"


# ---- NAVIGATION ----
st.page_link("app.py", label="📊 Dashboard")
st.markdown("**🧬 Archetypes** (👈 you're here!)")


# ---- ARCHETYPE INFO ----
ARCHETYPE_INFO = {
    "The Chaos Engine": {
        "emoji": "🔥",
        "description": "High scoring but volatile - capable of dominating or collapsing from one episode to the next.",
        "examples": ["Katherine Ryan", "Dara Ó Briain", "Liza Tarbuck"],
        "traits": {
            "Scoring": 5,
            "Consistency": 2,
            "Momentum": 3,
        },
    },
    "The Silent Assassin": {
        "emoji": "🎯",
        "description": "Consistently high-performing - steadily accumulates points with minimal variation.",
        "examples": ["Noel Fielding", "Kerry Godliman", "Sarah Millican"],
        "traits": {
            "Scoring": 4,
            "Consistency": 5,
            "Momentum": 4,
        },
    },
    "The Late Bloomer": {
        "emoji": "🌸",
        "description": "Builds momentum over time - starts slower, but performance improves across the series.",
        "examples": ["Mel Giedroyc", "Asim Chaudhry", "Kiell Smith-Bynoe"],
        "traits": {
            "Scoring": 2,
            "Consistency": 1,
            "Momentum": 5,
        },
    },
    "The Early Leader": {
        "emoji": "🏁",
        "description": "Strong early performance - but harder to sustain, with results often declining over time.",
        "examples": ["Chris Ramsey", "Rhod Gilbert", "Guz Khan"],
        "traits": {
            "Scoring": 3,
            "Consistency": 3,
            "Momentum": 2,
        },
    },
    "The Underdog": {
        "emoji": "🍍",
        "description": "Lower overall scoring - less consistent, but still capable of occasional standout moments.",
        "examples": ["Julian Clary", "Tim Key", "Sara Pascoe"],
        "traits": {
            "Scoring": 1,
            "Consistency": 4,
            "Momentum": 1,
        },
    },
}


# ---- IMAGE MAP ----
IMAGE_MAP = {
    "Amy Gledhill": "https://taskmaster.tv/sites/default/files/styles/contestant_in_frame/public/contestant/AMY.png?itok=midtxzy5",
    "Armando Iannucci": "https://taskmaster.tv/sites/default/files/styles/contestant_in_frame/public/contestant/ARMANDO.png?itok=hJNlu4BS",
    "Joanna Page": "https://taskmaster.tv/sites/default/files/styles/contestant_in_frame/public/contestant/JOANNA.png?itok=xtZ8J7uv",
    "Joel Dommett": "https://taskmaster.tv/sites/default/files/styles/contestant_in_frame/public/contestant/JOEL.png?itok=eDR4d6Tg",
    "Kumail Nanjiani": "https://taskmaster.tv/sites/default/files/styles/contestant_in_frame/public/contestant/KUMAIL.png?itok=WqqlT5e3",
}


# ---- HELPER FUNCTIONS ----

def render_trait_dots(label, value, max_dots=5):
    filled = "●" * value
    empty = "○" * (max_dots - value)
    return f"{label} {filled}{empty}"


def render_archetype_card(title, description, examples=None, emoji="", traits=None):
    examples_text = f"e.g. {', '.join(examples)}" if examples else "&nbsp;"

    traits_html = ""
    if traits:
        trait_lines = []
        for label, value in traits.items():
            dots = "●" * value + "○" * (5 - value)
            trait_lines.append(
                f"<div style='margin-bottom: 6px;'><strong>{label}</strong> {dots}</div>"
            )
        traits_html = "".join(trait_lines)

    html = f"""
    <div style="
        border: 1px solid rgba(91, 42, 110, 0.2);
        border-top: 3px solid #5B2A6E;
        border-radius: 12px;
        padding: 22px 18px;
        min-height: 180px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    ">
        <div>
            <div style="font-size: 1.05rem; font-weight: 700; margin-bottom: 14px;">
                {emoji} {title}
            </div>
            <div style="margin-bottom: 16px; line-height: 1.6;">
                {description}
            </div>
            <div style="margin-bottom: 16px; line-height: 1.6;">
                {traits_html}
            </div>
        </div>
        <div style="color: #6b7280; font-size: 0.95rem;">
            {examples_text}
        </div>
    </div>
    """
    st.html(html)


def render_current_contestant_card(row, archetype_info, image_map):
    name = row["contestant"]
    archetype = row["archetype_name"]
    rank = int(row["current_rank"])
    win_prob = float(row["win_probability"])

    info = archetype_info.get(archetype, {})
    emoji = info.get("emoji", "❓")

    image_url = image_map.get(name)

    image_html = ""
    if image_url:
        image_html = f"""
        <img src="{image_url}" style="
            width:72px;
            height:72px;
            object-fit:cover;
            border-radius:50%;
            margin-bottom:10px;
        ">
        """

    html = f"""
    <div style="text-align:center;">
        {image_html}
        <div style="font-weight:700; margin-bottom:6px;">{name}</div>
        <div style="margin-bottom:6px; color:#5B2A6E;">{emoji} {archetype}</div>
        <div style="font-size:0.9rem; color:#6b7280;">Rank {rank}</div>
    </div>
    """
    st.html(html)

    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    st.progress(win_prob)
    st.caption(f"{win_prob:.0%} win chance")


# --- LOAD DATA ---
latest_snapshot = pd.read_csv(PROCESSED_PATH / "latest_snapshot.csv")
score_trajectory = pd.read_csv(PROCESSED_PATH / "score_trajectory.csv")

episodes_played = score_trajectory["episode"].max()


# ---- TITLE AND INTRO ----
st.title("🧬 Meet the Archetypes")

st.markdown("""
<div style="
    background-color: rgba(91, 42, 110, 0.06);
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 12px;
">

**Taskmaster looks chaotic - but patterns emerge over time.**

Some contestants quietly accumulate points. Others swing between brilliance and disaster. Some peak early, while others grow into the series.

TaskLab groups these patterns into five recurring archetypes - helping explain not just who is winning, but how they're playing the game.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border: 1px solid #D4A017; opacity: 0.3;'>", unsafe_allow_html=True)


# ---- CURRENT CONTESTANTS ----
st.markdown("### ⭐️ Series 21 so far")

if episodes_played <= 1:
    st.caption("With only one episode aired, these are very provisional - expect them to shift quickly.")

cols = st.columns(len(latest_snapshot), gap="medium")

for col, (_, row) in zip(cols, latest_snapshot.iterrows()):
    with col:
        render_current_contestant_card(row, ARCHETYPE_INFO, IMAGE_MAP)

st.markdown("<hr style='border: 1px solid #D4A017; opacity: 0.3;'>", unsafe_allow_html=True)

# ---- ARCHETYPES GRID ----
st.subheader("The five archetypes at a glance")

col1, col2 = st.columns(2, gap="large")
with col1:
    render_archetype_card(
        title="What are archetypes?",
        description=(
            "Archetypes group contestants by how they perform over time - not just how well they score.<br><br>"
            "Each archetype reflects typical patterns across scoring level, consistency, and momentum over time."
        ),
        emoji="🧠",
        traits=None
    )
with col2:
    info = ARCHETYPE_INFO["The Chaos Engine"]
    render_archetype_card(
        title="The Chaos Engine",
        description=info["description"],
        examples=info["examples"],
        emoji=info["emoji"],
        traits=info["traits"]
    )

st.write("")

col3, col4 = st.columns(2, gap="large")
with col3:
    info = ARCHETYPE_INFO["The Silent Assassin"]
    render_archetype_card(
        title="The Silent Assassin",
        description=info["description"],
        examples=info["examples"],
        emoji=info["emoji"],
        traits=info["traits"]
    )
with col4:
    info = ARCHETYPE_INFO["The Late Bloomer"]
    render_archetype_card(
        title="The Late Bloomer",
        description=info["description"],
        examples=info["examples"],
        emoji=info["emoji"],
        traits=info["traits"]
    )

st.write("")

col5, col6 = st.columns(2, gap="large")
with col5:
    info = ARCHETYPE_INFO["The Early Leader"]
    render_archetype_card(
        title="The Early Leader",
        description=info["description"],
        examples=info["examples"],
        emoji=info["emoji"],
        traits=info["traits"]
    )
with col6:
    info = ARCHETYPE_INFO["The Underdog"]
    render_archetype_card(
        title="The Underdog",
        description=info["description"],
        examples=info["examples"],
        emoji=info["emoji"],
        traits=info["traits"]
    )


# ---- HOW IT WORKS ----
st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

with st.expander("How does this work?", expanded=False):
    st.markdown("""
    <div style="
        background-color: rgba(91, 42, 110, 0.06);
        padding: 16px;
        border-radius: 10px;
    ">

*This is a simplified overview - for a more detailed explanation of the methods and data, check out the [GitHub repo](https://github.com/keira-p/tasklab).*

We analysed historical Taskmaster contestants and grouped them into behavioural archetypes using clustering.

Each contestant is represented using three core signals:

- **Scoring** - how strongly they perform overall
- **Consistency** - how stable or variable those scores are
- **Momentum** - whether their performance improves or fades over time

These signals are combined to form a multi-dimensional profile for each contestant, and KMeans clustering is used to identify five recurring archetypes.

Each archetype is represented by a centroid - the average profile of contestants in that group.
Current contestants are then matched to the closest centroid based on their performance so far.

Simple rule-based definitions (e.g. “high score = strong performer”) only matched these archetypes ~37% of the time, whereas assigning contestants based on distance to centroids matched ~86% - suggesting the clustering captures more nuanced behaviour than simple thresholds.

This is not a definitive label, but a way of providing a grounded, interpretable read on the kind of series a contestant is having.

⚠️ *This is a fan-made data project for entertainment and analysis only.*
""", unsafe_allow_html=True)
