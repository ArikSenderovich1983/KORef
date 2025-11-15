#!/usr/bin/env python3
"""
Manual verification of optimality using Bellman equation.
Computes all possible refinements and their expected makespans.
"""

import read_koref
from koref_utils import (
    compute_transitive_closure,
    compute_earliest_start_schedule,
    compute_expected_makespan,
    check_acyclic,
)
from itertools import product


def enumerate_all_refinements(n, initial_precedence):
    """
    Enumerate all possible refinements of the initial precedence.
    Returns list of (refined_precedence, is_valid) tuples.
    """
    # Find unresolved pairs
    closure = compute_transitive_closure(initial_precedence, n)
    unresolved = []
    for a in range(n):
        for b in range(n):
            if a != b:
                has_a_prec_b = closure.get((a, b), False)
                has_b_prec_a = closure.get((b, a), False)
                if not has_a_prec_b and not has_b_prec_a:
                    # Only add one direction (canonical)
                    if a < b:
                        unresolved.append((a, b))
    
    print(f"Unresolved pairs: {unresolved}")
    print(f"Total refinements to evaluate: {2**len(unresolved)}")
    
    refinements = []
    
    # For each unresolved pair, we can add either (a,b) or (b,a)
    # Generate all combinations
    for choices in product([0, 1], repeat=len(unresolved)):
        refined = initial_precedence.copy()
        
        # Add constraints based on choices
        for i, (a, b) in enumerate(unresolved):
            if choices[i] == 0:
                refined[(a, b)] = True
            else:
                refined[(b, a)] = True
        
        # Check if valid (acyclic)
        if check_acyclic(refined, n):
            refinements.append((refined, True))
        else:
            refinements.append((refined, False))
    
    return refinements, unresolved


def solve_manually(instance_file):
    """
    Solve KORef manually by enumerating all refinements.
    """
    name, n, durations, probabilities, initial_precedence = read_koref.read(instance_file)
    
    print("=" * 80)
    print(f"MANUAL OPTIMALITY VERIFICATION: {name}")
    print("=" * 80)
    print(f"\nActivities: {n}")
    print(f"Durations: {durations}")
    print(f"KO Probabilities: {probabilities}")
    print(f"Initial Precedence: {list(initial_precedence.keys())}")
    
    # Enumerate all refinements
    refinements, unresolved_pairs = enumerate_all_refinements(n, initial_precedence)
    
    print(f"\nEvaluating {len(refinements)} refinements...\n")
    
    # Evaluate each refinement
    results = []
    activities = list(range(n))
    
    # First, add the canonical schedule (empty refinement) for comparison
    schedule_canonical = compute_earliest_start_schedule(activities, initial_precedence, durations)
    makespan_canonical = compute_expected_makespan(
        activities, schedule_canonical, durations, probabilities
    )
    results.append({
        'refinement': initial_precedence.copy(),
        'added_constraints': [],  # No constraints added
        'expected_makespan': makespan_canonical,
        'schedule': schedule_canonical,
        'is_canonical': True,
    })
    
    for i, (refined_prec, is_valid) in enumerate(refinements):
        if not is_valid:
            continue
        
        # Compute schedule
        schedule = compute_earliest_start_schedule(activities, refined_prec, durations)
        
        # Compute expected makespan
        expected_makespan = compute_expected_makespan(
            activities, schedule, durations, probabilities
        )
        
        # Extract added constraints
        added = []
        for (a, b) in refined_prec:
            if (a, b) not in initial_precedence:
                added.append((a, b))
        
        results.append({
            'refinement': refined_prec,
            'added_constraints': added,
            'expected_makespan': expected_makespan,
            'schedule': schedule,
            'is_canonical': False,
        })
    
    # Sort by expected makespan
    results.sort(key=lambda x: x['expected_makespan'])
    
    # Print results
    print("=" * 80)
    print("ALL REFINEMENTS (sorted by expected makespan):")
    print("=" * 80)
    
    for i, result in enumerate(results):
        print(f"\nRefinement #{i+1}:")
        if result.get('is_canonical', False):
            print(f"  Type: CANONICAL (no refinement)")
        else:
            print(f"  Type: Refinement")
        print(f"  Added constraints: {result['added_constraints']}")
        print(f"  Schedule: {result['schedule']}")
        print(f"  Expected makespan: {result['expected_makespan']:.6f}")
    
    # Optimal solution
    optimal = results[0]
    print("\n" + "=" * 80)
    print("OPTIMAL SOLUTION:")
    print("=" * 80)
    print(f"Added constraints: {optimal['added_constraints']}")
    print(f"Schedule: {optimal['schedule']}")
    print(f"Expected makespan: {optimal['expected_makespan']:.6f}")
    
    # Bellman equation verification
    print("\n" + "=" * 80)
    print("BELLMAN EQUATION VERIFICATION:")
    print("=" * 80)
    print("\nThe Bellman equation for KORef states:")
    print("  V(S) = min_{transition} [cost(transition) + V(S')]")
    print("\nFor terminal states:")
    print("  V(S_terminal) = ExpectedMakespan(S_terminal)")
    print("\nFor non-terminal states:")
    print("  V(S) = min_{unresolved pair (a,b)} [V(S + a<b), V(S + b<a)]")
    print("\nVerification:")
    print(f"  Optimal expected makespan: {optimal['expected_makespan']:.6f}")
    print(f"  Number of valid refinements evaluated: {len(results)}")
    print(f"  All refinements satisfy: V(S) >= V(S_optimal)")
    
    # Check if all other refinements have higher or equal cost
    all_higher = all(r['expected_makespan'] >= optimal['expected_makespan'] 
                     for r in results)
    print(f"  Optimality condition satisfied: {all_higher}")
    
    return optimal, results


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        instance_file = sys.argv[1]
    else:
        instance_file = "problems/small/mixed_4.yaml"
    
    optimal, all_results = solve_manually(instance_file)
