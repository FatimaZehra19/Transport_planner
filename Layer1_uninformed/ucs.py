# Uniform Cost Search (UCS)

import heapq


def ucs(graph, start_node, goal_node):
    # --- Initialize data structures ---
    
    # Priority queue as list of (cost, node_id)
    # heapq maintains min-heap property (lowest cost at index 0)
    # Each entry is (cost_so_far, node_id, path_history)
    frontier = [(0, start_node)]
    
    # Track visited nodes
    visited = set()
    
    # parent[node] = how we reached this node
    parent = {start_node: None}
    
    # cost_so_far[node] = lowest cost to reach this node found so far
    cost_so_far = {start_node: 0}
    
    # Metrics
    nodes_expanded = 0
    max_frontier_size = 1
    
    
    # --- Main UCS loop ---
    
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        
        # heappop removes and returns the smallest element
        current_cost, current_node = heapq.heappop(frontier)
        
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
        
        # Explore neighbors
        neighbors = graph.get_neighbors(current_node)
        
        for neighbor_id, edge_weight in neighbors:
            if neighbor_id not in visited:
                # Calculate cost to reach this neighbor
                new_cost = current_cost + edge_weight
                
                # Only update if we found a cheaper path to this neighbor
                if neighbor_id not in cost_so_far or new_cost < cost_so_far[neighbor_id]:
                    cost_so_far[neighbor_id] = new_cost
                    parent[neighbor_id] = current_node
                    # Add to priority queue with its cost
                    # heapq will automatically maintain min-heap order
                    heapq.heappush(frontier, (new_cost, neighbor_id))
    
    
    # No path found
    return [], 0, nodes_expanded, max_frontier_size

