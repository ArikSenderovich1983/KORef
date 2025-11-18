#!/usr/bin/env python3
"""
Analyze which constraints are "forced" in KORef problems.

A constraint a < b is "forced" if any optimal solution must include it.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
import read_koref


def compute_dominance_constraints(n: int, durations: List[float], probabilities: List[float]) -> Set[Tuple[int, int]]:
    """
    Compute constraints forced by activity dominance.
    
    Activity i dominates activity j if:
    - duration_i <= duration_j AND
    - p_i >= p_j
    
    In this case, i < j should be in any optimal solution.
    
    Returns:
        Set of (i, j) pairs where i < j is forced
    """
    forced = set()
    
    for i in range(n):
        for j in range(n):
            if i != j:
                # Check if i dominates j
                if durations[i] <= durations[j] and probabilities[i] >= probabilities[j]:
                    # Strict dominance (at least one inequality is strict)
                    if durations[i] < durations[j] or probabilities[i] > probabilities[j]:
                        forced.add((i, j))
    
    return forced


def compute_risk_ratio_heuristic(
    n: int, 
    durations: List[float], 
    probabilities: List[float],
    threshold: float = 2.0
) -> Set[Tuple[int, int]]:
    """
    Compute heuristic constraints based on risk-duration ratio.
    
    If p_i/d_i is much larger than p_j/d_j, suggest i < j.
    
    WARNING: This is a HEURISTIC, not a guarantee!
    
    Returns:
        Set of (i, j) pairs where i < j is suggested
    """
    ratios = []
    for i in range(n):
        if durations[i] > 0:
            ratios.append((probabilities[i] / durations[i], i))
        else:
            ratios.append((0.0, i))
    
    suggested = set()
    
    for i in range(n):
        for j in range(n):
            if i != j and ratios[i][0] > 0 and ratios[j][0] > 0:
                ratio_i = ratios[i][0]
                ratio_j = ratios[j][0]
                
                # If i has significantly higher ratio than j
                if ratio_i / ratio_j > threshold:
                    suggested.add((i, j))
    
    return suggested


def analyze_problem(problem_path: str):
    """Analyze a single problem for forced constraints."""
    print(f"\nAnalyzing: {problem_path}")
    print("=" * 80)
    
    # Read problem
    name, n, durations, probabilities, precedence = read_koref.read(problem_path)
    
    print(f"Problem: {name}")
    print(f"Number of activities: {n}")
    print(f"Initial constraints: {len(precedence)}")
    
    # Compute number of unordered pairs
    num_unordered = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in precedence and (j, i) not in precedence:
                num_unordered += 1
    
    print(f"Unordered pairs: {num_unordered}")
    print(f"Total possible refinements: 2^{num_unordered} = {2**num_unordered}")
    
    # Compute dominance constraints
    dominance = compute_dominance_constraints(n, durations, probabilities)
    
    print(f"\n--- DOMINANCE ANALYSIS (PROVABLY CORRECT) ---")
    print(f"Forced constraints by dominance: {len(dominance)}")
    
    if dominance:
        print("\nDominance-forced constraints:")
        for i, j in sorted(dominance):
            print(f"  {i} < {j}  (d={durations[i]:.2f} <= {durations[j]:.2f}, p={probabilities[i]:.3f} >= {probabilities[j]:.3f})")
    else:
        print("  None - no strict dominance relationships found")
    
    # Compute risk-ratio heuristic
    heuristic = compute_risk_ratio_heuristic(n, durations, probabilities, threshold=2.0)
    
    print(f"\n--- RISK-RATIO HEURISTIC (THRESHOLD=2.0) ---")
    print(f"Suggested constraints: {len(heuristic)}")
    
    if heuristic:
        # Compute ratios for display
        ratios = [(probabilities[i] / durations[i] if durations[i] > 0 else 0.0, i) for i in range(n)]
        
        print("\nHeuristic suggestions:")
        for i, j in sorted(heuristic):
            ratio_i = probabilities[i] / durations[i] if durations[i] > 0 else 0.0
            ratio_j = probabilities[j] / durations[j] if durations[j] > 0 else 0.0
            ratio_ratio = ratio_i / ratio_j if ratio_j > 0 else float('inf')
            print(f"  {i} < {j}  (p/d: {ratio_i:.3f} vs {ratio_j:.3f}, ratio: {ratio_ratio:.2f}x)")
    else:
        print("  None - no strong ratio differences found")
    
    # Check if heuristic suggests a total order
    if len(heuristic) >= n * (n - 1) / 2:
        print("\n⚠️  Heuristic suggests a TOTAL ORDER (chain) might be optimal!")
    
    # Potential reduction in search space
    if dominance or heuristic:
        forced_count = len(dominance)
        remaining_unordered = num_unordered - forced_count
        
        print(f"\n--- SEARCH SPACE REDUCTION ---")
        print(f"If we apply dominance preprocessing:")
        print(f"  Forced constraints: {forced_count}")
        print(f"  Remaining unordered: {remaining_unordered}")
        print(f"  Search space: 2^{remaining_unordered} = {2**remaining_unordered}")
        print(f"  Reduction: {100 * (1 - 2**remaining_unordered / 2**num_unordered):.1f}%")


def analyze_directory(directory: str, pattern: str = "*.yaml"):
    """Analyze all problems in a directory."""
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"Error: Directory {directory} not found")
        return
    
    problem_files = list(dir_path.glob(pattern))
    
    if not problem_files:
        print(f"No problems found in {directory}")
        return
    
    print(f"Found {len(problem_files)} problems in {directory}")
    
    total_forced = 0
    total_unordered = 0
    problems_with_dominance = 0
    
    for problem_file in sorted(problem_files):
        try:
            name, n, durations, probabilities, precedence = read_koref.read(str(problem_file))
            
            # Count unordered pairs
            num_unordered = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if (i, j) not in precedence and (j, i) not in precedence:
                        num_unordered += 1
            
            # Compute dominance
            dominance = compute_dominance_constraints(n, durations, probabilities)
            
            total_forced += len(dominance)
            total_unordered += num_unordered
            
            if dominance:
                problems_with_dominance += 1
                print(f"\n{problem_file.name}: {len(dominance)} forced constraints out of {num_unordered} unordered pairs")
        
        except Exception as e:
            print(f"Error processing {problem_file}: {e}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total problems analyzed: {len(problem_files)}")
    print(f"Problems with dominance constraints: {problems_with_dominance}")
    print(f"Average forced constraints per problem: {total_forced / len(problem_files):.1f}")
    print(f"Average unordered pairs per problem: {total_unordered / len(problem_files):.1f}")
    
    if total_unordered > 0:
        print(f"Percentage of constraints forced by dominance: {100 * total_forced / total_unordered:.1f}%")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detect_forced_constraints.py <problem_file_or_directory>")
        print("\nExamples:")
        print("  python detect_forced_constraints.py problems/empty/small/empty_4_high_01.yaml")
        print("  python detect_forced_constraints.py problems/empty/ultra_large_ultra_risky/")
        sys.exit(1)
    
    path = sys.argv[1]
    
    if Path(path).is_dir():
        analyze_directory(path)
    else:
        analyze_problem(path)

