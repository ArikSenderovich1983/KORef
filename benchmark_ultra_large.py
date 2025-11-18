#!/usr/bin/env python3
"""
Benchmark ultra-large, ultra-risky problems and generate focused report.
"""

import csv
import time
from pathlib import Path
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from read_koref import read_yaml
from koref_domain import create_model, solve
from koref_utils import compute_expected_makespan, compute_earliest_start_schedule


def find_ultra_large_problems():
    """Find all ultra-large problems."""
    base_dir = Path("problems") / "empty" / "ultra_large_ultra_risky"
    
    if not base_dir.exists():
        print(f"Error: Directory {base_dir} does not exist")
        return []
    
    problems = []
    for yaml_file in sorted(base_dir.glob("*.yaml")):
        # Extract info from filename: ultra_N_risk_ID.yaml
        parts = yaml_file.stem.split('_')
        if len(parts) >= 4:
            n = int(parts[1])
            risk_level = parts[2]
            instance_id = parts[3]
            
            problems.append({
                'path': str(yaml_file),
                'name': yaml_file.stem,
                'n': n,
                'risk_level': risk_level,
                'instance_id': instance_id
            })
    
    return problems


def solve_refined(instance_path, time_limit=30):
    """Solve a problem instance and return results."""
    name, n, durations, probabilities, precedence = read_yaml(instance_path)
    
    model, pair_to_info, initial_prec, unresolved_pair_map, duration_table, prob_table = create_model(
        n, durations, probabilities, precedence
    )
    
    start_time = time.time()
    
    # Create temp history file
    import tempfile
    history_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
    history_file.close()
    
    try:
        refined_precedence, refined_makespan, _, is_optimal, is_timeout = solve(
            model,
            pair_to_info,
            n,
            durations,
            probabilities,
            initial_prec,
            unresolved_pair_map,
            duration_table,
            prob_table,
            "Optimal",
            history_file.name,
            time_limit=time_limit
        )
    finally:
        if os.path.exists(history_file.name):
            os.remove(history_file.name)
    
    runtime = time.time() - start_time
    
    return refined_makespan, is_optimal, runtime, not is_timeout


def benchmark_ultra_large(time_limit=30, output_csv="ultra_large_results.csv"):
    """Run benchmark on ultra-large problems."""
    problems = find_ultra_large_problems()
    
    if not problems:
        print("No problems found!")
        return
    
    print(f"Found {len(problems)} problems")
    print(f"Time limit: {time_limit}s per problem")
    print()
    
    results = []
    
    for i, problem in enumerate(problems, 1):
        print(f"[{i}/{len(problems)}] Solving {problem['name']}...", end=' ', flush=True)
        
        try:
            # Read original makespan
            name, n, durations, probabilities, precedence = read_yaml(problem['path'])
            
            # Compute original expected makespan
            activities_list = list(range(n))
            precedence_dict = {}
            schedule = compute_earliest_start_schedule(activities_list, precedence_dict, durations)
            original_makespan = compute_expected_makespan(activities_list, schedule, durations, probabilities)
            
            # Solve
            refined_makespan, is_optimal, runtime, completed = solve_refined(problem['path'], time_limit)
            
            if refined_makespan is None:
                print("FAILED")
                results.append({
                    'instance': problem['name'],
                    'n': n,
                    'risk_level': problem['risk_level'],
                    'instance_id': problem['instance_id'],
                    'original': original_makespan,
                    'refined': None,
                    'improvement': None,
                    'improvement_pct': None,
                    'runtime': runtime,
                    'optimal': False,
                    'completed': completed,
                    'status': 'FAILED'
                })
            else:
                improvement = original_makespan - refined_makespan
                improvement_pct = (improvement / original_makespan * 100) if original_makespan > 0 else 0
                
                status = 'OK'
                if not completed:
                    status = 'TIMEOUT'
                elif not is_optimal:
                    status = 'HEURISTIC'
                
                print(f"{'[OK]' if completed else '[TIMEOUT]'} Runtime: {runtime:.3f}s, Improvement: {improvement_pct:.2f}%")
                
                results.append({
                    'instance': problem['name'],
                    'n': n,
                    'risk_level': problem['risk_level'],
                    'instance_id': problem['instance_id'],
                    'original': original_makespan,
                    'refined': refined_makespan,
                    'improvement': improvement,
                    'improvement_pct': improvement_pct,
                    'runtime': runtime,
                    'optimal': is_optimal,
                    'completed': completed,
                    'status': status
                })
        
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                'instance': problem['name'],
                'n': problem['n'],
                'risk_level': problem['risk_level'],
                'instance_id': problem['instance_id'],
                'original': None,
                'refined': None,
                'improvement': None,
                'improvement_pct': None,
                'runtime': None,
                'optimal': False,
                'completed': False,
                'status': f'ERROR: {str(e)}'
            })
    
    # Save to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'instance', 'n', 'risk_level', 'instance_id', 'original', 'refined',
            'improvement', 'improvement_pct', 'runtime', 'optimal', 'completed', 'status'
        ])
        writer.writeheader()
        writer.writerows(results)
    
    print()
    print(f"Results saved to {output_csv}")
    
    # Generate summary
    generate_report(results, output_csv.replace('.csv', '_report.md'))
    
    return results


