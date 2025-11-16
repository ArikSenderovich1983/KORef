#!/usr/bin/env python3
"""
Benchmark script for empty constraint problems.
Tests refinement from completely empty precedence constraints.
"""

import os
import sys
import time
import yaml
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from koref_domain import solve, create_model
from koref_utils import compute_expected_makespan, compute_earliest_start_schedule
from read_koref import read

def find_all_empty_constraint_problems():
    """Find all empty constraint problem files."""
    base_dir = Path("problems/empty")
    problems = []
    
    for size_category in ['small', 'medium', 'large']:
        category_dir = base_dir / size_category
        if category_dir.exists():
            for yaml_file in sorted(category_dir.glob("*.yaml")):
                problems.append({
                    'path': str(yaml_file),
                    'category': size_category,
                    'name': yaml_file.stem
                })
    
    return problems

def solve_empty_constraint_problem(problem_path, time_limit=None):
    """Solve a single empty constraint problem."""
    print(f"\n{'='*80}")
    print(f"Testing: {problem_path}")
    print(f"{'='*80}")
    
    try:
        # Read problem
        name, n, durations, probabilities, precedence = read(problem_path)
        
        print(f"  Activities: {n}")
        print(f"  Precedence constraints: {len(precedence)} (should be 0 for empty)")
        print(f"  Unresolved pairs: {n * (n - 1) // 2}")
        
        # Compute original makespan (with empty precedence)
        print("\nComputing original makespan (empty precedence)...")
        activities = list(range(n))
        schedule = compute_earliest_start_schedule(activities, precedence, durations)
        original_makespan = compute_expected_makespan(activities, schedule, durations, probabilities)
        print(f"  Original makespan: {original_makespan:.6f}")
        
        # Solve refinement
        print("\nSolving refinement problem...")
        start_time = time.time()
        
        # Create model
        model, pair_to_info, initial_precedence, unresolved_pair_map, duration_table, prob_table = create_model(
            n, durations, probabilities, precedence
        )
        
        # Solve with optimal exhaustive search
        history = []  # Empty history for empty constraint problems
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
            "Optimal",
            history,
            time_limit=time_limit
        )
        
        runtime = time.time() - start_time
        
        if refined_precedence is None:
            print("  FAILED: No solution found")
            return {
                'problem': name,
                'category': Path(problem_path).parent.name,
                'n_activities': n,
                'original_makespan': original_makespan,
                'refined_makespan': None,
                'improvement': None,
                'improvement_pct': None,
                'runtime': runtime,
                'status': 'FAIL',
                'optimal': False,
                'timeout': is_timeout
            }
        
        improvement = original_makespan - refined_makespan
        improvement_pct = (improvement / original_makespan * 100) if original_makespan > 0 else 0
        
        print(f"\nResults:")
        print(f"  Original makespan: {original_makespan:.6f}")
        print(f"  Refined makespan:  {refined_makespan:.6f}")
        print(f"  Improvement:       {improvement:.6f} ({improvement_pct:.2f}%)")
        print(f"  Runtime:           {runtime:.2f}s")
        print(f"  Status:            {'Optimal' if is_optimal else 'Heuristic'}")
        print(f"  Constraints added: {len(refined_precedence) - len(precedence)}")
        
        return {
            'problem': name,
            'category': Path(problem_path).parent.name,
            'n_activities': n,
            'original_makespan': original_makespan,
            'refined_makespan': refined_makespan,
            'improvement': improvement,
            'improvement_pct': improvement_pct,
            'runtime': runtime,
            'status': 'OK',
            'optimal': is_optimal,
            'timeout': is_timeout,
            'constraints_added': len(refined_precedence) - len(precedence)
        }
        
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            'problem': Path(problem_path).stem,
            'category': Path(problem_path).parent.name,
            'n_activities': None,
            'original_makespan': None,
            'refined_makespan': None,
            'improvement': None,
            'improvement_pct': None,
            'runtime': None,
            'status': 'ERROR',
            'optimal': False,
            'timeout': False,
            'error': str(e)
        }

