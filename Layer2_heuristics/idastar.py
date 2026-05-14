# Iterative Deepening A* (IDA*)
# Strategy: Like DFS but with f(n) threshold, increase threshold when needed
# Result: Optimal like A*, but uses much less memory

import sys


def ida_star(graph, heuristics, start_node, goal_node, heuristic_func):
    """
    Iterative Deepening A* (IDA*) algorithm.
    """

    # Global tracking
    nodes_expanded_total = 0
    max_frontier_size = 0

    # Initial threshold = h(start)
    threshold = heuristic_func(start_node, goal_node)

    while True:

        # Perform DFS with current threshold
        result, min_f = _ida_star_search(
            graph,
            heuristics,
            start_node,
            goal_node,
            heuristic_func,
            threshold
        )

        # Update metrics
        nodes_expanded_total += result["nodes_expanded"]

        max_frontier_size = max(
            max_frontier_size,
            result["max_frontier"]
        )

        # Goal found
        if result["found"]:

            return (
                result["path"],
                result["cost"],
                nodes_expanded_total,
                max_frontier_size
            )

        # No solution exists
        if min_f == float("inf"):

            return (
                [],
                0,
                nodes_expanded_total,
                max_frontier_size
            )

        # Increase threshold
        threshold = min_f


def _ida_star_search(
        graph,
        heuristics,
        node,
        goal,
        heuristic_func,
        threshold,
        cost_so_far=0,
        parent=None,
        visited_path=None,
        parent_map=None,
        best_costs=None,
        metrics=None
):
    """
    Helper function: DFS search with f(n) threshold.
    """

    if visited_path is None:
        visited_path = {}

    if parent_map is None:
        parent_map = {}

    if best_costs is None:
        best_costs = {}

    if metrics is None:
        metrics = {
            "nodes_expanded": 0,
            "max_frontier": 0
        }

    # Mark current node in DFS path
    visited_path[node] = True

    # Track frontier size
    metrics["max_frontier"] = max(
        metrics["max_frontier"],
        len(visited_path)
    )

    # Calculate f(n)
    h_value = heuristic_func(node, goal)

    f_value = cost_so_far + h_value

    metrics["nodes_expanded"] += 1

    # COST-BASED PRUNING
    # Avoid revisiting expensive duplicate states
    if node in best_costs and cost_so_far >= best_costs[node]:

        del visited_path[node]

        return {
            "found": False,
            "path": [],
            "cost": 0,
            "min_f": float("inf"),
            "nodes_expanded": metrics["nodes_expanded"],
            "max_frontier": metrics["max_frontier"]
        }, float("inf")

    best_costs[node] = cost_so_far

    # Prune if threshold exceeded
    if f_value > threshold:

        del visited_path[node]

        return {
            "found": False,
            "path": [],
            "cost": 0,
            "min_f": f_value,
            "nodes_expanded": metrics["nodes_expanded"],
            "max_frontier": metrics["max_frontier"]
        }, f_value

    # Goal test
    if node == goal:

        path = [node]

        current = node

        while current in parent_map:

            current = parent_map[current]

            path.append(current)

        path.reverse()

        del visited_path[node]

        return {
            "found": True,
            "path": path,
            "cost": cost_so_far,
            "min_f": f_value,
            "nodes_expanded": metrics["nodes_expanded"],
            "max_frontier": metrics["max_frontier"]
        }, f_value

    # Explore neighbors
    neighbors = graph.get_neighbors(node)

    # SORT NEIGHBORS USING HEURISTIC
    # Helps IDA* explore promising nodes first
    neighbors = sorted(
        neighbors,
        key=lambda x: heuristic_func(x[0], goal)
    )

    min_f = float("inf")

    for neighbor_id, edge_weight in neighbors:

        # Avoid cycles
        if neighbor_id not in visited_path:

            # Store parent
            parent_map[neighbor_id] = node

            new_cost = cost_so_far + edge_weight

            result, f_exceeded = _ida_star_search(
                graph,
                heuristics,
                neighbor_id,
                goal,
                heuristic_func,
                threshold,
                new_cost,
                node,
                visited_path,
                parent_map,
                best_costs,
                metrics
            )

            # Goal found
            if result["found"]:

                return result, f_exceeded

            min_f = min(min_f, f_exceeded)

    # Backtrack
    del visited_path[node]

    return {
        "found": False,
        "path": [],
        "cost": 0,
        "min_f": min_f,
        "nodes_expanded": metrics["nodes_expanded"],
        "max_frontier": metrics["max_frontier"]
    }, min_f