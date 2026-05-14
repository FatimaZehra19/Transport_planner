# Run all three algorithms on all test cases and produce comparison table

from .bfs import bfs
from .dfs import dfs
from .ucs import ucs
from .test_cases import get_test_cases, get_test_tuples
import sys
import os

# Add parent directory to path so we can import graph module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from karachi_transport.graph import KarachiGraph


def run_layer1_tests():
    """
    Run all three uninformed search algorithms on all test cases.
    Compare results in a detailed table.
    """
    
    graph = KarachiGraph()
    test_cases = get_test_cases()
    test_tuples = get_test_tuples()
    
    print("=" * 120)
    print("LAYER 1: UNINFORMED SEARCH ALGORITHMS")
    print("=" * 120)
    print()
    
    # Store results for each test
    results = []
    
    # Run each test case
    for i, test in enumerate(test_cases):
        print(f"\n{test['name']}")
        print(f"  From: {graph.get_node_name(test['start'])} -> To: {graph.get_node_name(test['goal'])}")
        print(f"  Purpose: {test['why']}")
        print()
        
        # Extract tuple for algorithm calls
        start, goal, name = test_tuples[i]
        
        # Run BFS
        bfs_path, bfs_cost, bfs_expanded, bfs_frontier = bfs(graph, start, goal)
        bfs_path_names = [graph.get_node_name(n) for n in bfs_path]
        
        # Run DFS
        dfs_path, dfs_cost, dfs_expanded, dfs_frontier = dfs(graph, start, goal)
        dfs_path_names = [graph.get_node_name(n) for n in dfs_path]
        
        # Run UCS
        ucs_path, ucs_cost, ucs_expanded, ucs_frontier = ucs(graph, start, goal)
        ucs_path_names = [graph.get_node_name(n) for n in ucs_path]
        
        # Print results for this test
        print(f"  BFS:  Path: {' -> '.join(bfs_path_names)}")
        print(f"        Cost: {bfs_cost} min | Nodes expanded: {bfs_expanded} | Max frontier: {bfs_frontier}")
        print()
        print(f"  DFS:  Path: {' -> '.join(dfs_path_names)}")
        print(f"        Cost: {dfs_cost} min | Nodes expanded: {dfs_expanded} | Max frontier: {dfs_frontier}")
        print()
        print(f"  UCS:  Path: {' -> '.join(ucs_path_names)}")
        print(f"        Cost: {ucs_cost} min | Nodes expanded: {ucs_expanded} | Max frontier: {ucs_frontier}")
        print()
        
        # Store for summary table
        results.append({
            "test": name,
            "bfs_cost": bfs_cost,
            "bfs_expanded": bfs_expanded,
            "dfs_cost": dfs_cost,
            "dfs_expanded": dfs_expanded,
            "ucs_cost": ucs_cost,
            "ucs_expanded": ucs_expanded
        })
        
        # Analysis
        print(f"  ANALYSIS:")
        if bfs_cost == ucs_cost:
            print(f"    [OK] BFS and UCS found same cost path (weights not important for hop count)")
        else:
            print(f"    [OK] BFS cost: {bfs_cost}, UCS cost: {ucs_cost} (UCS better by {bfs_cost - ucs_cost} min)")
        
        if dfs_expanded > bfs_expanded + 5:
            print(f"    [OK] DFS expanded {dfs_expanded - bfs_expanded} MORE nodes than BFS (less efficient)")
        elif dfs_expanded < bfs_expanded:
            print(f"    [OK] DFS was lucky — expanded fewer nodes than BFS")
        else:
            print(f"    [OK] DFS expanded similar number as BFS")
        
        print("-" * 120)
    
    
    # Print summary comparison table
    print("\n\n" + "=" * 120)
    print("SUMMARY TABLE")
    print("=" * 120)
    print()
    print(f"{'Test Case':<40} {'BFS Nodes':<15} {'DFS Nodes':<15} {'UCS Nodes':<15} {'BFS Cost':<15} {'DFS Cost':<15} {'UCS Cost':<15}")
    print("-" * 120)
    
    for result in results:
        print(f"{result['test']:<40} {result['bfs_expanded']:<15} {result['dfs_expanded']:<15} {result['ucs_expanded']:<15} {result['bfs_cost']:<15} {result['dfs_cost']:<15} {result['ucs_cost']:<15}")
    
    print()
    print("=" * 120)
    print("KEY INSIGHTS:")
    print("=" * 120)
    
    # Calculate averages
    avg_bfs_expanded = sum(r['bfs_expanded'] for r in results) / len(results)
    avg_dfs_expanded = sum(r['dfs_expanded'] for r in results) / len(results)
    avg_ucs_expanded = sum(r['ucs_expanded'] for r in results) / len(results)
    
    print(f"Average nodes expanded:")
    print(f"  BFS: {avg_bfs_expanded:.1f}")
    print(f"  DFS: {avg_dfs_expanded:.1f}")
    print(f"  UCS: {avg_ucs_expanded:.1f}")
    print()
    
    print("Path cost comparison (lower is better):")
    bfs_total = sum(r['bfs_cost'] for r in results)
    dfs_total = sum(r['dfs_cost'] for r in results)
    ucs_total = sum(r['ucs_cost'] for r in results)
    print(f"  BFS total: {bfs_total} min")
    print(f"  DFS total: {dfs_total} min")
    print(f"  UCS total: {ucs_total} min (OPTIMAL)")
    print()
    
    print("Observations:")
    print(f"  - BFS explores systematically by hops, so frontier size grows uniformly")
    print(f"  - DFS can explore very deep, leading to large frontier in some cases")
    print(f"  - UCS always finds optimal cost path, but explores more nodes than BFS for hop distance")
    print()
    print("=" * 120)


if __name__ == "__main__":
    run_layer1_tests()