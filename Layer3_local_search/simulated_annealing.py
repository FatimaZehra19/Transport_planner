"""
Simulated Annealing for Karachi network optimisation (Layer 3).

SA escapes local optima by probabilistically accepting worse states.
The acceptance probability for a worsening move of magnitude |delta| at
temperature T is  exp(delta / T)  (delta < 0 for a decline in score).

As T decreases, the algorithm becomes increasingly greedy — early on it
explores widely; late in the run it refines the current best.

Three cooling schedules are tested: r = 0.90 (fast), 0.95 (medium), 0.99 (slow).
Each is run 50 independent times from random starts.
"""

import math
import random
from .network_optimizer import NetworkState


# ---------------------------------------------------------------------------
# Single SA run
# ---------------------------------------------------------------------------

def simulated_annealing(graph, cooling_rate=0.95, initial_temp=0.30,
                        min_temp=0.0001, max_iter=2000):
    """
    Single Simulated Annealing run for network optimisation.

    Maximises NetworkState.objective() using random single-swap neighbours.

    Parameters
    ----------
    graph        : KarachiGraph
    cooling_rate : float  — multiplicative cooling factor per iteration
    initial_temp : float  — starting temperature (score scale: 0–1)
    min_temp     : float  — stop when temperature drops below this
    max_iter     : int    — hard cap on iterations

    Returns
    -------
    best_state : NetworkState  — best configuration visited during the run
    best_score : float
    iterations : int           — number of iterations completed
    """
    state = NetworkState.random_state(graph)
    best_state = state
    temperature = initial_temp

    for iteration in range(max_iter):
        if temperature < min_temp:
            break

        neighbour = state.random_neighbour()
        delta = neighbour.objective() - state.objective()

        if delta > 0:
            # Always accept improvement
            state = neighbour
        else:
            # Accept decline with Boltzmann probability
            probability = math.exp(delta / temperature)
            if random.random() < probability:
                state = neighbour

        # Track global best (not just current)
        if state.objective() > best_state.objective():
            best_state = state

        temperature *= cooling_rate

    return best_state, best_state.objective(), iteration + 1


# ---------------------------------------------------------------------------
# Multi-run experiment
# ---------------------------------------------------------------------------

def run_sa_experiment(graph, cooling_rate, num_runs=50):
    """
    Run SA `num_runs` times with the given cooling rate.

    Parameters
    ----------
    graph       : KarachiGraph
    cooling_rate: float
    num_runs    : int

    Returns
    -------
    scores : list[float]   — best score from each run
    stats  : dict          — summary statistics
    """
    scores = []
    for _ in range(num_runs):
        _, score, _ = simulated_annealing(graph, cooling_rate=cooling_rate)
        scores.append(score)

    avg = sum(scores) / len(scores)
    variance = sum((s - avg) ** 2 for s in scores) / len(scores)
    std_dev = variance ** 0.5

    stats = {
        "cooling_rate": cooling_rate,
        "num_runs":     num_runs,
        "scores":       scores,
        "avg_score":    avg,
        "best_score":   max(scores),
        "worst_score":  min(scores),
        "std_dev":      std_dev,
    }
    return scores, stats
