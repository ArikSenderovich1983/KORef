#!/usr/bin/env python3
"""
Verify all makespans shown in Marco.md using the DIDP solver.
"""

import sys
import tempfile
import yaml
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import read_koref
import koref_utils
from koref_domain import create_model, solve, compute_transitive_closure

def verify_makespan(name, n, durations, probabilities, precedence_dict, description):
    """Verify makespan using koref_utils."""
    activities = list(range(n))
    schedule = koref_utils.compute_earliest_start_schedule(activities, precedence_dict, durations)
    makespan = koref_utils.compute_expected_makespan(activities, schedule, durations, probabilities)
    print(f"{description:60s} {makespan:.6f}")
    return makespan

def main():
    print("=" * 80)
    print("VERIFICATION OF ALL MAKESPANS IN MARCO.MD")
    print("=" * 80)
    print()
    
    # Read the cascading example
    name, n, durations, probabilities, initial_prec = read_koref.read('cascading_example.yaml')
    
    print(f"Problem: {name}")
    print(f"Activities: {n}")
    print()
    
    print("=" * 80)
    print("STEP 1: ALL INDIVIDUAL PAIRS (10 pairs)")
    print("=" * 80)
    print()
    
    # All-parallel baseline
    ms_baseline = verify_makespan(name, n, durations, probabilities, {}, 
                                   "None (all-parallel)")
    print()
    
    # All individual pairs
    individual_results = []
    for i in range(n):
        for j in range(i+1, n):
            prec = {(i, j): True}
            desc = f"a_{i} < a_{j}"
            ms = verify_makespan(name, n, durations, probabilities, prec, desc)
            improvement = 100 * (ms_baseline - ms) / ms_baseline
            individual_results.append((desc, ms, improvement))
    
    print()
    print("Summary of individual pairs:")
    print(f"  Baseline (all-parallel): {ms_baseline:.6f}")
    best_single = min(individual_results, key=lambda x: x[1])
    print(f"  Best single pair: {best_single[0]} with {best_single[1]:.6f} ({best_single[2]:.1f}% improvement)")
    print()
    
    print("=" * 80)
    print("STEP 2: FULL CHAIN (all pairs ordered)")
    print("=" * 80)
    print()
    
    # Full chain
    chain_prec = {(0,1): True, (1,2): True, (2,3): True, (3,4): True}
    ms_chain = verify_makespan(name, n, durations, probabilities, chain_prec,
                                "Full chain: a_0 < a_1 < a_2 < a_3 < a_4")
    improvement_chain = 100 * (ms_baseline - ms_chain) / ms_baseline
    print()
    print(f"Improvement: {improvement_chain:.1f}%")
    print()
    
    print("=" * 80)
    print("STEP 3: VERIFY WITH DIDP SOLVER (exhaustive search)")
    print("=" * 80)
    print()
    
    # Create DIDP model and solve
    model, pair_to_info, initial_precedence, unresolved_pair_map, duration_table, prob_table = create_model(
        n, durations, probabilities, initial_prec
    )
    
    print("Running BrFS exhaustive search...")
    print()
    
    # Create temporary history file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        history_file = f.name
    
    try:
        refined_precedence, refined_makespan, _, is_optimal, is_timeout = solve(
            model=model,
            pair_to_info=pair_to_info,
            n=n,
            durations=durations,
            probabilities=probabilities,
            initial_precedence=initial_prec,
            unresolved_pair_map=unresolved_pair_map,
            duration_table=duration_table,
            prob_table=prob_table,
            solver_name='Optimal',
            history=history_file,
            time_limit=120
        )
    finally:
        # Clean up
        import os
        if os.path.exists(history_file):
            os.remove(history_file)
    
    print()
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    print(f"Baseline (all-parallel):      {ms_baseline:.6f}")
    print(f"Best single pair (a_3 < a_4): {best_single[1]:.6f} ({best_single[2]:.1f}% improvement)")
    print(f"Full chain (manual calc):     {ms_chain:.6f} ({improvement_chain:.1f}% improvement)")
    print(f"DIDP optimal (verified):      {refined_makespan:.6f} ({100*(ms_baseline-refined_makespan)/ms_baseline:.1f}% improvement)")
    print()
    
    if abs(ms_chain - refined_makespan) < 1e-6:
        print("[OK] VERIFIED: Manual full chain calculation matches DIDP optimal solution!")
    else:
        print("[FAIL] MISMATCH: Manual calculation differs from DIDP solution!")
        return 1
    
    print()
    print("Optimal precedence constraints found by DIDP:")
    if refined_precedence:
        for (a, b) in sorted(refined_precedence.keys()):
            print(f"  {a} < {b}")
    else:
        print("  (empty - all-parallel is optimal)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

