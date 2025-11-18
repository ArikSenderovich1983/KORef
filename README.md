# KORef: KO-plan Refinement using DIDP

This implementation solves the KO-plan Refinement (KORef) problem using the DIDP (Domain-Independent Dynamic Programming) framework.

## Problem Description

Given a KO-plan `K=(A, ≺, d, p)` where:
- `A` is a set of activities
- `≺` is a partial order (precedence constraints)
- `d` assigns durations to activities
- `p` assigns knock-out probabilities to activities

The goal is to find a refinement `≺'` of `≺` (i.e., `≺ ⊆ ≺'`) that minimizes the expected makespan of the canonical earliest-start schedule, where makespan accounts for stochastic knock-out events.

## Quick Start: Pipeline Overview

### Step 1: Generate Problems
```bash
# Generate standard problem suite (small, medium, large, very_large)
python generate_problems.py

# Generate ultra-large problems (100-200 activities, varying risk levels)
python generate_ultra_large.py
```

### Step 2: Run Benchmarks
```bash
# Benchmark standard problems (default: 30s timeout per problem)
python benchmark_unified.py --time-limit 30 --output benchmark_results_30sec

# Benchmark ultra-large problems (recommended: longer timeout)
python benchmark_ultra_large.py --time-limit 30 --output ultra_large_results
```

### Step 3: Generate Reports
```bash
# Create enhanced markdown report from CSV results
python create_enhanced_report.py benchmark_results_30sec.csv BENCHMARK_REPORT_ENHANCED.md

# The script automatically generates:
# - Summary statistics
# - Optimality breakdown
# - Detailed results table
```

### Step 4: Analyze Problem Structure (Optional)
```bash
# Analyze which constraints are forced by dominance or risk-ratio heuristics
python detect_forced_constraints.py problems/empty/ultra_large_ultra_risky/ultra_118_high_01.yaml

# Analyze entire directory
python detect_forced_constraints.py problems/empty/ultra_large_ultra_risky/
```

## Main Pipeline Files

### Core Components
- **`koref_utils.py`**: Core algorithms for computing schedules and expected makespan
- **`read_koref.py`**: Problem reader and validation utilities
- **`koref_domain.py`**: DIDP model implementation and solver

### Problem Generation
- **`generate_problems.py`**: Generate standard problem suite
  - Sizes: small (3-5), medium (6-10), large (11-15), very_large (50-100)
  - Types: empty precedence, non-empty (chain, parallel, mixed, DAG)
  - Risk levels: high, medium, low
  
- **`generate_ultra_large.py`**: Generate ultra-large problems
  - Sizes: 100-200 activities
  - Empty precedence only
  - Risk levels: high (p/d ∈ [0.7,1.0]), medium (p/d ∈ [0.3,0.5]), low (p/d ∈ [0.05,0.15])

### Benchmarking
- **`benchmark_unified.py`**: Benchmark all standard problems
  - Default timeout: 30 seconds per problem
  - Outputs CSV with detailed results
  - Tracks optimality status (proven optimal vs. timeout)

- **`benchmark_ultra_large.py`**: Benchmark ultra-large problems
  - Specialized for very large instances
  - Longer recommended timeout (60-300s)

### Analysis & Reporting
- **`create_enhanced_report.py`**: Generate markdown reports from CSV results
- **`detect_forced_constraints.py`**: Analyze problem structure
  - Detects dominance relationships (provably forced constraints)
  - Identifies risk-ratio heuristic suggestions
  - Estimates search space reduction

## Problem Structure

Problems are organized in the following directory structure:

```
problems/
├── empty/                     # Problems with empty initial precedence
│   ├── small/                 # 3-5 activities
│   ├── medium/                # 6-10 activities
│   ├── large/                 # 11-15 activities
│   ├── very_large/            # 50-100 activities
│   └── ultra_large_ultra_risky/  # 100-200 activities (high/medium/low risk)
└── non_empty/                 # Problems with existing precedence
    ├── small/                 # 3-5 activities
    │   ├── chain/
    │   ├── parallel/
    │   ├── mixed/
    │   └── dag/
    ├── medium/                # 6-10 activities
    │   ├── chain/
    │   ├── parallel/
    │   ├── mixed/
    │   └── dag/
    ├── large/                 # 11-15 activities
    │   ├── chain/
    │   ├── parallel/
    │   ├── mixed/
    │   └── dag/
    └── very_large/            # 50-100 activities
        ├── chain/
        ├── parallel/
        ├── mixed/
        └── dag/
```

## YAML Problem Format

Each problem file is in YAML format:

```yaml
name: problem_name
n: 5
activities:
  - id: 0
    duration: 2.5
    ko_probability: 0.1
  - id: 1
    duration: 3.0
    ko_probability: 0.2
  # ... more activities
precedence:
  - [0, 1]  # activity 0 must precede activity 1
  - [1, 2]
  # ... more constraints
metadata:
  size: small
  constraint_type: empty
  risk_level: high
  original_expected_makespan: 8.456
```

## Documentation Files

