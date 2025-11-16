#!/usr/bin/env python3
"""
Unified benchmark script for KORef problems.
Runs all problems (empty/non-empty, all structures, all sizes) and presents a single outcome table.
Default timeout: 30 seconds per problem.
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


def find_all_problems():
    """Find all problem files in the problems directory."""
    problems = []
    base_dir = Path("problems")
    
    # Find empty problems
    empty_dir = base_dir / "empty"
    if empty_dir.exists():
        for size in ["small", "medium", "large", "very_large"]:
            size_dir = empty_dir / size
            if size_dir.exists():
                for yaml_file in sorted(size_dir.glob("*.yaml")):
                    problems.append({
                        'path': str(yaml_file),
                        'constraint_type': 'empty',
                        'size': size,
                        'struct_type': 'empty',  # Empty problems don't have structure
                        'name': yaml_file.stem
                    })
    
    # Find non-empty problems
    non_empty_dir = base_dir / "non_empty"
    if non_empty_dir.exists():
        for size in ["small", "medium", "large", "very_large"]:
            size_dir = non_empty_dir / size
            if size_dir.exists():
                for struct_type in ["chain", "parallel", "mixed", "dag"]:
                    struct_dir = size_dir / struct_type
                    if struct_dir.exists():
                        for yaml_file in sorted(struct_dir.glob("*.yaml")):
                            problems.append({
                                'path': str(yaml_file),
                                'constraint_type': 'non_empty',
                                'size': size,
                                'struct_type': struct_type,
                                'name': yaml_file.stem
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


def solve_refined(instance_path, time_limit=30):
    """Solve the refinement problem and return refined makespan and runtime."""
    name, n, durations, probabilities, precedence = read_koref.read(instance_path)
    
    # Create model
    model, pair_to_info, initial_precedence, unresolved_pair_map, duration_table, prob_table = create_model(
        n, durations, probabilities, precedence
    )
    
    start_time = time.time()
    
    # Solve with optimal exhaustive search
    history = []  # Empty history
    refined_precedence, refined_makespan, _, is_optimal, is_timeout = solve(
        model,
        pair_to_info,
        n,
        durations,
        probabilities,
        initial_precedence,
        unresolved_pair_map,
        duration_table,
        prob_table,
        "Optimal",  # solver_name
        history,
        time_limit=time_limit
    )
    
    runtime = time.time() - start_time
    
    return refined_makespan, is_optimal, runtime, not is_timeout


def run_benchmark(time_limit=30, output_prefix="benchmark_unified"):
    """Run benchmark on all problems."""
    problems = find_all_problems()
    
    if not problems:
        print("No problems found!")
        return
    
    print("=" * 100)
    print("KORef Unified Benchmark")
    print("=" * 100)
    print(f"Found {len(problems)} problems")
    print(f"Time limit per problem: {time_limit}s")
    print("=" * 100)
    print()
    
    results = []
    
    for i, problem_info in enumerate(problems, 1):
        instance_path = problem_info['path']
        instance_name = problem_info['name']
        
        print(f"[{i}/{len(problems)}] Processing: {instance_name}")
        print(f"  Path: {instance_path}")
        print(f"  Type: {problem_info['constraint_type']} | Size: {problem_info['size']} | Structure: {problem_info['struct_type']}")
        
        try:
            # Compute original makespan
            original_makespan = compute_original_makespan(instance_path)
            print(f"  Original makespan: {original_makespan:.6f}")
            
            # Solve refinement
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
                    'status': 'TIMEOUT' if runtime >= time_limit else 'FAIL'
                })
                print(f"  Failed or timeout")
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            try:
                n = read_koref.read(instance_path)[1]
            except:
                n = None
            results.append({
                'instance': instance_name,
                'constraint_type': problem_info['constraint_type'],
                'size': problem_info['size'],
                'struct_type': problem_info['struct_type'],
                'n': n,
                'original': None,
                'refined': None,
                'improvement': None,
                'improvement_pct': None,
                'runtime': None,
                'optimal': False,
                'status': f'ERROR: {str(e)[:30]}'
            })
        
        print()
    
    # Save results
    save_results(results, output_prefix)
    
    return results


def save_results(results, prefix="benchmark_unified"):
    """Save results to CSV and Markdown files."""
    # CSV file
    csv_path = f"{prefix}.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    print(f"Results saved to {csv_path}")
    
    # Markdown file
    md_path = f"{prefix}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# KORef Unified Benchmark Results\n\n")
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
        heuristic = [r for r in results if r['status'] == 'HEURISTIC']
        improved = [r for r in successful + heuristic if r['improvement'] is not None and r['improvement'] > 0]
        
        f.write(f"\n## Summary Statistics\n\n")
        f.write(f"- **Total problems**: {len(results)}\n")
        f.write(f"- **Successfully solved**: {len(successful) + len(heuristic)}/{len(results)}\n")
        f.write(f"- **Optimal solutions**: {len(successful)}/{len(successful) + len(heuristic)}\n")
        f.write(f"- **Heuristic solutions**: {len(heuristic)}/{len(successful) + len(heuristic)}\n")
        if improved:
            avg_imp = sum(r['improvement_pct'] for r in improved) / len(improved)
            f.write(f"- **Problems with improvement**: {len(improved)}/{len(successful) + len(heuristic)} ({len(improved)/(len(successful) + len(heuristic))*100:.1f}%)\n")
            f.write(f"- **Average improvement** (for improved): {avg_imp:.2f}%\n")
        
        # Print console summary
        print("\n" + "=" * 100)
        print("RESULTS SUMMARY")
        print("=" * 100)
        print(f"Total problems: {len(results)}")
        print(f"Successfully solved: {len(successful) + len(heuristic)}/{len(results)}")
        print(f"Optimal solutions: {len(successful)}/{len(successful) + len(heuristic)}")
        print(f"Heuristic solutions: {len(heuristic)}/{len(successful) + len(heuristic)}")
        if improved:
            avg_imp = sum(r['improvement_pct'] for r in improved) / len(improved)
            print(f"Problems with improvement: {len(improved)}/{len(successful) + len(heuristic)} ({len(improved)/(len(successful) + len(heuristic))*100:.1f}%)")
            print(f"Average improvement (for improved): {avg_imp:.2f}%")
        print("=" * 100)
    
    print(f"Results saved to {md_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified benchmark for KORef solver")
    parser.add_argument("--time-limit", type=int, default=30,
                       help="Time limit per problem in seconds (default: 30)")
    parser.add_argument("--output", default="benchmark_unified",
                       help="Output file prefix (default: benchmark_unified)")
    
    args = parser.parse_args()
    
    run_benchmark(
        time_limit=args.time_limit,
        output_prefix=args.output
    )

