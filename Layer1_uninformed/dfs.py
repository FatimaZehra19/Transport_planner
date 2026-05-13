# Depth-First Search (DFS)


def dfs(graph, start_node, goal_node):
    
    # --- Initialize data structures ---
    
    # Stack holds nodes to explore. We process from the end (LIFO behavior)
    frontier = [start_node]
    
    # Track which nodes we've visited (cycle detection)
    visited = set([start_node])
    
    # parent[node] = how we reached this node (for path reconstruction)
    parent = {start_node: None}
    
    # cost_so_far[node] = total travel time to reach this node
    cost_so_far = {start_node: 0}
    
    # Metrics
    nodes_expanded = 0
    max_frontier_size = 1
    
    
    # --- Main DFS loop ---
    
    while frontier:
        # Track largest frontier
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # Pop from END of list (LIFO — this is what makes it DFS)
        current_node = frontier.pop()
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
        
        # Get neighbors
        neighbors = graph.get_neighbors(current_node)
        
        # IMPORTANT: In DFS, the order we add neighbors matters!
        # Reverse the order so we explore neighbors in a sensible order
        neighbors.reverse()
        
        for neighbor_id, edge_weight in neighbors:
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                frontier.append(neighbor_id)
                parent[neighbor_id] = current_node
                cost_so_far[neighbor_id] = cost_so_far[current_node] + edge_weight
    
    
    # No path found
    return [], 0, nodes_expanded, max_frontier_size


