# Master script to run all of Layer 3

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from Layer3_local_search.results import run_layer3_tests

if __name__ == "__main__":
    run_layer3_tests()