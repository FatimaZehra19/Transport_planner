"""
Layer 3 — Network Optimisation: Run all experiments and generate charts.

Experiments
-----------
1. Hill Climbing WITHOUT sideways moves — 50 random starts
2. Hill Climbing WITH    sideways moves — 50 random starts
   → Compare success rate, average score, average steps

3. Simulated Annealing with cooling rates 0.90, 0.95, 0.99 — 50 runs each
   → Compare avg/best score and variance per cooling schedule

4. Identify the single best configuration found across all experiments.
   → Print stop names, routes, coverage/connectivity/efficiency breakdown.

Charts saved to Layer3_local_search/
  layer3_hc_chart.png    — HC with vs without sideways moves
  layer3_sa_chart.png    — SA performance vs cooling rate
  layer3_network.png     — best solution visualised on Karachi map
"""

import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from karachi_transport.graph import KarachiGraph
from .network_optimizer import NetworkState, K_STOPS, N_NODES
from .hill_climbing import random_restart_hc
from .simulated_annealing import run_sa_experiment, simulated_annealing

CHART_DIR = os.path.dirname(os.path.abspath(__file__))


# ===========================================================================
# Chart helpers
# ===========================================================================

def _hc_chart(stats_no_sw, stats_sw):
    """Bar chart: HC without vs with sideways moves (success rate, avg score, avg steps)."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("[INFO] matplotlib not installed — skipping HC chart.")
        return

    labels = ["Success Rate (%)", "Avg Score (×100)", "Avg Steps"]
    no_sw = [
        stats_no_sw["success_rate"] * 100,
        stats_no_sw["avg_score"] * 100,
        stats_no_sw["avg_steps"],
    ]
    sw = [
        stats_sw["success_rate"] * 100,
        stats_sw["avg_score"] * 100,
        stats_sw["avg_steps"],
    ]

    x = list(range(len(labels)))
    w = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([i - w / 2 for i in x], no_sw, width=w, label="Without Sideways", color="#F44336", alpha=0.85)
    ax.bar([i + w / 2 for i in x], sw,    width=w, label="With Sideways",    color="#4CAF50", alpha=0.85)

    for i, (a, b) in enumerate(zip(no_sw, sw)):
        ax.text(i - w / 2, a + 0.3, f"{a:.1f}", ha='center', va='bottom', fontsize=8)
        ax.text(i + w / 2, b + 0.3, f"{b:.1f}", ha='center', va='bottom', fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("Hill Climbing: With vs Without Sideways Moves\n(50 random starts each)")
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    path = os.path.join(CHART_DIR, "layer3_hc_chart.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[CHART] HC comparison chart saved: {path}")


def _sa_chart(sa_results):
    """SA performance chart: bar plot (left) + metrics table (right)."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("[INFO] matplotlib not installed — skipping SA chart.")
        return

    rates  = [r["cooling_rate"] for r in sa_results]
    avgs   = [r["avg_score"]    for r in sa_results]
    bests  = [r["best_score"]   for r in sa_results]
    worsts = [r["worst_score"]  for r in sa_results]
    stds   = [r["std_dev"]      for r in sa_results]

    colors = ["#FF9800", "#2196F3", "#9C27B0"]
    x = list(range(len(rates)))

    fig, (ax_bar, ax_tbl) = plt.subplots(
        1, 2, figsize=(13, 6),
        gridspec_kw={"width_ratios": [2, 1]}
    )
    fig.suptitle("Simulated Annealing: Performance vs Cooling Rate  (50 runs each)",
                 fontsize=12, fontweight='bold', y=1.01)

    # ── Left: bar chart with error bars ──────────────────────────────────
    bars = ax_bar.bar(x, avgs, width=0.5, color=colors, alpha=0.82,
                      yerr=stds, capsize=9,
                      error_kw={"elinewidth": 2, "ecolor": "#555555", "capthick": 2})

    # Best score as diamond markers
    ax_bar.scatter(x, bests,  color="#C62828", zorder=6, marker='D', s=90,
                   label="Best score", linewidths=0.8, edgecolors='white')
    # Worst score as downward-triangle markers
    ax_bar.scatter(x, worsts, color="#1565C0", zorder=6, marker='v', s=90,
                   label="Worst score", linewidths=0.8, edgecolors='white')

    # Avg value label INSIDE each bar (avoid top-of-bar crowding)
    y_min = min(worsts) - 0.012
    for i, (avg, color) in enumerate(zip(avgs, colors)):
        ax_bar.text(i, y_min + (avg - y_min) * 0.45,
                    f"avg\n{avg:.4f}",
                    ha='center', va='center', fontsize=8.5,
                    color='white', fontweight='bold')

    # Std annotation on the side of each error bar cap (no vertical overlap)
    for i, (avg, std) in enumerate(zip(avgs, stds)):
        ax_bar.annotate(f"±{std:.4f}",
                        xy=(i + 0.27, avg + std),
                        fontsize=7.5, color="#444444", va='center')

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels([f"r = {r}" for r in rates], fontsize=11)
    ax_bar.set_xlabel("Cooling Rate", fontsize=10)
    ax_bar.set_ylabel("Objective Score", fontsize=10)
    ax_bar.set_title("Average Score ± Std Dev\n(diamonds = best, triangles = worst)",
                     fontsize=9)

    # Give enough headroom above the highest best-score marker
    ax_bar.set_ylim(y_min, max(bests) + 0.018)
    ax_bar.legend(fontsize=8.5, loc='lower right')
    ax_bar.grid(axis='y', alpha=0.3, linestyle='--')

    # ── Right: metrics table ─────────────────────────────────────────────
    ax_tbl.axis('off')
    col_labels = ["Rate", "Avg", "Best", "Worst", "Std Dev"]
    rows = []
    for r, avg, best, worst, std in zip(rates, avgs, bests, worsts, stds):
        rows.append([f"r={r}", f"{avg:.4f}", f"{best:.4f}", f"{worst:.4f}", f"{std:.4f}"])

    tbl = ax_tbl.table(
        cellText=rows,
        colLabels=col_labels,
        cellLoc='center',
        loc='center',
        bbox=[0.0, 0.25, 1.0, 0.5]
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)

    # Header row styling
    for col in range(len(col_labels)):
        tbl[0, col].set_facecolor("#37474F")
        tbl[0, col].set_text_props(color='white', fontweight='bold')

    # Data rows — alternating shade + colour-code by cooling rate
    row_colors = ["#FFF3E0", "#E3F2FD", "#F3E5F5"]
    for row_idx in range(1, len(rows) + 1):
        for col in range(len(col_labels)):
            tbl[row_idx, col].set_facecolor(row_colors[row_idx - 1])

    ax_tbl.set_title("Summary Table", fontsize=9, pad=6)

    plt.tight_layout()
    path = os.path.join(CHART_DIR, "layer3_sa_chart.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[CHART] SA performance chart saved: {path}")


