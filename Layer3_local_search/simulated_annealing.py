import math
import random
from karachi_transport.graph import KarachiGraph


def simulated_annealing(
        graph,
        heuristics,
        start,
        goal,
        heuristic_func,
        initial_temp=300,
        cooling_rate=0.98,
        max_iterations=1000
):

    """
    Simulated Annealing using heuristic guidance.
    """

    current = start

    current_path = [current]

    current_h = heuristic_func(current, goal)

    nodes_expanded = 0

    temperature = initial_temp

    for iteration in range(max_iterations):

        # Goal reached
        if current == goal:

            total_cost = graph.calculate_path_cost(current_path)

            return current_path, total_cost, nodes_expanded

        neighbors = graph.get_neighbors(current)

        valid_neighbors = [
            (n, c)
            for n, c in neighbors
            if n not in current_path
        ]

        if not valid_neighbors:

            break

        # Pick random neighbor
        next_node, edge_cost = random.choice(valid_neighbors)

        next_h = heuristic_func(next_node, goal)

        # Energy difference
        delta = next_h - current_h

        # Accept better move
        if delta < 0:

            accept = True

        else:

            probability = math.exp(-delta / temperature)

            accept = random.random() < probability

        if accept:

            current = next_node

            current_h = next_h

            current_path.append(current)

            nodes_expanded += 1

        # Cool temperature
        temperature *= cooling_rate

        # Stop when temperature too low
        if temperature < 0.01:

            break

    # Final success check
    if current == goal:

        total_cost = graph.calculate_path_cost(current_path)

        return current_path, total_cost, nodes_expanded

    return None, float("inf"), nodes_expanded