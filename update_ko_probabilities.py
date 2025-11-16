#!/usr/bin/env python3
"""
Update all problem instances to have knockout-heavy probabilities.
Makes KO probabilities higher to better test the refinement algorithms.
"""

import os
import glob
import yaml

def update_ko_probabilities(filepath, difficulty_level):
    """Update KO probabilities based on difficulty level."""
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    # Define KO probability ranges based on difficulty
    if difficulty_level == 'small':
        min_ko = 0.3
        max_ko = 0.6
    elif difficulty_level == 'medium':
        min_ko = 0.4
        max_ko = 0.7
    else:  # large
        min_ko = 0.5
        max_ko = 0.8
    
    # Update metadata
    if 'metadata' in data:
        data['metadata']['ko_probability_distribution'] = 'high_risk_heavy'
    
    # Update description if present
    if 'description' in data:
        data['description'] = data['description'].replace('low KO', 'high KO').replace('low risk', 'high risk')
        if 'heavy' not in data['description'].lower():
            data['description'] += ' (knockout-heavy)'
    
    # Update activities with higher KO probabilities
    import random
    random.seed(42)  # For reproducibility
    
    updated_count = 0
    for activity in data.get('activities', []):
        # Generate a new KO probability in the range
        new_ko = round(random.uniform(min_ko, max_ko), 2)
        old_ko = activity.get('ko_probability', 0.0)
        activity['ko_probability'] = new_ko
        updated_count += 1
        print(f"  Activity {activity.get('id', '?')}: {old_ko:.2f} -> {new_ko:.2f}")
    
    # Write back
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return updated_count

def main():
    """Update all YAML problem files."""
    print("Updating problem instances to be knockout-heavy...")
    print("=" * 60)
    
    problem_files = []
    for pattern in ["problems/small/*.yaml", "problems/medium/*.yaml", "problems/large/*.yaml"]:
        problem_files.extend(glob.glob(pattern))
    
    problem_files.sort()
    
    for filepath in problem_files:
        # Determine difficulty level from path (use backslash for Windows paths)
        filepath_normalized = filepath.replace('\\', '/')
        if '/small/' in filepath_normalized:
            difficulty = 'small'
        elif '/medium/' in filepath_normalized:
            difficulty = 'medium'
        elif '/large/' in filepath_normalized:
            difficulty = 'large'
        else:
            difficulty = 'small'  # Default
        
        filename = os.path.basename(filepath)
        print(f"\n{filename} ({difficulty}):")
        
        try:
            count = update_ko_probabilities(filepath, difficulty)
            print(f"  Updated {count} activities")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("Done! All problem instances updated to be knockout-heavy.")

if __name__ == "__main__":
    main()