def generate_report(results, output_file):
    """Generate markdown report from results."""
    import pandas as pd
    
    df = pd.DataFrame(results)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Ultra-Large, Ultra-Risky Problems: Benchmark Results\n\n")
        f.write("## Configuration\n\n")
        f.write("- **Problem Size**: 100-200 activities\n")
        f.write("- **Precedence**: Empty\n")
        f.write("- **Durations**: All unit (1.0)\n")
        f.write("- **Risk Levels**: high, medium, low\n")
        f.write("- **Instances**: 10 of each risk level (30 total)\n")
        f.write("- **Matching**: All parameters match except risk level\n")
        f.write("- **Solver**: DIDP with DFBB\n")
        f.write("- **Time Limit**: 30 seconds per problem\n\n")
        
        f.write("## Summary Statistics\n\n")
        
        total = len(df)
        completed = df['completed'].sum() if 'completed' in df.columns else 0
        optimal = df['optimal'].sum() if 'optimal' in df.columns else 0
        
        f.write(f"- **Total Problems**: {total}\n")
        f.write(f"- **Completed**: {completed}/{total} ({completed/total*100:.1f}%)\n")
        f.write(f"- **Proven Optimal**: {optimal}/{total} ({optimal/total*100:.1f}%)\n")
        
        if 'improvement_pct' in df.columns:
            improved = df[df['improvement_pct'] > 0.001]
            f.write(f"- **Problems with Improvement**: {len(improved)}/{total} ({len(improved)/total*100:.1f}%)\n")
            if len(improved) > 0:
                f.write(f"- **Average Improvement** (for improved): {improved['improvement_pct'].mean():.2f}%\n")
                f.write(f"- **Maximum Improvement**: {df['improvement_pct'].max():.2f}%\n")
        
        if 'runtime' in df.columns:
            valid_runtimes = df[df['runtime'].notna()]['runtime']
            if len(valid_runtimes) > 0:
                f.write(f"- **Average Runtime**: {valid_runtimes.mean():.3f}s\n")
                f.write(f"- **Max Runtime**: {valid_runtimes.max():.3f}s\n")
                f.write(f"- **Min Runtime**: {valid_runtimes.min():.3f}s\n")
        
        f.write("\n## Results by Risk Level\n\n")
        
        for risk_level in ['high', 'medium', 'low']:
            risk_df = df[df['risk_level'] == risk_level]
            if len(risk_df) > 0:
                f.write(f"### {risk_level.upper()} Risk\n\n")
                f.write(f"- **Total**: {len(risk_df)}\n")
                
                if 'completed' in risk_df.columns:
                    completed_count = risk_df['completed'].sum()
                    f.write(f"- **Completed**: {completed_count}/{len(risk_df)} ({completed_count/len(risk_df)*100:.1f}%)\n")
                
                if 'optimal' in risk_df.columns:
                    optimal_count = risk_df['optimal'].sum()
                    f.write(f"- **Proven Optimal**: {optimal_count}/{len(risk_df)} ({optimal_count/len(risk_df)*100:.1f}%)\n")
                
                if 'improvement_pct' in risk_df.columns:
                    improved = risk_df[risk_df['improvement_pct'] > 0.001]
                    f.write(f"- **Problems with Improvement**: {len(improved)}/{len(risk_df)} ({len(improved)/len(risk_df)*100:.1f}%)\n")
                    if len(improved) > 0:
                        f.write(f"- **Average Improvement**: {improved['improvement_pct'].mean():.2f}%\n")
                        f.write(f"- **Max Improvement**: {risk_df['improvement_pct'].max():.2f}%\n")
                
                if 'runtime' in risk_df.columns:
                    valid_runtimes = risk_df[risk_df['runtime'].notna()]['runtime']
                    if len(valid_runtimes) > 0:
                        f.write(f"- **Average Runtime**: {valid_runtimes.mean():.3f}s\n")
                        f.write(f"- **Max Runtime**: {valid_runtimes.max():.3f}s\n")
                
                f.write("\n")
        
        f.write("## Detailed Results\n\n")
        f.write("| Instance | N | Risk | Original | Refined | Improvement % | Runtime (s) | Optimal | Status |\n")
        f.write("|----------|---|------|----------|---------|---------------|-------------|---------|--------|\n")
        
        for _, row in df.iterrows():
            instance = row['instance']
            n = row['n']
            risk = row['risk_level']
            original = f"{row['original']:.3f}" if pd.notna(row['original']) else "N/A"
            refined = f"{row['refined']:.3f}" if pd.notna(row['refined']) else "N/A"
            improvement = f"{row['improvement_pct']:.2f}%" if pd.notna(row['improvement_pct']) else "N/A"
            runtime = f"{row['runtime']:.3f}" if pd.notna(row['runtime']) else "N/A"
            optimal = "[YES]" if row.get('optimal', False) else "[NO]"
            status = row.get('status', 'OK')
            
            f.write(f"| {instance} | {n} | {risk} | {original} | {refined} | {improvement} | {runtime} | {optimal} | {status} |\n")
        
        f.write("\n## Comparison: Matching Instances\n\n")
        f.write("For each instance ID, compare high vs medium vs low risk:\n\n")
        f.write("| Instance ID | N | High Risk | Medium Risk | Low Risk |\n")
        f.write("|-------------|---|-----------|-------------|----------|\n")
        
        for instance_id in sorted(df['instance_id'].unique()):
            id_df = df[df['instance_id'] == instance_id]
            if len(id_df) > 0:
                n = id_df.iloc[0]['n']
                high_row = id_df[id_df['risk_level'] == 'high'].iloc[0] if len(id_df[id_df['risk_level'] == 'high']) > 0 else None
                medium_row = id_df[id_df['risk_level'] == 'medium'].iloc[0] if len(id_df[id_df['risk_level'] == 'medium']) > 0 else None
                low_row = id_df[id_df['risk_level'] == 'low'].iloc[0] if len(id_df[id_df['risk_level'] == 'low']) > 0 else None
                
                high_str = f"{high_row['improvement_pct']:.2f}%" if high_row is not None and pd.notna(high_row.get('improvement_pct')) else "N/A"
                medium_str = f"{medium_row['improvement_pct']:.2f}%" if medium_row is not None and pd.notna(medium_row.get('improvement_pct')) else "N/A"
                low_str = f"{low_row['improvement_pct']:.2f}%" if low_row is not None and pd.notna(low_row.get('improvement_pct')) else "N/A"
                
                f.write(f"| {instance_id} | {n} | {high_str} | {medium_str} | {low_str} |\n")
    
    print(f"Report saved to {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark ultra-large problems")
    parser.add_argument("--time-limit", type=int, default=30, help="Time limit per problem (seconds)")
    parser.add_argument("--output", type=str, default="ultra_large_results.csv", help="Output CSV file")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("ULTRA-LARGE, ULTRA-RISKY PROBLEMS BENCHMARK")
    print("=" * 80)
    print()
    
    results = benchmark_ultra_large(time_limit=args.time_limit, output_csv=args.output)

