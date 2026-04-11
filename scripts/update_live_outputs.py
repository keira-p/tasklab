from pathlib import Path
import pandas as pd

from simulation import simulate_many_from_snapshot

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
PROCESSED_PATH = DATA_DIR / "processed"
LIVE_PATH = DATA_DIR / "live"

TOTAL_EPISODES = 10
N_SIMULATIONS = 1000


def build_modelling_snapshot(results_so_far, total_episodes, global_std):
    """
    Build the snapshot of contestant performance to be used for modelling.

    Inputs:
    - results_so_far: DataFrame with columns ["contestant", "episode", "episode_score"]
    - total_episodes: Total number of episodes in the season
    - global_std: Global standard deviation of episode scores (used for contestants with no variance)

    Output:
    - modelling_snapshot: DataFrame with columns ["contestant", "cumulative_score",
      "mean_score_so_far", "std_score_so_far", "remaining_episodes"]
    """

    live_snapshot = (
        results_so_far
        .sort_values(["contestant", "episode"])
        .groupby("contestant")["episode_score"]
        .agg(["sum", "mean", "std", "count"])
        .reset_index()
        .rename(columns={
            "sum": "cumulative_score",
            "mean": "mean_score_so_far",
            "std": "std_score_so_far",
            "count": "episodes_played"
        })
    )

    live_snapshot["remaining_episodes"] = (
        total_episodes - live_snapshot["episodes_played"]
    )

    live_snapshot["std_score_so_far"] = live_snapshot["std_score_so_far"].fillna(global_std)
    live_snapshot["std_score_so_far"] = live_snapshot["std_score_so_far"].replace(0, global_std)

    return live_snapshot


def calculate_win_probabilities(modelling_snapshot, n_simulations):
    """
    Calculate win probabilities for each contestant based on the modelling snapshot.

    Inputs:
    - modelling_snapshot: DataFrame with columns ["contestant", "cumulative_score",
      "mean_score_so_far", "std_score_so_far", "remaining_episodes"]
    - n_simulations: Number of simulations to run for estimating win probabilities

    Output:
    - win_probs: DataFrame with columns ["contestant", "win_probability"]
    """

    simulations = simulate_many_from_snapshot(
        modelling_snapshot,
        n_simulations=n_simulations
    )

    win_probs = (
        simulations[simulations["rank"] == 1]
        .groupby("contestant")
        .size()
        .reset_index(name="wins")
    )

    all_contestants = modelling_snapshot[["contestant"]].copy()

    win_probs = all_contestants.merge(win_probs, on="contestant", how="left")
    win_probs["wins"] = win_probs["wins"].fillna(0)
    win_probs["win_probability"] = win_probs["wins"] / n_simulations

    return win_probs[["contestant", "win_probability"]]


def build_latest_snapshot(results_so_far, win_probs):
    """
    Build the latest snapshot of contestant performance, combining scores and win probabilities.

    Inputs:
    - results_so_far: DataFrame with columns ["contestant", "episode", "episode_score"]
    - win_probs: DataFrame with columns ["contestant", "win_probability"]

    Output:
    - latest_snapshot: DataFrame with columns ["contestant", "latest_episode_score",
      "cumulative_score", "current_rank", "win_probability"]
    """

    cum_scores = (
        results_so_far
        .groupby("contestant")["episode_score"]
        .sum()
        .reset_index(name="cumulative_score")
    )

    latest_ep = results_so_far["episode"].max()

    latest_scores = (
        results_so_far[results_so_far["episode"] == latest_ep]
        [["contestant", "episode_score"]]
        .rename(columns={"episode_score": "latest_episode_score"})
    )

    latest_snapshot = cum_scores.merge(win_probs, on="contestant", how="left")
    latest_snapshot = latest_snapshot.merge(latest_scores, on="contestant", how="left")

    latest_snapshot["win_probability"] = latest_snapshot["win_probability"].fillna(0)

    latest_snapshot["current_rank"] = (
        latest_snapshot["cumulative_score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    latest_snapshot = latest_snapshot.sort_values(
        ["current_rank", "win_probability"],
        ascending=[True, False]
    ).reset_index(drop=True)

    return latest_snapshot[
        [
            "contestant",
            "latest_episode_score",
            "cumulative_score",
            "current_rank",
            "win_probability"
        ]
    ]


def main():
    """
    Update live outputs based on the latest results.

    This script should be run after each episode's results are added to the live_results.csv file.

    Inputs:
    - live_results.csv: DataFrame with columns ["contestant", "episode", "episode_score"]
    - snapshot_df.csv: DataFrame with historical episode scores for all contestants (used to calculate global std)

    Outputs:
    - latest_snapshot.csv: DataFrame with columns ["contestant", "latest_episode_score",
      "cumulative_score", "current_rank", "win_probability"]
    - win_probability_trajectory.csv: DataFrame with columns ["contestant", "episode", "win_probability"]
    - score_trajectory.csv: DataFrame with columns ["contestant", "episode", "episode_score", "cumulative_score"]
    """

    live_results = pd.read_csv(LIVE_PATH / "live_results.csv")
    snapshot_df = pd.read_csv(PROCESSED_PATH / "snapshot_df.csv")

    global_std = snapshot_df["episode_score"].std()

    # Latest snapshot
    modelling_snapshot = build_modelling_snapshot(
        live_results,
        TOTAL_EPISODES,
        global_std
    )

    win_probs = calculate_win_probabilities(
        modelling_snapshot,
        N_SIMULATIONS
    )

    latest_snapshot = build_latest_snapshot(
        live_results,
        win_probs
    )

    latest_snapshot.to_csv(PROCESSED_PATH / "latest_snapshot.csv", index=False)

    # Win probability trajectory
    trajectory = []
    latest_episode = live_results["episode"].max()

    for episode_t in range(1, latest_episode + 1):
        results_so_far = live_results[live_results["episode"] <= episode_t].copy()

        modelling_snapshot_t = build_modelling_snapshot(
            results_so_far,
            TOTAL_EPISODES,
            global_std
        )

        win_probs_t = calculate_win_probabilities(
            modelling_snapshot_t,
            N_SIMULATIONS
        )

        win_probs_t["episode"] = episode_t
        trajectory.append(win_probs_t)

    trajectory_df = pd.concat(trajectory, ignore_index=True)
    trajectory_df = trajectory_df[["contestant", "episode", "win_probability"]]
    trajectory_df.to_csv(PROCESSED_PATH / "win_probability_trajectory.csv", index=False)

    # Score trajectory
    score_trajectory = live_results.copy()
    score_trajectory = score_trajectory.sort_values(["contestant", "episode"])
    score_trajectory["cumulative_score"] = (
        score_trajectory.groupby("contestant")["episode_score"].cumsum()
    )

    score_trajectory.to_csv(PROCESSED_PATH / "score_trajectory.csv", index=False)

    print("✅ Live outputs updated successfully.")


if __name__ == "__main__":
    main()
