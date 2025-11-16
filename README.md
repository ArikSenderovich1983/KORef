# KORef: KO-plan Refinement using DIDP

This implementation solves the KO-plan Refinement (KORef) problem using the DIDP (Dynamic Integer Decision Programming) framework.

## Problem Description

Given a KO-plan `K=(A, ≺, d, p)` where:
- `A` is a set of activities
- `≺` is a partial order (precedence constraints)
- `d` assigns durations to activities
- `p` assigns knock-out probabilities to activities

The goal is to find a refinement `≺'` of `≺` (i.e., `≺ ⊆ ≺'`) that minimizes the expected makespan of the canonical earliest-start schedule, where makespan accounts for stochastic knock-out events.

## Files

- `koref_utils.py`: Core algorithms for computing schedules and expected makespan
- `read_koref.py`: Instance reader and validation utilities
- `koref_domain.py`: DIDP model implementation and solver
- `benchmark.py`: Unified benchmark script for all problem types
- `benchmark_all_problems.py`: Benchmark script for non-empty constraint problems
- `benchmark_empty_constraints.py`: Benchmark script for empty constraint problems
- `test_single_instance.py`: Quick test script
- `test_instance.koref`: Example instance file

## Problem Structure

Problems are organized in the following directory structure:

```
problems/
├── empty/              # Problems with empty initial precedence constraints
│   ├── small/          # 3-5 activities (all files directly here)
│   ├── medium/         # 6-10 activities (all files directly here)
│   └── large/          # 11-15 activities (all files directly here)
└── non_empty/          # Problems with existing precedence constraints
    ├── small/          # 3-5 activities
    │   ├── chain/      # Chain structures
    │   ├── parallel/   # Parallel structures
    │   ├── mixed/      # Mixed structures
    │   └── dag/        # DAG structures
    ├── medium/         # 6-10 activities
    │   ├── chain/
    │   ├── parallel/
    │   ├── mixed/
    │   └── dag/
    └── large/          # 11-15 activities
        ├── chain/
        ├── parallel/
        ├── mixed/
        └── dag/
```

Each problem file is in YAML format and includes:
- Activity definitions (id, name, duration, ko_probability)
- Precedence constraints (list of [predecessor, successor] pairs)
- Metadata (category, difficulty, structure type)

## Instance Format

```
n
duration_0 probability_0
duration_1 probability_1
...
duration_{n-1} probability_{n-1}
m
a_0 b_0
a_1 b_1
...
a_{m-1} b_{m-1}
```

Where:
- `n` is the number of activities (numbered 0 to n-1)
- Each activity has a duration (float) and KO probability (float in [0,1])
- `m` is the number of precedence constraints
- Each constraint `a b` means activity `a` must precede activity `b`

## Usage

### Prerequisites

Install the DIDP Python package (`didppy`):
```bash
pip install didppy
```

### Running the Solver

```bash
python koref_domain.py <instance_file> [options]
```

Options:
- `--time-out`: Time limit in seconds (default: 1800)
- `--history`: History file for search progress (default: history.csv)
- `--config`: Solver configuration (default: Optimal)
  - `Optimal` or `EXHAUSTIVE`: Exhaustively explores all terminal states, computes exact expected makespan for each, returns optimal (guaranteed)
  - `FR` or `ForwardRecursion`: Uses DIDP ForwardRecursion (may not explore all states)
  - Other DIDP solvers: `CABS`, `LNBS`, etc. (heuristic, not guaranteed optimal)
- `--seed`: Random seed (default: 2023)
- `--threads`: Number of threads (default: 1)
- `--initial-beam-size`: Initial beam size (default: 1)
- `--parallel-type`: Parallelization type (default: 0)

### Example

```bash
# Find optimal solution with exact makespan computation
python koref_domain.py problems/non_empty/small/chain/chain_3.yaml --config Optimal --time-out 60

# Use heuristic solver (faster but not guaranteed optimal)
python koref_domain.py problems/non_empty/small/chain/chain_3.yaml --config CABS --time-out 60
```

### Benchmarking

Run benchmarks on all problems:

```bash
# Benchmark all problems (empty and non-empty)
python benchmark.py --type all --time-limit 1800 --output benchmark_all

# Benchmark only empty constraint problems
python benchmark.py --type empty --time-limit 30 --output benchmark_empty

# Benchmark only non-empty constraint problems
python benchmark.py --type non_empty --time-limit 3600 --output benchmark_non_empty
```

Results are saved as CSV and Markdown files with detailed tables showing:
- Original makespan (before refinement)
- Refined makespan (after refinement)
- Improvement percentage
- Runtime
- Optimality status

## Implementation Notes

### State Representation

The DIDP state tracks:
- `unresolved`: Set of unresolved unordered pairs of activities
- `added_constraints`: Set of precedence constraints that have been added

### Transitions

For each unresolved pair `{a, b}`, we can add either:
- `a < b` (activity a precedes b)
- `b < a` (activity b precedes a)

Transitions check that adding the constraint doesn't immediately create a cycle (based on initial precedence).

### Optimal Search with Exact Makespan Computation

The implementation supports **optimal search** with **exact expected makespan computation**:

1. **Exhaustive Search Mode** (`--config Optimal`):
   - Explores all terminal states using BreadthFirstSearch
   - For each terminal state, computes the **exact expected makespan** using the bucket-based algorithm
   - Returns the refinement with minimum expected makespan
   - **Guarantees optimality** (exhaustive exploration)

2. **Expected Makespan Computation**:
   - Uses the exact algorithm from the specification:
     1. Compute canonical earliest-start schedule from precedence relation
     2. Compute abort times for each activity (max finish time of overlapping activities)
     3. Group activities by abort time into buckets
     4. Compute survival probabilities: Q_j = ∏(1-p(a)) for a in bucket j
     5. Compute cumulative probabilities: P_j = ∏Q_i for i=1..j
     6. Apply formula: E[M] = Σ(t_j * P_{j-1} * (1-Q_j)) + T * P_k

3. **Terminal State Evaluation**:
   - When a terminal state is reached (all pairs resolved), the precedence relation is extracted
   - The exact expected makespan is computed using the algorithm above
   - All terminal states are evaluated to find the optimal one

This approach ensures **optimal solutions** with **exact makespan computation** as specified in the LaTeX document.

### Expected Makespan Algorithm

The implementation uses the bucket-based algorithm from the specification:
1. Compute earliest-start schedule from precedence relation
2. Compute abort times for each activity (max finish time of overlapping activities)
3. Group activities by abort time into buckets
4. Compute survival probabilities for each bucket
5. Compute expected makespan using the formula:
   ```
   E[M] = Σ(t_j * P_{j-1} * (1-Q_j)) + T * P_k
   ```

## Validation

The solution is validated by:
1. Checking that refined precedence extends original precedence
2. Checking acyclicity
3. Recomputing expected makespan and comparing with reported value

## References

- DIDP Models Repository: https://github.com/Kurorororo/didp-models.git
- Formal specification: See LaTeX specification provided
