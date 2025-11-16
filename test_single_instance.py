#!/usr/bin/env python3
"""Quick test with a single small instance to verify everything works."""

import time
import read_koref
from koref_utils import (
    compute_earliest_start_schedule,
    compute_expected_makespan,
)
from koref_domain import create_model, solve

# Test with one small instance
instance_path = "problems/non_empty/small/chain/chain_3.yaml"

print(f"Testing with: {instance_path}")
print("=" * 60)

# Compute original makespan
print("Computing original makespan...")
name, n, durations, probabilities, precedence = read_koref.read(instance_path)
activities = list(range(n))

schedule = compute_earliest_start_schedule(activities, precedence, durations)
original_makespan = compute_expected_makespan(activities, schedule, durations, probabilities)
print(f"Original makespan: {original_makespan:.6f}")

# Solve refinement
print("\nSolving refinement problem...")
model, pair_to_info, initial_precedence, unresolved_pair_map, duration_table, prob_table = create_model(
    n, durations, probabilities, precedence
)

start_time = time.time()
solution, cost, bound, is_optimal, is_infeasible = solve(
    model,
    pair_to_info,
    n,
    durations,
    probabilities,
    initial_precedence,
    unresolved_pair_map,
    duration_table,
    prob_table,
    "Optimal",
    "history.csv",
    time_limit=300,  # 5 minute timeout for test
)
runtime = time.time() - start_time

if is_infeasible or solution is None or cost is None:
    print(f"Failed to find solution (runtime: {runtime:.2f}s)")
else:
    improvement = original_makespan - cost
    improvement_pct = (improvement / original_makespan * 100) if original_makespan > 0 else 0
    
    print(f"\nResults:")
    print(f"  Original makespan: {original_makespan:.6f}")
    print(f"  Refined makespan:  {cost:.6f}")
    print(f"  Improvement:       {improvement:.6f} ({improvement_pct:.2f}%)")
    print(f"  Runtime:            {runtime:.2f}s")
    print(f"  Optimal:            {is_optimal}")

