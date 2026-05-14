"""
Network Optimization Problem — Karachi Transport Planner (Layer 3)

Problem Statement
-----------------
KMC wants to select K=8 bus stops from 20 candidate locations and design
direct routes between them to maximise city-wide service quality.

This is fundamentally different from Layers 1 & 2:
  - There is no start/goal pair.
  - The "path" to the solution does not matter — only the final configuration.
  - We cannot use A* here because the search space is combinatorial (C(20,8) = 125,970
    possible stop sets) with no path structure to exploit.
  - Local search explores nearby configurations (swap one stop) guided by an
    objective function.

State
-----
A tuple of K sorted node IDs representing which stops are active.
Routes are derived automatically: any original-graph edge whose both endpoints
are active stops becomes a route.

Objective Function (maximise, range 0–1)
-----------------------------------------
  score = 0.40 * coverage + 0.35 * connectivity + 0.25 * efficiency

  coverage     — fraction of all 20 city nodes that are "served"
                 (a node is served if it IS a stop or directly adjacent to one)
  connectivity — fraction of active-stop pairs joined by a direct route
  efficiency   — normalised inverse of average route travel time
                 (faster routes score higher)

Neighbourhood
-------------
Single-swap: replace exactly one active stop with one inactive stop.
  size = K * (N - K) = 8 * 12 = 96 neighbours per state
Rationale: small enough for steepest-ascent, large enough to escape many
local optima with random restarts.
"""

import random
from karachi_transport.edges import EDGES

K_STOPS = 8       # bus stops to select
N_NODES = 20      # total candidate locations
MAX_EDGE_W = 35   # maximum edge weight in the graph (normalisation denominator)

# Objective function component weights — must sum to 1.0
W_COVERAGE     = 0.40
W_CONNECTIVITY = 0.35
W_EFFICIENCY   = 0.25


class NetworkState:
    """
    Immutable snapshot of a candidate bus-network configuration.

    Attributes
    ----------
    active_stops : tuple[int]
        Sorted tuple of K stop node IDs.
    """

    def __init__(self, graph, active_stops):
        self.graph = graph
        self.active_stops = tuple(sorted(active_stops))
        self._score = None
        self._routes = None

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def random_state(cls, graph):
        """Create a uniformly random initial configuration."""
        stops = random.sample(range(N_NODES), K_STOPS)
        return cls(graph, stops)

    # ------------------------------------------------------------------
    # Derived attributes
    # ------------------------------------------------------------------

    def get_routes(self):
        """All original-graph edges whose both endpoints are active stops."""
        if self._routes is None:
            active = set(self.active_stops)
            self._routes = [(a, b, w) for a, b, w in EDGES
                            if a in active and b in active]
        return self._routes

    def objective(self):
        """
        Compute and cache the objective score.

        coverage     (40 %): fraction of 20 nodes served
        connectivity (35 %): fraction of K*(K-1)/2 stop-pairs with a direct route
        efficiency   (25 %): 1 – avg_route_time / MAX_EDGE_W
        """
        if self._score is not None:
            return self._score

        active = set(self.active_stops)

        # --- Coverage ---
        covered = set(self.active_stops)
        for stop in self.active_stops:
            for neighbor, _ in self.graph.get_neighbors(stop):
                covered.add(neighbor)
        coverage = len(covered) / N_NODES

        # --- Connectivity ---
        routes = self.get_routes()
        max_pairs = K_STOPS * (K_STOPS - 1) / 2
        connectivity = len(routes) / max_pairs if max_pairs > 0 else 0.0

        # --- Efficiency ---
        if routes:
            avg_time = sum(w for _, _, w in routes) / len(routes)
            efficiency = 1.0 - (avg_time / MAX_EDGE_W)
        else:
            efficiency = 0.0

        self._score = (W_COVERAGE * coverage +
                       W_CONNECTIVITY * connectivity +
                       W_EFFICIENCY * efficiency)
        return self._score

    # ------------------------------------------------------------------
    # Neighbourhood
    # ------------------------------------------------------------------

    def get_all_neighbours(self):
        """
        Return all 96 single-swap neighbours.
        Used by steepest-ascent hill climbing.
        """
        active = set(self.active_stops)
        inactive = [n for n in range(N_NODES) if n not in active]
        neighbours = []
        for idx, stop in enumerate(self.active_stops):
            for new_stop in inactive:
                new_stops = list(self.active_stops)
                new_stops[idx] = new_stop
                neighbours.append(NetworkState(self.graph, new_stops))
        return neighbours

    def random_neighbour(self):
        """
        Return one random single-swap neighbour.
        Used by simulated annealing.
        """
        active = set(self.active_stops)
        inactive = [n for n in range(N_NODES) if n not in active]
        remove = random.choice(list(self.active_stops))
        add = random.choice(inactive)
        new_stops = [s for s in self.active_stops if s != remove] + [add]
        return NetworkState(self.graph, new_stops)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def describe(self):
        """Return a dict of human-readable metrics for this configuration."""
        active = set(self.active_stops)
        covered = set(self.active_stops)
        for stop in self.active_stops:
            for neighbor, _ in self.graph.get_neighbors(stop):
                covered.add(neighbor)

        routes = self.get_routes()
        score = self.objective()
        max_pairs = K_STOPS * (K_STOPS - 1) / 2
        avg_time = (sum(w for _, _, w in routes) / len(routes)) if routes else 0

        return {
            "stop_ids":       list(self.active_stops),
            "stop_names":     [self.graph.get_node_name(s) for s in self.active_stops],
            "routes":         len(routes),
            "covered_nodes":  len(covered),
            "coverage_pct":   round(len(covered) / N_NODES * 100, 1),
            "connectivity_pct": round(len(routes) / max_pairs * 100, 1),
            "avg_route_time": round(avg_time, 1),
            "score":          round(score, 4),
        }

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __eq__(self, other):
        return self.active_stops == other.active_stops

    def __hash__(self):
        return hash(self.active_stops)

    def __repr__(self):
        return f"NetworkState(stops={self.active_stops}, score={self.objective():.4f})"
