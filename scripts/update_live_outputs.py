from pathlib import Path
from pyexpat import features
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler

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


def build_latest_archetype_features(results_so_far, global_std):
    """
    Build the latest archetype features for each contestant in the new series.

    Inputs:
    - results_so_far: DataFrame with columns ["contestant", "episode", "episode_score"]

    Output:
    - features: DataFrame with columns ["contestant", "avg_score", "avg_std", "avg_momentum"]
    """

    df = results_so_far.sort_values(["contestant", "episode"])

    # Mean and std
    features = (
        df.groupby("contestant")["episode_score"]
        .agg(["mean", "std"])
        .reset_index()
        .rename(columns={
            "mean": "avg_score",
            "std": "avg_std"
        })
    )

    # Latest score per contestant
    latest_score = (
        df.groupby("contestant")
        .tail(1)[["contestant", "episode_score"]]
        .rename(columns={"episode_score": "latest_episode_score"})
    )

    # Merge before calculating momentum
    features = features.merge(latest_score, on="contestant", how="left")

    # Momentum: latest vs average
    features["avg_momentum"] = (
        features["latest_episode_score"] - features["avg_score"]
    )

    # Clean up
    features["avg_std"] = features["avg_std"].fillna(global_std)
    features["avg_std"] = features["avg_std"].replace(0, global_std)
    features["avg_momentum"] = features["avg_momentum"].fillna(0)

    print("Latest archetype features:")
    print(features)

    return features[["contestant", "avg_score", "avg_std", "avg_momentum"]]


def load_archetype_model(processed_path):
    """
    Load the saved archetype celntroids and scaler parameters.

    Output:
    - scaler: StandardScaler object fitted on the original archetype features
    - centroids: DataFrame with columns ["archetype_name", "avg_score", "avg_std", "avg_momentum"]
    """

    feature_cols = ["avg_score", "avg_std", "avg_momentum"]

    raw_centroids = pd.read_csv(PROCESSED_PATH / "archetype_centroids.csv", index_col=0)
    scaler_params = pd.read_csv(PROCESSED_PATH / "archetype_scaler.csv")

    # Rebuild scaler
    scaler = StandardScaler()
    scaler.mean_ = scaler_params["mean"].values
    scaler.scale_ = scaler_params["std"].values
    scaler.n_features_in_ = len(feature_cols)
    scaler.feature_names_in_ = np.array(feature_cols)

    # Scale centroids
    centroids = pd.DataFrame(
        scaler.transform(raw_centroids[feature_cols]),
        index=raw_centroids.index,
        columns=feature_cols
    )

    return scaler, centroids


def assign_nearest_archetype(row, centroids, scaler):
    """
    Assign the nearest archetype to a contestant based on distance to scaled centroids.

    Inputs:
    - row: Series with index ["contestant", "avg_score", "avg_std", "avg_momentum"]
    - centroids: DataFrame with columns ["archetype_name", "avg_score", "avg_std", "avg_momentum"]
    - scaler: StandardScaler object fitted on the original archetype features

    Output:
    - archetype_name: Name of the nearest archetype
    """

    best_archetype = None
    best_distance = float("inf")

    contestant_features = pd.DataFrame([{
        "avg_score": row["avg_score"],
        "avg_std": row["avg_std"],
        "avg_momentum": row["avg_momentum"]
    }])

    contestant_scaled = scaler.transform(contestant_features)[0]

    # Loop through centroids to find nearest archetype
    for archetype_name, centroid in centroids.iterrows():

        # Calculate Euclidean distance to the centroid
        distance = np.linalg.norm(contestant_scaled - centroid)

        # Update best archetype if this one is closer
        if distance < best_distance:
            best_distance = distance
            best_archetype = archetype_name

    return best_archetype


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

    scaler, centroids = load_archetype_model(PROCESSED_PATH)

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

    # Latest archetype features
    live_archetype_features = build_latest_archetype_features(live_results, global_std)
    live_archetype_features["archetype_name"] = live_archetype_features.apply(
        assign_nearest_archetype,
        axis=1,
        centroids=centroids,
        scaler=scaler
    )
    latest_snapshot = latest_snapshot.merge(
        live_archetype_features[["contestant", "archetype_name"]],
        on="contestant",
        how="left"
    )

    latest_snapshot.to_csv(PROCESSED_PATH / "latest_snapshot.csv", index=False)

    print("✅ Live outputs updated successfully.")
    print("✅ Live archetype features added to latest snapshot.")


if __name__ == "__main__":
    main()
