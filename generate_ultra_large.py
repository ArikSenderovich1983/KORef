#!/usr/bin/env python3
"""
Generate ultra-large, ultra-risky problems (100-200 activities) with:
- Empty precedence constraints
- Varying durations (0.1 to 10.0)
- Risk-to-duration ratio (p/d) uniformly distributed between 0 and 1
- Three risk levels: high, medium, low (distinguished by p/d ranges)
- 10 instances of each risk level
- All parameters match except risk level
"""

import os
import random
import yaml
from pathlib import Path
from typing import List, Dict

# Import makespan computation functions
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from koref_utils import (
    compute_earliest_start_schedule,
    compute_expected_makespan,
)


def generate_ultra_large_problems(
    base_seed: int = 2024,
    num_instances: int = 10,
    min_n: int = 100,
    max_n: int = 200,
    min_duration: float = 0.1,
    max_duration: float = 10.0
):
    """
    Generate ultra-large problems with matching parameters except risk level.
    
    For each instance:
    - Same n (random between min_n and max_n)
    - Same durations (uniformly distributed between min_duration and max_duration)
    - Same random seed for duration generation
    - p/d ratios vary by risk level but are uniformly distributed within their ranges
    - Only risk level varies (high, medium, low)
    """
    base_dir = Path("problems") / "empty" / "ultra_large_ultra_risky"
    base_dir.mkdir(parents=True, exist_ok=True)
    
    problems_generated = []
    
    for instance_id in range(1, num_instances + 1):
        # Use same seed for this instance across all risk levels
        instance_seed = base_seed + instance_id * 1000
        
        # Generate same n for all risk levels
        random.seed(instance_seed)
        n = random.randint(min_n, max_n)
        
        # Generate same durations for all risk levels (use same seed)
        duration_seed = instance_seed + 100
        random.seed(duration_seed)
        durations = [round(random.uniform(min_duration, max_duration), 2) for _ in range(n)]
        
        # Generate for each risk level
        for risk_level in ["high", "medium", "low"]:
            # Use same seed pattern but offset by risk level for p/d ratios
            prob_seed = instance_seed + hash(risk_level) % 1000
            
            # Generate p/d ratios based on risk level
            random.seed(prob_seed)
            if risk_level == "high":
                p_d_ratios = [random.uniform(0.7, 1.0) for _ in range(n)]
            elif risk_level == "medium":
                p_d_ratios = [random.uniform(0.3, 0.5) for _ in range(n)]
            elif risk_level == "low":
                p_d_ratios = [random.uniform(0.05, 0.15) for _ in range(n)]
            
            # Compute probabilities: p = d * (p/d), clamped to [0, 1]
            probabilities = []
            for d, ratio in zip(durations, p_d_ratios):
                p = d * ratio
                p = max(0.0, min(1.0, p))  # Clamp to [0, 1]
                probabilities.append(round(p, 4))
            
            # Empty precedence
            precedence = []
            
            # Convert precedence to dict format for makespan computation
            precedence_dict = {}
            
            # Compute original expected makespan
            activities_list = list(range(n))
            schedule = compute_earliest_start_schedule(activities_list, precedence_dict, durations)
            original_makespan = compute_expected_makespan(activities_list, schedule, durations, probabilities)
            
            # Create activities list
            activities = []
            for i in range(n):
                activities.append({
                    'id': i,
                    'duration': durations[i],
                    'ko_probability': probabilities[i]
                })
            
            # Create problem name
            problem_name = f"ultra_{n}_{risk_level}_{instance_id:02d}"
            
            # Compute p/d ratios for metadata
            p_d_ratios_actual = [p/d if d > 0 else 0.0 for p, d in zip(probabilities, durations)]
            avg_p_d_ratio = sum(p_d_ratios_actual) / len(p_d_ratios_actual) if len(p_d_ratios_actual) > 0 else 0.0
            
            # Create problem dict
            problem = {
                'name': problem_name,
                'n': n,
                'activities': activities,
                'precedence': precedence,
                'metadata': {
                    'size': 'ultra_large',
                    'constraint_type': 'empty',
                    'risk_level': risk_level,
                    'instance_id': instance_id,
                    'n_activities': n,
                    'varying_durations': True,
                    'min_duration': min_duration,
                    'max_duration': max_duration,
                    'avg_p_d_ratio': round(avg_p_d_ratio, 4),
                    'original_expected_makespan': round(original_makespan, 6)
                }
            }
            
            # Save to YAML
            output_path = base_dir / f"{problem_name}.yaml"
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(problem, f, default_flow_style=False, sort_keys=False)
            
            problems_generated.append({
                'name': problem_name,
                'path': str(output_path),
                'n': n,
                'risk_level': risk_level,
                'instance_id': instance_id
            })
            
            print(f"Generated: {problem_name} (n={n}, risk={risk_level})")
    
    print(f"\nGenerated {len(problems_generated)} problems")
    return problems_generated


if __name__ == "__main__":
    print("=" * 80)
    print("GENERATING ULTRA-LARGE, ULTRA-RISKY PROBLEMS")
    print("=" * 80)
    print()
    print("Parameters:")
    print("  - Size: 100-200 activities")
    print("  - Precedence: Empty")
    print("  - Durations: Varying uniformly between 0.1 and 10.0")
    print("  - Risk-to-duration ratio (p/d): Uniformly distributed")
    print("    * High risk: p/d ~ Uniform(0.7, 1.0)")
    print("    * Medium risk: p/d ~ Uniform(0.3, 0.5)")
    print("    * Low risk: p/d ~ Uniform(0.05, 0.15)")
    print("  - Risk levels: high, medium, low")
    print("  - Instances: 10 of each risk level (30 total)")
    print("  - Matching: All parameters match except risk level (p/d ratios)")
    print()
    
    problems = generate_ultra_large_problems(
        base_seed=2024,
        num_instances=10,
        min_n=100,
        max_n=200,
        min_duration=0.1,
        max_duration=10.0
    )
    
    print()
    print("=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(f"Total problems: {len(problems)}")
    print(f"Output directory: problems/empty/ultra_large_ultra_risky/")

