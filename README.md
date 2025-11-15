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
- `test_instance.koref`: Example instance file

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
- `--config`: Solver configuration (default: CABS)
- `--seed`: Random seed (default: 2023)
- `--threads`: Number of threads (default: 1)
- `--initial-beam-size`: Initial beam size (default: 1)
- `--parallel-type`: Parallelization type (default: 0)

### Example

```bash
python koref_domain.py test_instance.koref --config FR --time-out 60
```

## Implementation Notes

### State Representation

The DIDP state tracks:
- `unresolved`: Set of unresolved unordered pairs of activities

### Transitions

For each unresolved pair `{a, b}`, we can add either:
- `a < b` (activity a precedes b)
- `b < a` (activity b precedes a)

Transitions check that adding the constraint doesn't immediately create a cycle (based on initial precedence).

### Cost Computation

**Current Limitation**: The implementation uses zero cost for transitions and computes expected makespan only after extracting the solution. This means:

1. DIDP will find *a* valid refinement, but not necessarily the optimal one
2. For optimal search, expected makespan should be computed during search, which requires more complex state tracking

**Future Improvement**: To enable optimal search, the state should track the current precedence relation and compute expected makespan incrementally. This would require:
- Tracking added constraints in state variables
- Computing schedule and expected makespan in DIDP cost expressions (complex)
- Or using custom cost computation callbacks if supported by DIDP

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
