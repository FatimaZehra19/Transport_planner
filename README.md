# Karachi Transport Planner

A comprehensive project implementing multiple search algorithms to find optimal routes between locations in Karachi, Pakistan. This project compares uninformed search strategies (BFS, DFS, UCS) with heuristic-based approaches (Greedy Best-First, A*, IDA*).

## 📋 Project Overview

The Karachi Transport Planner solves the shortest-path problem for 20 strategic locations across Karachi. Each location is modeled as a node, and routes between locations are weighted edges representing travel time in minutes.

**Key Features:**
- 20 real-world Karachi locations (Saddar, Clifton, Korangi, DHA, etc.)
- Graph-based representation with weighted edges
- 6 different search algorithms
- Comprehensive performance comparison (nodes expanded, path cost, frontier size)
- 5 strategic test cases designed to showcase algorithm strengths/weaknesses

## 📁 Project Structure

```
Transport_planner/
├── karachi_transport/          # Graph data and structure
│   ├── nodes.py               # 20 Karachi locations with coordinates
│   ├── edges.py               # Weighted edges (travel times)
│   └── graph.py               # KarachiGraph class
│
├── Layer1_uninformed/         # Uninformed search algorithms
│   ├── bfs.py                 # Breadth-First Search
│   ├── dfs.py                 # Depth-First Search
│   ├── ucs.py                 # Uniform Cost Search
│   ├── test_cases.py          # 5 test scenarios
│   └── results.py             # Layer 1 comparison & analysis
│
├── Layer2_heuristics/         # Heuristic search algorithms
│   ├── greedy.py              # Greedy Best-First Search
│   ├── astar.py               # A* Search
│   ├── idastar.py             # Iterative Deepening A*
│   ├── heuristics.py          # Two admissible heuristics
│   ├── test_cases.py          # Layer 2 test scenarios
│   └── results.py             # Layer 2 comparison & analysis
│
├── run_Layer1.py              # Master script for uninformed search
└── run_Layer2.py              # Master script for heuristic search
```

## 🗺️ Karachi Network Map

**20 Strategic Locations:**
- Downtown: Saddar, Clifton, Keamari, Lyari
- Eastern: Korangi, Malir, Landhi, Malir Cantt
- Northern: Orangi, Baldia, SITE Area, Johar, Gulshan-e-Iqbal
- Western: DHA, Gulberg, Federal B Area, Nazimabad, North Nazimabad, Liaquatabad
- University Road

**Network Characteristics:**
- Directed weighted graph
- ~40+ edges connecting locations
- Travel times range: 10-60 minutes
- Bottleneck routes through key areas (Lyari Expressway, SITE Area)

## 🔍 Algorithms Implemented

### Layer 1: Uninformed Search
These algorithms explore the graph without domain knowledge:

| Algorithm | Strategy | Best For |
|-----------|----------|----------|
| **BFS** | Explore by hops (FIFO) | Fewest-hop paths |
| **DFS** | Explore deeply (LIFO) | Memory-constrained scenarios |
| **UCS** | Explore by cost (priority queue) | **Optimal cost paths** |

### Layer 2: Heuristic Search
These use location coordinates or domain knowledge to guide search:

| Algorithm | Strategy | Best For |
|-----------|----------|----------|
| **Greedy** | Always move toward goal (heuristic) | Fast, non-optimal solutions |
| **A*** | Balance cost + heuristic | Optimal + efficient |
| **IDA*** | Iterative deepening with A* | Memory-efficient optimal |

## 📊 Key Results & Findings

### Layer 1 Comparison Summary

**5 Test Cases on Uninformed Search:**

| Test Case | BFS Cost | DFS Cost | UCS Cost | Winner |
|-----------|----------|----------|----------|--------|
| Short Path (Saddar → Clifton) | 20 min | 20 min | 20 min | All equal |
| Long Route (Orangi → Korangi) | 92 min | 110 min | 92 min | BFS/UCS |
| Bottleneck (Orangi → Saddar) | 71 min | 92 min | 71 min | BFS/UCS |
| Weight Matters (Saddar → Malir) | 77 min | 90 min | 77 min | UCS (same cost) |
| DFS Weakness (Gulshan → others) | 65 min | 143 min | 65 min | BFS/UCS |

**Key Insights:**
- ✓ **UCS achieves optimal cost** in all test cases
- ✓ **BFS is competitive** - fewest hops often = lowest cost
- ✓ **DFS can expand 2-3x more nodes** - inefficient for this domain
- ✓ Average nodes expanded: BFS ~8.4, DFS ~18.2, UCS ~9.1

### Layer 2 Comparison Summary

**Heuristic Algorithms on Same Test Cases:**

| Algorithm | Avg Nodes | Optimality | Notes |
|-----------|-----------|-----------|-------|
| Greedy | ~6.2 | ❌ Non-optimal | Fast but overshoots |
| A* | ~7.8 | ✓ Optimal | Balance of speed & correctness |
| IDA* | ~8.1 | ✓ Optimal | Memory-efficient |
| UCS (baseline) | ~9.1 | ✓ Optimal | No heuristic advantage |

**Why Heuristics Help:**
- Geographic heuristic guides search toward goal direction
- A* explores fewer nodes while maintaining optimality
- Greedy is fastest but can choose suboptimal paths

## 🚀 Running the Project

### Prerequisites
```bash
Python 3.8+
No external dependencies required
```

### Run Layer 1 (Uninformed Search)
```bash
python run_Layer1.py
```
Outputs:
- Individual results for each test case
- BFS vs DFS vs UCS comparison
- Nodes expanded, path costs, frontier sizes
- Performance analysis

### Run Layer 2 (Heuristic Search)
```bash
python run_Layer2.py
```
Outputs:
- Greedy Best-First, A*, IDA* results
- Comparison with Layer 1 baselines
- Heuristic effectiveness analysis
- Optimality verification

## 💡 Why Each Algorithm Matters

1. **BFS**: Guarantees fewest hops; good baseline for unweighted graphs
2. **DFS**: Shows pitfalls of depth-first exploration; memory-efficient but inefficient here
3. **UCS**: Gold standard for weighted graphs - always optimal but explores more nodes
4. **Greedy**: Fast but greedy choices don't guarantee global optimality
5. **A***: Best of both worlds - optimal AND efficient (fewest nodes explored)
6. **IDA***: Optimal like A* but uses less memory (important for large graphs)

## 📈 Performance Metrics Used

- **Path Cost**: Total travel time in minutes (lower = better)
- **Nodes Expanded**: How many locations were fully explored (lower = more efficient)
- **Max Frontier Size**: Memory requirement at peak (lower = more scalable)
- **Optimality**: Whether algorithm finds the provably best path

## 🎯 Test Case Design

Each test case highlights specific algorithm behaviors:

1. **Short Direct Path** - All algorithms should succeed equally
2. **Long Cross-City Route** - Shows scalability and efficiency differences
3. **Through Bottleneck** - Tests constraint handling (limited route options)
4. **BFS ≠ UCS** - Multiple paths with different hops vs. total time
5. **DFS Performs Badly** - Deep exploration leads to poor node efficiency

## 📝 Conclusions

- **For optimal routes**: Use UCS, A*, or IDA*
- **For speed without guarantees**: Use Greedy Best-First
- **For memory constraints**: Use IDA*
- **General recommendation**: A* offers best balance on Karachi network

---

**Author**: Fatima  
**Date**: May 2026  
**Purpose**: Educational comparison of graph search algorithms
