# A* Search
# Strategy: Explore nodes with lowest f(n) = g(n) + h(n)
# where g(n) = actual cost so far, h(n) = heuristic estimate to goal
# Result: Optimal AND efficient!

import heapq

def astar(graph, heuristics, start_node, goal_node, heuristic_func):
    """
    A* (A-Star) algorithm — the gold standard for pathfinding.
    
    How it works:
    1. f(n) = g(n) + h(n)
       - g(n) = actual cost traveled to reach n
       - h(n) = heuristic estimate from n to goal
    2. Priority queue sorts by f(n)
    3. Always explore node with lowest f(n) next
    
    Why it's optimal:
    - If h(n) is admissible (never overestimates), A* finds optimal path
    - Proof: when goal is popped, it has lowest f(n), so must be optimal
    
    Why it's efficient:
    - h(n) guides search toward goal
    - Expands far fewer nodes than UCS or BFS
    - The better the heuristic, the fewer nodes explored
    
    Args:
        graph: KarachiGraph object
        heuristics: KarachiHeuristics object
        start_node: integer ID of starting location
        goal_node: integer ID of destination
        heuristic_func: function reference (h1_straight_line or h2_karachi_aware)
    
    Returns:
        path, total_cost, nodes_expanded, max_frontier_size
    """
    
    # Initialize
    # Frontier entries: (f_value, node_id)
    # where f_value = cost_so_far + heuristic_estimate
    frontier = [(0, start_node)]
    
    visited = set()
    parent = {start_node: None}
    cost_so_far = {start_node: 0}
    
    nodes_expanded = 0
    max_frontier_size = 1
    
    
    # Main loop
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # Pop node with lowest f(n) = g(n) + h(n)
        f_value, current_node = heapq.heappop(frontier)
        
        # Skip if already visited
        if current_node in visited:
            continue
        
        visited.add(current_node)
        nodes_expanded += 1
        
        # Goal test
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
                
                # Only consider if we found a cheaper path
                if neighbor_id not in cost_so_far or new_cost < cost_so_far[neighbor_id]:
                    cost_so_far[neighbor_id] = new_cost
                    parent[neighbor_id] = current_node
                    
                    # Calculate h(n) for this neighbor
                    h_value = heuristic_func(neighbor_id, goal_node)
                    
                    # Calculate f(n) = g(n) + h(n)
                    # This is the KEY DIFFERENCE from Greedy and UCS
                    f_value = new_cost + h_value
                    
                    # Add to frontier with f(n)
                    heapq.heappush(frontier, (f_value, neighbor_id))
    
    # No path found
    return [], 0, nodes_expanded, max_frontier_size