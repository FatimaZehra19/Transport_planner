from karachi_transport.graph import KarachiGraph
from Layer1_uninformed.ucs import ucs
from Layer2_heuristics.astar import astar
from Layer2_heuristics.heuristics import KarachiHeuristics
from .test_cases import test_cases
from .hill_climbing import hill_climbing, hill_climbing_random_restart
from .simulated_annealing import simulated_annealing


def run_layer3_tests():

    graph = KarachiGraph()

    heuristics = KarachiHeuristics(graph)

    print("\n" + "=" * 120)
    print("LAYER 3: LOCAL SEARCH ALGORITHMS")
    print("=" * 120 + "\n")

    all_results = {
        "hill_climbing": [],
        "hill_climbing_rr": [],
        "simulated_annealing": []
    }

    for test in test_cases:

        name = test["name"]

        start = test["start"]

        goal = test["goal"]

        start_name = graph.get_node_name(start)

        goal_name = graph.get_node_name(goal)

        print(f"\n{name}")

        print(f"  From: {start_name} -> To: {goal_name}")

        # UCS baseline
        ucs_path, ucs_cost, ucs_nodes, _ = ucs(
            graph,
            start,
            goal
        )

        ucs_cost = ucs_cost or float("inf")

        print(
            f"\n  BASELINE (UCS): Cost {ucs_cost} min | Nodes: {ucs_nodes}"
        )

        # A* baseline
        a_path, a_cost, a_nodes, _ = astar(
            graph,
            heuristics,
            start,
            goal,
            heuristics.h1_straight_line
        )

        a_cost = a_cost or float("inf")

        print(
            f"  BASELINE (A*):  Cost {a_cost} min | Nodes: {a_nodes}"
        )

        # Hill Climbing
        hc_path, hc_cost, hc_nodes = hill_climbing(
            graph,
            heuristics,
            start,
            goal,
            heuristics.h1_straight_line
        )

        if hc_path:

            hc_path_str = " -> ".join(
                [graph.get_node_name(n) for n in hc_path]
            )

            print(
                f"\n  Hill Climbing:           Cost {hc_cost} min | Nodes: {hc_nodes} | Path: {hc_path_str}"
            )

            all_results["hill_climbing"].append(
                (hc_cost, hc_nodes)
            )

        else:

            print(
                f"\n  Hill Climbing:           FAILED (stuck in local optimum)"
            )

            all_results["hill_climbing"].append(
                (float("inf"), hc_nodes)
            )

        # Hill Climbing with Random Restart
        hcrr_path, hcrr_cost, hcrr_nodes = hill_climbing_random_restart(
            graph,
            heuristics,
            start,
            goal,
            heuristics.h1_straight_line,
            num_restarts=5
        )

        if hcrr_path:

            hcrr_path_str = " -> ".join(
                [graph.get_node_name(n) for n in hcrr_path]
            )

            print(
                f"  Hill Climbing (5 RS):    Cost {hcrr_cost} min | Nodes: {hcrr_nodes} | Path: {hcrr_path_str}"
            )

            all_results["hill_climbing_rr"].append(
                (hcrr_cost, hcrr_nodes)
            )

        else:

            print(
                f"  Hill Climbing (5 RS):    FAILED"
            )

            all_results["hill_climbing_rr"].append(
                (float("inf"), hcrr_nodes)
            )

        # Simulated Annealing
        sa_path, sa_cost, sa_nodes = simulated_annealing(
            graph,
            heuristics,
            start,
            goal,
            heuristics.h1_straight_line,
            initial_temp=100,
            cooling_rate=0.95
        )

        if sa_path:

            sa_path_str = " -> ".join(
                [graph.get_node_name(n) for n in sa_path]
            )

            print(
                f"  Simulated Annealing:     Cost {sa_cost} min | Nodes: {sa_nodes} | Path: {sa_path_str}"
            )

            all_results["simulated_annealing"].append(
                (sa_cost, sa_nodes)
            )

        else:

            print(
                f"  Simulated Annealing:     FAILED"
            )

            all_results["simulated_annealing"].append(
                (float("inf"), sa_nodes)
            )

        print("-" * 120)

    # Summary
    print("\n" + "=" * 120)

    print("SUMMARY: PATH COST COMPARISON")

    print("=" * 120)

    for algo in [
        "hill_climbing",
        "hill_climbing_rr",
        "simulated_annealing"
    ]:

        # Ignore failed searches
        costs = [
            c for c, n in all_results[algo]
            if c != float("inf")
        ]

        avg_cost = (
            sum(costs) / len(costs)
            if costs else float("inf")
        )

        if avg_cost == float("inf"):

            print(
                f"{algo:25} avg cost: FAILED"
            )

        else:

            print(
                f"{algo:25} avg cost: {avg_cost:.1f} min"
            )


if __name__ == "__main__":

    run_layer3_tests()