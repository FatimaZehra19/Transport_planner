from karachi_transport.graph import KarachiGraph
import random


def hill_climbing(graph, heuristics, start, goal, heuristic_func, max_iterations=100):

    """
    Hill Climbing using heuristic guidance.

    Moves to neighbor with lowest heuristic value.
    Stops if no improvement possible.
    """

    current = start

    path = [current]

    nodes_expanded = 0

    iterations = 0

    while current != goal and iterations < max_iterations:

        neighbors = graph.get_neighbors(current)

        current_h = heuristic_func(current, goal)

        best_neighbor = None

        best_h = current_h

        # Explore neighbors
        for neighbor, edge_cost in neighbors:

            if neighbor not in path:

                neighbor_h = heuristic_func(neighbor, goal)

                # Move ONLY if heuristic improves
                if neighbor_h < best_h:

                    best_h = neighbor_h

                    best_neighbor = neighbor

        # Local optimum reached
        if best_neighbor is None:

            break

        current = best_neighbor

        path.append(current)

        nodes_expanded += 1

        iterations += 1

    # Success
    if current == goal:

        total_cost = graph.calculate_path_cost(path)

        return path, total_cost, nodes_expanded

    # Failure
    return None, float("inf"), nodes_expanded


def hill_climbing_random_restart(
        graph,
        heuristics,
        start,
        goal,
        heuristic_func,
        num_restarts=5
):

    """
    Hill Climbing with Random Restarts.
    """

    best_path = None

    best_cost = float("inf")

    total_nodes = 0

    for _ in range(num_restarts):

        neighbors = graph.get_neighbors(start)

        if not neighbors:

            return None, float("inf"), 0

        # Random first move
        random_neighbor = random.choice(neighbors)[0]

        # Run HC from random neighbor
        path, cost, nodes = hill_climbing(
            graph,
            heuristics,
            random_neighbor,
            goal,
            heuristic_func
        )

        total_nodes += nodes

        if path:

            # Reconnect original start
            if path[0] != start:

                full_path = [start] + path

            else:

                full_path = path

            full_cost = graph.calculate_path_cost(full_path)

            # Keep best solution
            if full_cost < best_cost:

                best_cost = full_cost

                best_path = full_path

    return best_path, best_cost, total_nodes