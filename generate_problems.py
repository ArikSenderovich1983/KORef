#!/usr/bin/env python3
"""
Unified problem generator for KORef problems.
Generates problems with different characteristics:
- Empty/non-empty constraints
- High risk/non-high risk
- Different constraint types (chain, parallel, mixed, dag)
- Different sizes (small, medium, large)
"""

import os
import random
import yaml
from pathlib import Path
from typing import List, Tuple, Dict

# Import makespan computation functions
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from koref_utils import (
    compute_earliest_start_schedule,
    compute_expected_makespan,
)


def generate_durations(n: int, seed: int = None) -> List[float]:
    """Generate random durations for n activities."""
    if seed is not None:
        random.seed(seed)
    return [round(random.uniform(2.0, 8.0), 1) for _ in range(n)]


def generate_probabilities(n: int, risk_level: str, seed: int = None) -> List[float]:
    """Generate KO probabilities based on risk level."""
    if seed is not None:
        random.seed(seed)
    
    if risk_level == "high":
        # High risk: 0.7-0.9
        return [round(random.uniform(0.7, 0.9), 2) for _ in range(n)]
    elif risk_level == "very_high":
        # Very high risk: 0.75-0.95
        return [round(random.uniform(0.75, 0.95), 2) for _ in range(n)]
    elif risk_level == "medium":
        # Medium risk: 0.3-0.5
        return [round(random.uniform(0.3, 0.5), 2) for _ in range(n)]
    else:  # low or non-high
        # Low/non-high risk: 0.1-0.3
        return [round(random.uniform(0.1, 0.3), 2) for _ in range(n)]


def generate_chain_precedence(n: int) -> List[List[int]]:
    """Generate chain structure: 0->1->2->...->n-1"""
    precedence = []
    for i in range(n - 1):
        precedence.append([i, i + 1])
    return precedence


def generate_parallel_precedence(n: int) -> List[List[int]]:
    """Generate parallel structure: no precedence constraints"""
    return []


def generate_mixed_precedence(n: int, seed: int = None) -> List[List[int]]:
    """Generate mixed structure: some common predecessors, some chains"""
    if seed is not None:
        random.seed(seed)
    
    precedence = []
    # Create a few common predecessors
    if n >= 4:
        # First activity precedes multiple activities
        for i in range(1, min(3, n)):
            precedence.append([0, i])
        
        # Then create some chains
        if n >= 6:
            for i in range(2, min(5, n - 1)):
                precedence.append([i, i + 1])
    
    return precedence


