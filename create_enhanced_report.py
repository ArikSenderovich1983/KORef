#!/usr/bin/env python3
"""
Create an enhanced benchmark report with explicit optimality information.
"""

import csv
from pathlib import Path


def create_enhanced_report(csv_path="benchmark_results_30sec.csv", output_path="BENCHMARK_REPORT_ENHANCED.md"):
    """Create an enhanced markdown report with optimality information."""
    
    if not Path(csv_path).exists():
        print(f"Error: {csv_path} not found!")
        return
    
    # Read results
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        results = list(reader)
    
    if not results:
        print("No results found!")
        return
    
    # Create enhanced report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# KORef Benchmark Results - Enhanced Report\n\n")
        f.write("## Configuration\n\n")
        f.write("- **Solver**: DIDP with DFBB (Depth-First Branch & Bound)\n")
        f.write("- **Timeout**: 30 seconds per problem\n")
        f.write("- **Optimality**: Exhaustive search for optimal solutions\n")
        f.write("- **Total Problems**: {}\n\n".format(len(results)))
        
        # Summary statistics
        optimal_count = sum(1 for r in results if r['optimal'] == 'True')
        heuristic_count = sum(1 for r in results if r['optimal'] == 'False' and r['status'] not in ['TIMEOUT', 'FAIL'])
        timeout_count = sum(1 for r in results if 'TIMEOUT' in r['status'])
        failed_count = sum(1 for r in results if 'FAIL' in r['status'] or 'ERROR' in r['status'])
        
        f.write("## Summary Statistics\n\n")
        f.write(f"- **Proven optimal**: {optimal_count}/{len(results)} ({optimal_count/len(results)*100:.1f}%)\n")
        f.write(f"- **Heuristic (not proven optimal)**: {heuristic_count}/{len(results)} ({heuristic_count/len(results)*100:.1f}%)\n")
        f.write(f"- **Timeouts**: {timeout_count}/{len(results)} ({timeout_count/len(results)*100:.1f}%)\n")
        f.write(f"- **Failed**: {failed_count}/{len(results)} ({failed_count/len(results)*100:.1f}%)\n\n")
        
        # Improvement statistics
        improved = [r for r in results if r.get('improvement_pct') and float(r['improvement_pct']) > 0.001]
        if improved:
            avg_improvement = sum(float(r['improvement_pct']) for r in improved) / len(improved)
            max_improvement = max((float(r['improvement_pct']), r['instance']) for r in improved)
            f.write(f"- **Problems with improvement**: {len(improved)}/{len(results)} ({len(improved)/len(results)*100:.1f}%)\n")
            f.write(f"- **Average improvement** (for improved problems): {avg_improvement:.2f}%\n")
            f.write(f"- **Maximum improvement**: {max_improvement[0]:.2f}% ({max_improvement[1]})\n\n")
        
        # Runtime statistics
        runtimes = [float(r['runtime']) for r in results if r['runtime']]
        if runtimes:
            avg_runtime = sum(runtimes) / len(runtimes)
            max_runtime_val = max(runtimes)
            max_runtime_inst = [r['instance'] for r in results if float(r['runtime']) == max_runtime_val][0]
            min_runtime = min(runtimes)
            f.write(f"- **Average runtime**: {avg_runtime:.3f}s\n")
            f.write(f"- **Max runtime**: {max_runtime_val:.3f}s ({max_runtime_inst})\n")
            f.write(f"- **Min runtime**: {min_runtime:.3f}s\n\n")
        
        # Main results table with optimality column
        f.write("## Detailed Results\n\n")
        f.write("| Instance | Type | Size | Struct | N | Original | Refined | Improvement % | Runtime (s) | Proven Optimal | Status |\n")
        f.write("|----------|------|------|--------|---|----------|---------|---------------|-------------|----------------|--------|\n")
        
        for r in results:
            orig = f"{float(r['original']):.6f}" if r.get('original') and r['original'] else "N/A"
            ref = f"{float(r['refined']):.6f}" if r.get('refined') and r['refined'] else "N/A"
            imp_pct = f"{float(r['improvement_pct']):.2f}%" if r.get('improvement_pct') and r['improvement_pct'] else "N/A"
            rt = f"{float(r['runtime']):.3f}" if r.get('runtime') and r['runtime'] else "N/A"
            n = r.get('n', 'N/A')
            
            # Optimality indicator
            if r['optimal'] == 'True':
                optimal_str = "[YES]"
            elif 'TIMEOUT' in r['status']:
                optimal_str = "[TIMEOUT]"
            elif 'FAIL' in r['status'] or 'ERROR' in r['status']:
                optimal_str = "[FAILED]"
            else:
                optimal_str = "[HEURISTIC]"
            
            f.write(f"| {r['instance']} | {r['constraint_type']} | {r['size']} | {r['struct_type']} | {n} | {orig} | {ref} | {imp_pct} | {rt} | {optimal_str} | {r['status']} |\n")
        
        # Breakdown by category
        f.write("\n## Results by Category\n\n")
        
        # Group by constraint type and size
        categories = {}
        for r in results:
            key = (r['constraint_type'], r['size'])
            if key not in categories:
                categories[key] = []
            categories[key].append(r)
        
        for (constraint_type, size), cat_results in sorted(categories.items()):
            f.write(f"### {constraint_type.title()} - {size.title()}\n\n")
            optimal_cat = sum(1 for r in cat_results if r['optimal'] == 'True')
            improved_cat = [r for r in cat_results if r.get('improvement_pct') and float(r['improvement_pct']) > 0.001]
            avg_runtime_cat = sum(float(r['runtime']) for r in cat_results if r['runtime']) / len(cat_results)
            
            f.write(f"- **Problems**: {len(cat_results)}\n")
            f.write(f"- **Proven optimal**: {optimal_cat}/{len(cat_results)} ({optimal_cat/len(cat_results)*100:.1f}%)\n")
            f.write(f"- **Average runtime**: {avg_runtime_cat:.3f}s\n")
            if improved_cat:
                avg_imp = sum(float(r['improvement_pct']) for r in improved_cat) / len(improved_cat)
                f.write(f"- **Problems with improvement**: {len(improved_cat)}/{len(cat_results)} ({len(improved_cat)/len(cat_results)*100:.1f}%)\n")
                f.write(f"- **Average improvement**: {avg_imp:.2f}%\n")
            f.write("\n")
        
        # Top improvements
        f.write("## Top 10 Improvements\n\n")
        top_improvements = sorted(
            [(float(r['improvement_pct']), r['instance'], r['constraint_type'], r['size'], r['struct_type']) 
             for r in results if r.get('improvement_pct') and float(r['improvement_pct']) > 0],
            reverse=True
        )[:10]
        
        if top_improvements:
            f.write("| Rank | Instance | Type | Size | Struct | Improvement % |\n")
            f.write("|------|----------|------|------|--------|---------------|\n")
            for i, (imp, inst, ctype, sz, struct) in enumerate(top_improvements, 1):
                f.write(f"| {i} | {inst} | {ctype} | {sz} | {struct} | {imp:.2f}% |\n")
            f.write("\n")
        
        # Runtime analysis
        f.write("## Runtime Analysis\n\n")
        
        # Group by size
        size_groups = {'small': [], 'medium': [], 'large': []}
        for r in results:
            if r['runtime']:
                size_groups[r['size']].append(float(r['runtime']))
        
        f.write("| Size | Count | Avg Runtime | Min Runtime | Max Runtime |\n")
        f.write("|------|-------|-------------|-------------|-------------|\n")
        for size in ['small', 'medium', 'large']:
            if size_groups[size]:
                avg_rt = sum(size_groups[size]) / len(size_groups[size])
                min_rt = min(size_groups[size])
                max_rt = max(size_groups[size])
                f.write(f"| {size.title()} | {len(size_groups[size])} | {avg_rt:.3f}s | {min_rt:.3f}s | {max_rt:.3f}s |\n")
        
        f.write("\n")
        
        # Notes
        f.write("## Notes\n\n")
        f.write("- **Proven Optimal [YES]**: The solution was proven optimal through exhaustive search\n")
        f.write("- **Timeout [TIMEOUT]**: The solver reached the 30-second timeout without proving optimality\n")
        f.write("- **Heuristic [HEURISTIC]**: A heuristic solution (not proven optimal)\n")
        f.write("- **Failed [FAILED]**: The solver failed to find a solution\n")
        f.write("- **Improvement %**: Percentage improvement from original to refined expected makespan\n")
        f.write("- **Runtime**: Time taken to solve the problem (in seconds)\n")
    
    print(f"[OK] Enhanced report created: {output_path}")
    print(f"[OK] Total problems: {len(results)}")
    print(f"[OK] Proven optimal: {optimal_count}/{len(results)}")


if __name__ == "__main__":
    import sys
    
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "benchmark_results_30sec.csv"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "BENCHMARK_REPORT_ENHANCED.md"
    
    create_enhanced_report(csv_path, output_path)

