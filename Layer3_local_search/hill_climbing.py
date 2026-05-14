"""
Hill Climbing algorithms for Karachi network optimization (Layer 3).

Two steepest-ascent variants:
  - Without sideways moves: stops the moment no strict improvement exists.
  - With sideways moves: also accepts equal-score moves (plateau walking)
    up to max_sideways consecutive steps.

Random-Restart Hill Climbing runs one of the above variants 50 times from
independent random initial states and keeps the best result.
"""

import random
from .network_optimizer import NetworkState


# ---------------------------------------------------------------------------
# Core steepest-ascent function
# ---------------------------------------------------------------------------

def hill_climbing_steepest(graph, initial_state=None, allow_sideways=False,
                           max_sideways=10):
    """
    Steepest-ascent hill climbing for network optimisation.

    Parameters
    ----------
    graph          : KarachiGraph
    initial_state  : NetworkState or None  (random if None)
    allow_sideways : bool  — whether to allow moves to equal-score neighbours
    max_sideways   : int   — max consecutive sideways moves before stopping

    Returns
    -------
    best_state : NetworkState
    best_score : float
    steps      : int  (number of moves made)
    """
    state = initial_state if initial_state is not None else NetworkState.random_state(graph)
    steps = 0
    sideways_streak = 0

    while True:
        neighbours = state.get_all_neighbours()
        best_next = max(neighbours, key=lambda s: s.objective())
        delta = best_next.objective() - state.objective()

        if delta > 1e-9:
            # Strict improvement — always accept
            state = best_next
            steps += 1
            sideways_streak = 0

        elif allow_sideways and abs(delta) <= 1e-9 and sideways_streak < max_sideways:
            # Sideways move (plateau walking)
            state = best_next
            steps += 1
            sideways_streak += 1

        else:
            # Local optimum or plateau limit reached
            break

    return state, state.objective(), steps


# ---------------------------------------------------------------------------
# Random-Restart Hill Climbing
# ---------------------------------------------------------------------------

def random_restart_hc(graph, num_restarts=50, allow_sideways=False,
                      max_sideways=10):
    """
    Random-Restart Hill Climbing.

    Runs hill_climbing_steepest `num_restarts` times from fresh random states
    and returns the best configuration found, plus per-run statistics.

    Parameters
    ----------
    graph         : KarachiGraph
    num_restarts  : int  — number of independent restarts (assignment: 50)
    allow_sideways: bool — passed through to hill_climbing_steepest
    max_sideways  : int  — passed through to hill_climbing_steepest

    Returns
    -------
    best_state : NetworkState   — best configuration across all restarts
    best_score : float
    stats      : dict           — per-run metrics for reporting
    """
    # Estimate baseline from random states
    baseline_scores = [NetworkState.random_state(graph).objective()
                       for _ in range(10)]
    baseline = sum(baseline_scores) / len(baseline_scores)

    best_state = None
    best_score = -1.0
    all_scores = []
    all_steps = []

    for _ in range(num_restarts):
        state, score, steps = hill_climbing_steepest(
            graph,
            allow_sideways=allow_sideways,
            max_sideways=max_sideways
        )
        all_scores.append(score)
        all_steps.append(steps)
        if score > best_score:
            best_score = score
            best_state = state

    # "Success" = final score at least 5 % above the random baseline
    success_threshold = baseline * 1.05
    success_count = sum(1 for s in all_scores if s >= success_threshold)

    stats = {
        "scores":         all_scores,
        "steps":          all_steps,
        "success_rate":   success_count / num_restarts,
        "avg_score":      sum(all_scores) / len(all_scores),
        "best_score":     best_score,
        "avg_steps":      sum(all_steps) / len(all_steps),
        "baseline":       baseline,
        "n_restarts":     num_restarts,
        "allow_sideways": allow_sideways,
    }

    return best_state, best_score, stats
