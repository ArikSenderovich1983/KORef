#!/usr/bin/env python3
"""
Benchmark script to compare original vs refined solutions for all problem instances.
Generates a table with original makespan, refined makespan, improvement, and runtime.
"""

import os
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


def compute_original_makespan(instance_path):
    """Compute expected makespan for the original precedence (no refinement)."""
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
    # Large problems (50+ activities) need much more time
    if n >= 50:
        time_limit = max(time_limit, 7200)  # At least 2 hours for 50+ activities
    elif n >= 20:
        time_limit = max(time_limit, 3600)  # At least 1 hour for 20+ activities
    
    # Create model
    model, pair_to_info, initial_precedence, unresolved_pair_map, duration_table, prob_table = create_model(
        n, durations, probabilities, precedence
    )
    
    # Solve with optimal exhaustive search
    start_time = time.time()
    try:
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
            "Optimal",  # Use optimal exhaustive search
            "history.csv",
            time_limit=time_limit,
        )
        runtime = time.time() - start_time
        
        if is_infeasible:
            return None, False, runtime, False
        if solution is None or cost is None:
            return None, False, runtime, False
        
        return cost, is_optimal, runtime, True
    except Exception as e:
        runtime = time.time() - start_time
        print(f"    Error during solving: {e}")
        return None, False, runtime, False


