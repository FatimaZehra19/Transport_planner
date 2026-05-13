# Same test cases as Layer 1 for comparison

def get_test_cases():
    """
    Returns list of test cases as dicts.
    Same 5 tests as Layer 1 so we can compare Heuristic vs Uninformed algorithms.
    """
    
    test_cases = [
        {
            "name": "Test 1: Short Direct Path",
            "start": 0,      # Saddar
            "goal": 1,       # Clifton
            "description": "Direct edge, minimal exploration expected",
            "why": "Sanity check — heuristics should recognize this is trivial"
        },
        
        {
            "name": "Test 2: Long Cross-City Route",
            "start": 9,      # Orangi
            "goal": 3,       # Korangi
            "description": "Far apart, multiple paths possible",
            "why": "Tests if heuristic guides search efficiently over long distances"
        },
        
        {
            "name": "Test 3: Through a Bottleneck",
            "start": 9,      # Orangi
            "goal": 0,       # Saddar
            "description": "Must use Lyari Expressway (Orangi → SITE → Saddar path)",
            "why": "Tests if heuristic navigates constrained geography correctly"
        },
        
        {
            "name": "Test 4: BFS vs UCS Disagree (A* Should Win)",
            "start": 0,      # Saddar
            "goal": 4,       # Malir
            "description": "Multiple paths with different hop counts vs total time",
            "why": "Tests if A* beats both BFS (wrong path) and UCS (inefficient)"
        },
        
        {
            "name": "Test 5: DFS Performs Badly (A* Should Dominate)",
            "start": 6,      # Gulshan-e-Iqbal
            "goal": 12,      # Keamari
            "description": "Goal is in different region from where DFS explores first",
            "why": "Tests if A* handles disorienting geography better than uninformed search"
        }
    ]
    
    return test_cases


def get_test_tuples():
    """Returns list of (start, goal, name) tuples for easier iteration"""
    return [(t["start"], t["goal"], t["name"]) for t in get_test_cases()]