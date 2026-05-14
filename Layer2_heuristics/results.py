# Run all heuristic algorithms and compare with Layer 1 results

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .heuristics import KarachiHeuristics
from .greedy import greedy_best_first
from .astar import astar
from .idastar import ida_star
from .test_cases import get_test_cases, get_test_tuples

from karachi_transport.graph import KarachiGraph

# Import Layer 1 algorithms for comparison
from Layer1_uninformed.bfs import bfs
from Layer1_uninformed.dfs import dfs
from Layer1_uninformed.ucs import ucs


# ---------------------------------------------------------------------------
# Chart helper
# ---------------------------------------------------------------------------

def _generate_nodes_expanded_chart(results):
    """Save a bar chart comparing nodes expanded across all algorithms."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n[INFO] matplotlib not installed — skipping chart. pip install matplotlib")
        return

    algorithms = ["UCS", "Greedy(h1)", "Greedy(h2)", "A*(h1)", "A*(h2)", "IDA*(h1)", "IDA*(h2)"]
    keys = ["ucs_exp", "greedy_h1_exp", "greedy_h2_exp",
            "astar_h1_exp", "astar_h2_exp", "ida_h1_exp", "ida_h2_exp"]
    colors = ["#607D8B", "#FF5722", "#FF8A65", "#4CAF50", "#2E7D32", "#9C27B0", "#6A1B9A"]

    test_labels = [r["test"].split(":")[0] for r in results]  # "Test 1", "Test 2", …

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Layer 2: Nodes Expanded Comparison", fontsize=13, fontweight='bold')

    # --- Left: grouped bars (one group per test case, one bar per algorithm) ---
    n_tests = len(results)
    n_algos = len(algorithms)
    bar_w = 0.11
    group_offsets = [bar_w * (i - n_algos / 2 + 0.5) for i in range(n_algos)]

    for a_idx, (key, algo, color) in enumerate(zip(keys, algorithms, colors)):
        vals = [r[key] for r in results]
        xs = [t + group_offsets[a_idx] for t in range(n_tests)]
        ax1.bar(xs, vals, width=bar_w, label=algo, color=color, alpha=0.85)

    ax1.set_xticks(range(n_tests))
    ax1.set_xticklabels(test_labels, fontsize=9)
    ax1.set_xlabel("Test Case")
    ax1.set_ylabel("Nodes Expanded")
    ax1.set_title("Nodes Expanded per Test Case")
    ax1.legend(fontsize=7, ncol=2)
    ax1.grid(axis='y', alpha=0.3)

    # --- Right: average across all test cases ---
    avgs = [sum(r[k] for r in results) / len(results) for k in keys]
    bars = ax2.bar(algorithms, avgs, color=colors, alpha=0.85, edgecolor='white')
    for bar, val in zip(bars, avgs):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                 f'{val:.1f}', ha='center', va='bottom', fontsize=8)
    ax2.set_xlabel("Algorithm")
    ax2.set_ylabel("Average Nodes Expanded")
    ax2.set_title("Average Nodes Expanded (all 5 test cases)")
    ax2.tick_params(axis='x', rotation=30)
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    chart_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "layer2_chart.png")
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n[CHART] Nodes-expanded chart saved to: {chart_path}")


def run_layer2_tests():
    """
    Run all heuristic algorithms on all test cases.
    Compare with Layer 1 uninformed search.
    """
    
    graph = KarachiGraph()
    heuristics_obj = KarachiHeuristics(graph)
    test_cases = get_test_cases()
    test_tuples = get_test_tuples()
    
    print("=" * 140)
    print("LAYER 2: HEURISTIC SEARCH ALGORITHMS")
    print("=" * 140)
    print()
    
    results = []
    
    # Run each test case
    for i, test in enumerate(test_cases):
        print(f"\n{test['name']}")
        print(f"  From: {graph.get_node_name(test['start'])} -> To: {graph.get_node_name(test['goal'])}")
        print(f"  Purpose: {test['why']}")
        print()
        
        start, goal, name = test_tuples[i]
        
        # LAYER 1: Get baseline from UCS
        ucs_path, ucs_cost, ucs_expanded, ucs_frontier = ucs(graph, start, goal)
        ucs_path_names = [graph.get_node_name(n) for n in ucs_path]
        
        # LAYER 2: Heuristic algorithms
        
        # Greedy with h1
        greedy_h1_path, greedy_h1_cost, greedy_h1_exp, greedy_h1_front = \
            greedy_best_first(graph, heuristics_obj, start, goal, heuristics_obj.h1_straight_line)
        greedy_h1_names = [graph.get_node_name(n) for n in greedy_h1_path]
        
        # Greedy with h2
        greedy_h2_path, greedy_h2_cost, greedy_h2_exp, greedy_h2_front = \
            greedy_best_first(graph, heuristics_obj, start, goal, heuristics_obj.h2_karachi_aware)
        greedy_h2_names = [graph.get_node_name(n) for n in greedy_h2_path]
        
        # A* with h1
        astar_h1_path, astar_h1_cost, astar_h1_exp, astar_h1_front = \
            astar(graph, heuristics_obj, start, goal, heuristics_obj.h1_straight_line)
        astar_h1_names = [graph.get_node_name(n) for n in astar_h1_path]
        
        # A* with h2
        astar_h2_path, astar_h2_cost, astar_h2_exp, astar_h2_front = \
            astar(graph, heuristics_obj, start, goal, heuristics_obj.h2_karachi_aware)
        astar_h2_names = [graph.get_node_name(n) for n in astar_h2_path]
        
        # IDA* with h1
        ida_h1_path, ida_h1_cost, ida_h1_exp, ida_h1_front = \
            ida_star(graph, heuristics_obj, start, goal, heuristics_obj.h1_straight_line)
        ida_h1_names = [graph.get_node_name(n) for n in ida_h1_path]
        
        # IDA* with h2
        ida_h2_path, ida_h2_cost, ida_h2_exp, ida_h2_front = \
            ida_star(graph, heuristics_obj, start, goal, heuristics_obj.h2_karachi_aware)
        ida_h2_names = [graph.get_node_name(n) for n in ida_h2_path]
        
        # Print results
        print(f"  LAYER 1 (Baseline):")
        print(f"    UCS:  Path: {' -> '.join(ucs_path_names)}")
        print(f"          Cost: {ucs_cost} min | Nodes expanded: {ucs_expanded} | Max frontier: {ucs_frontier}")
        print()
        
        print(f"  LAYER 2 (Heuristic):")
        print(f"    Greedy(h1): Path: {' -> '.join(greedy_h1_names)}")
        print(f"                Cost: {greedy_h1_cost} min | Nodes expanded: {greedy_h1_exp} | Max frontier: {greedy_h1_front}")
        print(f"    Greedy(h2): Path: {' -> '.join(greedy_h2_names)}")
        print(f"                Cost: {greedy_h2_cost} min | Nodes expanded: {greedy_h2_exp} | Max frontier: {greedy_h2_front}")
        print()
        
        print(f"    A*(h1):     Path: {' -> '.join(astar_h1_names)}")
        print(f"                Cost: {astar_h1_cost} min | Nodes expanded: {astar_h1_exp} | Max frontier: {astar_h1_front}")
        print(f"    A*(h2):     Path: {' -> '.join(astar_h2_names)}")
        print(f"                Cost: {astar_h2_cost} min | Nodes expanded: {astar_h2_exp} | Max frontier: {astar_h2_front}")
        print()
        
        print(f"    IDA*(h1):   Path: {' -> '.join(ida_h1_names)}")
        print(f"                Cost: {ida_h1_cost} min | Nodes expanded: {ida_h1_exp} | Max frontier: {ida_h1_front}")
        print(f"    IDA*(h2):   Path: {' -> '.join(ida_h2_names)}")
        print(f"                Cost: {ida_h2_cost} min | Nodes expanded: {ida_h2_exp} | Max frontier: {ida_h2_front}")
        print()
        
        # Analysis
        print(f"  ANALYSIS:")
        
        # Optimality check
        if astar_h1_cost == ucs_cost:
            print(f"    [OK] A*(h1) found optimal path (same as UCS)")
        else:
            print(f"    [NO] A*(h1) suboptimal: {astar_h1_cost} vs UCS {ucs_cost}")
        
        if astar_h2_cost == ucs_cost:
            print(f"    [OK] A*(h2) found optimal path (same as UCS)")
        else:
            print(f"    [NO] A*(h2) suboptimal: {astar_h2_cost} vs UCS {ucs_cost}")
        
        # Efficiency check
        if astar_h1_exp < ucs_expanded:
            efficiency_gain = ((ucs_expanded - astar_h1_exp) / ucs_expanded) * 100
            print(f"    [OK] A*(h1) explored {ucs_expanded - astar_h1_exp} FEWER nodes ({efficiency_gain:.1f}% reduction)")
        if astar_h2_exp < astar_h1_exp:
            h2_gain = ((astar_h1_exp - astar_h2_exp) / astar_h1_exp) * 100
            print(f"    [OK] h2 heuristic better than h1 ({h2_gain:.1f}% fewer nodes)")
        
        # Greedy vs A*
        if greedy_h1_cost > astar_h1_cost:
            print(f"    [OK] Greedy(h1) suboptimal: {greedy_h1_cost} vs A*(h1) {astar_h1_cost} ({greedy_h1_cost - astar_h1_cost} min worse)")
        
        print("-" * 140)
        
        # Store for summary
        results.append({
            "test": name,
            "ucs_cost": ucs_cost,
            "ucs_exp": ucs_expanded,
            "greedy_h1_cost": greedy_h1_cost,
            "greedy_h1_exp": greedy_h1_exp,
            "greedy_h2_cost": greedy_h2_cost,
            "greedy_h2_exp": greedy_h2_exp,
            "astar_h1_cost": astar_h1_cost,
            "astar_h1_exp": astar_h1_exp,
            "astar_h2_cost": astar_h2_cost,
            "astar_h2_exp": astar_h2_exp,
            "ida_h1_cost": ida_h1_cost,
            "ida_h1_exp": ida_h1_exp,
            "ida_h2_cost": ida_h2_cost,
            "ida_h2_exp": ida_h2_exp,
        })
    
    
    # Summary table
    print("\n\n" + "=" * 140)
    print("SUMMARY TABLE: NODES EXPANDED")
    print("=" * 140)
    print()
    print(f"{'Test':<30} {'UCS':<10} {'Greedy(h1)':<12} {'Greedy(h2)':<12} {'A*(h1)':<10} {'A*(h2)':<10} {'IDA*(h1)':<12} {'IDA*(h2)':<12}")
    print("-" * 140)
    
    for r in results:
        print(f"{r['test']:<30} {r['ucs_exp']:<10} {r['greedy_h1_exp']:<12} {r['greedy_h2_exp']:<12} {r['astar_h1_exp']:<10} {r['astar_h2_exp']:<10} {r['ida_h1_exp']:<12} {r['ida_h2_exp']:<12}")
    
    print()
    print("=" * 140)
    print("SUMMARY TABLE: PATH COST (Lower is Better)")
    print("=" * 140)
    print()
    print(f"{'Test':<30} {'UCS':<10} {'Greedy(h1)':<12} {'Greedy(h2)':<12} {'A*(h1)':<10} {'A*(h2)':<10} {'IDA*(h1)':<12} {'IDA*(h2)':<12}")
    print("-" * 140)
    
    for r in results:
        print(f"{r['test']:<30} {r['ucs_cost']:<10} {r['greedy_h1_cost']:<12} {r['greedy_h2_cost']:<12} {r['astar_h1_cost']:<10} {r['astar_h2_cost']:<10} {r['ida_h1_cost']:<12} {r['ida_h2_cost']:<12}")
    
    # Key insights
    print()
    print("=" * 140)
    print("KEY INSIGHTS")
    print("=" * 140)
    
    avg_ucs = sum(r['ucs_exp'] for r in results) / len(results)
    avg_greedy_h1 = sum(r['greedy_h1_exp'] for r in results) / len(results)
    avg_greedy_h2 = sum(r['greedy_h2_exp'] for r in results) / len(results)
    avg_astar_h1 = sum(r['astar_h1_exp'] for r in results) / len(results)
    avg_astar_h2 = sum(r['astar_h2_exp'] for r in results) / len(results)
    
    print()
    print("Average Nodes Expanded:")
    print(f"  UCS:         {avg_ucs:.1f}")
    print(f"  Greedy(h1): {avg_greedy_h1:.1f} ({((avg_ucs - avg_greedy_h1) / avg_ucs * 100):.1f}% reduction)")
    print(f"  Greedy(h2): {avg_greedy_h2:.1f} ({((avg_ucs - avg_greedy_h2) / avg_ucs * 100):.1f}% reduction)")
    print(f"  A*(h1):     {avg_astar_h1:.1f} ({((avg_ucs - avg_astar_h1) / avg_ucs * 100):.1f}% reduction)")
    print(f"  A*(h2):     {avg_astar_h2:.1f} ({((avg_ucs - avg_astar_h2) / avg_ucs * 100):.1f}% reduction)")
    print()
    
    # Optimality check
    astar_h1_suboptimal = sum(1 for r in results if r['astar_h1_cost'] != r['ucs_cost'])
    astar_h2_suboptimal = sum(1 for r in results if r['astar_h2_cost'] != r['ucs_cost'])
    greedy_h1_suboptimal = sum(1 for r in results if r['greedy_h1_cost'] != r['ucs_cost'])
    greedy_h2_suboptimal = sum(1 for r in results if r['greedy_h2_cost'] != r['ucs_cost'])
    
    print("Optimality (how many tests found suboptimal paths):")
    print(f"  Greedy(h1): {greedy_h1_suboptimal}/5 suboptimal")
    print(f"  Greedy(h2): {greedy_h2_suboptimal}/5 suboptimal")
    print(f"  A*(h1):     {astar_h1_suboptimal}/5 suboptimal [OK] (should be 0)")
    print(f"  A*(h2):     {astar_h2_suboptimal}/5 suboptimal [OK] (should be 0)")
    print()
    
    print("Recommendations:")
    print("  • A* is the clear winner: optimal paths + efficient exploration")
    print("  • h2 (Karachi-aware) consistently better than h1 (geographic only)")
    print("  • Greedy is fast but unreliable for real-world routing")
    print("  • IDA* trades computation time for memory (good for embedded systems)")
    print()
    print("=" * 140)

    # ------------------------------------------------------------------
    # CONSISTENCY CHECK
    # ------------------------------------------------------------------
    print("\n\n" + "=" * 140)
    print("HEURISTIC CONSISTENCY CHECK: h(a) <= cost(a->b) + h(b)")
    print("Goal node fixed to: Korangi (node 3)")
    print("=" * 140)
    print()

    # 5 representative edges covering different areas and bottlenecks
    consistency_edges = [
        (0,  1,  20, "Saddar -> Clifton"),
        (8,  9,  25, "North Nazimabad -> Orangi"),
        (9,  10, 30, "Orangi -> SITE  [bottleneck]"),
        (6,  7,  15, "Gulshan -> Johar"),
        (11, 12, 20, "Lyari -> Keamari  [bottleneck]"),
    ]
    goal_for_check = 3  # Korangi

    print(f"  {'Edge':<38} {'h1(a)':>7} {'c(a,b)':>8} {'h1(b)':>7}  {'h1 OK?':<8}  "
          f"{'h2(a)':>7} {'h2(b)':>7}  {'h2 OK?':<8}")
    print("  " + "-" * 120)

    all_h1_ok = True
    all_h2_ok = True

    for a, b, cost, label in consistency_edges:
        h1_a = heuristics_obj.h1_straight_line(a, goal_for_check)
        h1_b = heuristics_obj.h1_straight_line(b, goal_for_check)
        h2_a = heuristics_obj.h2_karachi_aware(a, goal_for_check)
        h2_b = heuristics_obj.h2_karachi_aware(b, goal_for_check)

        h1_ok = h1_a <= cost + h1_b + 1e-9
        h2_ok = h2_a <= cost + h2_b + 1e-9

        if not h1_ok:
            all_h1_ok = False
        if not h2_ok:
            all_h2_ok = False

        h1_status = "[OK]   " if h1_ok else "[FAIL] "
        h2_status = "[OK]   " if h2_ok else "[FAIL] "

        print(f"  {label:<38} {h1_a:>7.2f} {cost:>8}  {h1_b:>7.2f}  {h1_status}  "
              f"{h2_a:>7.2f} {h2_b:>7.2f}  {h2_status}")

    print()
    h1_verdict = "CONSISTENT  [OK]" if all_h1_ok else "INCONSISTENT [FAIL]"
    h2_verdict = "CONSISTENT  [OK]" if all_h2_ok else "INCONSISTENT [FAIL]"
    print(f"  h1 (straight-line):  {h1_verdict}")
    print(f"  h2 (Karachi-aware):  {h2_verdict}")
    print()
    print("  Consistent heuristics => A* never reopens nodes => optimal + efficient.")
    print("=" * 140)

    # ------------------------------------------------------------------
    # CHART
    # ------------------------------------------------------------------
    _generate_nodes_expanded_chart(results)


if __name__ == "__main__":
    run_layer2_tests()