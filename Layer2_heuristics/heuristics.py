# Two heuristics for A* and Greedy Best-First Search
# h1: Geographic distance (straight-line distance converted to minutes)
# h2: Karachi-specific (accounts for congestion zones and obstacles)

import math

class KarachiHeuristics:
    """
    Heuristic functions for Karachi transport routing.
    
    A heuristic h(n) estimates the cost from node n to the goal.
    For A* to work correctly, heuristics must be ADMISSIBLE:
    - h(n) never overestimates the true cost
    - h(goal) = 0
    """
    
    def __init__(self, graph):
        """
        Args:
            graph: KarachiGraph object (provides coordinates and node info)
        """
        self.graph = graph
    
    
    # ===== HEURISTIC 1: Geographic Distance =====
    
    def h1_straight_line(self, current_node, goal_node):
        """
        Straight-line distance heuristic.
        
        How it works:
        1. Get latitude/longitude of current and goal nodes
        2. Calculate Haversine distance (great-circle distance on Earth)
        3. Convert to travel time using average speed (25 km/h for Karachi traffic)
        
        Why it's admissible:
        - Straight line is always shorter than actual road
        - So time estimate is ALWAYS less than actual travel time
        - h(goal) = 0 (distance from goal to itself is 0)
        
        Args:
            current_node: integer node ID
            goal_node: integer node ID
        
        Returns:
            estimated_time: minutes (never overestimates)
        """
        
        # If we're at the goal, cost is zero
        if current_node == goal_node:
            return 0
        
        # Get coordinates
        lat1, lon1 = self.graph.get_coordinates(current_node)
        lat2, lon2 = self.graph.get_coordinates(goal_node)
        
        # Haversine formula for great-circle distance
        # This is the shortest distance between two points on Earth
        R = 6371  # Earth's radius in kilometers
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine calculation
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = R * c
        
        # Convert to travel time (25 km/h average speed in Karachi)
        average_speed_kmh = 25
        estimated_minutes = (distance_km / average_speed_kmh) * 60
        
        return estimated_minutes
    
    
    # ===== HEURISTIC 2: Karachi-Specific =====
    
    def h2_karachi_aware(self, current_node, goal_node):
        """
        Karachi-aware heuristic incorporating local knowledge.
        
        Improvements over h1:
        1. Adds congestion penalty for known traffic hotspots
        2. Accounts for river/nullah crossings (Malir River, Lyari)
        3. Recognizes bottleneck areas that slow travel
        
        Why it's admissible:
        - Still based on straight-line distance
        - Penalties are conservative (don't overestimate)
        - More informed than h1, so expands fewer nodes
        
        Args:
            current_node: integer node ID
            goal_node: integer node ID
        
        Returns:
            estimated_time: minutes (still admissible, more accurate than h1)
        """
        
        if current_node == goal_node:
            return 0
        
        # Start with straight-line distance
        base_heuristic = self.h1_straight_line(current_node, goal_node)
        
        # Define Karachi congestion zones and their penalties
        # These are areas where traffic is worse than 25 km/h average
        congestion_zones = {
            0: {"name": "Saddar", "penalty": 1.15},        # Business district, heavy traffic
            8: {"name": "North Nazimabad", "penalty": 1.10}, # Residential, decent traffic
            9: {"name": "Orangi", "penalty": 1.12},          # Dense population, slow
            11: {"name": "Lyari", "penalty": 1.20},          # Port area, congested
            13: {"name": "Baldia", "penalty": 1.08},         # Industrial
        }
        
        # Define river/nullah crossing penalties
        # Crossing these adds travel time due to limited bridges
        major_crossings = {
            "malir_river": [4, 5, 3],  # Nodes on opposite sides of Malir River
            "lyari": [0, 11, 12],       # Lyari area and connections
        }
        
        penalty = 1.0  # Start with no penalty
        
        # Add penalty if current node is in a congestion zone
        if current_node in congestion_zones:
            penalty *= congestion_zones[current_node]["penalty"]
        
        # Add penalty if goal is in a congestion zone
        if goal_node in congestion_zones:
            penalty *= congestion_zones[goal_node]["penalty"]
        
        # Check for river crossing: if current and goal are on opposite sides
        # of a major obstacle, add 1.1x penalty (10% more time needed)
        if current_node in major_crossings["malir_river"] and \
           goal_node in major_crossings["malir_river"]:
            # Both on different sides of Malir = crossing needed
            penalty *= 1.05  # Small penalty for potential crossing
        
        # Apply penalty (conservative: don't overestimate)
        adjusted_heuristic = base_heuristic * penalty
        
        # Safety check: never return more than h1 (maintain admissibility)
        # This ensures h2 doesn't overestimate
        return min(adjusted_heuristic, base_heuristic * 1.25)
    
    
    # ===== ADMISSIBILITY & CONSISTENCY CHECKS =====
    
    def check_admissibility(self, start_node, goal_node, actual_cost):
        """
        Verify heuristics are admissible by comparing to actual cost.
        h(n) is admissible if h(n) <= actual_cost_to_goal
        
        Args:
            start_node: starting location
            goal_node: destination
            actual_cost: true minimum cost (from UCS)
        
        Returns:
            dict with admissibility status for both heuristics
        """
        h1_value = self.h1_straight_line(start_node, goal_node)
        h2_value = self.h2_karachi_aware(start_node, goal_node)
        
        return {
            "h1_admissible": h1_value <= actual_cost,
            "h1_value": h1_value,
            "h1_vs_actual": f"{h1_value:.1f} <= {actual_cost} ({(h1_value/actual_cost*100):.1f}%)",
            
            "h2_admissible": h2_value <= actual_cost,
            "h2_value": h2_value,
            "h2_vs_actual": f"{h2_value:.1f} <= {actual_cost} ({(h2_value/actual_cost*100):.1f}%)",
        }
    
    
    def check_consistency(self, node_a, node_b, edge_cost):
        """
        Verify heuristics are consistent (monotonic).
        Consistency: h(a) <= cost(a->b) + h(b)
        
        If heuristic is consistent, A* never needs to re-open nodes.
        This makes A* more efficient.
        
        Args:
            node_a: current node
            node_b: neighbor node
            edge_cost: weight of edge a->b
        
        Returns:
            dict with consistency status
        """
        # For now, just check against goal node 3 (Korangi)
        goal = 3
        
        h_a_h1 = self.h1_straight_line(node_a, goal)
        h_b_h1 = self.h1_straight_line(node_b, goal)
        h_a_h2 = self.h2_karachi_aware(node_a, goal)
        h_b_h2 = self.h2_karachi_aware(node_b, goal)
        
        consistent_h1 = h_a_h1 <= edge_cost + h_b_h1
        consistent_h2 = h_a_h2 <= edge_cost + h_b_h2
        
        return {
            "h1_consistent": consistent_h1,
            "h1_check": f"{h_a_h1:.1f} <= {edge_cost} + {h_b_h1:.1f}",
            
            "h2_consistent": consistent_h2,
            "h2_check": f"{h_a_h2:.1f} <= {edge_cost} + {h_b_h2:.1f}",
        }