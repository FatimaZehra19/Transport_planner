# Master script to run all of Layer 1

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'karachi_transport'))

from Layer1_uninformed.results import run_layer1_tests

if __name__ == "__main__":
    run_layer1_tests()