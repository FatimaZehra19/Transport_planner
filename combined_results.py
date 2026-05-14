import pandas as pd
import matplotlib.pyplot as plt

from tabulate import tabulate

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

from karachi_transport.graph import KarachiGraph

# =========================================
# LAYER 1
# =========================================

from Layer1_uninformed.bfs import bfs
from Layer1_uninformed.dfs import dfs
from Layer1_uninformed.ucs import ucs

# =========================================
# LAYER 2
# =========================================

from Layer2_heuristics.greedy import greedy_best_first
from Layer2_heuristics.astar import astar
from Layer2_heuristics.idastar import ida_star
from Layer2_heuristics.heuristics import KarachiHeuristics

# =========================================
# LAYER 3
# =========================================

from Layer3_local_search.hill_climbing import (
    hill_climbing,
    hill_climbing_random_restart
)

from Layer3_local_search.simulated_annealing import (
    simulated_annealing
)

# =========================================
# TEST CASES
# =========================================

from Layer3_local_search.test_cases import test_cases


# =========================================
# CLEAN COST FUNCTION
# =========================================


def clean_cost(cost):

    if cost == float("inf"):
        return "FAILED"

    return cost


# =========================================
# MAIN FUNCTION
# =========================================


def run_complete_comparison():

    graph = KarachiGraph()
    run_complete_comparison()