def main():
    """Run benchmark on all empty constraint problems."""
    print("=" * 80)
    print("KORef Empty Constraint Benchmark")
    print("=" * 80)
    print("\nThis benchmark tests refinement from EMPTY precedence constraints.")
    print("All precedence constraints will be added by the refinement process.")
    print("=" * 80)
    
    # Find all problems
    problems = find_all_empty_constraint_problems()
    
    if not problems:
        print("\nERROR: No empty constraint problems found!")
        print("Run generate_empty_constraint_problems.py first.")
        return
    
    print(f"\nFound {len(problems)} empty constraint problems")
    print(f"Categories: small, medium, large")
    
    # Use 30 seconds maximum for all problems
    def get_time_limit(n):
        return 30  # 30 seconds maximum per problem
    
    # Run benchmarks
    results = []
    start_time = time.time()
    
    for i, problem_info in enumerate(problems, 1):
        print(f"\n[{i}/{len(problems)}] Processing {problem_info['name']}...")
        
        n_activities = None
        # Try to read n_activities from file
        try:
            name, n, _, _, _ = read(problem_info['path'])
            n_activities = n
        except:
            pass
        
        time_limit = get_time_limit(n_activities) if n_activities else None
        
        result = solve_empty_constraint_problem(problem_info['path'], time_limit=time_limit)
        results.append(result)
    
    total_runtime = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    
    # Sort results by category and name
    results.sort(key=lambda x: (x['category'], x['problem']))
    
    # Print table
    print(f"\n{'Instance':<40} {'Category':<10} {'N':<4} {'Original':<12} {'Refined':<12} {'Improvement':<12} {'%':<8} {'Runtime':<10} {'Status':<8}")
    print("-" * 120)
    
    successful = 0
    optimal = 0
    total_improvement = 0
    improvement_count = 0
    
    for r in results:
        if r['status'] == 'OK':
            successful += 1
            if r['optimal']:
                optimal += 1
            if r['improvement'] is not None and r['improvement'] > 0:
                total_improvement += r['improvement_pct']
                improvement_count += 1
        
        n_str = str(r['n_activities']) if r['n_activities'] else '?'
        orig_str = f"{r['original_makespan']:.6f}" if r['original_makespan'] is not None else 'N/A'
        ref_str = f"{r['refined_makespan']:.6f}" if r['refined_makespan'] is not None else 'N/A'
        imp_str = f"{r['improvement']:.6f}" if r['improvement'] is not None else 'N/A'
        pct_str = f"{r['improvement_pct']:.2f}%" if r['improvement_pct'] is not None else 'N/A'
        rt_str = f"{r['runtime']:.2f}s" if r['runtime'] is not None else 'N/A'
        status_str = r['status']
        
        print(f"{r['problem']:<40} {r['category']:<10} {n_str:<4} {orig_str:<12} {ref_str:<12} {imp_str:<12} {pct_str:<8} {rt_str:<10} {status_str:<8}")
    
    print("=" * 120)
    print(f"\nSuccessfully solved: {successful}/{len(results)}")
    print(f"Optimal solutions: {optimal}/{successful}" if successful > 0 else "Optimal solutions: 0/0")
    if improvement_count > 0:
        avg_improvement = total_improvement / improvement_count
        print(f"Average improvement (for improved problems): {avg_improvement:.2f}%")
    print(f"Total runtime: {total_runtime:.2f}s ({total_runtime/60:.2f} minutes)")
    
    # Save to CSV
    import csv
    csv_filename = "benchmark_empty_constraints.csv"
    print(f"\nSaving results to {csv_filename}...")
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Instance', 'Category', 'N_Activities', 'Original_Makespan', 'Refined_Makespan',
            'Improvement', 'Improvement_Pct', 'Runtime_s', 'Status', 'Optimal', 'Timeout',
            'Constraints_Added'
        ])
        
        for r in results:
            writer.writerow([
                r['problem'],
                r['category'],
                r['n_activities'] if r['n_activities'] else '',
                r['original_makespan'] if r['original_makespan'] is not None else '',
                r['refined_makespan'] if r['refined_makespan'] is not None else '',
                r['improvement'] if r['improvement'] is not None else '',
                r['improvement_pct'] if r['improvement_pct'] is not None else '',
                r['runtime'] if r['runtime'] is not None else '',
                r['status'],
                'Yes' if r['optimal'] else 'No',
                'Yes' if r.get('timeout', False) else 'No',
                r.get('constraints_added', '')
            ])
    
    print(f"Saved {len(results)} results to {csv_filename}")
    
    # Save to Markdown
    md_filename = "benchmark_empty.md"
    print(f"Saving results to {md_filename}...")
    
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write("# KORef Empty Constraint Benchmark Results\n\n")
        f.write("Comparison of original (empty precedence) vs refined solutions.\n\n")
        f.write("## Results Summary\n\n")
        f.write("| Instance | Category | N | Original Makespan | Refined Makespan | ")
        f.write("Improvement | Improvement % | Runtime (s) | Status |\n")
        f.write("|----------|----------|---|-------------------|------------------|")
        f.write("-------------|--------------|-------------|--------|\n")
        
        for r in results:
            n_str = str(r['n_activities']) if r['n_activities'] else '?'
            orig_str = f"{r['original_makespan']:.6f}" if r['original_makespan'] is not None else 'N/A'
            ref_str = f"{r['refined_makespan']:.6f}" if r['refined_makespan'] is not None else 'N/A'
            imp_str = f"{r['improvement']:.6f}" if r['improvement'] is not None else 'N/A'
            pct_str = f"{r['improvement_pct']:.2f}%" if r['improvement_pct'] is not None else 'N/A'
            rt_str = f"{r['runtime']:.2f}" if r['runtime'] is not None else 'N/A'
            status_str = '✓' if r['status'] == 'OK' else '✗'
            
            f.write(f"| {r['problem']} | {r['category']} | {n_str} | {orig_str} | {ref_str} | ")
            f.write(f"{imp_str} | {pct_str} | {rt_str} | {status_str} |\n")
        
        f.write("\n## Summary Statistics\n\n")
        f.write(f"- **Successfully solved**: {successful}/{len(results)}\n")
        f.write(f"- **Optimal solutions**: {optimal}/{successful}\n" if successful > 0 else "- **Optimal solutions**: 0/0\n")
        if improvement_count > 0:
            avg_improvement = total_improvement / improvement_count
            f.write(f"- **Average improvement** (for improved problems): {avg_improvement:.2f}%\n")
        f.write(f"- **Total runtime**: {total_runtime:.2f}s ({total_runtime/60:.2f} minutes)\n")
        
        f.write("\n## Notes\n\n")
        f.write("- All problems start with EMPTY precedence constraints\n")
        f.write("- Refinement adds all precedence constraints from scratch\n")
        f.write("- Original makespan: Expected makespan with no precedence constraints\n")
        f.write("- Refined makespan: Optimal expected makespan after adding constraints\n")
        f.write("- Status: ✓ = Optimal solution found, ✗ = Failed to find solution\n")
    
    print(f"Results saved to {md_filename}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
