# Same as Layer 2 test cases

test_cases = [
    {"name": "Test 1: Short Direct Path", "start": 0, "goal": 1},
    {"name": "Test 2: Long Cross-City Route", "start": 9, "goal": 3},
    {"name": "Test 3: Through a Bottleneck", "start": 9, "goal": 0},
    {"name": "Test 4: BFS vs UCS Disagree (A* Should Win)", "start": 0, "goal": 4},
    {"name": "Test 5: DFS Performs Badly (A* Should Dominate)", "start": 6, "goal": 12},
]