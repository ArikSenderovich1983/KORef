#!/usr/bin/env python3
"""
Compute canonical expected makespan for all problem instances.
Updates YAML files with the canonical makespan value.
"""

import os
import yaml
import read_koref
from koref_utils import (
    compute_earliest_start_schedule,
    compute_expected_makespan,
)


def compute_canonical_makespan(yaml_file):
    """
    Compute the canonical expected makespan for a problem instance.
    Uses the initial precedence (no refinement).
    """
    name, n, durations, probabilities, precedence = read_koref.read(yaml_file)
    
    activities = list(range(n))
    
    # Compute canonical earliest-start schedule
    schedule = compute_earliest_start_schedule(activities, precedence, durations)
    
    # Compute expected makespan
    expected_makespan = compute_expected_makespan(
        activities, schedule, durations, probabilities
    )
    
    return expected_makespan, schedule


def update_yaml_with_makespan(yaml_file, expected_makespan, schedule):
    """
    Update YAML file to include canonical expected makespan.
    """
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # Add canonical makespan to metadata
    if 'metadata' not in data:
        data['metadata'] = {}
    
    data['metadata']['canonical_expected_makespan'] = round(expected_makespan, 6)
    data['metadata']['canonical_schedule'] = {str(k): float(v) for k, v in schedule.items()}
    
    # Write back to file
    with open(yaml_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return data


def process_all_problems():
    """
    Process all YAML files in the problems directory.
    """
    problems_dir = "problems"
    
    # Find all YAML files
    yaml_files = []
    for root, dirs, files in os.walk(problems_dir):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                yaml_files.append(os.path.join(root, file))
    
    yaml_files.sort()
    
    print("=" * 80)
    print("COMPUTING CANONICAL EXPECTED MAKESPANS")
    print("=" * 80)
    print()
    
    results = []
    
    for yaml_file in yaml_files:
        try:
            print(f"Processing: {yaml_file}")
            
            # Compute canonical makespan
            expected_makespan, schedule = compute_canonical_makespan(yaml_file)
            
            # Update YAML file
            update_yaml_with_makespan(yaml_file, expected_makespan, schedule)
            
            print(f"  ✓ Canonical expected makespan: {expected_makespan:.6f}")
            print(f"  ✓ Schedule: {schedule}")
            print()
            
            results.append({
                'file': yaml_file,
                'makespan': expected_makespan,
                'schedule': schedule
            })
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    for result in results:
        print(f"{result['file']:50} {result['makespan']:10.6f}")
    
    print()
    print(f"Total problems processed: {len(results)}")
    print("All YAML files updated successfully!")


if __name__ == "__main__":
    process_all_problems()
