# Greedy Best-First Search
# Strategy: Always explore the node with LOWEST HEURISTIC VALUE (closest to goal)
# Result: Fast but not guaranteed optimal

import heapq

def greedy_best_first(graph, heuristics, start_node, goal_node, heuristic_func):
    """
    Greedy Best-First Search using a heuristic.
    
    How it works:
    1. Use a priority queue sorted by h(n) only (ignore cost-so-far)
    2. Always explore the node that "looks closest" to goal
    3. Stop as soon as you reach the goal
    
    Why it's fast:
    - h(n) directly points toward goal
    - Explores fewer nodes than uninformed search
    
    Why it's not optimal:
    - Ignores actual cost traveled so far
    - Might take a scenic route that looks close but costs more
    
    Args:
        graph: KarachiGraph object
        heuristics: KarachiHeuristics object
        start_node: integer ID of starting location
        goal_node: integer ID of destination
        heuristic_func: function reference (heuristics.h1_straight_line or h2_karachi_aware)
    
    Returns:
        path, total_cost, nodes_expanded, max_frontier_size
    """
    
    # Initialize
    # Priority queue entry: (heuristic_value, node_id)
    frontier = [(0, start_node)]
    
    visited = set()
    parent = {start_node: None}
    cost_so_far = {start_node: 0}
    
    nodes_expanded = 0
    max_frontier_size = 1
    
    
    # Main loop
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # Pop node with lowest h(n)
        h_value, current_node = heapq.heappop(frontier)
        
        # Skip if already visited
        if current_node in visited:
            continue
        
        visited.add(current_node)
        nodes_expanded += 1
        
        # Goal test: as soon as we pop the goal, we're done
        # (Note: this is different from UCS — Greedy stops immediately)
        if current_node == goal_node:
            # Reconstruct path
            path = []
            node = goal_node
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            
            total_cost = cost_so_far[goal_node]
            return path, total_cost, nodes_expanded, max_frontier_size
        
        # Expand neighbors
        neighbors = graph.get_neighbors(current_node)
        
        for neighbor_id, edge_weight in neighbors:
            if neighbor_id not in visited:
                # Calculate actual cost to reach this neighbor
                new_cost = cost_so_far[current_node] + edge_weight
                
                # Update if we found a cheaper path
                if neighbor_id not in cost_so_far or new_cost < cost_so_far[neighbor_id]:
                    cost_so_far[neighbor_id] = new_cost
                    parent[neighbor_id] = current_node
                    
                    # Calculate h(n) for this neighbor
                    h_value = heuristic_func(neighbor_id, goal_node)
                    
                    # Add to frontier with ONLY the heuristic value
                    # (not f(n) = g(n) + h(n) like in A*)
                    heapq.heappush(frontier, (h_value, neighbor_id))
    
    # No path found
    return [], 0, nodes_expanded, max_frontier_size