def main():
    """Run benchmarks on all problem instances and generate a table."""
    # Find all YAML problem files
    problem_files = []
    # Find all non-empty constraint problems
    for size in ["small", "medium", "large"]:
        for struct_type in ["chain", "parallel", "mixed", "dag"]:
            pattern = f"problems/non_empty/{size}/{struct_type}/*.yaml"
            problem_files.extend(glob.glob(pattern))
    
    problem_files.sort()
    
    print("=" * 100)
    print("KORef Benchmark: Original vs Refined Solutions")
    print("=" * 100)
    print()
    
    results = []
    
    for instance_path in problem_files:
        instance_name = os.path.basename(instance_path)
        print(f"Processing: {instance_name}")
        print(f"  Computing original makespan...")
        
        try:
            # Compute original makespan
            original_makespan = compute_original_makespan(instance_path)
            
            print(f"  Original makespan: {original_makespan:.6f}")
            print(f"  Solving refinement problem (this may take a while)...")
            
            # Solve refinement (with adaptive timeout based on problem size)
            # Timeout will be adjusted in solve_refined based on problem size
            refined_makespan, is_optimal, runtime, success = solve_refined(
                instance_path, time_limit=3600  # Base timeout, adjusted for large problems
            )
            
            if success and refined_makespan is not None:
                improvement = original_makespan - refined_makespan
                improvement_pct = (improvement / original_makespan * 100) if original_makespan > 0 else 0
                
                results.append({
                    'instance': instance_name,
                    'original': original_makespan,
                    'refined': refined_makespan,
                    'improvement': improvement,
                    'improvement_pct': improvement_pct,
                    'runtime': runtime,
                    'optimal': is_optimal,
                    'status': '✓' if is_optimal else '?'
                })
                
                print(f"  Refined makespan: {refined_makespan:.6f}")
                print(f"  Improvement: {improvement:.6f} ({improvement_pct:.2f}%)")
                print(f"  Runtime: {runtime:.2f}s")
                print(f"  Status: {'Optimal' if is_optimal else 'Heuristic'}")
            else:
                results.append({
                    'instance': instance_name,
                    'original': original_makespan,
                    'refined': None,
                    'improvement': None,
                    'improvement_pct': None,
                    'runtime': runtime,
                    'optimal': False,
                    'status': '✗ Failed'
                })
                print(f"  Failed to find solution")
                
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                'instance': instance_name,
                'original': None,
                'refined': None,
                'improvement': None,
                'improvement_pct': None,
                'runtime': None,
                'optimal': False,
                'status': f'✗ Error: {str(e)[:30]}'
            })
        
        print()
    
    # Print summary table
    print("=" * 100)
    print("RESULTS SUMMARY")
    print("=" * 100)
    print()
    
    # Prepare table data for both console and markdown
    table_rows = []
    
    # Table header
    header = f"{'Instance':<25} {'Original':<15} {'Refined':<15} {'Improvement':<15} {'%':<10} {'Runtime (s)':<15} {'Status':<10}"
    separator = "-" * 100
    
    # Replace Unicode characters for console output
    header_console = header.replace('✓', 'OK').replace('✗', 'FAIL')
    print(header_console)
    print(separator)
    
    for r in results:
        instance = r['instance']
        original = f"{r['original']:.6f}" if r['original'] is not None else "N/A"
        refined = f"{r['refined']:.6f}" if r['refined'] is not None else "N/A"
        improvement = f"{r['improvement']:.6f}" if r['improvement'] is not None else "N/A"
        improvement_pct = f"{r['improvement_pct']:.2f}%" if r['improvement_pct'] is not None else "N/A"
        runtime = f"{r['runtime']:.2f}" if r['runtime'] is not None else "N/A"
        status = r['status']
        
        row = f"{instance:<25} {original:<15} {refined:<15} {improvement:<15} {improvement_pct:<10} {runtime:<15} {status:<10}"
        row_console = row.replace('✓', 'OK').replace('✗', 'FAIL')
        print(row_console)
        
        table_rows.append({
            'instance': instance,
            'original': original,
            'refined': refined,
            'improvement': improvement,
            'improvement_pct': improvement_pct,
            'runtime': runtime,
            'status': status
        })
    
    print()
    print("=" * 100)
    
    # Summary statistics
    successful = [r for r in results if r['refined'] is not None]
    if successful:
        avg_improvement = sum(r['improvement_pct'] for r in successful if r['improvement_pct'] is not None) / len(successful)
        total_runtime = sum(r['runtime'] for r in successful if r['runtime'] is not None)
        optimal_count = sum(1 for r in successful if r['optimal'])
        
        print(f"Successfully solved: {len(successful)}/{len(results)}")
        print(f"Optimal solutions: {optimal_count}/{len(successful)}")
        print(f"Average improvement: {avg_improvement:.2f}%")
        print(f"Total runtime: {total_runtime:.2f}s ({total_runtime/60:.2f} minutes)")
        print("=" * 100)
    
    # Save results to CSV (using UTF-8 encoding to handle Unicode characters)
    csv_filename = "benchmark_results.csv"
    print(f"\nSaving results to {csv_filename}...")
    print(f"Total results to save: {len(results)}")
    
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['instance', 'original_makespan', 'refined_makespan', 'improvement', 'improvement_pct', 'runtime_seconds', 'is_optimal', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for r in results:
                # Replace Unicode characters with ASCII equivalents for CSV compatibility
                status_ascii = r['status'].replace('✓', 'OK').replace('✗', 'FAIL')
                writer.writerow({
                    'instance': r['instance'],
                    'original_makespan': r['original'] if r['original'] is not None else '',
                    'refined_makespan': r['refined'] if r['refined'] is not None else '',
                    'improvement': r['improvement'] if r['improvement'] is not None else '',
                    'improvement_pct': r['improvement_pct'] if r['improvement_pct'] is not None else '',
                    'runtime_seconds': r['runtime'] if r['runtime'] is not None else '',
                    'is_optimal': r['optimal'],
                    'status': status_ascii
                })
        
        print(f"Successfully saved {len(results)} results to {csv_filename}")
    except Exception as e:
        print(f"ERROR saving CSV: {e}")
        import traceback
        traceback.print_exc()
    
    # Also save results to markdown file
    md_filename = "benchmark_results.md"
    print(f"\nSaving results to {md_filename}...")
    try:
        with open(md_filename, 'w', encoding='utf-8') as mdfile:
            mdfile.write("# KORef Benchmark Results\n\n")
            mdfile.write("Comparison of original vs refined solutions for all problem instances.\n\n")
            mdfile.write("## Results Summary\n\n")
            
            # Markdown table
            mdfile.write("| Instance | Original Makespan | Refined Makespan | Improvement | Improvement % | Runtime (s) | Status |\n")
            mdfile.write("|----------|-------------------|------------------|-------------|--------------|-------------|--------|\n")
            
            for r in table_rows:
                instance = r['instance']
                original = r['original']
                refined = r['refined']
                improvement = r['improvement']
                improvement_pct = r['improvement_pct']
                runtime = r['runtime']
                status = r['status']
                
                mdfile.write(f"| {instance} | {original} | {refined} | {improvement} | {improvement_pct} | {runtime} | {status} |\n")
            
            # Summary statistics
            successful = [r for r in results if r['refined'] is not None]
            if successful:
                avg_improvement = sum(r['improvement_pct'] for r in successful if r['improvement_pct'] is not None) / len(successful)
                total_runtime = sum(r['runtime'] for r in successful if r['runtime'] is not None)
                optimal_count = sum(1 for r in successful if r['optimal'])
                
                mdfile.write("\n## Summary Statistics\n\n")
                mdfile.write(f"- **Successfully solved**: {len(successful)}/{len(results)}\n")
                mdfile.write(f"- **Optimal solutions**: {optimal_count}/{len(successful)}\n")
                mdfile.write(f"- **Average improvement**: {avg_improvement:.2f}%\n")
                mdfile.write(f"- **Total runtime**: {total_runtime:.2f}s ({total_runtime/60:.2f} minutes)\n")
            
            mdfile.write("\n## Notes\n\n")
            mdfile.write("- All problems use knockout-heavy probabilities (0.3-0.8 range)\n")
            mdfile.write("- Original makespan: Expected makespan of the original precedence\n")
            mdfile.write("- Refined makespan: Optimal expected makespan after refinement\n")
            mdfile.write("- Improvement: Difference between original and refined makespan\n")
            mdfile.write("- Status: OK = Optimal solution found, FAIL = Failed to find solution\n")
        
        print(f"Results saved to {md_filename}")
    except Exception as e:
        print(f"ERROR saving markdown: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

