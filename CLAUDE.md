# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Karachi Transport Planner is a pure Python 3.8+ educational project implementing 6 graph search algorithms across 3 layers to solve shortest-path routing between 20 real locations in Karachi, Pakistan. No external dependencies — only standard library (`collections`, `heapq`, `math`).

## Running the Project

```bash
# Layer 1: Uninformed search (BFS, DFS, UCS)
python run_Layer1.py

# Layer 2: Heuristic search (Greedy Best-First, A*, IDA*)
python run_Layer2.py

# Layer 3: Local search (Hill Climbing, Simulated Annealing)
python run_layer3.py
```

Each script instantiates `KarachiGraph`, runs all algorithms across 5 predefined test cases, prints per-case results (path, cost, nodes expanded, max frontier size), and prints a comparison summary table.

There is no test runner, linter, or build system.

## Architecture

### Data Layer: `karachi_transport/`

- **`graph.py`** — Central `KarachiGraph` class. Builds a bidirectional adjacency list from `nodes.py` and `edges.py`. Key methods: `get_neighbors(node_id)` → `(neighbor_id, travel_time)` tuples; `get_coordinates(node_id)` → `(lat, lon)`; `calculate_path_cost(path)`; `straight_line_distance(a, b)` using the Haversine formula converted to minutes.
- **`nodes.py`** — 20 locations as `{id: {name, lat, lon}}`.
- **`edges.py`** — ~40 undirected weighted edges as `(node_a, node_b, travel_time_minutes)` tuples.

### Algorithm Layers

Each layer is self-contained: algorithm files + `test_cases.py` + `results.py`. All algorithms track `nodes_expanded` and `max_frontier_size` for comparison.

**`Layer1_uninformed/`** — BFS (deque/FIFO), DFS (stack/LIFO), UCS (priority queue by cost). UCS is the only optimal algorithm in this layer.

**`Layer2_heuristics/`** — Greedy Best-First (`h(n)` only), A* (`f(n) = g(n) + h(n)`), IDA* (iterative deepening with `f(n)` threshold). Heuristics live in `heuristics.py`:
- `h1_straight_line`: Haversine distance → minutes (admissible baseline)
- `h2_karachi_aware`: Adds congestion-zone penalties while remaining admissible

**`Layer3_local_search/`** — Hill Climbing (greedy neighbor ascent, stops at local optima) and Simulated Annealing (probabilistic escape). Neither guarantees optimality.

### Algorithm Pattern

All algorithms share the same structure: initialize frontier → maintain visited set → track parent pointers for path reconstruction → pop node → goal test → expand neighbors.

### Entry Points

`run_Layer*.py` → `Layer*/results.py` → `run_layer*_tests()` → instantiates `KarachiGraph` → runs algorithms → prints output.

## Key Design Decisions

- Edges are bidirectional but stored as one-directional tuples in `edges.py`; `graph.py` mirrors them when building the adjacency list.
- Heuristics must remain admissible (never overestimate) to preserve A*/IDA* optimality — `h2_karachi_aware` adds penalties carefully to avoid violating this.
- Test cases are designed to expose specific algorithm weaknesses (e.g., a case where BFS and UCS disagree to show why edge weights matter).
