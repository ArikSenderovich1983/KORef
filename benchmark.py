#!/usr/bin/env python3
"""
Unified benchmark script for KORef problems.
Supports both empty and non-empty constraint problems.
"""

import os
import sys
import time
import glob
import csv
from pathlib import Path

import read_koref
from koref_utils import (
    compute_earliest_start_schedule,
    compute_expected_makespan,
)
from koref_domain import create_model, solve


def find_all_problems(constraint_type="all"):
    """
    Find all problem files.
    
    Args:
        constraint_type: "empty", "non_empty", or "all"
    """
    problems = []
    
    types_to_search = []
    if constraint_type == "all":
        types_to_search = ["empty", "non_empty"]
    else:
        types_to_search = [constraint_type]
    
    for ct in types_to_search:
        base_dir = Path(f"problems/{ct}")
        if not base_dir.exists():
            continue
            
        for size in ["small", "medium", "large"]:
            if ct == "empty":
                # Empty problems: no structure subdirectories (all have empty precedence)
                pattern = base_dir / size / "*.yaml"
                for yaml_file in sorted(glob.glob(str(pattern))):
                    # Extract structure type from filename (e.g., chain_3_high.yaml -> chain)
                    struct_type = Path(yaml_file).stem.split('_')[0] if '_' in Path(yaml_file).stem else "unknown"
                    problems.append({
                        'path': yaml_file,
                        'constraint_type': ct,
                        'size': size,
                        'struct_type': struct_type,
                        'name': Path(yaml_file).stem
                    })
            else:
                # Non-empty problems: organized by structure type
                for struct_type in ["chain", "parallel", "mixed", "dag"]:
                    pattern = base_dir / size / struct_type / "*.yaml"
                    for yaml_file in sorted(glob.glob(str(pattern))):
                        problems.append({
                            'path': yaml_file,
                            'constraint_type': ct,
                            'size': size,
                            'struct_type': struct_type,
                            'name': Path(yaml_file).stem
                        })
    
    return problems


def compute_original_makespan(instance_path):
    """Compute expected makespan for the original precedence."""
    name, n, durations, probabilities, precedence = read_koref.read(instance_path)
    activities = list(range(n))
    
    # Compute canonical schedule for original precedence
    schedule = compute_earliest_start_schedule(activities, precedence, durations)
    
    # Compute expected makespan
    expected_makespan = compute_expected_makespan(
        activities, schedule, durations, probabilities
    )
    
    return expected_makespan


def solve_refined(instance_path, time_limit=1800):
    """Solve the refinement problem and return refined makespan and runtime."""
    name, n, durations, probabilities, precedence = read_koref.read(instance_path)
    
    # Adjust time limit based on problem size
    if n >= 50:
        time_limit = max(time_limit, 7200)  # 2 hours for 50+ activities
    elif n >= 20:
        time_limit = max(time_limit, 3600)  # 1 hour for 20+ activities
    
    # Create model
    model, pair_to_info, initial_precedence, unresolved_pair_map, duration_table, prob_table = create_model(
        n, durations, probabilities, precedence
    )
    
    start_time = time.time()
    
    # Solve with optimal exhaustive search
    refined_precedence, refined_makespan, history, is_optimal, is_timeout = solve(
        model, pair_to_info, unresolved_pair_map, duration_table, prob_table, history=None,
        config="Optimal", time_limit=time_limit
    )
    
    runtime = time.time() - start_time
    
    return refined_makespan, is_optimal, runtime, not is_timeout


