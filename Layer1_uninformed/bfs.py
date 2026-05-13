# Breadth-First Search (BFS)

from collections import deque


def bfs(graph, start_node, goal_node):

    # --- Initialize data structures ---
    
    # Queue holds nodes to explore. We process from front (FIFO behavior)
    frontier = deque([start_node])
    
    # Track which nodes we've already visited to avoid cycles
    visited = set([start_node])
    
    # For each node, remember which node we came from
    # parent[node] = the node we arrived from when reaching this node
    # Used to reconstruct the path once we find the goal
    parent = {start_node: None}
    
    # Track edge cost: cost_so_far[node] = total minutes traveled to reach this node
    cost_so_far = {start_node: 0}
    
    # Metrics for analysis
    nodes_expanded = 0
    max_frontier_size = 1
    
    
    # --- Main BFS loop ---
    
    while frontier:
        # Track the largest frontier we ever had
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # Pop the FIRST node from queue (FIFO — this is what makes it BFS)
        current_node = frontier.popleft()
        nodes_expanded += 1
        
        # Goal test: did we reach the destination?
        if current_node == goal_node:
            # Reconstruct path by following parent pointers backwards
            path = []
            node = goal_node
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()  # reverse to get start -> goal order
            
            total_cost = cost_so_far[goal_node]
            return path, total_cost, nodes_expanded, max_frontier_size
        
        # Get all neighbors of the current node
        # neighbors is a list of (neighbor_id, travel_time_in_minutes) tuples
        neighbors = graph.get_neighbors(current_node)
        
        # Explore each neighbor
        for neighbor_id, edge_weight in neighbors:
            # Only process unvisited neighbors (cycle detection)
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                frontier.append(neighbor_id)
                parent[neighbor_id] = current_node
                cost_so_far[neighbor_id] = cost_so_far[current_node] + edge_weight
    
    
    # --- No path found ---
    # If we exit the while loop without finding the goal, no path exists
    return [], 0, nodes_expanded, max_frontier_size