def generate_dag_precedence(n: int, seed: int = None) -> List[List[int]]:
    """Generate DAG structure: layered graph with branching"""
    if seed is not None:
        random.seed(seed)
    
    precedence = []
    
    # Create layers
    if n <= 5:
        # Small DAG: 2-3 layers
        layers = [[0], [1, 2], list(range(3, n))]
    elif n <= 10:
        # Medium DAG: 3-4 layers
        layer1_size = max(2, n // 4)
        layer2_size = max(2, n // 3)
        layers = [
            list(range(layer1_size)),
            list(range(layer1_size, layer1_size + layer2_size)),
            list(range(layer1_size + layer2_size, n))
        ]
    else:
        # Large DAG: 4-5 layers
        layer1_size = max(2, n // 5)
        layer2_size = max(3, n // 4)
        layer3_size = max(3, n // 3)
        layers = [
            list(range(layer1_size)),
            list(range(layer1_size, layer1_size + layer2_size)),
            list(range(layer1_size + layer2_size, layer1_size + layer2_size + layer3_size)),
            list(range(layer1_size + layer2_size + layer3_size, n))
        ]
    
    # Connect layers
    for layer_idx in range(len(layers) - 1):
        current_layer = layers[layer_idx]
        next_layer = layers[layer_idx + 1]
        
        # Each node in current layer connects to 1-3 nodes in next layer
        for node in current_layer:
            # Randomly select 1-3 targets from next layer
            num_targets = min(random.randint(1, 3), len(next_layer))
            targets = random.sample(next_layer, num_targets)
            for target in targets:
                precedence.append([node, target])
    
    return precedence


def generate_problem(
    n: int,
    constraint_type: str,  # "empty" or "non_empty"
    structure: str,  # "chain", "parallel", "mixed", "dag" (only for non_empty)
    risk_level: str,  # "high", "very_high", "medium", "low"
    seed: int = None
) -> Dict:
    """Generate a single problem instance."""
    if seed is not None:
        random.seed(seed)
    
    # Generate activities
    durations = generate_durations(n, seed)
    probabilities = generate_probabilities(n, risk_level, seed)
    
    activities = []
    for i in range(n):
        activities.append({
            'id': i,
            'name': f'Activity_{i:02d}',
            'duration': durations[i],
            'ko_probability': probabilities[i]
        })
    
    # Generate precedence
    if constraint_type == "empty":
        precedence = []
        structure_label = "empty"
    else:  # non_empty
        if structure == "chain":
            precedence = generate_chain_precedence(n)
        elif structure == "parallel":
            precedence = generate_parallel_precedence(n)
        elif structure == "mixed":
            precedence = generate_mixed_precedence(n, seed)
        elif structure == "dag":
            precedence = generate_dag_precedence(n, seed)
        else:
            raise ValueError(f"Unknown structure: {structure}")
        structure_label = structure
    
    # Determine size category
    if n <= 5:
        size = "small"
    elif n <= 10:
        size = "medium"
    elif n <= 15:
        size = "large"
    else:
        size = "very_large"
    
    # Convert precedence list to dict format for makespan computation
    precedence_dict = {}
    for constraint in precedence:
        if isinstance(constraint, list) and len(constraint) == 2:
            a, b = constraint[0], constraint[1]
            precedence_dict[(a, b)] = True
    
    # Compute original expected makespan
    activities_list = list(range(n))
    schedule = compute_earliest_start_schedule(activities_list, precedence_dict, durations)
    original_makespan = compute_expected_makespan(activities_list, schedule, durations, probabilities)
    
    # Build problem data
    problem = {
        'name': f'{structure_label}_{n}_{risk_level}',
        'description': f'{structure_label.capitalize()} structure with {n} activities, {risk_level} risk',
        'category': structure_label,
        'difficulty': size,
        'risk_level': risk_level,
        'metadata': {
            'n_activities': n,
            'n_precedence': len(precedence),
            'n_unresolved_pairs': (n * (n - 1) // 2) - len(precedence),
            'graph_structure': structure_label,
            'duration_distribution': 'varied',
            'ko_probability_distribution': risk_level,
            'precedence_type': constraint_type,
            'original_expected_makespan': round(original_makespan, 6)
        },
        'activities': activities,
        'precedence': precedence
    }
    
    return problem


def save_problem(problem: Dict, output_path: Path):
    """Save problem to YAML file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        yaml.dump(problem, f, default_flow_style=False, sort_keys=False)


def generate_all_problems(
    base_dir: str = "problems",
    sizes: List[Tuple[int, int]] = None,  # List of (min_n, max_n) tuples
    constraint_types: List[str] = None,
    structures: List[str] = None,
    risk_levels: List[str] = None,
    instances_per_config: int = 1,
    seed: int = 42
):
    """
    Generate all problem instances.
    
    Args:
        base_dir: Base directory for problems
        sizes: List of (min_n, max_n) tuples for each size category
        constraint_types: List of constraint types ("empty", "non_empty")
        structures: List of structures ("chain", "parallel", "mixed", "dag")
        risk_levels: List of risk levels ("high", "very_high", "medium", "low")
        instances_per_config: Number of instances to generate per configuration
        seed: Random seed
    """
    if sizes is None:
        sizes = [
            (3, 5),    # small
            (6, 10),   # medium
            (11, 15),  # large
            (50, 100)  # very_large
        ]
    
    if constraint_types is None:
        constraint_types = ["empty", "non_empty"]
    
    if structures is None:
        structures = ["chain", "parallel", "mixed", "dag"]
    
    if risk_levels is None:
        risk_levels = ["high", "medium"]
    
    base_path = Path(base_dir)
    
    random.seed(seed)
    instance_counter = {}
    
    for constraint_type in constraint_types:
        for size_idx, (min_n, max_n) in enumerate(sizes):
            size_name = ["small", "medium", "large", "very_large"][size_idx]
            
            for risk_level in risk_levels:
                if constraint_type == "empty":
                    # Empty problems: generate for all structures (but structure doesn't affect precedence)
                    for structure in structures:
                        for instance_num in range(instances_per_config):
                            # Generate random n in range
                            n = random.randint(min_n, max_n)
                            
                            # Generate unique seed for this instance
                            instance_seed = seed + hash(f"{constraint_type}_{size_name}_{structure}_{risk_level}_{instance_num}") % 10000
                            
                            problem = generate_problem(
                                n=n,
                                constraint_type=constraint_type,
                                structure=structure,  # Not used for empty, but kept for naming
                                risk_level=risk_level,
                                seed=instance_seed
                            )
                            
                            # Determine filename
                            key = f"{constraint_type}_{size_name}_{structure}_{risk_level}"
                            if key not in instance_counter:
                                instance_counter[key] = 0
                            instance_counter[key] += 1
                            counter = instance_counter[key]
                            
                            filename = f"n{n}_{risk_level}_{counter:03d}.yaml"
                            output_path = base_path / constraint_type / size_name / filename
                            
                            save_problem(problem, output_path)
                            print(f"Generated: {output_path}")
                
                else:  # non_empty
                    for structure in structures:
                        for instance_num in range(instances_per_config):
                            # Generate random n in range
                            n = random.randint(min_n, max_n)
                            
                            # Generate unique seed for this instance
                            instance_seed = seed + hash(f"{constraint_type}_{size_name}_{structure}_{risk_level}_{instance_num}") % 10000
                            
                            problem = generate_problem(
                                n=n,
                                constraint_type=constraint_type,
                                structure=structure,
                                risk_level=risk_level,
                                seed=instance_seed
                            )
                            
                            # Determine filename
                            key = f"{constraint_type}_{size_name}_{structure}_{risk_level}"
                            if key not in instance_counter:
                                instance_counter[key] = 0
                            instance_counter[key] += 1
                            counter = instance_counter[key]
                            
                            filename = f"{structure}_{n}_{risk_level}"
                            if counter > 1:
                                filename += f"_v{counter}"
                            filename += ".yaml"
                            
                            output_path = base_path / constraint_type / size_name / structure / filename
                            
                            save_problem(problem, output_path)
                            print(f"Generated: {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate KORef problem instances")
    parser.add_argument("--base-dir", default="problems", help="Base directory for problems")
    parser.add_argument("--instances", type=int, default=1, help="Number of instances per configuration")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--constraint-types", nargs="+", default=["empty", "non_empty"],
                       choices=["empty", "non_empty"], help="Constraint types to generate")
    parser.add_argument("--structures", nargs="+", default=["chain", "parallel", "mixed", "dag"],
                       choices=["chain", "parallel", "mixed", "dag"], help="Structures to generate")
    parser.add_argument("--risk-levels", nargs="+", default=["high", "medium"],
                       choices=["high", "very_high", "medium", "low"], help="Risk levels to generate")
    parser.add_argument("--sizes", nargs="+", default=["small", "medium", "large", "very_large"],
                       choices=["small", "medium", "large", "very_large"], help="Sizes to generate")
    
    args = parser.parse_args()
    
    # Map size names to ranges
    size_ranges = {
        "small": (3, 5),
        "medium": (6, 10),
        "large": (11, 15),
        "very_large": (50, 100)
    }
    
    sizes = [size_ranges[s] for s in args.sizes]
    
    print("Generating KORef problems...")
    print(f"Constraint types: {args.constraint_types}")
    print(f"Structures: {args.structures}")
    print(f"Risk levels: {args.risk_levels}")
    print(f"Sizes: {args.sizes}")
    print(f"Instances per config: {args.instances}")
    print()
    
    generate_all_problems(
        base_dir=args.base_dir,
        sizes=sizes,
        constraint_types=args.constraint_types,
        structures=args.structures,
        risk_levels=args.risk_levels,
        instances_per_config=args.instances,
        seed=args.seed
    )
    
    print("\nDone!")

