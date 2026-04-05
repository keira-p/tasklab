# 🧠 TaskLab — Taskmaster Forecast

Forecasting Taskmaster outcomes using simulation and historical patterns.

A playful data project exploring how predictable Taskmaster really is — and how likely each contestant is to win as a series unfolds.

⚠️ We’re in no way affiliated with Taskmaster or its creators (we wish!), but we're big fans and hope this adds a bit of extra fun for fellow enthusiasts.

⚠️ This is a fan-made data project for entertainment and analysis only.

---

## 🔗 Live App

👉 [View the live dashboard]("https://tasklab.streamlit.app/")

---

## 🎯 What this project does

TaskLab estimates each contestant’s probability of winning a Taskmaster series based on performance so far.

As each episode airs, the model:

- updates contestant performance metrics
- simulates the remaining episodes many times
- estimates how often each contestant wins

This produces a **live, evolving forecast** of the series outcome.

---

## 🧠 How it works

At a high level:

1. Episode scores are added after each new episode
2. Current performance is summarised per contestant
3. Remaining episodes are simulated using a probabilistic model
4. The simulation is repeated many times (Monte Carlo simulation)
5. Win probability = how often each contestant wins across simulations

---

## 📊 Key features

- 📈 **Live win probabilities** updated after each episode
- 🏆 **Current performance snapshot** (scores + rankings)
- 🎲 **Simulation-based forecasting** (not just point predictions)
- 📉 **Win probability over time**
- 📊 **Score trajectory tracking**

---

## 🗂️ Project structure

```text
tasklab/
├── app.py                         # Streamlit app
├── simulation.py                  # Simulation logic
├── data/
│   ├── live/
│   │   └── live_results.csv       # Episode-level input data
│   └── processed/
│       ├── latest_snapshot.csv
│       ├── win_probability_trajectory.csv
│       └── score_trajectory.csv
├── notebooks/                    # Exploration & modelling
├── requirements.txt
```

---

## 🔬 Modelling & insights

Before building the live simulation, I explored what drives Taskmaster performance using historical data.

### Predicting final outcomes

A Ridge Regression model was trained to predict each contestant’s final score based on:

- cumulative score so far
- recent performance
- consistency (variance in scores)
- position within the series

This model showed that:

- the eventual winner is often identifiable early in the series
- prediction accuracy improves significantly after the halfway point
- mid-series outcomes are more volatile

### Simulation vs prediction

The project then moves beyond point prediction to **probabilistic simulation**.

- The regression model estimates expected performance
- The simulation models uncertainty and variability
- This is implemented using a Monte Carlo approach, simulating many possible series outcomes
- Together, they provide a more realistic view of possible outcomes

### Archetypes

Contestants were also grouped into performance archetypes based on scoring patterns:

| Archetype                                               | Description |
|---------------------------------------------------------|------------|
| 🔥 ** The Chaos Engine** aka Elite but Chaotic          | High scoring but inconsistent |
| 🎯 **The Silent Assassin** aka Strong & Consistent.     | High and reliable performers |
| 🎢 **The Late Bloomer** aka Chaotic Improvers           | Volatile but improving over time |
| 🏁 **The Early Leader** aka Strong early, decline later |
| 🍍 **The Underdog** aka Strugglers                      | Lower scoring and not improving |

These archetypes help explain *why* different contestants have different win probabilities.
