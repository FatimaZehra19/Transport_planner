# Master script to run all of Layer 2

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'karachi_transport'))

from Layer2_heuristics.results import run_layer2_tests

if __name__ == "__main__":
    run_layer2_tests()