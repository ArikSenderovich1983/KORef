#!/usr/bin/env python3
"""
Script to run DIDP solver on all problem instances and collect results.
"""

import os
import subprocess
import time
import yaml
from read_koref import read_yaml
from koref_utils import (
    compute_earliest_start_schedule,
    compute_expected_makespan,
)


def get_initial_makespan(yaml_file):
    """
    Compute the initial expected makespan (without any refinement).
    This uses only the original precedence constraints.
    """
    name, n, durations, probabilities, precedence = read_yaml(yaml_file)
    activities = list(range(n))
    
    # Compute schedule using initial precedence only
    schedule = compute_earliest_start_schedule(activities, precedence, durations)
    
    # Compute expected makespan
    initial_makespan = compute_expected_makespan(
        activities, schedule, durations, probabilities
    )
    
    return initial_makespan


def run_didp(yaml_file, timeout=300):
    """
    Run DIDP solver on a problem instance.
    Returns the optimal expected makespan or None if failed.
    """
    print(f"\nRunning DIDP on {yaml_file}...")
    
    try:
        # Run the solver
        result = subprocess.run(
            ['python3', 'koref_domain.py', yaml_file, '--config', 'Optimal', '--time-out', str(timeout)],
            capture_output=True,
            text=True,
            timeout=timeout + 30  # Add buffer to subprocess timeout
        )
        
        # Parse output to extract expected makespan
        output = result.stdout
        
        # Look for "expected makespan: " (lowercase check for case insensitivity)
        for line in output.split('\n'):
            if 'expected makespan:' in line.lower() and 'optimal' not in line.lower():
                # Extract the number
                parts = line.split(':')
                if len(parts) >= 2:
                    try:
                        makespan = float(parts[-1].strip())
                        return makespan
                    except ValueError:
                        continue
        
        # If we can't find the makespan, check if infeasible or error
        if 'infeasible' in output.lower():
            return None
        
        # Return None if we couldn't extract the value
        print(f"Warning: Could not extract makespan from output")
        return None
        
    except subprocess.TimeoutExpired:
        print(f"Timeout expired for {yaml_file}")
        return None
    except Exception as e:
        print(f"Error running DIDP on {yaml_file}: {e}")
        return None


def collect_all_results():
    """
    Collect results for all problem instances.
    """
    problem_dirs = ['problems/small', 'problems/medium', 'problems/large']
    results = []
    
    for problem_dir in problem_dirs:
        if not os.path.exists(problem_dir):
            continue
        
        category = os.path.basename(problem_dir)
        
        # Get all YAML files
        yaml_files = sorted([f for f in os.listdir(problem_dir) if f.endswith('.yaml')])
        
        for yaml_file in yaml_files:
            full_path = os.path.join(problem_dir, yaml_file)
            problem_name = yaml_file.replace('.yaml', '')
            
            print(f"\n{'='*60}")
            print(f"Processing: {category}/{yaml_file}")
            print(f"{'='*60}")
            
            # Get initial makespan
            try:
                initial_makespan = get_initial_makespan(full_path)
                print(f"Initial makespan (no refinement): {initial_makespan:.6f}")
            except Exception as e:
                print(f"Error computing initial makespan: {e}")
                initial_makespan = None
            
            # Run DIDP
            start_time = time.time()
            
            # Adjust timeout based on problem size
            if category == 'small':
                timeout = 60
            elif category == 'medium':
                timeout = 300
            else:  # large
                timeout = 600
            
            optimal_makespan = run_didp(full_path, timeout=timeout)
            solve_time = time.time() - start_time
            
            if optimal_makespan is not None:
                print(f"Optimal makespan: {optimal_makespan:.6f}")
                print(f"Solve time: {solve_time:.2f}s")
                
                if initial_makespan is not None:
                    improvement = initial_makespan - optimal_makespan
                    improvement_pct = (improvement / initial_makespan) * 100
                    print(f"Improvement: {improvement:.6f} ({improvement_pct:.2f}%)")
            
            results.append({
                'category': category,
                'problem': problem_name,
                'initial_makespan': initial_makespan,
                'optimal_makespan': optimal_makespan,
                'solve_time': solve_time,
            })
    
    return results


