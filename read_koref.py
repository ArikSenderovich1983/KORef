#!/usr/bin/env python3
"""
Instance reader for KO-plan refinement problems.
Supports both YAML format (preferred) and legacy text format.
"""

import os
import yaml


def read(filename):
    """
    Read a KO-plan instance from a file.
    
    Supports two formats:
    1. YAML format (preferred): Structured YAML with activities and precedence
    2. Legacy text format: Simple text format
    
    Returns:
        name: Instance name (from filename or YAML metadata)
        n: Number of activities
        durations: List of durations
        probabilities: List of KO probabilities
        precedence: Dict mapping (a, b) -> True if a precedes b
    """
    # Check file extension to determine format
    if filename.endswith('.yaml') or filename.endswith('.yml'):
        return read_yaml(filename)
    else:
        return read_legacy(filename)


def read_yaml(filename):
    """
    Read a KO-plan instance from a YAML file.
    
    Expected YAML structure:
    - activities: List of activity dicts with id, duration, ko_probability
    - precedence: List of [a, b] pairs meaning a precedes b
    
    Returns:
        name: Instance name
        n: Number of activities
        durations: List of durations
        probabilities: List of KO probabilities
        precedence: Dict mapping (a, b) -> True if a precedes b
    """
    with open(filename, 'r') as f:
        data = yaml.safe_load(f)
    
    # Extract name
    name = data.get('name', os.path.basename(filename))
    
    # Extract activities
    activities_data = data['activities']
    n = len(activities_data)
    
    # Sort activities by id to ensure correct ordering
    activities_data.sort(key=lambda x: x['id'])
    
    durations = []
    probabilities = []
    
    for activity in activities_data:
        durations.append(float(activity['duration']))
        probabilities.append(float(activity['ko_probability']))
    
    # Extract precedence constraints
    precedence = {}
    precedence_list = data.get('precedence', [])
    
    for constraint in precedence_list:
        if isinstance(constraint, list) and len(constraint) == 2:
            a = int(constraint[0])
            b = int(constraint[1])
            precedence[(a, b)] = True
        elif isinstance(constraint, str):
            # Handle "a -> b" format
            parts = constraint.split('->')
            if len(parts) == 2:
                a = int(parts[0].strip())
                b = int(parts[1].strip())
                precedence[(a, b)] = True
    
    return name, n, durations, probabilities, precedence


def read_legacy(filename):
    """
    Read a KO-plan instance from legacy text format.
    
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
    
    # Check that refined precedence extends original (using transitive closure)
    # A refinement means the refined precedence should include all original constraints
    # (either directly or transitively)
    from koref_utils import compute_transitive_closure
    
    original_closure = compute_transitive_closure(precedence, len(activities))
    refined_closure = compute_transitive_closure(refined_precedence, len(activities))
    
    # Check that every constraint in original_closure is also in refined_closure
    for (a, b) in original_closure:
        if original_closure.get((a, b), False) and not refined_closure.get((a, b), False):
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
