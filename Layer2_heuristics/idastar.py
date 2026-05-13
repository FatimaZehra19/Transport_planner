# Iterative Deepening A* (IDA*)
# Strategy: Like DFS but with f(n) threshold, increase threshold when needed
# Result: Optimal like A*, but uses much less memory

import sys


def ida_star(graph, heuristics, start_node, goal_node, heuristic_func):
    """
    Iterative Deepening A* (IDA*) algorithm.
    
    How it works:
    1. Perform depth-first search with f(n) threshold
    2. Set threshold = h(start)
    3. Explore nodes only if f(n) <= threshold
    4. If goal not found, increase threshold to smallest f(n) exceeded
    5. Repeat from step 3 until goal found
    
    Why it's memory-efficient:
    - Uses DFS (stack), not priority queue
    - Only stores current path (O(depth))
    - Compare: A* stores entire frontier (O(nodes))
    
    Why it's still optimal:
    - Like A*, guarantees optimal path if h(n) is admissible
    - But trades space for time (more iterations)
    
    Args:
        graph: KarachiGraph object
        heuristics: KarachiHeuristics object
        start_node: integer ID of starting location
        goal_node: integer ID of destination
        heuristic_func: function reference
    
    Returns:
        path, total_cost, nodes_expanded, max_frontier_size
    """
    
    # Global tracking
    nodes_expanded_total = 0
    max_frontier_size = 0
    
    # Initial threshold = h(start)
    threshold = heuristic_func(start_node, goal_node)
    
    # Keep track of best f(n) found in each iteration
    path_to_goal = None
    cost_to_goal = 0
    
    while True:
        # Perform DFS with current threshold
        result, min_f = _ida_star_search(
            graph, heuristics, start_node, goal_node,
            heuristic_func, threshold
        )
        
        # Update metrics
        nodes_expanded_total += result["nodes_expanded"]
        max_frontier_size = max(max_frontier_size, result["max_frontier"])
        
        # If we found the goal, return it
        if result["found"]:
            return result["path"], result["cost"], nodes_expanded_total, max_frontier_size
        
        # If no progress (min_f is infinity), no solution exists
        if min_f == float("inf"):
            return [], 0, nodes_expanded_total, max_frontier_size
        
        # Increase threshold for next iteration
        threshold = min_f


def _ida_star_search(graph, heuristics, node, goal, heuristic_func, threshold, 
                     cost_so_far=0, parent=None, visited_path=None, metrics=None):
    """
    Helper function: DFS search with f(n) threshold.
    
    Args:
        node: current node
        goal: goal node
        threshold: maximum f(n) to explore
        cost_so_far: actual cost to reach current node
        parent: parent node (for path reconstruction)
        visited_path: current path (to avoid cycles)
        metrics: tracking object
    
    Returns:
        result dict with found, path, cost, min_f exceeded, nodes_expanded
    """
    
    if visited_path is None:
        visited_path = {}
    if metrics is None:
        metrics = {"nodes_expanded": 0, "max_frontier": 0}
    
    # Calculate f(n)
    h_value = heuristic_func(node, goal)
    f_value = cost_so_far + h_value
    
    metrics["nodes_expanded"] += 1
    
    # If f(n) exceeds threshold, prune this branch
    if f_value > threshold:
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
        # Reconstruct path
        path = [node]
        current = node
        while current in visited_path and visited_path[current] is not None:
            current = visited_path[current]
            path.append(current)
        path.reverse()
        
        return {
            "found": True,
            "path": path,
            "cost": cost_so_far,
            "min_f": f_value,
            "nodes_expanded": metrics["nodes_expanded"],
            "max_frontier": metrics["max_frontier"]
        }, f_value
    
    # Mark as visited in this path
    visited_path[node] = parent
    
    # Track frontier size (current recursion depth)
    metrics["max_frontier"] = max(metrics["max_frontier"], len(visited_path))
    
    # Explore neighbors
    neighbors = graph.get_neighbors(node)
    min_f = float("inf")
    
    for neighbor_id, edge_weight in neighbors:
        # Avoid cycles
        if neighbor_id not in visited_path:
            new_cost = cost_so_far + edge_weight
            result, f_exceeded = _ida_star_search(
                graph, heuristics, neighbor_id, goal, heuristic_func,
                threshold, new_cost, node, visited_path, metrics
            )
            
            if result["found"]:
                return result, f_exceeded
            
            min_f = min(min_f, f_exceeded)
    
    # Remove from path for other branches
    del visited_path[node]
    
    return {
        "found": False,
        "path": [],
        "cost": 0,
        "min_f": min_f,
        "nodes_expanded": metrics["nodes_expanded"],
        "max_frontier": metrics["max_frontier"]
    }, min_f