def run_benchmark(constraint_type="all", time_limit=1800, output_prefix="benchmark"):
    """Run benchmark on all problems."""
    problems = find_all_problems(constraint_type)
    
    if not problems:
        print(f"No problems found for constraint_type={constraint_type}")
        return
    
    print(f"Found {len(problems)} problems")
    print(f"Constraint type: {constraint_type}")
    print(f"Time limit per problem: {time_limit}s")
    print("=" * 80)
    
    results = []
    
    for i, problem_info in enumerate(problems, 1):
        instance_path = problem_info['path']
        instance_name = problem_info['name']
        
        print(f"\n[{i}/{len(problems)}] Processing: {instance_name}")
        print(f"  Path: {instance_path}")
        print(f"  Category: {problem_info['size']} | Type: {problem_info['struct_type']}")
        
        try:
            # Compute original makespan
            print(f"  Computing original makespan...")
            original_makespan = compute_original_makespan(instance_path)
            print(f"  Original makespan: {original_makespan:.6f}")
            
            # Solve refinement
            print(f"  Solving refinement problem...")
            refined_makespan, is_optimal, runtime, success = solve_refined(
                instance_path, time_limit=time_limit
            )
            
            if success and refined_makespan is not None:
                improvement = original_makespan - refined_makespan
                improvement_pct = (improvement / original_makespan * 100) if original_makespan > 0 else 0
                
                results.append({
                    'instance': instance_name,
                    'constraint_type': problem_info['constraint_type'],
                    'size': problem_info['size'],
                    'struct_type': problem_info['struct_type'],
                    'n': read_koref.read(instance_path)[1],
                    'original': original_makespan,
                    'refined': refined_makespan,
                    'improvement': improvement,
                    'improvement_pct': improvement_pct,
                    'runtime': runtime,
                    'optimal': is_optimal,
                    'status': 'OK' if is_optimal else 'HEURISTIC'
                })
                
                print(f"  Refined makespan: {refined_makespan:.6f}")
                print(f"  Improvement: {improvement:.6f} ({improvement_pct:.2f}%)")
                print(f"  Runtime: {runtime:.2f}s")
                print(f"  Status: {'Optimal' if is_optimal else 'Heuristic'}")
            else:
                results.append({
                    'instance': instance_name,
                    'constraint_type': problem_info['constraint_type'],
                    'size': problem_info['size'],
                    'struct_type': problem_info['struct_type'],
                    'n': read_koref.read(instance_path)[1],
                    'original': original_makespan,
                    'refined': None,
                    'improvement': None,
                    'improvement_pct': None,
                    'runtime': runtime,
                    'optimal': False,
                    'status': 'FAIL'
                })
                print(f"  Failed to find solution")
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'instance': instance_name,
                'constraint_type': problem_info['constraint_type'],
                'size': problem_info['size'],
                'struct_type': problem_info['struct_type'],
                'n': None,
                'original': None,
                'refined': None,
                'improvement': None,
                'improvement_pct': None,
                'runtime': None,
                'optimal': False,
                'status': f'ERROR: {str(e)[:50]}'
            })
    
    # Save results
    save_results(results, output_prefix)
    
    return results


def save_results(results, prefix="benchmark"):
    """Save results to CSV and Markdown files."""
    # CSV file
    csv_path = f"{prefix}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    print(f"\nResults saved to {csv_path}")
    
    # Markdown file
    md_path = f"{prefix}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# KORef Benchmark Results\n\n")
        f.write(f"## Results Summary\n\n")
        f.write("| Instance | Type | Size | Struct | N | Original | Refined | Improvement | Improvement % | Runtime (s) | Status |\n")
        f.write("|----------|------|------|--------|---|----------|---------|-------------|---------------|-------------|--------|\n")
        
        for r in results:
            orig = f"{r['original']:.6f}" if r['original'] is not None else "N/A"
            ref = f"{r['refined']:.6f}" if r['refined'] is not None else "N/A"
            imp = f"{r['improvement']:.6f}" if r['improvement'] is not None else "N/A"
            imp_pct = f"{r['improvement_pct']:.2f}%" if r['improvement_pct'] is not None else "N/A"
            rt = f"{r['runtime']:.2f}" if r['runtime'] is not None else "N/A"
            n = str(r['n']) if r['n'] is not None else "N/A"
            
            f.write(f"| {r['instance']} | {r['constraint_type']} | {r['size']} | {r['struct_type']} | {n} | {orig} | {ref} | {imp} | {imp_pct} | {rt} | {r['status']} |\n")
        
        # Summary statistics
        successful = [r for r in results if r['status'] == 'OK']
        improved = [r for r in successful if r['improvement'] is not None and r['improvement'] > 0]
        
        f.write(f"\n## Summary Statistics\n\n")
        f.write(f"- **Total problems**: {len(results)}\n")
        f.write(f"- **Successfully solved**: {len(successful)}/{len(results)}\n")
        f.write(f"- **Optimal solutions**: {len([r for r in successful if r['optimal']])}/{len(successful)}\n")
        if improved:
            avg_imp = sum(r['improvement_pct'] for r in improved) / len(improved)
            f.write(f"- **Problems with improvement**: {len(improved)}/{len(successful)} ({len(improved)/len(successful)*100:.1f}%)\n")
            f.write(f"- **Average improvement** (for improved): {avg_imp:.2f}%\n")
    
    print(f"Results saved to {md_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark KORef solver")
    parser.add_argument("--type", choices=["empty", "non_empty", "all"], default="all",
                       help="Constraint type to benchmark")
    parser.add_argument("--time-limit", type=int, default=1800,
                       help="Time limit per problem in seconds")
    parser.add_argument("--output", default="benchmark",
                       help="Output file prefix")
    
    args = parser.parse_args()
    
    run_benchmark(
        constraint_type=args.type,
        time_limit=args.time_limit,
        output_prefix=args.output
    )

