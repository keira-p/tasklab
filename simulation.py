import numpy as np
import pandas as pd

def simulate_one_series(series_stats, n_episodes, random_state=None):
    """
    Simulate one full Taskmaster series.

    Parameters:
    - series_stats: dataframe with one row per contestant
      (must include mean + std of episode_score)
    - n_episodes: number of episodes to simulate
    - random_state: seed for reproducibility (optional)
    """

    # Create random number generator
    rng = np.random.default_rng(random_state)

    results = []

    # Loop over each contestant
    for _, row in series_stats.iterrows():
        # Extract contestant name and score stats
        contestant = row["contestant"]
        mean_score = row["episode_score_mean"]
        std_score = row["episode_score_std"]

        # Simulate scores for each episode
        simulated_scores = rng.normal(
            loc=mean_score,     # average performance
            scale=std_score,    # variability in performance
            size=n_episodes     # number of episodes to simulate
            )

        # Clean up values (e.g. no negative scores)
        simulated_scores = np.clip(simulated_scores, 0, 35) # historical max = 30

        # Total series score
        total_score = simulated_scores.sum()

        # Store results
        results.append({
            "contestant": contestant,
            "simulated_total_score": total_score
        })

    # Convert results to dataframe
    results_df = pd.DataFrame(results)

    # Rank contestants by simulated total score
    results_df = results_df.sort_values(
        "simulated_total_score", ascending=False
    ).reset_index(drop=True)

    return results_df


def simulate_many_series(series_stats, n_episodes, n_simulations=1000):
    """
    Simulate the sameTaskmaster series multiple times.

    Parameters:
     - series_stats: one row per contestant with mean/std stats
    - n_episodes: number of episodes in the series
    - n_simulations: how many full series to simulate

    Returns:
    - dataframe containing every contestant's result in every simulation
    """

    all_simulations = []

    for sim_id in range(n_simulations):

        sim_result = simulate_one_series(
            series_stats=series_stats,
            n_episodes=n_episodes,
            random_state=sim_id # Use sim number as seed for reproducibility
        )

        # Create new column to track which simulation this is
        sim_result["simulation"] = sim_id

        # Create rank within simulated series
        sim_result["simulated_rank"] = sim_result["simulated_total_score"].rank(
            method="min", ascending=False
        ).astype(int)

        # Store results
        all_simulations.append(sim_result)

    # Combine all simulations into one dataframe
    all_simulations_df = pd.concat(all_simulations, ignore_index=True)

    return all_simulations_df


def simulate_from_snapshot(simulation_inputs, random_state=None):
    """
    Simulate the rest of a series from a given snapshot of contestant performance up to a certain episode.

    Parameters:
    - simulation_inputs: DataFrame containing contestant performance metrics at the snapshot episode.
    - random_state: Optional random seed for reproducibility.

    Returns:
    - DataFrame with simulated final scores for each contestant at the end of the series.
    """

    # Generate random numbers for the simulation
    rng = np.random.default_rng(random_state)

    results = []

    # Iterate over each contestant in the snapshot
    for _, row in simulation_inputs.iterrows():

        # Extract contestant info and performance metrics
        contestant = row["contestant"]
        current_score = row["cumulative_score"]
        mean_score = row["mean_score_so_far"]
        std_score = row["std_score_so_far"]
        remaining_eps = int(row["remaining_episodes"])

        # Simulate scores for the remaining episodes
        simulated_future_scores = rng.normal(
            loc=mean_score,         # average performance so far
            scale=std_score,        # variability in performance so far
            size=remaining_eps      # number of remaining episodes to simulate
        )

        # Keep values realistic (capped at 35)
        simulated_future_scores = np.clip(
            simulated_future_scores, 0, 35  # based on historical max 30
            )

        # Total future score
        total_future_score = simulated_future_scores.sum()

        # Final total score for the contestant
        simulated_final_score = current_score + total_future_score

        results.append({
            "contestant": contestant,
            "final_score": simulated_final_score
        })

    # Return results as DataFrame
    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        "final_score", ascending=False
    ).reset_index(drop=True)

    return results_df


def simulate_many_from_snapshot(simulation_inputs, n_simulations=1000):
    """
    Simulate the rest of a series multiple times from a given snapshot of contestant performance.

    Parameters:
    - simulation_inputs: DataFrame containing contestant performance metrics at the snapshot episode.
    - n_simulations: Number of simulations to run.

    Returns:
    - DataFrame with simulated final scores for each contestant across all simulations.
    """
    all_results = []

    for sim_id in range(n_simulations):

        sim_result = simulate_from_snapshot(
            simulation_inputs,
            random_state=sim_id        # Use sim_id for reproducibility
        )

        # Add simulation ID to the results
        sim_result["simulation_id"] = sim_id

        # Add rank based on final score
        sim_result["rank"] = sim_result["final_score"].rank(
            method="min", ascending=False
        ).astype(int)

        all_results.append(sim_result)

    # Combine all simulation results into a single DataFrame
    all_results_df = pd.concat(all_results, ignore_index=True)

    return all_results_df
