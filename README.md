# Karachi Transport Planner

**CS-5101 Advanced Artificial Intelligence — Assignment 1 & 2**  
MS AI Evening Program, Spring 2026 | NED University of Engineering & Applied Sciences

A pure-Python project implementing **9 search algorithms across 3 layers** to solve transport planning problems on a real 20-node Karachi network.

---

## Project Overview

The Karachi Transport Planner models 20 real locations across Karachi as a weighted graph and applies progressively more sophisticated AI search techniques:

- **Layer 1** — Uninformed search (BFS, DFS, UCS): find routes with no domain knowledge
- **Layer 2** — Heuristic search (Greedy Best-First, A\*, IDA\*): use geographic coordinates to guide search
- **Layer 3** — Local search / combinatorial optimization (Hill Climbing, Simulated Annealing): select the best network configuration from 125,970 possible combinations

---

## Project Structure

```
Transport_planner/
├── karachi_transport/                  # Shared graph data and structure
│   ├── nodes.py                        # 20 Karachi locations with lat/lon
│   ├── edges.py                        # ~40 weighted edges (travel times in minutes)
│   └── graph.py                        # KarachiGraph class (adjacency list, Haversine)
│
├── Layer1_uninformed/                  # Uninformed search algorithms
│   ├── bfs.py                          # Breadth-First Search (FIFO queue)
│   ├── dfs.py                          # Depth-First Search (LIFO stack)
│   ├── ucs.py                          # Uniform Cost Search (min-heap)
│   ├── test_cases.py                   # 5 test scenarios
│   └── results.py                      # Runs all 3 algorithms, prints comparison table
│
├── Layer2_heuristics/                  # Heuristic search algorithms
│   ├── greedy.py                       # Greedy Best-First Search
│   ├── astar.py                        # A* Search (f = g + h)
│   ├── idastar.py                      # Iterative Deepening A*
│   ├── heuristics.py                   # h1: Haversine SLD; h2: Karachi-aware with congestion penalties
│   ├── test_cases.py                   # Same 5 test scenarios
│   ├── results.py                      # Runs algorithms + consistency check + generates chart
│   └── layer2_chart.png                # Nodes-expanded grouped bar chart (auto-generated)
│
├── Layer3_local_search/                # Local search / network optimisation
│   ├── network_optimizer.py            # NetworkState: 8-stop selection, objective function, neighbourhood
│   ├── hill_climbing.py                # Steepest-ascent HC (no/with sideways), random-restart x50
│   ├── simulated_annealing.py          # SA with Boltzmann acceptance, geometric cooling
│   ├── results.py                      # Runs experiments, prints tables, generates 3 charts
│   ├── layer3_hc_chart.png             # Hill Climbing comparison chart (auto-generated)
│   ├── layer3_sa_chart.png             # Simulated Annealing results chart (auto-generated)
│   └── layer3_network.png              # Geographic network plot of best solution (auto-generated)
│
├── run_Layer1.py                       # Entry point for Layer 1
├── run_Layer2.py                       # Entry point for Layer 2
├── run_layer3.py                       # Entry point for Layer 3
├── CLAUDE.md                           # Repository guide for Claude Code
├── Karachi_Transport_Planner_Report.docx  # Full academic report with all results
├── .gitignore
└── README.md
```

---

## Running the Project

**Prerequisites:** Python 3.8+ with no external dependencies for Layers 1 & 2. Layer 3 charts require `matplotlib`.

```bash
pip install matplotlib
```

```bash
# Layer 1: Uninformed search (BFS, DFS, UCS)
python run_Layer1.py

# Layer 2: Heuristic search (Greedy, A*, IDA*)
python run_Layer2.py

# Layer 3: Network optimisation (Hill Climbing, Simulated Annealing)
python run_layer3.py
```

Each script instantiates `KarachiGraph`, runs all algorithms, prints per-case results and a summary comparison table, then generates PNG charts.

---

## Karachi Network

**20 locations across the city:**

| Zone | Locations |
|------|-----------|
| Downtown / Port | Saddar, Clifton, Keamari, Lyari |
| Eastern | Korangi, Malir, Landhi, Malir Cantt |
| Northern | Orangi, Baldia, SITE Area, Gulshan-e-Iqbal, Johar |
| Central / Western | DHA, Gulberg, Federal B Area, Nazimabad, North Nazimabad, Liaquatabad, University Road |

~40 bidirectional weighted edges; travel times range from 10 to 60 minutes. Bottleneck corridors exist through SITE Area and Lyari Expressway.

---

## Algorithms

### Layer 1: Uninformed Search

