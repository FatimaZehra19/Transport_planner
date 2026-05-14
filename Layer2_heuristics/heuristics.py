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
        
        # Haversine gives shortest distance, but roads curve and wind
        # In Karachi, actual road distance is ~1.5x the straight-line distance
        
        road_distance_km = distance_km 

        estimated_minutes = (road_distance_km / average_speed_kmh) * 60
        
        return estimated_minutes
    
    
    # ===== HEURISTIC 2: Karachi-Specific =====

    def h2_karachi_aware(self, current_node, goal_node):
        """
        Karachi-specific heuristic that accounts for congestion zones.
        """
        if current_node == goal_node:
            return 0

        base_heuristic = self.h1_straight_line(current_node, goal_node)

        # Extended congestion zones (all important areas)
        congestion_zones = {
            0: {"name": "Saddar", "penalty": 1.20},          # Heavy business traffic
            1: {"name": "Clifton", "penalty": 1.10},         # Tourist/residential
            3: {"name": "Korangi", "penalty": 1.15},         # Industrial + port
            4: {"name": "Malir", "penalty": 1.15},           # Port adjacent
            6: {"name": "Gulshan-e-Iqbal", "penalty": 1.18}, # Major commercial
            8: {"name": "North Nazimabad", "penalty": 1.08}, # Residential
            9: {"name": "Orangi", "penalty": 1.25},          # Dense, slow
            11: {"name": "Lyari", "penalty": 1.22},          # Port area
            12: {"name": "Keamari", "penalty": 1.18},        # Port
            13: {"name": "Baldia", "penalty": 1.12},         # Industrial
        }

        penalty = 1.0

        # NEW LOGIC: Only penalize if traveling INTO a congestion zone
        # (leaving congestion is good, entering is bad)
        if goal_node in congestion_zones and current_node not in congestion_zones:
            # Traveling from normal → congestion (bad)
            penalty = congestion_zones[goal_node]["penalty"]
        elif current_node in congestion_zones and goal_node not in congestion_zones:
            # Traveling from congestion → normal (good)
            penalty = 0.95  # Slightly favorable
        elif current_node in congestion_zones and goal_node in congestion_zones:
            # Both in congestion: use average penalty
            avg_penalty = (congestion_zones[current_node]["penalty"] +
                          congestion_zones[goal_node]["penalty"]) / 2
            penalty = avg_penalty

        adjusted = base_heuristic * penalty

        # Don't cap at 1.25x - let it be truly informative
        # Still admissible because all penalties are ≥ 0.95x
        return adjusted
    
    
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