#!/usr/bin/env python3
"""
Generate large problem instances (50 activities) with various structures.
"""

import yaml
import random
import os

def generate_chain_problem(n, name_suffix=""):
    """Generate a chain structure: 0 -> 1 -> 2 -> ... -> n-1"""
    activities = []
    precedence = []
    
    for i in range(n):
        activities.append({
            'id': i,
            'name': f"Step_{i:02d}",
            'duration': round(random.uniform(2.0, 8.0), 1),
            'ko_probability': round(random.uniform(0.5, 0.8), 2)
        })
        if i > 0:
            precedence.append([i-1, i])
    
    return {
        'name': f'chain_{n}{name_suffix}',
        'description': f'Chain structure with {n} activities (knockout-heavy)',
        'category': 'chain',
        'difficulty': 'large',
        'metadata': {
            'n_activities': n,
            'n_precedence': len(precedence),
            'n_unresolved_pairs': n * (n - 1) // 2 - len(precedence),
            'graph_structure': 'chain',
            'duration_distribution': 'varied',
            'ko_probability_distribution': 'high_risk_heavy'
        },
        'activities': activities,
        'precedence': precedence
    }

def generate_parallel_problem(n, name_suffix=""):
    """Generate a parallel structure: all activities independent (no precedence)"""
    activities = []
    
    for i in range(n):
        activities.append({
            'id': i,
            'name': f"Task_{i:02d}",
            'duration': round(random.uniform(2.0, 8.0), 1),
            'ko_probability': round(random.uniform(0.5, 0.8), 2)
        })
    
    return {
        'name': f'parallel_{n}{name_suffix}',
        'description': f'Parallel structure with {n} independent activities (knockout-heavy)',
        'category': 'parallel',
        'difficulty': 'large',
        'metadata': {
            'n_activities': n,
            'n_precedence': 0,
            'n_unresolved_pairs': n * (n - 1) // 2,
            'graph_structure': 'parallel',
            'duration_distribution': 'varied',
            'ko_probability_distribution': 'high_risk_heavy'
        },
        'activities': activities,
        'precedence': []
    }

def generate_mixed_problem(n, name_suffix=""):
    """Generate a mixed structure: some chains, some parallel, some independent"""
    activities = []
    precedence = []
    
    # Create activities
    for i in range(n):
        activities.append({
            'id': i,
            'name': f"Activity_{i:02d}",
            'duration': round(random.uniform(2.0, 8.0), 1),
            'ko_probability': round(random.uniform(0.5, 0.8), 2)
        })
    
    # Create some chains (groups of 3-5 activities)
    used = set()
    chain_id = 0
    i = 0
    while i < n - 2:
        chain_size = random.randint(3, min(5, n - i))
        if i + chain_size > n:
            break
        
        # Create a chain
        for j in range(chain_size - 1):
            precedence.append([i + j, i + j + 1])
            used.add(i + j)
            used.add(i + j + 1)
        
        i += chain_size
    
    # Add some random precedence constraints between unused activities
    unused = [a for a in range(n) if a not in used]
    if len(unused) > 1:
        num_random = min(len(unused) // 2, 10)
        for _ in range(num_random):
            a, b = random.sample(unused, 2)
            if a < b:
                precedence.append([a, b])
    
    return {
        'name': f'mixed_{n}{name_suffix}',
        'description': f'Mixed structure with {n} activities: chains and parallel (knockout-heavy)',
        'category': 'mixed',
        'difficulty': 'large',
        'metadata': {
            'n_activities': n,
            'n_precedence': len(precedence),
            'n_unresolved_pairs': n * (n - 1) // 2 - len(precedence),
            'graph_structure': 'mixed',
            'duration_distribution': 'varied',
            'ko_probability_distribution': 'high_risk_heavy'
        },
        'activities': activities,
        'precedence': precedence
    }

def generate_dag_problem(n, name_suffix=""):
    """Generate a DAG structure: layered graph"""
    activities = []
    precedence = []
    
    # Create activities
    for i in range(n):
        activities.append({
            'id': i,
            'name': f"Node_{i:02d}",
            'duration': round(random.uniform(2.0, 8.0), 1),
            'ko_probability': round(random.uniform(0.5, 0.8), 2)
        })
    
    # Create layers
    num_layers = max(3, n // 15)
    layer_size = n // num_layers
    layers = []
    
    for layer_idx in range(num_layers):
        start = layer_idx * layer_size
        end = start + layer_size if layer_idx < num_layers - 1 else n
        layers.append(list(range(start, end)))
    
    # Add precedence: each layer connects to next layer
    for layer_idx in range(len(layers) - 1):
        current_layer = layers[layer_idx]
        next_layer = layers[layer_idx + 1]
        
        # Each node in current layer connects to 2-3 nodes in next layer
        for node in current_layer:
            targets = random.sample(next_layer, min(random.randint(2, 3), len(next_layer)))
            for target in targets:
                precedence.append([node, target])
    
    return {
        'name': f'dag_{n}{name_suffix}',
        'description': f'DAG structure with {n} activities in {num_layers} layers (knockout-heavy)',
        'category': 'dag',
        'difficulty': 'large',
        'metadata': {
            'n_activities': n,
            'n_precedence': len(precedence),
            'n_unresolved_pairs': n * (n - 1) // 2 - len(precedence),
            'graph_structure': 'dag',
            'duration_distribution': 'varied',
            'ko_probability_distribution': 'high_risk_heavy'
        },
        'activities': activities,
        'precedence': precedence
    }

def main():
    """Generate large problem instances."""
    random.seed(42)  # For reproducibility
    
    # Create large directory if it doesn't exist
    large_dir = "problems/large"
    os.makedirs(large_dir, exist_ok=True)
    
    n = 50  # Target size
    
    print(f"Generating large problem instances with {n} activities...")
    print("=" * 60)
    
    problems = [
        ("chain", generate_chain_problem(n)),
        ("parallel", generate_parallel_problem(n)),
        ("mixed", generate_mixed_problem(n)),
        ("dag", generate_dag_problem(n)),
    ]
    
    for problem_type, problem_data in problems:
        filename = f"{large_dir}/{problem_data['name']}.yaml"
        
        print(f"\nGenerating {problem_type} problem: {filename}")
        print(f"  Activities: {problem_data['metadata']['n_activities']}")
        print(f"  Precedence constraints: {problem_data['metadata']['n_precedence']}")
        print(f"  Unresolved pairs: {problem_data['metadata']['n_unresolved_pairs']}")
        
        with open(filename, 'w') as f:
            yaml.dump(problem_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        print(f"  Saved to {filename}")
    
    print("\n" + "=" * 60)
    print(f"Generated {len(problems)} large problem instances with {n} activities each")
    print("\nNote: These problems will take significant time to solve optimally.")
    print("Consider using time limits or heuristic solvers for very large instances.")

if __name__ == "__main__":
    main()