def generate_markdown_table(results):
    """
    Generate a markdown table with the results.
    """
    md = "# DIDP KORef Results Comparison\n\n"
    md += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md += "This report compares the initial expected makespan (no refinement) vs. optimal expected makespan (with DIDP refinement) for all problem instances.\n\n"
    md += "## Summary\n\n"
    md += f"Total problems: {len(results)}\n"
    
    successful = sum(1 for r in results if r['optimal_makespan'] is not None)
    md += f"Successfully solved: {successful}/{len(results)}\n\n"
    
    md += "## Results by Category\n\n"
    
    # Group by category
    categories = {}
    for result in results:
        cat = result['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result)
    
    for category in ['small', 'medium', 'large']:
        if category not in categories:
            continue
        
        md += f"\n### {category.capitalize()} Problems\n\n"
        md += "| Problem | Initial Makespan | Optimal Makespan | Improvement | Improvement % | Runtime (s) |\n"
        md += "|---------|-----------------|------------------|-------------|---------------|-------------|\n"
        
        for result in categories[category]:
            problem = result['problem']
            initial = result['initial_makespan']
            optimal = result['optimal_makespan']
            solve_time = result['solve_time']
            
            if initial is not None and optimal is not None:
                improvement = initial - optimal
                improvement_pct = (improvement / initial) * 100
                md += f"| {problem} | {initial:.6f} | {optimal:.6f} | {improvement:.6f} | {improvement_pct:.2f}% | {solve_time:.3f} |\n"
            elif initial is not None and optimal is None:
                md += f"| {problem} | {initial:.6f} | *timeout/error* | - | - | {solve_time:.3f} |\n"
            elif initial is None and optimal is not None:
                md += f"| {problem} | *error* | {optimal:.6f} | - | - | {solve_time:.3f} |\n"
            else:
                md += f"| {problem} | *error* | *timeout/error* | - | - | {solve_time:.3f} |\n"
    
    # Add overall table
    md += "\n## All Results (Complete Comparison Table)\n\n"
    md += "| Category | Problem | Initial Makespan | Optimal Makespan | Improvement | Improvement % | Runtime (s) |\n"
    md += "|----------|---------|-----------------|------------------|-------------|---------------|-------------|\n"
    
    for result in results:
        category = result['category']
        problem = result['problem']
        initial = result['initial_makespan']
        optimal = result['optimal_makespan']
        solve_time = result['solve_time']
        
        if initial is not None and optimal is not None:
            improvement = initial - optimal
            improvement_pct = (improvement / initial) * 100
            md += f"| {category} | {problem} | {initial:.6f} | {optimal:.6f} | {improvement:.6f} | {improvement_pct:.2f}% | {solve_time:.3f} |\n"
        elif initial is not None and optimal is None:
            md += f"| {category} | {problem} | {initial:.6f} | *timeout/error* | - | - | {solve_time:.3f} |\n"
        elif initial is None and optimal is not None:
            md += f"| {category} | {problem} | *error* | {optimal:.6f} | - | - | {solve_time:.3f} |\n"
        else:
            md += f"| {category} | {problem} | *error* | *timeout/error* | - | - | {solve_time:.3f} |\n"
    
    return md


if __name__ == '__main__':
    print("Starting DIDP evaluation on all problem instances...")
    print("This may take some time...\n")
    
    results = collect_all_results()
    
    print("\n" + "="*60)
    print("Generating report...")
    print("="*60)
    
    markdown_report = generate_markdown_table(results)
    
    # Write to file
    output_file = 'DIDP_RESULTS.md'
    with open(output_file, 'w') as f:
        f.write(markdown_report)
    
    print(f"\nReport saved to: {output_file}")
    print("\nDone!")