| Algorithm | Data Structure | Optimal? |
|-----------|---------------|----------|
| BFS | FIFO queue (by hops) | Only for unweighted graphs |
| DFS | LIFO stack | No |
| UCS | Min-heap (by cost) | Yes — always finds cheapest path |

### Layer 2: Heuristic Search

Two admissible heuristics used by all three algorithms:

- **h1 (Haversine SLD):** Straight-line geographic distance converted to minutes — admissible baseline
- **h2 (Karachi-aware):** Adds traffic-zone congestion multipliers (up to 1.25×) while staying admissible; improves node efficiency

| Algorithm | Strategy | Optimal? |
|-----------|----------|----------|
| Greedy Best-First | Minimise h(n) only | No |
| A\* | Minimise f(n) = g(n) + h(n) | Yes, with admissible heuristic |
| IDA\* | Iterative deepening on f threshold | Yes, memory-efficient |

Layer 2 also outputs a **heuristic consistency verification** for 5 selected edges (checking h(a) ≤ cost(a→b) + h(b) for both h1 and h2) and generates `layer2_chart.png` showing nodes expanded per test case across all algorithms.

### Layer 3: Network Optimisation

This layer solves a **combinatorial optimisation problem**, not a pathfinding problem.

**Problem:** Select K=8 bus stops from 20 candidate locations to maximise city-wide service quality.

**State:** A sorted tuple of 8 stop node IDs. There are C(20,8) = 125,970 possible configurations.

**Objective function (maximise, range 0–1):**

| Component | Weight | Formula |
|-----------|--------|---------|
| Coverage | 40% | Fraction of 20 nodes served (stop or adjacent to a stop) |
| Connectivity | 35% | Fraction of stop-pairs with a direct route |
| Efficiency | 25% | 1 − avg\_route\_time / 35 |

**Neighbourhood:** Single-swap — replace one active stop with one inactive stop → 96 neighbours per state.

| Algorithm | Variant | Description |
|-----------|---------|-------------|
| Hill Climbing | No sideways moves | Steepest ascent, stops at local optimum |
| Hill Climbing | With sideways moves | Also accepts equal-score moves (plateau walking, max 10 steps) |
| Random-Restart HC | 50 independent starts | Keeps best result across all restarts |
| Simulated Annealing | r = 0.90 (fast cooling) | Boltzmann acceptance, 50 runs |
| Simulated Annealing | r = 0.95 (medium cooling) | Boltzmann acceptance, 50 runs |
| Simulated Annealing | r = 0.99 (slow cooling) | Boltzmann acceptance, 50 runs |

---

## Key Results

### Layer 1

| Test Case | BFS Cost | DFS Cost | UCS Cost |
|-----------|----------|----------|----------|
| Saddar → Clifton (short) | 20 min | 20 min | 20 min |
| Orangi → Korangi (long) | 92 min | 110 min | 92 min |
| Orangi → Saddar (bottleneck) | 71 min | 92 min | 71 min |
| Saddar → Malir (weight matters) | 77 min | 90 min | 77 min |
| Gulshan → Baldia (DFS weakness) | 65 min | 143 min | 65 min |

UCS is always optimal. DFS can expand 2–3× more nodes and finds suboptimal paths.

### Layer 2

Both A\* and IDA\* found optimal paths on all 5 test cases. Greedy Best-First was fastest but suboptimal on 2/5 cases. h2 improved node efficiency for A\* by ~15% compared to h1. All 5 consistency checks passed for both heuristics. IDA\* shows high node-expansion counts because it re-expands nodes on each threshold iteration — this is expected behaviour, not a bug.

### Layer 3

Random-Restart HC (with sideways moves) and SA at slow cooling (r=0.99) both achieved objective scores above 0.64. SA at r=0.99 showed the most consistent results across 50 runs (lowest standard deviation). HC achieved a 100% success rate (all 50 starts improved over the random baseline), indicating a smooth optimisation landscape for this objective function.

---

## Output Files

| File | Generated by | Description |
|------|-------------|-------------|
| `layer2_chart.png` | `run_Layer2.py` | Grouped bar chart: nodes expanded per test case |
| `layer3_hc_chart.png` | `run_layer3.py` | HC variant comparison (success rate, avg score, avg steps) |
| `layer3_sa_chart.png` | `run_layer3.py` | SA results bar chart + summary table panel |
| `layer3_network.png` | `run_layer3.py` | Geographic plot of the best 8-stop network found |
| `Karachi_Transport_Planner_Report.docx` | Pre-generated | Full academic report with all results, tables, and figures |

---

**Course:** CS-5101 Advanced Artificial Intelligence  
**Institution:** NED University of Engineering & Applied Sciences  
**Program:** MS AI Evening — Spring 2026  
**Author:** Fatima Zehra  
**Last Updated:** May 2026