- **`explain.md`**: Detailed explanation of KORef problem, makespan computation, DIDP formulation, and knockout semantics
- **`DIDP_TUTORIAL.md`**: Tutorial on DIDP formulation and solution approach for KORef
- **`proof_of_complexity.md`**: NP-hardness proof for the KORef decision problem
- **`runtime_discussion.md`**: Analysis of factors affecting problem difficulty and runtime
- **`constraint_analysis.md`**: Discussion of forced constraints and search space reduction
- **`main_results.md`**: Summary of benchmark results and key findings
- **`koref_icaps.tex`**: ICAPS 2026 submission draft (LaTeX)

## Prerequisites

Install the DIDP Python package:
```bash
pip install didppy pyyaml
```

## Advanced Usage

### Running the Solver Directly

```bash
python koref_domain.py <instance_file> [options]
```

Options:
- `--time-out`: Time limit in seconds (default: 1800)
- `--history`: History file for search progress (default: history.csv)
- `--config`: Solver configuration (default: Optimal)
  - `Optimal` or `EXHAUSTIVE`: DFBB with exhaustive search (guaranteed optimal)
  - `FR` or `ForwardRecursion`: Forward recursion (may not explore all states)
  - Other DIDP solvers: `CABS`, `LNBS`, `DFBB`, `CBFS`, etc.
- `--seed`: Random seed (default: 2023)
- `--threads`: Number of threads (default: 1)

Example:
```bash
# Find optimal solution with 60s timeout
python koref_domain.py problems/empty/small/empty_4_high_01.yaml --config Optimal --time-out 60
```

### Custom Problem Generation

```bash
# Generate specific problem types
python generate_problems.py \
  --constraint-types empty non_empty \
  --structures chain dag \
  --risk-levels high medium \
  --instances 10 \
  --seed 42

# Generate ultra-large with custom parameters
python generate_ultra_large.py --base-seed 2024 --num-instances 20
```

### Custom Benchmarking

```bash
# Benchmark with longer timeout
python benchmark_unified.py --time-limit 120 --output my_results

# Benchmark specific directory
python benchmark_ultra_large.py --time-limit 300 --output ultra_results
```

## Implementation Notes

### State Representation

The DIDP state tracks:
- `unresolved`: Set of unresolved unordered pairs of activities
- `added_constraints`: Set of precedence constraints that have been added

### Transitions

For each unresolved pair `{a, b}`, we can add either:
- `a < b` (activity a precedes b)
- `b < a` (activity b precedes a)

### Search Strategy

The implementation uses **DFBB (Depth-First Branch & Bound)** for optimal search:
1. Explores the state space depth-first (memory efficient)
2. For each terminal state, extracts the precedence relation
3. Computes exact expected makespan using bucket-based algorithm
4. Tracks the best solution found
5. Continues until all states are explored or timeout

**Note**: Due to the non-monotonic nature of the objective function (adding constraints can either increase or decrease makespan), traditional bound-based pruning is not suitable for guaranteeing optimality. The solver performs exhaustive search on smaller instances and times out on larger ones.

### Expected Makespan Algorithm

The implementation uses the bucket-based algorithm:
1. Compute earliest-start schedule from precedence relation
2. Compute abort times for each activity (considering overlapping activities)
3. Group activities by abort time into buckets
4. Compute survival probabilities: Q_j = ∏(1-p(a)) for activities in bucket j
5. Compute cumulative probabilities: P_j = ∏Q_i for i=1..j
6. Apply formula: E[M] = Σ(t_j * P_{j-1} * (1-Q_j)) + T * P_k

**Knockout Semantics**: Activities execute fully before knockout evaluation. When an activity knocks out, all concurrently running activities finish first, then the process stops.

## Complete Workflow Example

```bash
# 1. Generate all problems
python generate_problems.py
python generate_ultra_large.py

# 2. Run benchmarks
python benchmark_unified.py --time-limit 30 --output standard_results
python benchmark_ultra_large.py --time-limit 60 --output ultra_results

# 3. Generate reports
python create_enhanced_report.py standard_results.csv STANDARD_REPORT.md

# 4. Analyze problem structure
python detect_forced_constraints.py problems/empty/ultra_large_ultra_risky/

# 5. Review results
# - Check markdown reports (*.md)
# - Review CSV files (*.csv)
# - Analyze constraint structure
```

## Key Results

- **Small/Medium problems**: Solver finds proven optimal solutions within seconds
- **Large problems**: Most instances solved optimally within 30s timeout
- **Very large problems**: Timeout common, but good solutions found
- **Ultra-large problems**: Primarily exploratory, demonstrate scalability limits
- **High-risk problems**: Show largest improvements from refinement (up to 60%+)
- **Empty precedence**: Often benefits more from refinement than constrained problems

See `main_results.md` for detailed analysis of benchmark results.

## References

- DIDP Framework: https://didp.ai/
- DIDPPy Documentation: https://didppy.readthedocs.io/
- DIDP Models Repository: https://github.com/Kurorororo/didp-models
