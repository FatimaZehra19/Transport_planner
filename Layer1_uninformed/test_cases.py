# Define the 5 strategic test cases for Layer 1

def get_test_cases():
    """
    Returns list of test cases as tuples: (start_node, goal_node, description)
    
    Each test case is chosen to test a specific property:
    1. Short path — sanity check
    2. Long cross-city path — tests scalability
    3. Through bottleneck — tests constraint handling
    4. Where BFS ≠ UCS — shows importance of weights
    5. Where DFS is bad — demonstrates inefficiency
    """
    
    test_cases = [
        {
            "name": "Test 1: Short Direct Path",
            "start": 0,      # Saddar
            "goal": 1,       # Clifton
            "description": "Direct edge, minimal exploration expected",
            "why": "Sanity check — all algorithms should find the direct 20-min route"
        },
        
        {
            "name": "Test 2: Long Cross-City Route",
            "start": 9,      # Orangi
            "goal": 3,       # Korangi
            "description": "Far apart, multiple paths possible",
            "why": "Tests if algorithm scales to longer routes and explores efficiently"
        },
        
        {
            "name": "Test 3: Through a Bottleneck",
            "start": 9,      # Orangi
            "goal": 0,       # Saddar
            "description": "Must use Lyari Expressway (Orangi → SITE → Saddar path)",
            "why": "Tests if algorithm respects constraints — only 1-2 realistic routes"
        },
        
        {
            "name": "Test 4: BFS vs UCS Disagree",
            "start": 0,      # Saddar
            "goal": 4,       # Malir
            "description": "Multiple paths with different hop counts vs total time",
            "why": "BFS finds fewest hops, UCS finds cheapest by minutes — shows weights matter"
        },
        
        {
            "name": "Test 5: DFS Performs Badly",
            "start": 6,      # Gulshan-e-Iqbal
            "goal": 12,      # Keamari
            "description": "Goal is in a different region from where DFS explores first",
            "why": "DFS might explore entire eastern Karachi before reaching western Keamari"
        }
    ]
    
    return test_cases


# Helper function to extract just the tuples (for running tests)
def get_test_tuples():
    """Returns list of (start, goal, name) tuples for easier iteration"""
    return [(t["start"], t["goal"], t["name"]) for t in get_test_cases()]