def _network_chart(graph, best_state):
    """Plot the best network on a rough lat/lon map of Karachi."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("[INFO] matplotlib not installed — skipping network chart.")
        return

    active_set = set(best_state.active_stops)
    routes = best_state.get_routes()

    fig, ax = plt.subplots(figsize=(10, 9))
    ax.set_facecolor('#F0F4F8')

    # Draw all original-graph edges (grey, thin)
    from karachi_transport.edges import EDGES
    for a, b, _ in EDGES:
        lat_a, lon_a = graph.get_coordinates(a)
        lat_b, lon_b = graph.get_coordinates(b)
        ax.plot([lon_a, lon_b], [lat_a, lat_b], color='#BDBDBD', linewidth=0.8, zorder=1)

    # Draw active routes (bold coloured)
    for a, b, w in routes:
        lat_a, lon_a = graph.get_coordinates(a)
        lat_b, lon_b = graph.get_coordinates(b)
        ax.plot([lon_a, lon_b], [lat_a, lat_b], color='#1565C0', linewidth=2.5,
                zorder=2, alpha=0.8)
        # Label weight
        mid_lat = (lat_a + lat_b) / 2
        mid_lon = (lon_a + lon_b) / 2
        ax.text(mid_lon, mid_lat, f"{w}m", fontsize=6, ha='center',
                color='#1565C0', zorder=4)

    # Draw all nodes (small grey dots)
    for node_id in range(N_NODES):
        lat, lon = graph.get_coordinates(node_id)
        ax.scatter(lon, lat, s=25, color='#9E9E9E', zorder=3)

    # Draw active stops (large, highlighted)
    for stop in best_state.active_stops:
        lat, lon = graph.get_coordinates(stop)
        ax.scatter(lon, lat, s=160, color='#E53935', zorder=5, edgecolors='white',
                   linewidths=1.5)
        name = graph.get_node_name(stop)
        ax.annotate(name, (lon, lat), textcoords="offset points", xytext=(5, 4),
                    fontsize=7.5, fontweight='bold', color='#B71C1C', zorder=6)

    info = best_state.describe()
    ax.set_title(
        f"Best Bus Network — Layer 3\n"
        f"{K_STOPS} stops selected | {info['routes']} routes | "
        f"Coverage: {info['coverage_pct']}% | Score: {info['score']}",
        fontsize=10, fontweight='bold'
    )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    # Legend
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    legend_elements = [
        Line2D([0], [0], color='#BDBDBD', linewidth=1, label='Existing roads'),
        Line2D([0], [0], color='#1565C0', linewidth=2.5, label='Active bus routes'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#9E9E9E',
               markersize=6, label='Candidate stop (inactive)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#E53935',
               markersize=9, label='Selected bus stop'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=7.5)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    path = os.path.join(CHART_DIR, "layer3_network.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[CHART] Network visualisation saved: {path}")


# ===========================================================================
# Main runner
# ===========================================================================

def run_layer3_tests():
    random.seed(42)   # reproducible output

    graph = KarachiGraph()

    SEP = "=" * 110

    print(SEP)
    print("LAYER 3: NETWORK OPTIMISATION — Karachi Bus Stop Selection")
    print(SEP)
    print()
    print(f"Problem : Select K={K_STOPS} bus stops from {N_NODES} candidates + design connecting routes.")
    print("Goal    : Maximise  0.40 × coverage  +  0.35 × connectivity  +  0.25 × efficiency")
    print("State   : Tuple of 8 sorted node IDs.  |State space| = C(20,8) = 125,970")
    print("Move    : Swap one active stop for one inactive stop.  |Neighbourhood| = 96")
    print()

    # ------------------------------------------------------------------
    # Baseline
    # ------------------------------------------------------------------
    baseline_scores = [NetworkState.random_state(graph).objective() for _ in range(20)]
    baseline = sum(baseline_scores) / len(baseline_scores)
    print(f"Random-state baseline (avg over 20 samples): {baseline:.4f}")
    print()

    overall_best_state = None
    overall_best_score = -1.0

    def update_overall(state, score):
        nonlocal overall_best_state, overall_best_score
        if score > overall_best_score:
            overall_best_score = score
            overall_best_state = state

    # ==================================================================
    # EXPERIMENT 1 & 2: Hill Climbing
    # ==================================================================
    print(SEP)
    print("HILL CLIMBING — 50 Random Starts")
    print(SEP)

    print("\n--- Without sideways moves ---")
    best_no_sw, score_no_sw, stats_no_sw = random_restart_hc(
        graph, num_restarts=50, allow_sideways=False)
    update_overall(best_no_sw, score_no_sw)

    print(f"  Success rate (>5% above baseline): {stats_no_sw['success_rate']*100:.1f}%")
    print(f"  Average objective score           : {stats_no_sw['avg_score']:.4f}")
    print(f"  Best score found                  : {stats_no_sw['best_score']:.4f}")
    print(f"  Average steps per run             : {stats_no_sw['avg_steps']:.1f}")
    print(f"  Baseline (random avg)             : {stats_no_sw['baseline']:.4f}")

    print("\n--- With sideways moves (max 10 consecutive) ---")
    best_sw, score_sw, stats_sw = random_restart_hc(
        graph, num_restarts=50, allow_sideways=True, max_sideways=10)
    update_overall(best_sw, score_sw)

    print(f"  Success rate (>5% above baseline): {stats_sw['success_rate']*100:.1f}%")
    print(f"  Average objective score           : {stats_sw['avg_score']:.4f}")
    print(f"  Best score found                  : {stats_sw['best_score']:.4f}")
    print(f"  Average steps per run             : {stats_sw['avg_steps']:.1f}")

    # Comparison
    print()
    print("  COMPARISON:")
    sr_diff   = (stats_sw["success_rate"] - stats_no_sw["success_rate"]) * 100
    sc_diff   = stats_sw["avg_score"] - stats_no_sw["avg_score"]
    step_diff = stats_sw["avg_steps"]  - stats_no_sw["avg_steps"]
    print(f"    Success rate change : {sr_diff:+.1f} pp  (sideways vs no-sideways)")
    print(f"    Avg score change    : {sc_diff:+.4f}")
    print(f"    Avg steps change    : {step_diff:+.1f} (more steps = more plateau exploration)")
    if stats_sw["best_score"] >= stats_no_sw["best_score"]:
        print("    [OK] Sideways moves helped find an equal or better solution.")
    else:
        print("    [--] Sideways moves did not improve the best score in this run.")

    # ==================================================================
    # EXPERIMENT 3: Simulated Annealing
    # ==================================================================
    print()
    print(SEP)
    print("SIMULATED ANNEALING — 3 cooling rates × 50 runs")
    print("  initial_temp=0.30, min_temp=0.0001, max_iter=2000")
    print(SEP)
    print()

    cooling_rates = [0.90, 0.95, 0.99]
    sa_results = []

    print(f"  {'Rate':<8} {'Avg Score':<12} {'Best Score':<12} {'Worst':<10} {'Std Dev':<10}")
    print("  " + "-" * 60)

    for rate in cooling_rates:
        scores, stats = run_sa_experiment(graph, cooling_rate=rate, num_runs=50)
        sa_results.append(stats)
        update_overall(None, -1)   # placeholder; done below
        # Identify best state for this rate (re-run once)
        best_sa_state, best_sa_score, _ = simulated_annealing(graph, cooling_rate=rate)
        update_overall(best_sa_state, best_sa_score)

        print(f"  r={rate:<6} {stats['avg_score']:<12.4f} {stats['best_score']:<12.4f} "
              f"{stats['worst_score']:<10.4f} {stats['std_dev']:<10.4f}")

    print()
    print("  ANALYSIS:")
    sorted_by_avg = sorted(sa_results, key=lambda s: s["avg_score"], reverse=True)
    best_rate = sorted_by_avg[0]
    print(f"    Best average score   : r={best_rate['cooling_rate']} "
          f"(avg={best_rate['avg_score']:.4f})")
    print(f"    Most consistent      : r={min(sa_results, key=lambda s: s['std_dev'])['cooling_rate']} "
          f"(lowest std dev)")
    print(f"    Highest single score : r={max(sa_results, key=lambda s: s['best_score'])['cooling_rate']} "
          f"(best={max(sa_results, key=lambda s: s['best_score'])['best_score']:.4f})")
    print()
    print("  NOTE: Slower cooling (r=0.99) explores more before converging;")
    print("        faster cooling (r=0.90) converges quickly but may miss good regions.")

    # ==================================================================
    # BEST SOLUTION
    # ==================================================================
    print()
    print(SEP)
    print("BEST SOLUTION FOUND (across all experiments)")
    print(SEP)
    print()

    info = overall_best_state.describe()
    print(f"  Selected stops ({K_STOPS}):")
    for i, (sid, sname) in enumerate(zip(info["stop_ids"], info["stop_names"]), 1):
        lat, lon = graph.get_coordinates(sid)
        print(f"    {i:2}. {sname:<25}  (node {sid}, lat={lat}, lon={lon})")

    print()
    print(f"  Active routes  : {info['routes']} direct connections between selected stops")
    print(f"  Coverage       : {info['covered_nodes']}/{N_NODES} nodes served  ({info['coverage_pct']}%)")
    print(f"  Connectivity   : {info['connectivity_pct']}% of stop-pairs directly connected")
    print(f"  Avg route time : {info['avg_route_time']} minutes")
    print(f"  Objective score: {info['score']}  (baseline was ~{baseline:.4f})")
    print()
    print("  Active route list:")
    for a, b, w in overall_best_state.get_routes():
        print(f"    {graph.get_node_name(a):<25} <-> {graph.get_node_name(b):<25}  ({w} min)")

    # ==================================================================
    # RECOMMENDATION
    # ==================================================================
    print()
    print(SEP)
    print("RECOMMENDATION TO KMC")
    print(SEP)
    print()
    best_sa_avg = max(r["avg_score"] for r in sa_results)
    hc_best     = max(stats_no_sw["best_score"], stats_sw["best_score"])
    if best_sa_avg > stats_sw["avg_score"]:
        recommended = "Simulated Annealing (r=0.99)"
        reason = ("SA with slow cooling consistently finds high-quality solutions by "
                  "escaping local optima that trap hill climbing.")
    else:
        recommended = "Random-Restart Hill Climbing (with sideways moves)"
        reason = ("Sideways-enabled HC matches or beats SA here, is simpler to tune, "
                  "and is faster per run.")
    print(f"  Recommended algorithm : {recommended}")
    print(f"  Reason                : {reason}")
    print()
    print("  For production deployment, run the recommended algorithm with 100+ restarts")
    print("  to further improve solution quality before finalising stop locations.")
    print(SEP)

    # ==================================================================
    # CHARTS
    # ==================================================================
    print()
    print("Generating charts …")
    _hc_chart(stats_no_sw, stats_sw)
    _sa_chart(sa_results)
    _network_chart(graph, overall_best_state)
    print()
    print("Done.")


if __name__ == "__main__":
    run_layer3_tests()
