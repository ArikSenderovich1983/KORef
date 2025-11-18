# KORef Repository Structure

## Main Pipeline Files (Core Workflow)

### 1. Problem Generation
- **`generate_problems.py`** - Generate standard problem suite
  - Sizes: small (3-5), medium (6-10), large (11-15), very_large (50-100)
  - Types: empty, non_empty (chain, parallel, mixed, DAG)
  - Risk levels: high, medium, low

- **`generate_ultra_large.py`** - Generate ultra-large problems
  - Sizes: 100-200 activities
  - Empty precedence only
  - Risk-to-duration ratio controlled: high/medium/low

### 2. Core Components
- **`koref_utils.py`** - Makespan computation and scheduling algorithms
- **`read_koref.py`** - Problem file reader
- **`koref_domain.py`** - DIDP model and solver

### 3. Benchmarking
- **`benchmark_unified.py`** - Benchmark standard problems
- **`benchmark_ultra_large.py`** - Benchmark ultra-large problems

### 4. Reporting & Analysis
- **`create_enhanced_report.py`** - Generate markdown reports from CSV results
- **`detect_forced_constraints.py`** - Analyze problem structure and forced constraints

## Documentation Files (Keep)

### Problem & Method Documentation
- **`explain.md`** - KORef problem explanation, makespan computation, DIDP formulation
- **`DIDP_TUTORIAL.md`** - DIDP formulation tutorial
- **`proof_of_complexity.md`** - NP-hardness proof
- **`runtime_discussion.md`** - Factors affecting problem difficulty
- **`constraint_analysis.md`** - Constraint forcing and search space analysis

### Results & Papers
- **`main_results.md`** - Benchmark results summary
- **`BENCHMARK_REPORT_ENHANCED.md`** - Detailed benchmark report
- **`ultra_large_results_report.md`** - Ultra-large benchmark report
- **`koref_icaps.tex`** - ICAPS 2026 paper draft

## Data Files (Keep)

### Benchmark Results
- **`benchmark_results_30sec.csv`** - Standard benchmark results (30s timeout)
- **`ultra_large_results.csv`** - Ultra-large benchmark results

### Problem Instances
- **`problems/`** directory structure:
  ```
  problems/
  ├── empty/
  │   ├── small/
  │   ├── medium/
  │   ├── large/
  │   ├── very_large/
  │   └── ultra_large_ultra_risky/
  └── non_empty/
      ├── small/{chain,parallel,mixed,dag}/
      ├── medium/{chain,parallel,mixed,dag}/
      ├── large/{chain,parallel,mixed,dag}/
      └── very_large/{chain,parallel,mixed,dag}/
  ```

## Complete Pipeline Workflow

```bash
# Step 1: Generate problems
python generate_problems.py
python generate_ultra_large.py

# Step 2: Run benchmarks
python benchmark_unified.py --time-limit 30 --output standard_results
python benchmark_ultra_large.py --time-limit 60 --output ultra_results

# Step 3: Generate reports
python create_enhanced_report.py standard_results.csv STANDARD_REPORT.md

# Step 4: Analyze structure (optional)
python detect_forced_constraints.py problems/empty/ultra_large_ultra_risky/
```

## Files Removed (No Longer in Repository)

These were temporary analysis/test files:
- `analyze_n3_problem.py` - Specific problem analysis
- `explain_parallel_optimal.py` - Temporary explanation script
- `test_single_instance.py` - Test script
- `verify_with_didp.py` - Verification script
- `test_instance.koref` - Test problem file
- `didp_verification_output.txt` - Output file
- `n3_analysis_output.txt` - Output file
- `parallel_analysis.txt` - Output file

## Quick Reference

**Generate & benchmark standard problems:**
```bash
python generate_problems.py && python benchmark_unified.py --time-limit 30
```

**Generate & benchmark ultra-large problems:**
```bash
python generate_ultra_large.py && python benchmark_ultra_large.py --time-limit 60
```

**Solve a single problem:**
```bash
python koref_domain.py problems/empty/small/empty_4_high_01.yaml --config Optimal --time-out 30
```

**Analyze problem structure:**
```bash
python detect_forced_constraints.py problems/empty/ultra_large_ultra_risky/ultra_118_high_01.yaml
```

