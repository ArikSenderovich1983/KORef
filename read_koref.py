#!/usr/bin/env python3
"""
Instance reader for KO-plan refinement problems.
"""


def read(filename):
    """
    Read a KO-plan instance from a file.
    
    Format:
    Line 1: n (number of activities)
    Lines 2 to n+1: duration probability (one per activity)
    Line n+2: m (number of precedence constraints)
    Lines n+3 to n+m+2: a b (meaning activity a precedes activity b)
    
    Activities are numbered 0 to n-1.
    
    Returns:
        name: Instance name (filename)
        n: Number of activities
        durations: List of durations
        probabilities: List of KO probabilities
        precedence: Dict mapping (a, b) -> True if a precedes b
    """
    with open(filename) as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    n = int(lines[0])
    durations = []
    probabilities = []
    
    for i in range(1, n + 1):
        parts = lines[i].split()
        durations.append(float(parts[0]))
        probabilities.append(float(parts[1]))
    
    m = int(lines[n + 1])
    precedence = {}
    
    for i in range(n + 2, n + m + 2):
        parts = lines[i].split()
        a = int(parts[0])
        b = int(parts[1])
        precedence[(a, b)] = True
    
    # Extract name from filename
    import os
    name = os.path.basename(filename)
    
    return name, n, durations, probabilities, precedence


def validate(activities, precedence, durations, probabilities, refined_precedence, expected_makespan):
    """
    Validate a solution by recomputing expected makespan.
    
    Args:
        activities: List of activity indices
        precedence: Original precedence constraints
        durations: List of durations
        probabilities: List of KO probabilities
        refined_precedence: Refined precedence constraints (solution)
        expected_makespan: Claimed expected makespan
    
    Returns:
        True if valid, False otherwise
    """
    from koref_utils import (
        compute_earliest_start_schedule,
        compute_expected_makespan,
        check_acyclic,
    )
    
    # Check that refined precedence extends original
    for (a, b) in precedence:
        if not refined_precedence.get((a, b), False):
            print(f"Error: Refined precedence missing original constraint ({a}, {b})")
            return False
    
    # Check acyclicity
    if not check_acyclic(refined_precedence, len(activities)):
        print("Error: Refined precedence contains cycles")
        return False
    
    # Compute schedule
    schedule = compute_earliest_start_schedule(
        activities, refined_precedence, durations
    )
    
    # Recompute expected makespan
    computed_makespan = compute_expected_makespan(
        activities, schedule, durations, probabilities
    )
    
    # Allow small floating point differences
    if abs(computed_makespan - expected_makespan) > 1e-6:
        print(
            f"Error: Expected makespan mismatch. "
            f"Computed: {computed_makespan}, Claimed: {expected_makespan}"
        )
        return False
    
    return True
